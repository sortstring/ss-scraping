from . import helper


# def get_available_programs_div(html_content):
#     tag_name = 'div'
#     class_name = 'avail_prog'
#     elements = helper.get_html_elements(html_content, tag_name, class_name)
#     programs_list_id = 'aptabs'

#     try:
#         program_list = elements[0].find_all('ul', id=programs_list_id)
#         list_elements = program_list[0].find_all('li')
#         assert list_elements
#     except:
#         list_elements = []

#     return list_elements


def get_available_programs_data(html_content):
    data = {
        "student_faculty_ratio": "N/A",
        "class_stats": {
            "under_20_students": "N/A",
            "under_50_students": "N/A",
        },
        "most_popular_majors": [

        ],
        "graduation_rates": {
            "4_year": "N/A",
            "6_year": "N/A",
        },
        "retention_rate": "N/A",
    }

    div_elements = helper.get_html_elements(html_content, 'p', 'AcademicSection__DataHeader-sc-1g5x16k-5')
    if div_elements:
        try:
            data["graduation_rates"]["4_year"] = div_elements[0].text
        except:
            pass

        try:
            data["student_faculty_ratio"] = div_elements[1].text
        except:
            pass

        try:
            data["class_stats"]["under_20_students"] = div_elements[2].text
        except:
            pass

    popular_major_div = helper.get_html_elements(html_content, 'div', 'AcademicSection__StyledDataRow-sc-1g5x16k-12')
    for div in popular_major_div:
        paragraphs = div.find_all('p')
        if paragraphs and len(paragraphs) >= 2:
            data["most_popular_majors"].append(f"{paragraphs[0].text} ({paragraphs[1].text})")

    return data

