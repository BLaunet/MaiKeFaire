import requests
import logging
from trainline_crawler.utils import configureLogger, LogDecorator

class Station:
    _base_url = 'https://www.trainline.fr/api/v5_1/stations?context=search&q={}'
    _logger_name = "trainline-logger"

    @LogDecorator(_logger_name)
    def __init__(self, city_name):
        logger = logging.getLogger(self._logger_name)
        r = requests.get(self._base_url.format(city_name))
        if r.ok:
            try:
                self.__dict__ = r.json()['stations'][0]
                logger.debug("Found station: {}".format(self.name))
            except:
                raise ValueError(r.json())
        else:
            raise ValueError(r.status_code)
    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return self.__str__()
