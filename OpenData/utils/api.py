import requests

BASE_URL = 'https://opendata.paris.fr/api/records/1.0/search/'

def get(dataset, **params):
    p='&'.join(['{}={}'.format(k,v) for k,v in params.items()])
    url = BASE_URL+'?dataset='+dataset+'&'+p
    return requests.get(url)
