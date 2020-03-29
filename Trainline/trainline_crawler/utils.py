import time
import logging
import functools
import inspect
from requests.exceptions import RequestException
import tenacity

def configureLogger(name, level):
    # création de l'objet logger qui va nous servir à écrire dans les logs
    logger = logging.getLogger(name)
    # on met le niveau du logger à DEBUG, comme ça il écrit tout
    logger.setLevel(logging.DEBUG)

    # création d'un formateur qui va ajouter le temps, le niveau
    # de chaque message quand on écrira un message dans le log
    formatter = logging.Formatter('%(asctime)s :: %(message)s')

    # création d'un handler qui va rediriger chaque écriture de log
    # sur la console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level)
    logger.addHandler(stream_handler)

    return logger

class TooManyCallsError(RequestException):
    def __init__(self, *args, **kwargs):
        error_code = kwargs.pop('error_code', None)
        num_requests = kwargs.pop('num_requests', None)
        requests_start_time = kwargs.pop('requests_start_time', None)
        error_type = "TooManyCallsError"
        error_message = "Triggered {} requests in {:.2f}s".format(num_requests, time.time()-requests_start_time)
        super(RequestException, self).__init__(error_code, error_type, error_message, *args, **kwargs)


class LogDecorator(object):
    def __init__(self, name=None):
        self.logger = logging.getLogger(name)

    def __call__(self, fn):
        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            try:
                arg_names = inspect.getfullargspec(fn).args
                if arg_names[0] == 'self':
                    arg_values=list(args)
                    arg_values[0] = 'self'
                    arg_values = tuple(arg_values)
                self.logger.debug("Entering {0}: args = {1} kwargs = {2}".format(fn.__qualname__, arg_values, kwargs))
                result = fn(*args, **kwargs)
                self.logger.debug("Exiting {0}: ouput = {1}".format(fn.__qualname__,result))
                return result
            except Exception as ex:
                self.logger.debug("Exception {0}".format(ex))
                raise ex
            return result
        return decorated

def retry(max_waiting_time):
    return tenacity.retry(
        reraise = True,
        stop=tenacity.stop_after_delay(max_waiting_time),
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=max_waiting_time),
        retry=tenacity.retry_if_exception_type(TooManyCallsError)
    )
