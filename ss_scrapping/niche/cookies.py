from datetime import datetime, timedelta
import json
from . import helper

BASE_DIR = helper.os.path.abspath(helper.os.path.dirname(__file__))
COOKIIES_RAW = helper.os.path.join(BASE_DIR, 'cookies_raw.json')
if helper.os.path.exists(COOKIIES_RAW):
    with open(COOKIIES_RAW, 'r') as f:
        cookies_list = json.loads(f.read())
else:
    cookies_list = ''


def get_cookies():
    # cookies_list = json.loads(cookies)  # Assuming 'cookies' is a valid JSON string.
    for item in cookies_list:
        if 'sameSite' in item and (not item['sameSite'] or item['sameSite'] in ['no_restriction', 'unspecified']):
            item['sameSite'] = 'None'
        elif 'sameSite' in item and item['sameSite'] == 'lax':
            item['sameSite'] = 'Lax'


    return cookies_list