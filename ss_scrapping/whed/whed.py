from multiprocessing import Pool
import logging
import requests
import time
import pickle
import os
import json
import sys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha
from . import helper
from . import utils
# solver = TwoCaptcha('9acdf0d598b74edfa9eaf8f32f444f16')

RETRIES = 3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CACHE_FILE = os.path.join(BASE_DIR, 'cachefiles/cache.pkl')
LAST_UPDATED_FILE = os.path.join(BASE_DIR, 'cachefiles/last_updated.txt')
CHROMEDRIVER = os.path.join(BASE_DIR, '../chromedriver/chromedriver')
COUNTRY_LIST = os.path.join(BASE_DIR, 'cachefiles/countries.json')
# Load cache from disk
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'rb') as f:
        cache = pickle.load(f)
else:
    cache = {}  # Cache for the current country

if os.path.exists(LAST_UPDATED_FILE):
    with open(LAST_UPDATED_FILE, 'r') as f:
        last_updated = json.loads(f.read())
else:
    last_updated = {}

if os.path.exists(COUNTRY_LIST):
    with open(COUNTRY_LIST, 'r') as f:
        countries = json.loads(f.read())
else:
    countries = {}

chrome_options = Options()
# chrome_options.add_argument("--user-data-dir=/home/sortstring/.config/google-chrome")
# chrome_options.add_argument("--profile-directory=Default")
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("User-Agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")

chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
service = Service(CHROMEDRIVER)
driver = webdriver.Chrome(service=service, options=chrome_options)


def get_country_list():
    driver.get("https://whed.net/home.php")
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#pays'))
        )

        select_element = driver.find_element(By.ID, 'pays')
        options = select_element.find_elements(By.TAG_NAME, 'option')

        country_list = [option.text for option in options]
    except Exception as e:
        logger.error(f"Failed to retrieve the list of countries. Error: {e}")
        return False

    count = 1
    for country in country_list[1:]:
        countries[count] = country
        print(f"{count} - {country}")
        count += 1

    with open(COUNTRY_LIST, 'w') as f:
        f.write(json.dumps(countries))
    logger.info(f"Successfully retrieved the list of countries. Exiting...")
    return True


def validate():
    if not len(sys.argv) in [2, 3, 4]:
        logger.error("Invalid number of arguments. Exiting...")
        return False

    if not countries:
        logger.error("Country list not found. Exiting...")
        return False

    try:
        assert sys.argv[1] in countries
    except Exception as e:
        logger.error(f"Invalid country code {e}. Exiting...")
        return False

    directory = f'whed/{helper.to_slug(countries[sys.argv[1]])}'
    if os.path.exists(f'{directory}/whed.json'):
        logger.info(f"Data already exists for country: {countries[sys.argv[1]]}. Exiting...")
        return False

    return True

def update_cache():
    countries = json.loads(open(COUNTRY_LIST, 'r').read())
    for country in countries:
        if country not in cache:
            cache[country] = {}

        if country not in last_updated:
            last_updated[country] = {}


def main():
    try:
        assert len(sys.argv) == 2
        display_university_list = int(sys.argv[1])
        assert display_university_list == 0
    except:
        pass
    else:
        try:
            assert get_country_list()
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        else:
            update_cache()
            save_cache()
            save_last_updated()
        finally:
            return

    if not validate():
        logger.error("Validation failed. Exiting...")
        return

    try:
        page_number = int(sys.argv[2])
    except:
        page_number = 1

    scrapped_universities = 0
    first_page = get_page(page_number=1)

    try:
        total_pages = int(sys.argv[3])
    except:
        total_pages = helper.get_total_pages(first_page)
    print(page_number, total_pages)
    all_universities = []
    while page_number <= total_pages:
        next_page = first_page if page_number == 1 else get_page(page_number=page_number)

        if not next_page:
            del cache[sys.argv[1]][page_number]
            if page_number in last_updated[sys.argv[1]]:
                del last_updated[sys.argv[1]][page_number]
            logger.error(f"Failed to retrieve the page: {page_number}. Exiting...")
            break

        universities = helper.get_university_details(next_page)

        for university in universities:
            scrapped_universities += 1
            university_name = university['university_name']
            university_url = university['href']
            parent_university_name = university['parent_university_name']
            logger.info(f"Scrapping university: {scrapped_universities} - {university_name}. Page {page_number}")
            university_page = get_university_page_html_content(university_url)
            university_dict = process_university(university_page, university_name, parent_university_name)
            all_universities.append(university_dict)

        page_number += 1
    save_cache()
    save_last_updated()

    directory = f'whed/{helper.to_slug(countries[sys.argv[1]])}'
    os.makedirs(directory, exist_ok=True)

    with open(f'{directory}/whed.json', 'w') as f:
        json.dump(all_universities, f, indent=4)
    return


