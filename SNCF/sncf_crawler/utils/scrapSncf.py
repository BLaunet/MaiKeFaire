from utils.api import *
import pandas as pd
import logging
import json
logger = logging.getLogger()
def generateTrainOffers(origin, destination, startDate, endDate, discountCard="NONE"):
    daysSpan = (endDate-startDate).days
    logger.info("Number of days to query: %s"%daysSpan)
    results = []
    wishId = generateInitialWishId(origin, destination, startDate, discountCard)
    wish = getWishObject(wishId)
    logger.info("Original wish:")
    logger.info(json.dumps(wish, indent=2))
    offers, nextPagination = getFirstProposals(wish)
    results+=simplifyOffers(offers)

    days=0
    while days < daysSpan:
        if nextPagination['type'] == 'NEXT_HOUR':
            offers, nextPagination = getNextProposals(wish, offers)
        if nextPagination['type'] == 'NEXT_DAY':
            wish = getNextDayWish(wish)
            offers, nextPagination = getFirstProposals(wish)
            days+=1
        results+=simplifyOffers(offers)

    return pd.DataFrame(results)
