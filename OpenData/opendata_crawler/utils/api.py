import requests

BASE_URL = 'https://opendata.paris.fr/api/records/1.0/search/'



class OpenDataCrawler:
    def __init__(self, dataset):
        self.dataset = dataset

    def get(self, **params):
        p='&'.join(['{}={}'.format(k,v) for k,v in params.items()])
        url = BASE_URL+'?dataset='+self.dataset+'&'+p
        return requests.get(url)
