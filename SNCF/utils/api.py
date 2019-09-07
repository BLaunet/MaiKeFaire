import requests
import json
from datetime import date, timedelta

def generateInitialWishId(origin, destination, date, discountCard="NONE"):
    """
    Get the initial wishId for a travel from origin to destination
    """
    outward = date.strftime("%Y-%m-%dT05:00:00")
    initialPayload = {
        "mainJourney": {
            "origin": origin,
            "destination": destination,
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
                    "code": discountCard,
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
    r = requests.post('https://www.oui.sncf/wishes-api/wishes', json=initialPayload)
    return r.json()['id']

def getWishObject(wishId):
    """
    Get proper wish Object that will be used to get travel propositions
    """
    r = requests.get('https://www.oui.sncf/proposition/rest/wishes/{}'.format(wishId))
    return r.json()

def getFirstProposals(wish):
    """
    Returns first train proposals for a new wish
    """
    payload = {
        'context': {},
        'wish':wish
    }
    r = requests.post('https://www.oui.sncf/proposition/rest/travels/outward/train', json=payload)
    return r.json()['travelProposals'], r.json()['nextPagination']

def getNextProposals(wish, proposals=None):
    payload = {'wish': wish}
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
    r = requests.post('https://www.oui.sncf/proposition/rest/travels/outward/train/next', json=payload)
    try:
        return r.json()['travelProposals'], r.json()['nextPagination']
    except:
        print(r.status_code, r.json())
        return None, None

def getNextDayWish(wish):
    payload = {
        'context': {},
        'wish':wish
    }
    r = requests.post('https://www.oui.sncf/proposition/rest/wishes/next-day', json=payload)
    return r.json()

def simplifyOffers(travelProposals):
    """
    Parses the proposals to focus on the actual offers
    """
    offers = []
    for travelProposal in travelProposals:
        offer={}
        offer['departureDate'] = travelProposal['departureDate']
        offer['arrivalDate'] = travelProposal['arrivalDate']
        offer['trainNumber'] = travelProposal['segments'][0]['vehicleNumber']
        offer['firstClassMinPrice'] = travelProposal['firstClassOffers']['minPrice']
        offer['secondClassMinPrice'] = travelProposal['secondClassOffers']['minPrice']

        offers.append(offer)
    return offers
