from multiprocessing import Pool
import concurrent.futures
import logging
import requests
import pickle
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .utils import *
from . import helper

RETRIES = 5

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = helper.os.path.abspath(helper.os.path.dirname(__file__))
CACHE_FILE = helper.os.path.join(BASE_DIR, 'cachefiles/cache.pkl')
LAST_UPDATED_FILE = helper.os.path.join(BASE_DIR, 'cachefiles/last_updated.txt')
UNIVERSITY_FILE = helper.os.path.join(BASE_DIR, 'cachefiles/universities.json')
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

# Load universities from disk
if helper.os.path.exists(UNIVERSITY_FILE):
    with open(UNIVERSITY_FILE, 'r') as f:
        UNIVERSITIES = json.load(f)
else:
    UNIVERSITIES = {}

UNIVERSITY_ELEMENTS = []

chrome_options = Options()
chrome_options.add_argument("User-Agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36")
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-css")
chrome_options.add_argument("--disable-javascript")
chrome_options.add_argument("--disable-images")
chrome_options.add_argument("--disable-ads")
chrome_options.add_argument("--blink-settings=imagesEnabled=false")
chrome_options.add_argument("--disable-plugins")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--disable-site-isolation-trials")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
service = Service(CHROMEDRIVER)
driver = webdriver.Chrome(service=service, options=chrome_options)


def main():
    if not validate():
        logger.error("Validation failed. Exiting...")
        helper.sys.exit(1)
    url = f"https://www.usnews.com/best-colleges/search"

    if not UNIVERSITIES:
        home_page, url = get_home_page()
        if not home_page:
            logger.error(f"Failed to retrieve the page. Exiting...")
            return

        count_of_universities_on_homepage = helper.get_count_of_universities_on_page(home_page)
        count_of_university_elements_in_list = helper.get_universities_count(home_page)

        if count_of_universities_on_homepage != count_of_university_elements_in_list:
            logger.info(f"Count of universities on homepage: {count_of_universities_on_homepage} "
                         f"does not match with the count of universities in the list: {count_of_university_elements_in_list}.")
            logger.info("Retrieving the list of universities from the homepage.")

    # Anchor tags containing the university's url and nested name
    # university_list = helper.get_university_list(home_page)
    university_data = []
    c = len(UNIVERSITIES)
    count = 0
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for university_name, university_url in UNIVERSITIES.items():
            # university_name, university_url = helper.get_university_name_and_url(university)
            # if not university_url or not university_name:
            #     logger.error(f"\nFailed to retrieve the URL or name of the university. Skipping...\n")
            #     continue
            # print(university_url)
            university_home_page, is_cache = get_university_home_page(university_url)

            if not university_home_page:
                logger.error(f"\nFailed to retrieve the page. Skipping...\n")
                continue
            else:
                logger.info(f"\nSuccessfully retrieved the page: {university_url}")
                logger.info(f"{count + 1} of {c} universities processed.\n")
                if not is_cache:
                    executor.submit(update_cacahe_and_last_updated())
            university_data.append(process_university(university_home_page, university_name, url, university_url))
            count += 1


    with open('usnews.json', 'w') as f:
        json.dump(university_data, f, indent=4)
    # save_cache()
    # save_last_updated()
    return


def update_cacahe_and_last_updated():
    save_cache()
    save_last_updated()
    return

def process_university(university_home_page, university_name, url, university_url):
    about_us_paragraph = get_about_us_paragraph(university_home_page)

    institution_data = get_institution_data(university_home_page, university_name, about_us_paragraph)
    student_data = get_student_data(university_home_page, about_us_paragraph)
    admission_data = get_admission_data(university_home_page)
    academics_data = get_available_programs_data(university_home_page)
    rankings_data = get_ranking_data(university_home_page)
    financial_data = get_financial_data(university_home_page)
    after_graduation_data = get_after_graduation_data(university_home_page)
    features_data = get_notable_features(university_home_page, about_us_paragraph)
    meta_data = get_metadata(university_home_page, last_updated.get(university_url, 'N/A'))

    # with Pool() as pool:
    #     tasks = [
    #         pool.apply_async(get_institution_data, (university_home_page, university_name, about_us_paragraph)),
    #         pool.apply_async(get_student_data, (university_home_page, about_us_paragraph)),
    #         pool.apply_async(get_admission_data, (university_home_page,)),
    #         pool.apply_async(get_available_programs_data, (university_home_page,)),
    #         pool.apply_async(get_ranking_data, (university_home_page,)),
    #         pool.apply_async(get_financial_data, (university_home_page,)),
    #         pool.apply_async(get_after_graduation_data, (university_home_page,)),
    #         pool.apply_async(get_notable_features, (university_home_page, about_us_paragraph)),
    #         pool.apply_async(get_metadata, (university_home_page, last_updated.get(university_url, 'N/A'))),
    #     ]

    #     results = [task.get() for task in tasks]

    # institution_data, student_data, admission_data, academics_data, rankings_data, financial_data,  \
    #     after_graduation_data, features_data, meta_data = results

    return {
        "basic_info": institution_data,
        "rankings": rankings_data,
        "admissions": admission_data,
        "costs_and_aid": financial_data,
        "academics": academics_data,
        "student_life": student_data,
        "after_graduation": after_graduation_data,
        "notable_features": features_data,
        "metadata": meta_data,
        "url": university_url
    }

def validate():
    """
    Validate the command line arguments
    """
    if len(helper.sys.argv) not in [2, 3]:
        logger.error("Please provide the two command line arguments. Exiting...")
        return False

    try:
        use_cache = int(helper.sys.argv[1])
    except Exception as e:
        logger.error(f"Please provide a valid number of Cache choice: {e}")
        return False

    return True


