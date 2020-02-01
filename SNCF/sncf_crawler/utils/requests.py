import requests
import time

SLEEP_TIME=5
def wait(waiting_time):
    def timer(func):
        def wrapped(*args, **kwargs):
            time.sleep(waiting_time)
            return func(*args, **kwargs)
        return wrapped
    return timer

@wait(SLEEP_TIME)
def post(url, **kwargs):
    return requests.post(url, **kwargs)

@wait(SLEEP_TIME)
def get(url):
    return requests.get(url)
