import requests
import json
import datetime

def parse_date(date):
    if not date:
        return None
    if not isinstance(date, datetime.date):
        try:
            if isinstance(date, str):
                date = datetime.date.fromisoformat(date)
            elif isinstance(date, datetime.datetime):
                date = date.date()
            else:
                raise ValueError(type(date))
        except ValueError:
            raise ValueError("Accepted date types: datetime.date, datetime.datetime, or string in ISO format")
    return date

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
        try:
            offer['firstClassMinPrice'] = travelProposal['firstClassOffers']['minPrice']
        except:
            offer['firstClassMinPrice'] = None
        try:
            offer['secondClassMinPrice'] = travelProposal['secondClassOffers']['minPrice']
        except:
            offer['secondClassMinPrice'] = None

        offers.append(offer)
    return offers