def get_home_page(retries=0):
    url = f"https://www.usnews.com/best-colleges/search"
    home_page, is_cache = get_html_content(url)
    if not home_page and retries < RETRIES:
        logger.error(f"Failed to retrieve the page: {url}. Retrying...")
        return get_home_page(retries + 1)
    logger.info(f"Successfully retrieved the home page: {url}")
    return home_page, is_cache


def get_university_home_page(university_href, retries=0):
    university_home_page = None
    url = university_href
    try:
        university_home_page, is_cache = get_html_content(url, university_home=True)
    except Exception as e:
        if retries < RETRIES:
            logger.error(f"Failed to retrieve the page: {url}. Retrying...")
            return get_university_home_page(university_href, retries + 1)

    if not university_home_page and retries < RETRIES:
        logger.error(f"Failed to retrieve the page: {url}. Retrying...")
        return get_university_home_page(university_href, retries + 1)
    return university_home_page, is_cache

def save_universities_to_file():
    with open(UNIVERSITY_FILE, 'w') as f:
        json.dump(UNIVERSITIES, f, indent=4)

def get_university_name_and_url_from_driver(element):
    url = element.get_attribute('href')
    h3 = element.find_element(By.TAG_NAME, 'h3')
    span = h3.find_element(By.TAG_NAME, 'span')
    name = f"{h3.text} {span.text}"
    return name, url

def scroll_to_load_content(driver):
    scroll_pause_time = 2
    with concurrent.futures.ThreadPoolExecutor() as executor:
        while True:
            """
            scrollHeight is a property of an HTML element that returns the
            total height of the element's content,
            including content not visible on the screen due to overflow.
            It is commonly used to determine the full height of a webpage
            or a scrollable element, allowing scripts to scroll through
            the entire content.

            scrollTop is a property of an HTML element that measures
            the number of pixels that an element's content is scrolled vertically.
            It is used to get or set the vertical scroll position of an element.
            """

            driver.execute_script("""
                window.scrollTo({
                    top: document.body.scrollHeight - 1000,
                    behavior: 'smooth'
                });
            """)
            helper.time.sleep(4)
            try:
                # anchor tags containing the university's url and nested name
                university_elements = driver.find_elements(By.CSS_SELECTOR, '.Card__StyledAnchor-sc-1ra20i5-10')
                new_elements = 0
                for element in university_elements:
                    if element not in UNIVERSITY_ELEMENTS:
                        university_name, university_url = get_university_name_and_url_from_driver(element)
                        if university_name not in UNIVERSITIES:
                            UNIVERSITIES[university_name] = university_url
                            executor.submit(save_universities_to_file)
                            new_elements += 1
                            logger.info(f"{university_name} | URL: {university_url} added to the list {len(UNIVERSITIES)}.")
                        UNIVERSITY_ELEMENTS.append(element)

            except Exception as e:
                logger.error(f"Failed to retrieve the list of universities: {e}")
            else:
                logger.info(f"Found {new_elements}/{len(university_elements)} new universities.")

            try:
                helper.time.sleep(1)
                button = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'pager__ButtonStyled-sc-1i8e93j-1'))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.CLASS_NAME, 'pager__ButtonStyled-sc-1i8e93j-1')))
                button.click()
                helper.time.sleep(2)
            except Exception as e:
                logger.error(f"Failed to click the button. Retrying... ")
            else:
                logger.info("CLICKED ON THE BUTTON.")

    return driver.page_source


def get_html_content(url, university_home=False):
    if int(helper.sys.argv[1]) and url in cache:
        logger.info(f"Using cached content for URL: {url}")
        return cache[url], True

    last_modified = None

    # headers = {
    #     "User-Agent":
    #     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
    # }
    # try:
    #     response = requests.get(url, headers=headers, timeout=10)
    #     if response.status_code != 200:
    #         logger.error(f"Failed to retrieve the page. Status code: {response.status_code}")
    #         return None
    # except requests.exceptions.Timeout as e:
    #     logger.error(f"Request timed out {e}")
    #     return None
    # except requests.exceptions.RequestException as e:
    #     logger.error(f"Request failed: {e}")
    #     return None

    # last_modified = response.headers.get('Date', None)

    if last_modified and last_updated.get(url) == last_modified:
        logger.info(f"No update found. Using cached content for URL: {url}")
        return cache[url], True

    logger.info(f"Fetching live content for URL: {url}")
    if university_home:

        try:
            driver.get(url)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.pr-snippet-review-count, .ContentSection__Header-sc-699pa9-0'))
            )
            html_content = driver.page_source
        except Exception as e:
            logger.error(f"Failed to retrieve university home page: {url}. Error: {e}")
            return None, False
    else:
        try:
            driver.get(url)
            # helper.time.sleep(5)
            html_content = scroll_to_load_content(driver)
        except Exception as e:
            logger.error(f"Failed to retrieve the list of universities: {e}")
            return None, False

    cache[url] = html_content
    last_updated[url] = last_modified
    return html_content, False


# def save_cache():
#     with open(CACHE_FILE, 'wb') as f:
#         pickle.dump(cache, f)
#     return


def save_cache():
    temp_file = CACHE_FILE + ".tmp"
    try:
        with open(temp_file, "wb") as f:
            pickle.dump(cache, f)  # Save to temp file first
        helper.os.replace(temp_file, CACHE_FILE)  # Atomically replace the old file
    except Exception as e:
        print(f"Error saving cache: {e}")
        if helper.os.path.exists(temp_file):
            helper.os.remove(temp_file)  #


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
        # with open(UNIVERSITY_FILE, 'w') as f:
        #     json.dump(UNIVERSITIES, f, indent=4)
        driver.quit()
        helper.sys.exit(0)



