from . import helper


def has_student_div(html_content):
    tag_name = 'h2'
    id_attr = 'studentbody'
    element = helper.get_html_element_by_id(html_content, tag_name, id_attr)
    if not element:
        return False
    return True

def get_student_data(html_content, about_us_paragraph):
    res = helper.OrderedDict({
        "enrollment": {
            "total": "N/A",
            "undergraduate": "N/A",
            "graduate": "N/A",
            "full_time_percentage": "N/A",
        },
        "demographics": get_demographics_data(html_content),
        "housing": get_housing_data(html_content),
        "campus_life": get_campus_life(html_content, about_us_paragraph)
    })

    if not has_student_div(html_content):
        return res

    divs = get_student_details_div(html_content)
    try:
        assert divs and len(divs) in [1, 2]
    except:
        return res

    try:
        under_grad_enrollment = divs[0].find('p', class_='StudentsSection__DataHeader-sc-1tb3548-0 dfCQxG')
        res["enrollment"]["undergraduate"] = under_grad_enrollment.text
    except:
        pass

    for inner_div in divs[1].find_all('div', class_='ContentSection__StyledDataRow-sc-699pa9-4'):
        paragraphs = inner_div.find_all('p', class_='Paragraph-sc-1iyax29-0')
        name = paragraphs[0].text
        value = paragraphs[1].text

        if 'Graduate Enrollment' in name:
            res["enrollment"]["graduate"] = value
        elif 'Total Enrollment' in name:
            res["enrollment"]["total"] = value
        elif 'Full-Time Degree' in name:
            try:
                value = (int(value.replace(',', '')) * 100)/int((res["enrollment"]["undergraduate"].replace(',', '')))
            except:
                pass
            else:
                res["enrollment"]["full_time_percentage"] = round(float(value), 2)

    return res


def get_student_details_div(html_content):
    h2_element = helper.get_html_element_by_id(html_content, 'h2', 'studentbody')
    if h2_element:
        next_div = h2_element.find_next_sibling('div', class_='Grid-lx2f3i-0 ContentSection__StyledGrid-sc-699pa9-1 fQYHzS cZfsa-D')
        if next_div:
            return next_div.find_all('div', class_='ContentSection__StyledCell-sc-699pa9-3')

    return None


def get_genders(html_content):
    divs = helper.get_html_elements(html_content, 'div', 'BarChartStacked__Legend-wgxhoq-4 iLdLaQ')
    if divs and len(divs) > 0:
        gender_divs = divs[0].find_all('div')
    else:
        return False
    male = 'N/A'
    female = 'N/A'

    for div in gender_divs:

        if 'male' in div.text.lower() and 'female' not in div.text.lower():
            try:
                male = div.find('b').text.rstrip('%')
            except:
                pass

        if 'female' in div.text.lower():
            try:
                female = div.find('b').text.rstrip('%')
            except:
                pass

    return {
        "male": male,
        "female": female
    }


def get_ethnicity(html_content):
    e = helper.OrderedDict({
        "white": "N/A",
        "asian": "N/A",
        "hispanic": "N/A",
        "black": "N/A",
        "international": "N/A",
        "unknown": "N/A",
        "two_or_more": "N/A",
        "native_american": "N/A",
        "pacific_islander": "N/A"
    })

    # Minority Enrollment 50
    # White 36
    # Asian 24
    # International 12
    # Hispanic 10
    # Black 9
    # Two or more races 7
    # Unknown 2

    divs = helper.get_html_elements(html_content, 'div', 'Key__ItemBox-sc-12afmmk-0')
    for div in divs:
        try:
            ethnicity = div.find('p', class_="Key__Title-sc-12afmmk-1").text.lower()
            inner_div = div.find('div', class_="Key__DataBox-sc-12afmmk-5")
            percent = inner_div.find('p', class_="Key__Data-sc-12afmmk-3").text.rstrip('%')
        except:
            continue
        if 'white' in ethnicity:
            e["white"] = percent
        elif 'asian' in ethnicity:
            e["asian"] = percent
        elif 'hispanic' in ethnicity:
            e["hispanic"] = percent
        elif 'black' in ethnicity:
            e["black"] = percent
        elif 'international' in ethnicity:
            e["international"] = percent
        elif 'unknown' in ethnicity:
            e["unknown"] = percent
        elif 'two or more' in ethnicity:
            e["two_or_more"] = percent

    return e

def get_demographics_data(html_content):
    genders = get_genders(html_content)

    demographics = {
        "gender": {
            "male": genders["male"] if genders else "N/A",
            "female": genders["female"] if genders else "N/A"
        },
        "ethnicity": get_ethnicity(html_content)
    }
    return demographics


def get_housing_data(html_content):
    h = {
        "students_in_college_housing": "N/A",
        "housing_types": []
    }

    housing_types = helper.get_html_elements(html_content, 'li', 'CampusLifeSection__StyledListItem-x6yma0-2')
    if not housing_types:
        return h

    for housing_type in housing_types:
        try:
            ht = housing_type.find('span').text
        except:
            continue
        h["housing_types"].append(ht)

    return h

def get_campus_life(html_content, about_us_paragraph):
    greek_life_elements = helper.get_html_elements(html_content, 'p', 'CampusLifeSection__DataHeader-x6yma0-8 lczeeQ')

    try:
        sports_team_count = greek_life_elements[0].text.strip('+')
        sports_team_count = int(sports_team_count)
    except:
        sports_team_count = 0

    try:
        fraternities = greek_life_elements[1].text
    except:
        fraternities = 'N/A'

    try:
        sororities = greek_life_elements[2].text
    except:
        sororities = 'N/A'

    campus_life = {
        "greek_life": {
            "has_greek_life": True if sports_team_count == 0 else False,
            "fraternities": fraternities,
            "sororities": sororities
        },
        "varsity_athletics": {
            "division": helper.get_answer(
                "What is the division of varsity athletics?",
                about_us_paragraph
            ),
            "men_teams": [helper.get_answer(
                "Varsity sports for men?",
                about_us_paragraph
            )],
            "women_teams": [helper.get_answer(
                "Varsity sports for women?",
                about_us_paragraph
            )]
        }
    }

    return campus_life