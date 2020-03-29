from trainline_crawler.utils import configureLogger, LogDecorator
from trainline_crawler.station import Station
from trainline_crawler.crawler import TrainlineCrawler
import logging
import datetime
import pytz


if __name__ == "__main__":
    logger = configureLogger("trainline-logger", "DEBUG")
    discountCard = 'SNCF.AvantageJeune'
    start_date = datetime.datetime(2020, 3, 30, 4, tzinfo=pytz.timezone('CET'))
    #end_date = datetime.datetime(2020, 4, 1, tzinfo=pytz.timezone('CET'))
    crawler = TrainlineCrawler("paris", "auray", discountCard)
    response = crawler.getProposals(start_date)
