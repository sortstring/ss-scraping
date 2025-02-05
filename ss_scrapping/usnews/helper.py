from bs4 import BeautifulSoup
from collections import OrderedDict
import logging
import sys
import time
import datetime
import re

try:
    assert int(sys.argv[2]) == 1
except:
    pass
else:
    from transformers import pipeline

import os


NLP_MODEL = os.getenv("NLP_MODEL")
# NLP_MODEL = "distilbert/distilbert-base-cased-distilled-squad"
# NLP_MODEL = "bert-large-uncased-whole-word-masking-finetuned-squad"

logger = logging.getLogger(__name__)


def get_current_time_stamp():
    # format 2024-01-15T00:00:00Z
    return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

def get_html_elements(html_content, tag_name, class_name):
    elements = None
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        elements = soup.find_all(tag_name, class_=class_name)
    except Exception as e:
        logger.error(f"Error while parsing the html content: {e}")
    return elements

def get_innermost_nested_element(parent, nested_tag):
    nested_elements = parent.find_all(nested_tag)
    return (nested_elements[-1].text).rstrip('%')

def get_html_element_by_id(html_content, tag_name, id_name):
    soup = BeautifulSoup(html_content, 'html.parser')
    element = soup.find(tag_name, id=id_name)
    return element

def get_next_page(unordered_list, list_element):
    list_elements = unordered_list.find_all(list_element)
    list_element_anchor_tag = list_elements[-1].find('a')
    if not list_element_anchor_tag:
        return None
    next_page = list_element_anchor_tag['href'].lstrip('#')
    return next_page

def get_next_page_number_from_html_content(html_content):
    unordered_list = get_html_element_by_id(html_content, 'ul', 'alt-style-pagination')
    next_page = get_next_page(unordered_list, 'li')
    # next_page = page-2
    try:
        assert next_page
        next_page_number = int(next_page.split('-')[-1])
    except:
        return None
    return next_page_number

def get_count_of_universities_on_page(html_content):
    # gives the number written on homepage
    try:
        div = get_html_elements(html_content, 'div', 'filter-bar__CountContainer-sc-1glfoa-5')
        span = div[0].find('span')
        count = int(span.text.replace(',', '').strip())
    except Exception as e:
        logger.error(f"Error while getting the count of universities on page: {e}")
        return 0
    return count

def get_university_list(html_content):
    tag_name = 'a'
    class_name = 'Card__StyledAnchor-sc-1ra20i5-10'
    elements = get_html_elements(html_content, tag_name, class_name=class_name)
    return elements

def get_universities_count(html_content):
    # gives the count/len of university elements found on the page
    try:
        tag_name = 'a'
        class_name = 'Card__StyledAnchor-sc-1ra20i5-10'
        elements = get_html_elements(html_content, tag_name, class_name=class_name)
        count = len(elements)
    except:
        return 0
    return count


def get_about_us_paragraph(html_content):
    class_name = 'MultilineEllipsis__FullHeightReferenceWrapper-sc-1hoyc1r-4'
    tag_name = 'div'
    elements = get_html_elements(html_content, tag_name, class_name)
    try:
        paragraph_ele = elements[0].find('p')
        nested_elements = paragraph_ele.find_all('p')
        paragraph = '\n'.join([element.text for element in nested_elements])
    except:
        paragraph = None

    return paragraph

def get_answer(question, paragraph):
    # print(question)
    # if question in [
    #     'How many active companies have alumni launched?',
    #     'How many jobs were created by alumni?',
    #     "How much annual revenue is generated by alumni's companies?",
    #     "What scientific breakthrough did research from the institution contribute to related to the expanding universe?"
    # ]:
    #     return 'N/A'
    try:
        assert int(sys.argv[2]) == 1
        assert paragraph and isinstance(paragraph, str) and len(paragraph) > 0
    except:
        return 'N/A'

    qa_pipeline = pipeline(
        "question-answering",
        model=NLP_MODEL
    )
    return qa_pipeline(
        question=question,
        context=paragraph
    ).get('answer', None)


def get_answer_in_list(question, paragraph):
    try:
        assert int(sys.argv[2]) == 1
    except:
        return ['N/A']

    try:
        answers = get_answer(question, paragraph)
        assert answers
        answers = [answers]
    except:
        answers = []

    return answers


# def check_page_end(html_content):
#     tag_name = 'div'
#     class_name = 'no-ranking-results-found'

#     elements = helper.get_html_elements(html_content, tag_name, class_name)
#     return bool(elements)


def get_university_name_and_url(element):
    url = element['href']
    h3 = element.find('h3')
    span = h3.find('span')
    name = f"{h3.text} {span.text}"
    return name, url
