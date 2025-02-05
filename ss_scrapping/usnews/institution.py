from . import helper



# def get_university_name(html_content):
#     elements = helper.get_html_elements(html_content, 'h1', 'text-white')
#     return elements[0].text

def get_university_website(html_content):
    tag_name = 'a'
    class_name = 'OverviewContent__WebsiteAnchor-sc-1yondsr-4'
    elements = helper.get_html_elements(html_content, tag_name, class_name)
    if elements:
        return elements[0]['href']
    return 'N/A'


def get_university_address(html_content):
    class_name = 'OverviewContent__AddressDiv-sc-1yondsr-5'
    tag_name = 'div'
    elements = helper.get_html_elements(html_content, tag_name, class_name)
    if elements:
        return elements[0].text
    return 'N/A'

def get_university_stting(html_content):
    class_name = 'OverviewContent__StyledDataRow-sc-1yondsr-9'
    tag_name = 'div'
    elements = helper.get_html_elements(html_content, tag_name, class_name)
    try:
        assert elements and len(elements) > 1
    except:
        return 'N/A'

    for element in elements:
        try:
            paragraphs = element.find_all('p')
            if paragraphs[0].text == 'Setting':
                return paragraphs[1].text
        except:
            continue

    return 'N/A'


def get_institution_data(html_content, univ_name, about_us_paragraph):
    funding_type = get_university_funding_type(about_us_paragraph)
    univ_name = ' '.join(univ_name.split()[:-1])
    res = helper.OrderedDict({
        "name": univ_name,
        "website": get_university_website(html_content),
        "address": get_university_address(html_content),
        "founding_year": helper.get_answer(
            "When was the university founded?",
            about_us_paragraph
        ),
        "institution_type": funding_type,
        "setting": get_university_stting(html_content),
        "campus_size": helper.get_answer(
            "What is the size of the university campus?",
            about_us_paragraph
        ),
        "academic_calendar": helper.get_answer(
            "What is the academic calendar of the university?",
            about_us_paragraph
        ),
        "religious_affiliation": helper.get_answer(
            "What is the religious affiliation of the university?",
            about_us_paragraph
        )
    })
    return res


def get_university_abbreviation(univ_name):
    match = helper.re.search(r'\(([^)]+)\)', univ_name)
    if match:
        return match.group(1)
    return 'N/A'


# def get_university_motto_and_funding_type(html_content):
#     try:
#         import sys
#         assert int(sys.argv[4]) == 1
#     except:
#         return 'N/A', 'N/A'

#     class_name = 'details'
#     tag_name = 'div'
#     elements = helper.get_html_elements(html_content, tag_name, class_name)

#     paragraph = ''
#     for element in elements:
#         paragraph += f"\n{element.text}"

#     university_motto = 'N/A'
#     if not paragraph or not isinstance(paragraph, str) or len(paragraph) == 0:
#         return university_motto, 'N/A'

#     if 'motto' in paragraph:
#         university_motto = helper.get_answer(
#             "What is the University's motto?",
#             paragraph
#         )

#     return university_motto, get_university_funding_type(paragraph)

def get_university_funding_type(paragraph):
    if 'public university' in paragraph or\
            'state university' in paragraph or\
            'government university' in paragraph or\
            'publicly funded' in paragraph or\
            'publicly endowed' in paragraph or\
            'state-funded' in paragraph or\
            'government-funded' in paragraph:
        return 'Public'

    if 'private university' in paragraph or\
            'privately funded' in paragraph or\
            'private institution' in paragraph or\
            'private college' in paragraph or\
            'private school' in paragraph or\
            'privately endowed' in paragraph or\
            'independent institution' in paragraph or\
            'independent college' in paragraph or\
            'independent school' in paragraph or\
            'independently funded' in paragraph:
        return 'Private'

    return 'N/A'

# def get_location_data(html_content, paragraph):
#     class_names = [
#         'campus_city',
#         'campus_country_code',
#         'campus_state'
#     ]
#     location_data = {
#         'city': 'N/A',
#         'state': 'N/A',
#         'country': 'N/A',
#         'features': []
#     }
#     new_tag_name = 'p'
#     for class_name in class_names:
#         elements = helper.get_html_elements(html_content, new_tag_name, class_name)
#         for element in elements:
#             if class_name == 'campus_city':
#                 location_data['city'] = element.text
#             elif class_name == 'campus_country_code':
#                 location_data['country'] = element.text
#             elif class_name == 'campus_state':
#                 location_data['state'] = element.text

#     location_data["features"].append(
#         helper.get_answer(
#             "Where is the university located, and what is nearby?",
#             paragraph
#         )
#     )

#     location_data["features"].append(
#         helper.get_answer(
#             "What famous locations are mentioned near the university campus?",
#             paragraph
#         )
#     )
#     return location_data