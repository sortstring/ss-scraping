import os
import json


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UNIVERSITY_FILE1 = os.path.join(BASE_DIR, 'cachefiles/universities1.json')
UNIVERSITY_FILE = os.path.join(BASE_DIR, 'cachefiles/universities.json')


if os.path.exists(UNIVERSITY_FILE1):
    with open(UNIVERSITY_FILE1, 'r') as f:
        UNIVERSITIES1 = json.load(f)
else:
    UNIVERSITIES1 = {}


if os.path.exists(UNIVERSITY_FILE):
    with open(UNIVERSITY_FILE, 'r') as f:
        UNIVERSITIES = json.load(f)
else:
    UNIVERSITIES = {}


for key in UNIVERSITIES1:
    if key not in UNIVERSITIES:
        UNIVERSITIES[key] = UNIVERSITIES1[key]

with open(UNIVERSITY_FILE, 'w') as f:
    json.dump(UNIVERSITIES, f, indent=4)
    print('File written successfully')
