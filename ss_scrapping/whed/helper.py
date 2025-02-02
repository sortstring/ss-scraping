from bs4 import BeautifulSoup
from collections import OrderedDict
import re
import logging
import re
import unicodedata


logger = logging.getLogger(__name__)


def to_slug(text):
    # Normalize the text to remove accents and special characters
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    # Replace non-alphanumeric characters with hyphens
    text = re.sub(r'[^a-zA-Z0-9]+', '-', text)
    # Convert to lowercase
    text = text.lower()
    # Remove leading and trailing hyphens
    text = text.strip('-')
    return text

# def get_total_pages(html_content):
#     try:
#         elements = get_html_elements(html_content, 'div', 'pages')
#         assert elements and isinstance(elements, list) and len(elements) > 0
#         a_tags = elements[0].find_all('a')
#         assert a_tags and isinstance(a_tags, list) and len(a_tags) > 0
#         count = len(a_tags) + 1
#     except Exception as e:
#         logger.error(f"Failed to retrieve the total number of pages. Error: {e}")
#         return 0
#     return count

def get_total_pages(html_content):
    try:
        elements = get_html_elements(html_content, 'p', 'prem')
        assert elements and isinstance(elements, list) and len(elements) > 0
        numbers = extract_numbers(elements[0].text)
    except Exception as e:
        logger.error(f"Failed to retrieve the total number of pages. Error: {e}")
        return 0

    page_first_record = numbers[0]
    page_last_record = numbers[1]
    total_records = numbers[2]

    count = total_records // (page_last_record - page_first_record + 1)
    return count + 1

def get_html_elements(html_content, tag_name, class_name):
    soup = BeautifulSoup(html_content, 'html.parser')
    elements = soup.find_all(tag_name, class_=class_name)
    return elements


def get_html_content_by_id(html_content, tag_name, id_name):
    soup = BeautifulSoup(html_content, 'html.parser')
    element = soup.find(tag_name, id=id_name)
    return element


def extract_numbers(text):
    # Extract all integers from the string
    numbers = list(map(int, re.findall(r'\d+', text)))
    return numbers


def get_university_details(html_content):
    try:
        ul = get_html_content_by_id(html_content, 'ul', 'results')
        li_list = ul.find_all('li')
        assert li_list and isinstance(li_list, list) and len(li_list) > 0
    except:
        return []

    res = []
    for li in li_list:
        anchor_tag = li.find('a', class_='fancybox fancybox.iframe')
        p = li.find('p', class_='i_name')
        res.append({
            'href': anchor_tag['href'],
            'university_name': (anchor_tag.text).strip(),
            'parent_university_name': (p.text).strip()
        })

    return res


def get_data_sections(html_content):
    section = get_html_content_by_id(html_content, 'section', 'contenu')
    if not section:
        return 'N/A'

    option_list = []
    select_tag = section.find('select')
    options = select_tag.find_all('option')
    for option in options:
        option_list.append(option.text.strip())

    return option_list
