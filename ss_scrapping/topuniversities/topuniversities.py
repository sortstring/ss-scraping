from multiprocessing import Pool
import logging
import requests
import pickle
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .utils import *
from . import helper

RETRIES = 3

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
chrome_options.add_argument("--headless")  # Run in headless mode
service = Service(CHROMEDRIVER)  # Update with the path to your ChromeDriver
driver = webdriver.Chrome(service=service, options=chrome_options)


def main():
    if not validate():
        logger.error("Validation failed. Exiting...")
        helper.sys.exit(1)

    total_universities = int(helper.sys.argv[1])
    start_page_number = int(helper.sys.argv[2])
    filename = f'tu_{total_universities}_{start_page_number}.json'
    scrapped_universities = 0
    university_data = []
    while True:
        home_page, url = get_home_page(start_page_number)
        if not home_page:
            logger.error(f"Failed to retrieve the page. Exiting...")
            del cache[url]
            del last_updated[url]
            break

        count_of_universities_on_page = helper.get_count_of_universities_on_page(home_page)
        if not count_of_universities_on_page:
            logger.error(f"Failed to retrieve the count of universities per page. Exiting...")
            del cache[url]
            del last_updated[url]
            break

        university_list = helper.get_university_list(home_page)
        university_count = len(university_list)
        if not university_count:
            logger.error(f"\nFailed to retrieve the list of universities {start_page_number}. Skipping...\n")
            start_page_number += 1
            del cache[url]
            del last_updated[url]
            continue

        scrapped_universities += university_count
        if total_universities < scrapped_universities:
            university_list = university_list[:total_universities]
            university_count = len(university_list)

        if not university_count:
            logger.info("No more universities to scrape")
            break

        data = []
        for university in university_list:
            university_name = university.text
            university_url = university['href']
            if not university_url or not university_name:
                logger.error(f"\nFailed to retrieve the URL or name of the university. Skipping...\n")
                continue
            university_home_page, university_url = get_university_home_page(university_url)
            if not university_home_page:
                logger.error(f"\nFailed to retrieve the page. Skipping...\n")
                continue
            data.append(process_university(university_home_page, university_name, url, university_url))


        university_data.extend(data)
        total_universities -= university_count
        if total_universities <= 0:
            logger.info("Scraped the required number of universities")
            break

        start_page_number = helper.get_next_page_number_from_html_content(home_page)
        if not start_page_number:
            logger.info("No more pages to scrape")
            break


    with open(filename, 'w') as f:
        json.dump(university_data, f, indent=4)
    save_cache()
    save_last_updated()
    return


