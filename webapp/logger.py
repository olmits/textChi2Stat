import logging
from functools import wraps


def function_logger(foo):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur
    """

    @wraps(foo)
    def wrapper(*args, **kwargs):
        res = None
        args_str = ', '.join(map(str, args))
        kwargs_str = ';'.join('{0}={1}'.format(k, v) for k, v in kwargs.items()) or ''
        try:
            res = foo(*args, **kwargs)
        except Exception as error:
            log.exception('Error: {0}'.format(error))

        log.info('Foo: {0} runs with \n\targs: {1}\n\tkwargs: {2}'.format(foo.__name__, args_str, kwargs_str))
        return res
    return wrapper


level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(level)
logFormatter = logging.Formatter("__%(asctime)s %(levelname)s in %(module)s: %(message)s")

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(level)
consoleHandler.setFormatter(logFormatter)
log.addHandler(consoleHandler)
