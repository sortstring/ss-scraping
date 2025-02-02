from . import helper



def get_basic_info(university_home_page):


    res = {}

    try:
        res["name"] = helper.get_html_elements(
                university_home_page,
                'h1',
                'MuiTypography-root MuiTypography-headlineMedium nss-td0143'
            )[0].contents[0].text

        # soup = helper.BeautifulSoup(university_home_page, 'html.parser')
        # res["name"] = soup.find('h1', class_='MuiTypography-root MuiTypography-headlineMedium nss-td0143').contents[0]

    except:
        res["name"] = 'N/A'

    try:
        res["location"] = helper.get_location(university_home_page),
    except:
        res["location"] = 'N/A'

    try:
        res["website"] = helper.get_html_elements(
            university_home_page,
            'a',
            'profile__website__link'
        )[0].get('href')
    except:
        res["website"] = 'N/A'

    try:
        res["description"] = helper.get_html_elements(
            university_home_page,
            'p',
            'MuiTypography-root MuiTypography-bodySmall nss-1p11q53'
        )[0].text
    except:
        res["description"] = 'N/A'

    try:
        res["athletics"] = get_athletics_info(university_home_page)
    except:
        res["athletics"] = 'N/A'

    return res


def get_athletics_info(university_home_page):
    res = {
        "division": 'N/A',
        "conference": 'N/A',
    }
    athletics_info = helper.get_html_element_by_id(
        university_home_page,
        'section',
        'about'
    )
    if not athletics_info:
        return 'N/A'

    data = athletics_info.find_all('div', class_='scalar__value')
    if not data:
        return res
    try:
        division = data[0].text
    except:
        division = 'N/A'

    try:
        conference = data[1].text
    except:
        conference = 'N/A'

    res['division'] = division
    res['conference'] = conference
    return res


def get_niche_grades(university_home_page):
    res = {
        "overall": 'N/A',
        "academics": 'N/A',
        "value": 'N/A',
        "diversity": 'N/A',
        "campus": 'N/A',
        "athletics": 'N/A',
        "party_scene": 'N/A',
        "professors": 'N/A',
        "location": 'N/A',
        "dorms": 'N/A',
        "campus_food": 'N/A',
        "student_life": 'N/A',
        "safety": 'N/A',
    }

    soup = helper.BeautifulSoup(university_home_page, 'html.parser')

    # Extract overall grade
    overall_grade_element = soup.select_one('.overall-grade__niche-grade .niche__grade')
    if overall_grade_element:
        res["overall"] = overall_grade_element.text.strip().replace("grade\u00a0", "")

    # Extract other grades
    grade_elements = soup.select('.ordered__list__bucket__item')
    for element in grade_elements:
        label = element.select_one('.profile-grade__label').text.strip().lower().replace(' ', '_')
        grade = element.select_one('.niche__grade').text.strip()
        if label in res:
            res[label] = grade.replace("grade\u00a0", "")

    return res


def get_rankings(university_home_page):
    res = {
        "specialty_rankings": []
    }

    soup = helper.BeautifulSoup(university_home_page, 'html.parser')

    # Extract rankings
    ranking_items = soup.select('.rankings__collection__item')
    for item in ranking_items:
        category = item.select_one('.rankings__collection__name').text.strip()
        rank_info = item.select_one('.rankings__collection__ranking').text.strip()
        rank, total_schools = rank_info.split(' of ')
        rank = rank.strip()
        total_schools = total_schools.strip()

        res["specialty_rankings"].append({
            "category": category,
            "rank": rank,
            "total_schools": total_schools
        })

    return res