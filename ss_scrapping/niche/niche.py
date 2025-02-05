from multiprocessing import Pool
import logging
import requests
import pickle
import random
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha
from .utils import *
from . import helper
from .cookies import get_cookies
import concurrent.futures

solver = TwoCaptcha('9acdf0d598b74edfa9eaf8f32f444f16')

RETRIES = 3

USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
    # Add more user agents as needed
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = helper.os.path.abspath(helper.os.path.dirname(__file__))
CACHE_FILE = helper.os.path.join(BASE_DIR, 'cachefiles/cache.pkl')
LAST_UPDATED_FILE = helper.os.path.join(BASE_DIR, 'cachefiles/last_updated.txt')
CHROMEDRIVER = helper.os.path.join(BASE_DIR, '../chromedriver/chromedriver')

# Load cache from disk
if helper.os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'rb') as f:
        cache = pickle.load(f)
else:
    cache = {}

if helper.os.path.exists(LAST_UPDATED_FILE):
    with open(LAST_UPDATED_FILE, 'r') as f:
        last_updated = json.loads(f.read())
else:
    last_updated = {}

chrome_options = Options()
# chrome_options.add_argument(r"--user-data-dir=C:\Users\hp\AppData\Local\Google\Chrome\User Data")
# chrome_options.add_argument("--profile-directory=Default")
# chrome_options.add_argument("--user-data-dir=/home/sortstring/.config/google-chrome")
# chrome_options.add_argument("--profile-directory=Default")
# chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("User-Agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--enable-unsafe-swiftshader")

chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--ignore-gpu-blacklist")
chrome_options.add_argument("--enable-webgl")
chrome_options.add_argument("--enable-accelerated-2d-canvas")
chrome_options.add_argument("--disable-software-rasterizer")

chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
service = Service(CHROMEDRIVER)
driver = webdriver.Chrome(service=service, options=chrome_options)


def main():
    page = 1
    count_of_universities = 0
    all_universities = []
    while True:
        url = f"https://www.niche.com/colleges/search/top-public-universities/?page={page}"
        home_page, is_cache = get_home_page(page)
        if not home_page or helper.page_not_found(home_page):
            logger.error(f"Failed to retrieve the page {url}. Exiting...")
            break

        count_of_pages_in_html_content = helper.get_count_of_pages_in_html_content(home_page)
        if not count_of_pages_in_html_content:
            logger.error(f"Failed to retrieve the count of universities on the page {url}. Exiting...")
            del cache[url]
            del last_updated[url]
            break

        if page > count_of_pages_in_html_content:
            logger.info(f"There are only {count_of_pages_in_html_content} pages. Exiting...")
            break

        logger.info(f"Processing page {page} of {count_of_pages_in_html_content}")
        universities = helper.get_university_list(home_page)
        if not universities:
            logger.error(f"Failed to retrieve the list of universities on the page {url}. Exiting...")
            del cache[url]
            del last_updated[url]
            break

        for_loop_break = False
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for university in universities:
                university_url = university['href']
                university_name = university['aria-label']
                logger.info(f"Processing university: {university_name} at {university_url}")
                university, is_cache = get_university_home_page(university_url)
                if not university:
                    logger.error(f"Failed to retrieve the page {university_url}. Skipping...")
                    for_loop_break = True
                    break
                count_of_universities += 1
                if not is_cache:
                    import random
                    executor.submit(update_cacahe_and_last_updated())
                all_universities.append(process_university(university, university_url))


        if for_loop_break:
            break

        logger.info(f"Processed {count_of_universities} universities so far. On page {page} of {count_of_pages_in_html_content}")
        page += 1
    save_cache()
    save_last_updated()
    with open('niche.json', 'w') as f:
        json.dump(all_universities, f, indent=4)
    return

def update_cacahe_and_last_updated():
    save_cache()
    save_last_updated()
    return

