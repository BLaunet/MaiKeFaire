#!/usr/bin/env python3
import datetime
import argparse
from pathlib import Path
from trainline_crawler.crawler import TrainlineCrawler
from trainline_crawler.discountCards import discountCards

parser = argparse.ArgumentParser(description='Crawls Trainline website and save as a csv')
parser.add_argument('--data_dir', help='Absolute path of the directory where to save the csv. Defaults to ./data', type=str, default='./data')
parser.add_argument('--origin', help='City of origin', type=str, default='Paris')
parser.add_argument('--destination', help='City of destination', type=str, default='Annecy')
parser.add_argument('--discountCard', help='SNCF.AvantageJeune', type=str, default=discountCards.CARTE_JEUNE)
parser.add_argument('--nr_of_days', help='Number of days to crawl in the future', type=int, default=60)
parser.add_argument('--max_waiting_time', help='Time to wait in seconds between each http request', type=int, default=20)
parser.add_argument('--debug', help='Turn on debug mode', type=str, default='INFO')


args = parser.parse_args()

def crawl_trip(data_dir, origin, destination, discountCard, nr_of_days, max_waiting_time, debug):
    trip = TrainlineCrawler(origin, destination, discountCard, max_waiting_time=max_waiting_time, log_level=debug)
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=nr_of_days)
    offers = trip.getProposals(start_date, end_date)
    query_datetime = datetime.datetime.now()
    offers.loc[:, "query_datetime"] = query_datetime
    data_dir = Path(data_dir) / '{}_{}'.format(trip.origin.slug, trip.destination.slug)
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
    path = data_dir / "{}.csv".format(query_datetime.strftime("%Y_%m_%d_%H_%M"))
    offers.to_csv(path, index=False)

if __name__ == "__main__":
    crawl_trip(**vars(args))
