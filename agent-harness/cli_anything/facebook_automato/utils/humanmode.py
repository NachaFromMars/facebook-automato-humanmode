import random, time

def sleep(a=0.8,b=2.2):
    time.sleep(random.uniform(a,b))

def assert_facebook_url(url:str):
    if 'facebook.com' not in url:
        raise RuntimeError('HUMANMODE_GUARD: target is not facebook.com')
