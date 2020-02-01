import datetime
import logging
import requests
import json
import pandas as pd
from pathlib import Path
import time
from sncf_crawler.city import City
from sncf_crawler.utils.functions import parse_date, simplifyOffers
from sncf_crawler.utils.logger import configureLogger
from sncf_crawler.discountCards import discountCards

logger = configureLogger(logging.INFO)

class SncfCrawler:
    BASE_URL = "https://www.oui.sncf/{}"
    def __init__(self, origin, destination, discountCard=None, wait=30):
        self._wait = int(wait)
        self.origin = City(origin)
        time.sleep(self._wait)
        self.destination = City(destination)
        self.discountCard = discountCard if discountCard else discountCards.SANS_CARTE

    def getProposals(self, startDate, endDate=None):
        self.startDate = parse_date(startDate)
        self.endDate = parse_date(endDate)
        daysSpan = (self.endDate-self.startDate).days+1 if self.endDate else 1
        logger.debug("Number of days to query: %s"%daysSpan)

        self.queryDate = datetime.datetime.now()

        results = []
        while True:
            self._wish = self._getWishObject(self._generateInitialWishId())
            time.sleep(self._wait)
            logger.debug("Original wish: {}".format(json.dumps(self._wish, indent=2)))
            proposals, nextPagination = self._getFirstProposals()
            if not proposals:
                self.startDate+=datetime.timedelta(days=1)
                daysSpan-=1
                if daysSpan <= 0:
                    raise ValueError("No offer found for these dates")
            else:
                break
        results+=simplifyOffers(proposals)
        days=1
        while days < daysSpan:
            time.sleep(self._wait)
            if nextPagination['type'] == 'NEXT_HOUR':
                proposals, nextPagination = self._getNextProposals(proposals)
            if nextPagination['type'] == 'NEXT_DAY':
                self._wish = self._getNextDayWish()
                proposals, nextPagination = self._getFirstProposals()
                days+=1
            results+=simplifyOffers(proposals)
        self.offers = pd.DataFrame(results)
        self.offers['queryDate'] = self.queryDate
        self.offers['origin'] = self.origin.label
        self.offers['origin_id'] = self.origin.code
        self.offers['destination'] = self.destination.label
        self.offers['destination_id'] = self.destination.code
        return self.offers

    def _generateInitialWishId(self):
        """
        Get the initial wishId for a travel from origin to destination
        """
        outward = self.startDate.strftime("%Y-%m-%dT05:00:00")
        initialPayload = {
            "mainJourney": {
                "origin": self.origin.code,
                "destination": self.destination.code,
                "via": None
            },
            "directTravel": True,
            "schedule": {
                "outward": outward,
                "outwardType": "DEPARTURE_FROM",
                "inward": None,
                "inwardType": "DEPARTURE_FROM"
            },
            "travelClass": "SECOND",
            "passengers": [
                {
                    "firstname": "",
                    "lastname": "",
                    "typology": "ADULT",
                    "customerId": "",
                    "discountCard": {
                        "code": self.discountCard,
                        "number": ""
                    },
                    "fidelityCard": {
                        "type": "NONE",
                        "number": ""
                    },
                    "promoCode": "",
                    "bicycle": None
                }
            ],
            "checkBestPrices": False,
            "salesMarket": "fr-FR",
            "pets": [

            ],
            "codeFce": None
        }

        #get wish_id
        r = requests.post(SncfCrawler.BASE_URL.format('wishes-api/wishes'), json=initialPayload)
        return r.json()['id']

    def _getWishObject(self, wishId):
        """
        Get proper wish Object that will be used to get travel propositions
        """
        r = requests.get(SncfCrawler.BASE_URL.format('proposition/rest/wishes/{}'.format(wishId)))
        return r.json()

    def _getFirstProposals(self):
        """
        Returns first train proposals for a new wish
        """
        payload = {
            'context': {},
            'wish':self._wish
        }
        r = requests.post(SncfCrawler.BASE_URL.format('proposition/rest/travels/outward/train'), json=payload)
        try:
            return r.json()['travelProposals'], r.json()['nextPagination']
        except:
            return None, None

    def _getNextProposals(self, proposals=None):
        payload = {'wish': self._wish}
        if proposals:
            latestProposal = proposals[-1]
            context = {
                "paginationContext":{
                    "travelSchedule":{
                        "departureDate": latestProposal["departureDate"],
                        "arrivalDate": latestProposal["arrivalDate"]
                    }
                }
            }
        else:
            context = {

            }
        payload['context'] = context
        r = requests.post(SncfCrawler.BASE_URL.format('proposition/rest/travels/outward/train/next'), json=payload)
        try:
            return r.json()['travelProposals'], r.json()['nextPagination']
        except:
            print(r.status_code, r.json())
            return None, None

    def _getNextDayWish(self):
        payload = {
            'context': {},
            'wish':self._wish
        }
        r = requests.post(SncfCrawler.BASE_URL.format('proposition/rest/wishes/next-day'), json=payload)
        return r.json()
