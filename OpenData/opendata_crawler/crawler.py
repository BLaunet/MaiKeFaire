import requests

class OpenDataCrawler:
    BASE_URL = 'https://opendata.paris.fr/api/records/1.0/search/'

    def __init__(self, dataset):
        self.dataset = dataset

    def get(self, **params):
        p='&'.join(['{}={}'.format(k,v) for k,v in params.items()])
        url = OpenDataCrawler.BASE_URL+'?dataset='+self.dataset+'&'+p
        return requests.get(url)
