from utils import get
import pandas as pd
import datetime

def crawl_velib():
    dataset='velib-disponibilite-en-temps-reel'

    ##first get total number of rows
    params={'rows':1}
    r = get(dataset, **params)

    ##then query all rows
    params={'rows':r.json()['nhits']}
    query_datetime=datetime.datetime.now()
    r = get(dataset, **params)

    data = [record['fields'] for record in r.json()['records']]
    df = pd.DataFrame(data)
    df['query_datetime'] = query_datetime
    return df
