from utils.api import OpenDataCrawler
import pandas as pd
import datetime
import os


# def crawl_velib(save=False, path=None):
#     dataset='velib-disponibilite-en-temps-reel'
#
#     ##first get total number of rows
#     params={'rows':1}
#     r = get(dataset, **params)
#
#     ##then query all rows
#     params={'rows':r.json()['nhits']}
#     query_datetime=datetime.datetime.now()
#     r = get(dataset, **params)
#
#     data = [record['fields'] for record in r.json()['records']]
#     df = pd.DataFrame(data)
#     df['query_datetime'] = query_datetime
#
#     if save:
#         if not path:
#             dir_path = os.path.dirname(os.path.realpath(__file__))
#             path = dir_path+'/data/velib_dispo_{}.csv'.format(query_datetime.strftime("%Y_%m_%d_%H_%M_%S"))
#         df.to_csv(path)
#     return df

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

dir_path = os.path.dirname(os.path.realpath(__file__))
path = dir_path+'/data/velib_dispo_{}.csv'.format(query_datetime.strftime("%Y_%m_%d_%H_%M_%S"))
df.to_csv(path)
