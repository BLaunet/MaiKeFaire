#!/usr/bin/env python3
from opendata_crawler.utils.api import OpenDataCrawler
import pandas as pd
import datetime
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(description='Crawls https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel and save as a csv')
parser.add_argument('--data_dir', help='absolute path of the directory where to save the csv. default to ./data', type=str)
args = parser.parse_args()

def crawl_velib_dispo(data_dir=None):
    velib_crawler = OpenDataCrawler('velib-disponibilite-en-temps-reel')
    ##first get total number of rows
    params={'rows':1}
    r = velib_crawler.get(**params)

    ##then query all rows
    params={'rows':r.json()['nhits']}
    query_datetime=datetime.datetime.now()
    r = velib_crawler.get(**params)

    data = [record['fields'] for record in r.json()['records']]
    df = pd.DataFrame(data)
    df['query_datetime'] = query_datetime

    if not data_dir:
        data_dir = Path('./data')
    else:
        data_dir = Path(data_dir)
    if not data_dir.exists():
        data_dir.mkdir()
    path = data_dir / "velib_dispo_{}.csv".format(query_datetime.strftime("%Y_%m_%d_%H_%M"))
    df.to_csv(path, index=False)

if __name__ == "__main__":
    crawl_velib_dispo(**vars(args))