def process_university(university_page, university_name, parent_university_name):
    general_info = None
    sections = helper.get_data_sections(university_page)

    with Pool() as pool:
        tasks = []
        for index in range(len(sections)):
            if sections[index] == 'General Information':
                tasks.append(pool.apply_async(
                    utils.get_general_info,
                    (
                        university_page,
                        sections[index],
                        university_name,
                        parent_university_name
                    )
                ))

            if sections[index] == 'Divisions':
                tasks.append(pool.apply_async(
                    utils.get_divisions,
                    (
                        university_page,
                        sections[index]
                    )
                ))

            if sections[index] == 'Degrees':
                tasks.append(pool.apply_async(
                    utils.get_degrees_info,
                    (
                        university_page,
                        sections[index]
                    )
                ))

        tasks = tasks
        results = [task.get() for task in tasks]

    general_info, division_info, degrees_info = results

    return {
        "GeneralInformation": general_info,
        "Divisions": division_info,
        "Degrees": degrees_info
    }


def get_page(retries=0, page_number=1):
    url = f"https://whed.net/home.php"

    home_page = get_page_html_content(url, page_number)
    if not home_page and retries < RETRIES:
        logger.error(f"Failed to retrieve the page: {page_number}. Retrying...")
        return get_page(retries + 1, page_number)
    return home_page


def get_page_html_content(url, page_number=1):
    if page_number in cache[sys.argv[1]]:
        logger.info(f"Using cached content for page: {page_number}")
        return cache[sys.argv[1]][page_number]

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
    }
    response = requests.head(url, headers=headers)
    if response.status_code != 200:
        save_cache()
        save_last_updated()
        logger.error(f"Failed to retrieve the page: {url}. Status code: {response.status_code}")
        sys.exit(1)

    logger.info(f"Successfully retrieved the page header. Fetching live content for URL: {url}")
    driver.get(url)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#pays'))
        )

        select_element = driver.find_element(By.ID, 'pays')
        select = Select(select_element)
        select.select_by_visible_text(countries[sys.argv[1]])

        # Wait for the iframe to appear and switch to it
        WebDriverWait(driver, 20).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, 'iframe.fancybox-iframe'))
        )

        # Select "Higher education institutions (HEIs)"
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[value="results_institutions.php"]'))
        )

        heis_radio_button = driver.find_element(By.CSS_SELECTOR, 'input[value="results_institutions.php"]')
        heis_radio_button.click()
        ok_button = driver.find_element(By.CSS_SELECTOR, 'input.bouton[type="button"][onclick="Choisir();"]')
        ok_button.click()

        driver.switch_to.default_content()
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.infos'))
        )

        select_element = driver.find_element(By.NAME, 'nbr_ref_pge')
        select = Select(select_element)
        select.select_by_visible_text('100')
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.infos'))
        )
        if page_number > 1:
            html_content = navigate_to_page(page_number)
        else:
            html_content = driver.page_source
    except Exception as e:
        logger.error(f"Failed to retrieve the page: {page_number}. Error: {e}")
        return None

    logger.info(f"Successfully retrieved the page: {page_number}")
    cache[sys.argv[1]][page_number] = html_content
    last_updated[sys.argv[1]][page_number] = response.headers.get('Date', None)
    return html_content


def navigate_to_page(page_number):
    try:
        next_page = driver.find_element(By.CSS_SELECTOR, f'a[title="Page n°{page_number}"]')
        next_page.click()
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.infos'))
        )
        html_content = driver.page_source
    except Exception as e:
        while True:
            try:
                next_page = driver.find_element(By.CSS_SELECTOR, f'a[title="Next page"]')
                next_page.click()
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.infos'))
                )
            except Exception as e:
                logger.error(f"Failed to navigate to page {page_number}. Error: {e}")
                return None
            else:
                pages_div = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.pages'))
                )
                span_tags = pages_div.find_elements(By.TAG_NAME, 'span')
                try:
                    current_page = int(span_tags[0].text)
                except:
                    logger.error(f"Failed to retrieve the current page number. Exiting...")
                    return None
                else:
                    if current_page == page_number:
                        html_content = driver.page_source
                        break


    logger.info(f"Successfully navigated to page {page_number}")
    cache[sys.argv[1]][page_number] = html_content
    last_updated[sys.argv[1]][page_number] = last_updated[sys.argv[1]][page_number - 1]
    return html_content


def get_university_page_html_content(url):
    url = f"https://whed.net/{url}"

    if url in cache[sys.argv[1]]:
        logger.info(f"Using cached content for URL: {url}")
        return cache[sys.argv[1]][url]

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
    }
    response = requests.head(url, headers=headers)
    if response.status_code != 200:
        save_cache()
        save_last_updated()
        logger.error(f"Failed to retrieve the page: {url}. Status code: {response.status_code}")
        sys.exit(1)

    logger.info(f"Successfully retrieved the page header. Fetching live content for URL: {url}")
    driver.get(url)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.page_search'))
        )
        html_content = driver.page_source
    except Exception as e:
        logger.error(f"Failed to retrieve the page: {url}. Error: {e}")
        return None

    logger.info(f"Successfully retrieved the page: {url}")
    cache[sys.argv[1]][url] = html_content
    last_updated[sys.argv[1]][url] = response.headers.get('Date', None)
    return html_content


def save_cache():
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(cache, f)
    return


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
        sys.exit(0)



