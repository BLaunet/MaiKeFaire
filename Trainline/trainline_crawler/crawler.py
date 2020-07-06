import requests
import datetime
import pytz
import pandas as pd
import numpy as np
import time
from requests.exceptions import RequestException
from trainline_crawler.utils import retry, configureLogger, LogDecorator, TooManyCallsError, NoResultError, TimeoutError
from trainline_crawler.station import Station

class TrainlineCrawler:
    _base_url = 'https://www.trainline.fr/api/v5_1/search'
    _headers = {
          'authority': 'www.trainline.fr',
          'x-ct-client-id': '209d46bc-ae4f-4561-aadf-3b31e111a424',
          'x-user-agent': 'CaptainTrain/1583932639(web) (Ember 3.5.1)',
          'x-not-a-bot': 'i-am-human',
          'accept-language': 'fr-FR,fr;q=0.8',
          'x-ct-version': '5a0666876d9bf96c03d54eb204030e56b820a05d',
          'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
          'content-type': 'application/json; charset=UTF-8',
          'accept': 'application/json, text/javascript, */*; q=0.01',
          'sec-fetch-dest': 'empty',
          'x-ct-locale': 'fr',
          'x-requested-with': 'XMLHttpRequest',
          'x-ct-timestamp': '1583932639',
          'origin': 'https://www.trainline.fr',
          'sec-fetch-site': 'same-origin',
          'sec-fetch-mode': 'cors',
          'referer': 'https://www.trainline.fr/'
        }
    _logger_name = "trainline-logger"
    def __init__(self, origin, destination, discountCard, max_waiting_time=20, log_level='INFO'):
        self.logger = configureLogger(self._logger_name, log_level)
        self.origin = Station(origin)
        self.destination = Station(destination)
        self.discountCard = discountCard
        self.set_max_waiting_time(max_waiting_time)
        self.logger.info("Initialized trip {} -> {}".format(self.origin.name, self.destination.name))

    def set_max_waiting_time(self, max_waiting_time):
        self.max_waiting_time = max_waiting_time
        self.logger.debug("Setting waiting time: %ss"%self.max_waiting_time)
        self.request_trainline = retry(self.max_waiting_time)(self._request_trainline)

    def getProposals(self, start_date, end_date=None):
        self.request_counter = 0
        self.query_start_time = time.time()

        self.proposals = []

        if (not isinstance(start_date, datetime.datetime))\
            and not isinstance(start_date, datetime.date):
            raise TypeError(start_date, "start date must be datetime.datetime or datetime.date")
        if (isinstance(start_date, datetime.date)) and (not isinstance(start_date, datetime.datetime)):
            self.start_date = datetime.datetime(start_date.year, start_date.month, start_date.day)
        else:
            self.start_date = start_date
        if not self.start_date.tzinfo:
            self.start_date = self.start_date.replace(tzinfo=pytz.timezone('CET'))


        if not end_date:
            self.end_date = datetime.datetime(self.start_date.year, self.start_date.month, self.start_date.day) + datetime.timedelta(days=1)
        elif (not isinstance(end_date, datetime.datetime))\
            and not isinstance(end_date, datetime.date):
            raise TypeError(end_date, "start date must be datetime.datetime or datetime.date")
        elif (isinstance(end_date, datetime.date)) and (not isinstance(end_date, datetime.datetime)):
            self.end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)
        else:
            self.end_date = end_date
        if not self.end_date.tzinfo:
            self.end_date = self.end_date.replace(tzinfo=self.start_date.tzinfo)

        self.logger.info("Getting proposals between {} and {}".format(self.start_date, self.end_date))

        date = self.start_date
        is_next_available = False
        while date <= self.end_date:
            try:
                if is_next_available:
                    response = self.request_trainline(search["id"], next=True)
                else:
                    self.logger.info("Requesting with start_date = {}".format(date))
                    response = self.request_trainline(date)
            except NoResultError:
                self.logger.info("Found no result, pushing date by 12 hours")
                date+=datetime.timedelta(hours=12)
                continue

            # getting latest time we got. We need to make sure to move forward, so pushing time by 15 minutes if
            times = [trip["departure_date"] for trip in response["trips"]]
            max_date = max([datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S%z') for time in times])
            if max_date > date:
                date = max_date
            else:
                date += datetime.timedelta(minutes=30)

            search = response["search"]
            is_next_available=search["is_next_available"]
            if not is_next_available:
                try:
                    proposals = self.make_proposal(response)
                except Exception as e:
                    raise Exception(response) from e
                self.proposals.append(proposals)

        self.logger.info("Got all proposals by making {} HTTP requests in {:.2f}s".format(self.request_counter, time.time() - self.query_start_time))
        # transform response in proposals
        try:
            proposals = self.make_proposal(response)
        except Exception as e:
            raise Exception(response) from e
        self.proposals.append(proposals)
        # merge all proposals, drop duplicates
        self.proposals = pd.concat(self.proposals,ignore_index=True).drop_duplicates().reset_index(drop=True)
        # keeping relevant things
        self.proposals = self.proposals[(self.proposals["departure_date"] >= self.start_date) & (self.proposals["departure_date"] <= self.end_date)]
        self.logger.info("Found {} direct trips".format(len(self.proposals.index)))
        return self.proposals

    def format_date(self, date):
        return date.astimezone(pytz.UTC).strftime('%Y-%m-%dT%H:%M:%SUTC')

    @LogDecorator(_logger_name, output=False)
    def _request_trainline(self, param, next=False):
        self.request_counter+=1
        if next:
            # param is search_id
            response = self._make_next_request(param)
        else:
            # param is date
            response = self._make_initial_request(param)

        if response.status_code == 429:
            raise TooManyCallsError(error_code = 429, num_requests = self.request_counter, requests_start_time=self.query_start_time)
        if response.status_code == 400:
            self.logger.error("Got 400 error with response: {}".format(response.text))
            error_code = response.json()["code"]
            # if the error is "no result", raising custom error to carry on
            if error_code == "no_results":
                raise NoResultError("No Results")
            # if error is timeout, we want to retry so raising custom error
            elif error_code == "timeout":
                raise TimeoutError("Timeout")
            # if it's something different, raising 400
            else:
                raise RequestException(400, "sent param", param)
        return response.json()

    @LogDecorator(_logger_name)
    def _make_initial_request(self, date):
        self.logger.debug("Making initial request with start_date = {}".format(self.format_date(date)))

        payload = "{\"search\":{\"departure_date\":\"%s\",\"return_date\":null,\"passengers\":[{\"id\":\"b5966fff-a11a-4508-92de-5551c154d5c9\",\"label\":\"adult\",\"age\":26,\"cards\":[{\"reference\":\"%s\"}],\"cui\":null}],\"systems\":[\"sncf\",\"db\",\"idtgv\",\"ouigo\",\"trenitalia\",\"ntv\",\"hkx\",\"renfe\",\"cff\",\"benerail\",\"ocebo\",\"westbahn\",\"leoexpress\",\"locomore\",\"busbud\",\"flixbus\",\"distribusion\",\"cityairporttrain\",\"obb\",\"timetable\"],\"exchangeable_part\":null,\"source\":null,\"is_previous_available\":false,\"is_next_available\":false,\"departure_station_id\":\"%s\",\"via_station_id\":null,\"arrival_station_id\":\"%s\",\"exchangeable_pnr_id\":null}}"%(self.format_date(date), self.discountCard, self.origin.id, self.destination.id)

        return requests.post(self._base_url, headers=self._headers, data = payload)
    @LogDecorator(_logger_name)
    def _make_next_request(self, search_id):
        self.logger.debug("Making next request with search_id = {}".format(search_id))
        url = self._base_url+'/{}/next'.format(search_id)
        return requests.get(url, headers=self._headers)
    def make_proposal(self, response):
        # defining trip columns
        columns = [
            "departure_date",
            "departure_station_name",
            "arrival_date",
            "arrival_station_name",
            "price",
            "currency",
            "train_name",
            "train_number",
            "travel_class",
            "short_unsellable_reason",
            "carrier",
            "co2_emission",
            "departure_station_id",
            "departure_station_latitude",
            "departure_station_longitude",
            "departure_station_country",
            "arrival_station_id",
            "arrival_station_latitude",
            "arrival_station_longitude",
            "arrival_station_country",
        ]

        trips = pd.DataFrame(response["trips"])
        stations = pd.DataFrame(response["stations"])
        segments = pd.DataFrame(response["segments"])

        # keeping only direct trips
        trips = trips[trips["segment_ids"].apply(lambda l: len(l)) == 1]
        if trips.empty:
            return pd.DataFrame(columns=columns)

        trips.loc[:, "segment_id"] = trips["segment_ids"].apply(lambda l: l[0])
        trips.loc[:, "price"] = trips["cents"]/100.
        # sometimes, short_unsellable_reason is not present - we add it for consistency
        if 'short_unsellable_reason' not in trips.columns:
            trips.loc[:, "short_unsellable_reason"] = None
        trips.loc[trips['short_unsellable_reason'].notna(), 'price'] = np.nan
        trips = trips[[
            "departure_date",
            "departure_station_id",
            "arrival_date",
            "arrival_station_id",
            "price",
            "currency",
            "short_unsellable_reason",
            "segment_id"
        ]]
        trips = trips.astype({'departure_station_id': 'str', 'arrival_station_id': 'str'})
        trips["departure_date"] = pd.to_datetime(trips["departure_date"], format="%Y-%m-%dT%H:%M:%S%z")
        trips["arrival_date"] = pd.to_datetime(trips["arrival_date"], format="%Y-%m-%dT%H:%M:%S%z")
        # add station_names
        stations_columns = [
            "id",
            "name",
            "latitude",
            "longitude",
            "country"
        ]
        stations = stations[stations_columns]
        stations = stations.astype({'id': 'str'})
        # departure stations
        stations.set_axis(['departure_station_{}'.format(col) for col in stations_columns], axis=1, inplace=True)
        trips = trips.merge(
            stations,
            on="departure_station_id",
            how="left"
        )
        # arrival stations
        stations.set_axis(['arrival_station_{}'.format(col) for col in stations_columns], axis=1, inplace=True)
        trips = trips.merge(
            stations,
            on="arrival_station_id",
            how="left"
        )
        # add segment details
        segments.loc[:, "segment_id"] = segments["id"]
        segments = segments[[
            "segment_id",
            "carrier",
            "co2_emission",
            "train_name",
            "train_number",
            "travel_class"
        ]]

        trips = trips.merge(
            segments,
            on="segment_id",
            how="left"
        )

        # reordering for lisibility
        trips = trips[columns]
        trips.drop_duplicates(inplace=True)

        min_price = trips.groupby(
            [
                "departure_station_id",
                "departure_date",
                "arrival_station_id",
                "arrival_date",
                "travel_class"
            ])["price"].rank(method='min')
        trips = trips[(min_price == 1) | (min_price.isna())]
        return trips