def process_university(university_home_page, university_url):
    # basic_info = get_basic_info(university_home_page)
    # niche_grades = get_niche_grades(university_home_page)
    # ranking_info = get_rankings(university_home_page)
    # admission_info = get_admission_requirements(university_home_page)
    # cost_info = get_cost_info(university_home_page)
    # academics_info = get_academics_info(university_home_page)
    # student_info = get_student_info(university_home_page)
    # outcome_info = get_outcome(university_home_page)

    with Pool() as pool:
        tasks = [
            pool.apply_async(get_basic_info, args=(university_home_page,)),
            pool.apply_async(get_niche_grades, args=(university_home_page,)),
            pool.apply_async(get_rankings, args=(university_home_page,)),
            pool.apply_async(get_admission_requirements, args=(university_home_page,)),
            pool.apply_async(get_cost_info, args=(university_home_page,)),
            pool.apply_async(get_academics_info, args=(university_home_page,)),
            pool.apply_async(get_student_info, args=(university_home_page,)),
            pool.apply_async(get_outcome, args=(university_home_page,))
        ]

        results = [task.get() for task in tasks]

    basic_info, niche_grades, ranking_info, \
        admission_info, cost_info, academics_info, \
            student_info, outcome_info = results

    return {
        "basic_info": basic_info,
        "niche_grades": niche_grades,
        "rankings": ranking_info,
        "admissions": admission_info,
        "costs": cost_info,
        "academics": academics_info,
        "student_life": student_info,
        "outcomes": outcome_info,
        "metadata": {
            "source": "Niche.com",
            "last_updated": last_updated[university_url]
        }
    }



def get_home_page(page, retries=0):
    url = f"https://www.niche.com/colleges/search/top-public-universities/?page={page}"
    home_page, is_cache = get_html_content(url)
    if not home_page and retries < RETRIES:
        logger.error(f"Failed to retrieve the page: {url}. Retrying...")
        return get_home_page(page, retries + 1)
    return home_page, is_cache

def get_university_home_page(university_url, retries=0):
    home_page, is_cache = get_html_content(university_url, university_home=True)
    if not home_page and retries < RETRIES:
        logger.error(f"Failed to retrieve the page: {university_url}. Retrying...")
        return get_university_home_page(university_url, retries + 1)
    return home_page, is_cache


def solve_captcha(url, captcha_id):
    try:
        logger.info(f"Solving CAPTCHA...{url}: {captcha_id}")
        result = solver.recaptcha(
            sitekey=captcha_id,
            url=url
        )
        return result['code']
    except Exception as e:
        logger.error(f"Failed to solve CAPTCHA. Error: {e}")
        return None


def get_html_content(url, university_home=False):
    if url in cache:
        logger.info(f"Using cached content for URL: {url}")
        return cache[url], True

    cookies = get_cookies()
    headers = {
        'User-Agent': get_random_user_agent()
    }
    cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
    response = requests.head(url, headers=headers, cookies=cookies_dict)
    # if response.status_code not in [200, 301, 302, 300]:
    #     logger.error(f"Failed to retrieve the page: {url}. Status code: {response.status_code}")
    #     return None, False

    logger.info(f"Fetching live content for URL: {url}")
    driver.get(url)
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    helper.time.sleep(1)

    try:
        if university_home:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.block--rankings, .profile-blocks'))
            )
        else:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.MuiPagination-ul, .no-results__title'))
            )
        html_content = driver.page_source
    except Exception as e:
        logger.error(f"Failed to asretrieve the page: {url}. Error: {e}")
        return None, False
    else:
        helper.time.sleep(random.randint(4, 7))


    cache[url] = html_content
    last_updated[url] = response.headers.get('Date', None)
    return html_content, False


def save_cache():
    temp_file = CACHE_FILE + ".tmp"
    try:
        with open(temp_file, "wb") as f:
            pickle.dump(cache, f)  # Save to temp file first
        helper.os.replace(temp_file, CACHE_FILE)  # Atomically replace the old file
    except Exception as e:
        logger.error(f"Failed to save cache to disk. Error: {e}")
        if helper.os.path.exists(temp_file):
            helper.os.remove(temp_file)


def save_last_updated():
    with open(LAST_UPDATED_FILE, 'w') as f:
        f.write(json.dumps(last_updated))
    return


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"An error occurred {e}. Exiting...")
    finally:
        driver.quit()
        helper.sys.exit(0)

