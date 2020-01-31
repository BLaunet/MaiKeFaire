import requests

class City:
    _base_url = "https://www.oui.sncf/booking/autocomplete-d2d?uc=fr-FR&searchField=origin&searchTerm={}"
    def __init__(self, city_name):
        self.name = str(city_name).capitalize()
        try:
            self._request = requests.get(City._base_url.format(self.name))
        except e:
            raise requests.exceptions.ConnectionError(e)
        if self._request.status_code != 200:
            raise requests.exceptions.RequestException(self._request.status_code, self.requests.text)
        if len(self._request.json()) == 0:
            raise NameError('Unknown city name: {}'.format(city_name))
        else:
            try:
                station = next(match for match in self._request.json() if match["category"] == "station")
            except StopIteration as e:
                raise NameError('Not train station found for {}.\nBest result was {}'.format(self.name, self._request.json()[0]))
            self.code = station['id']
            self.label = station['label']
            # logger.info("City {} initialized with label {}".format(self.name, self.label))
