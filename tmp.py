from random import random
from functools import wraps
from time import sleep

def retry(*, retry_times=5, max_wait_second=5, errors=(Exception,)):

    def decorate(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(retry_times):
                try:
                    func(*args, **kwargs)
                except errors:
                    sleep(random()*max_wait_second)
            return None
            
        return wrapper
    
    return decorate



def singleton(cls):

    instance = {}

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instance:
            return instance[cls] = cls(*args, **kwargs)
        return instance[cls]

    return wrapper