def process_university(university_home_page, university_name, url, university_url):
    about_us_paragraph = get_about_us_paragraph(university_home_page)

    institution_data = get_institution_data(university_home_page, university_name, about_us_paragraph)
    student_data = get_student_data(university_home_page)
    faculty_data = get_faculty_data(university_home_page)
    admission_requirements = get_admission_data(university_home_page)
    available_programs = get_available_programs_data(university_home_page)
    ratings = get_ranking_data(university_home_page)
    financial_information = get_financial_data(university_home_page)
    meta_data = get_metadata(university_home_page, last_updated.get(university_url, 'N/A'))

    # with Pool() as pool:
    #     tasks = [
    #         pool.apply_async(get_institution_data, (university_home_page, university_name, about_us_paragraph)),
    #         pool.apply_async(get_student_data, (university_home_page,)),
    #         pool.apply_async(get_faculty_data, (university_home_page,)),
    #         pool.apply_async(get_admission_data, (university_home_page,)),
    #         pool.apply_async(get_available_programs_data, (university_home_page,)),
    #         pool.apply_async(get_ranking_data, (university_home_page,)),
    #         pool.apply_async(get_financial_data, (university_home_page,)),
    #         pool.apply_async(get_metadata, (university_home_page, last_updated.get(university_url, 'N/A'))),
    #     ]

    #     results = [task.get() for task in tasks]

    # institution_data, student_data, faculty_data, admission_requirements, available_programs, \
    # ratings, financial_information, meta_data = results

    parallel_results = {
        "schools_answer": get_answer_in_list("What are the schools and the college at the university?", about_us_paragraph),
        "varsity_teams_answer": get_answer("How many varsity sports does the institution boast?", about_us_paragraph),
        "student_participation_answer": get_answer("What percentage of undergraduates join a sports team?", about_us_paragraph),
        "museums_galleries_answer": get_answer("How many museums and galleries are on the campus?", about_us_paragraph),
        "museum_visitors_answer": get_answer("How many visitors does the Museum draw?", about_us_paragraph),
        "total_answer": get_answer("How many music, theatre, writing, and dance groups do students participate in?", about_us_paragraph),
        "categories_answer": get_answer("What art forms do students participate in at the university?", about_us_paragraph),
        "current_areas_answer": get_answer("What areas are researchers at the forefront of developments in?", about_us_paragraph),
        "radar_breakthrough": get_answer("What scientific breakthrough did research from this institution contribute to related to radar?", about_us_paragraph),
        "core_memory_breakthrough": get_answer("What scientific breakthrough did research from the institution contribute to related to magnetic core memory?", about_us_paragraph),
        "universe_breakthrough": get_answer("What scientific breakthrough did research from the institution contribute to related to the expanding universe?", about_us_paragraph),
        "total_active_answer": get_answer("How many active companies have alumni launched?", about_us_paragraph),
        "jobs_created_answer": get_answer("How many jobs were created by alumni?", about_us_paragraph),
        "annual_revenue_answer": get_answer("How much annual revenue is generated by alumni's companies?", about_us_paragraph),
    }

    # tasks_to_parallelize = {
    #     "schools_answer": ("get_answer_in_list", "What are the schools and the college at the university?"),
    #     "varsity_teams_answer": ("get_answer", "How many varsity sports does the institution boast?"),
    #     "student_participation_answer": ("get_answer", "What percentage of undergraduates join a sports team?"),
    #     "museums_galleries_answer": ("get_answer", "How many museums and galleries are on the campus?"),
    #     "museum_visitors_answer": ("get_answer", "How many visitors does the Museum draw?"),
    #     "total_answer": ("get_answer", "How many music, theatre, writing, and dance groups do students participate in?"),
    #     "categories_answer": ("get_answer", "What art forms do students participate in at the university?"),
    #     "current_areas_answer": ("get_answer", "What areas are researchers at the forefront of developments in?"),
    #     "radar_breakthrough": ("get_answer", "What scientific breakthrough did research from this institution contribute to related to radar?"),
    #     "core_memory_breakthrough": ("get_answer", "What scientific breakthrough did research from the institution contribute to related to magnetic core memory?"),
    #     "universe_breakthrough": ("get_answer", "What scientific breakthrough did research from the institution contribute to related to the expanding universe?"),
    #     "total_active_answer": ("get_answer", "How many active companies have alumni launched?"),
    #     "jobs_created_answer": ("get_answer", "How many jobs were created by alumni?"),
    #     "annual_revenue_answer": ("get_answer", "How much annual revenue is generated by alumni's companies?"),
    # }

    # with Pool() as pool:
    #     async_results = {
    #         key: pool.apply_async(globals()[func], (query, about_us_paragraph))
    #         for key, (func, query) in tasks_to_parallelize.items()
    #     }

    #     parallel_results = {key: result.get() for key, result in async_results.items()}

    historical_achievements_answer = ([
        parallel_results["radar_breakthrough"],
        parallel_results["core_memory_breakthrough"],
        parallel_results["universe_breakthrough"]
    ])

    return {
        "institution": institution_data, # ML Inside
        "student_body": student_data,
        "faculty": faculty_data,
        "admission_requirements": admission_requirements,
        "programs": {
            "schools": parallel_results["schools_answer"],
            "available_programs": available_programs
        },
        "campus_life": {
            "sports": {
                "varsity_teams": parallel_results["varsity_teams_answer"],
                "student_participation": parallel_results["student_participation_answer"]
            },
            "arts_culture": {
                "museums_galleries": parallel_results["museums_galleries_answer"],
                "museum_visitors": parallel_results["museum_visitors_answer"],
                "student_groups": {
                    "total": parallel_results["total_answer"],
                    "categories": [parallel_results["categories_answer"]]
                }
            }
        },
        "rankings": ratings,
        "research_focus": {
            "current_areas": [parallel_results["current_areas_answer"]],
            "historical_achievements": historical_achievements_answer
        },
        "alumni_impact": {
            "companies": {
                "total_active": parallel_results["total_active_answer"],
                "jobs_created": parallel_results["jobs_created_answer"],
                "annual_revenue": parallel_results["annual_revenue_answer"]
            }
        },
        "financial_information": financial_information,
        "metadata": meta_data,
        "urls": {
            "home_page_url": url,
            "university_url": university_url
        }
    }

