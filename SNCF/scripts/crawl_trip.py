#!/usr/bin/env python3
import datetime
import argparse
from pathlib import Path
from sncf_crawler.crawler import SncfCrawler
from sncf_crawler.discountCards import discountCards

parser = argparse.ArgumentParser(description='Crawls Oui.sncf website and save as a csv')
parser.add_argument('--data_dir', help='Absolute path of the directory where to save the csv. Defaults to ./data', type=str, default='./data')
parser.add_argument('--origin', help='City of origin', type=str, default='Paris')
parser.add_argument('--destination', help='City of destination', type=str, default='Annecy')
parser.add_argument('--discountCard', help='SANS_CARTE or YOUNGS', type=str, default='YOUNGS')
parser.add_argument('--nr_of_days', help='Number of days to crawl in the future', type=int, default=60)


args = parser.parse_args()

def crawl_trip(data_dir, origin, destination, discountCard, nr_of_days):
    trip = SncfCrawler(origin, destination, discountCard)
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=nr_of_days)
    _ = trip.getProposals(start_date, end_date)
    data_dir = Path(data_dir) / '{}_{}'.format(trip.origin.code, trip.destination.code)
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
    path = data_dir / "{}.csv".format(datetime.date.today().strftime("%Y_%m_%d_%H_%M"))
    trip.offers.to_csv(path, index=False)

if __name__ == "__main__":
    crawl_trip(**vars(args))