def validate():
    """
    Validate the command line arguments
    """
    if len(helper.sys.argv) not in [4, 5]:
        logger.error("Please provide the number of universities to scrape and the start page number")
        return False

    try:
        count_of_universities = int(helper.sys.argv[1])
    except Exception as e:
        logger.error(f"Please provide a valid number of universities {e}")
        return False

    try:
        start_page_number = int(helper.sys.argv[2])
        assert start_page_number >= 1
    except Exception as e:
        logger.error(f"Please provide a valid choice for start page number {e}")
        return False

    try:
        assert count_of_universities >= 1 and count_of_universities <= 1500
    except AssertionError as e:
        logger.error(f"Please provide the number of universities between 1 and 500 {e}")
        return False

    try:
        use_cache = int(helper.sys.argv[3])
        assert use_cache == 0 or use_cache == 1
    except Exception as e:
        logger.error(f"Please provide a valid choice for cache {e}")
        return False

    return True


def get_home_page(page, retries=0):
    url = f"https://www.topuniversities.com/world-university-rankings?page={page}"
    home_page = get_html_content(url)
    if not home_page and retries < RETRIES:
        logger.error(f"Failed to retrieve the page: {url}. Retrying...")
        return get_home_page(page, retries + 1)
    return home_page, url


def get_university_home_page(university_href, retries=0):
    university_home_page = None
    try:
        url = 'https://www.topuniversities.com' + university_href
        university_home_page = get_html_content(url, university_home=True)
    except Exception as e:
        if retries < RETRIES:
            logger.error(f"Failed to retrieve the page: {url}. Retrying...")
            return get_university_home_page(university_href, retries + 1)

    if not university_home_page and retries < RETRIES:
        logger.error(f"Failed to retrieve the page: {url}. Retrying...")
        return get_university_home_page(university_href, retries + 1)
    return university_home_page, url


def get_html_content(url, university_home=False):
    if int(helper.sys.argv[3]) and url in cache:
        logger.info(f"Using cached content for URL: {url}")
        return cache[url]

    response = requests.head(url)
    if response.status_code != 200:
        logger.error(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

    last_modified = response.headers.get('Last-Modified', None)
    if last_modified and last_updated.get(url) == last_modified:
        logger.info(f"Using cached content for URL: {url} as it has not been modified")
        return cache[url]

    logger.info(f"Fetching live content for URL: {url}")
    try:
        driver.get(url)
        if university_home:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.circle'))
            )
        else:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.uni-link'))
            )
        html_content = driver.page_source
    except Exception as e:
        try:
            driver.get(url)
            driver.implicitly_wait(20)
            html_content = driver.page_source
        except Exception as e:
            logger.error(f"Failed to asretrieve the page: {url}. Error: {e}")
            return None

    cache[url] = html_content
    last_updated[url] = last_modified
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
        helper.sys.exit(0)



