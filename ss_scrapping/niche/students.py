from bs4 import BeautifulSoup

def get_student_info(university_home_page):
    res = {
        "enrollment": {
            "full_time_undergrads": 'N/A',
            "part_time_undergrads": 'N/A',
            "over_25_percentage": 'N/A',
            "pell_grant_percentage": 'N/A',
            "varsity_athletes_percentage": 'N/A'
        },
        "campus_experience": get_campus_experience(university_home_page),
    }

    soup = BeautifulSoup(university_home_page, 'html.parser')

    # Extract enrollment information
    full_time_element = soup.select_one('.scalar__label:contains("Full-Time Enrollment") + .scalar__value span')
    if full_time_element:
        res["enrollment"]["full_time_undergrads"] = int(full_time_element.text.strip().replace(',', ''))

    part_time_element = soup.select_one('.scalar__label:contains("Part-Time Undergrads") + .scalar__value span')
    if part_time_element:
        res["enrollment"]["part_time_undergrads"] = int(part_time_element.text.strip().replace(',', ''))

    over_25_element = soup.select_one('.scalar__label:contains("Undergrads Over 25") + .scalar__value span')
    if over_25_element:
        res["enrollment"]["over_25_percentage"] = int(over_25_element.text.strip('%'))

    pell_grant_element = soup.select_one('.scalar__label:contains("Pell Grant") + .scalar__value span')
    if pell_grant_element:
        res["enrollment"]["pell_grant_percentage"] = int(pell_grant_element.text.strip('%'))

    varsity_athletes_element = soup.select_one('.scalar__label:contains("Varsity Athletes") + .scalar__value span')
    if varsity_athletes_element:
        res["enrollment"]["varsity_athletes_percentage"] = int(varsity_athletes_element.text.strip('%'))

    return res


def get_campus_experience(university_home_page):
    res = {
        "freshman_housing": {
            "live_on_campus_percentage": 'N/A'
        },
        "day_care_services": False,
        "greek_life": {
            "description": 'N/A',
            "agree_percentage": 'N/A',
            "responses": 'N/A'
        },
        "sports_culture": {
            "description": 'N/A',
            "agree_percentage": 'N/A',
            "responses": 'N/A'
        },
        "facility_ratings": {
            "athletics": {
                "highly_rated_percentage": 'N/A',
                "responses": 'N/A'
            },
            "dining": {
                "highly_rated_percentage": 'N/A',
                "responses": 'N/A'
            },
            "performing_arts": {
                "highly_rated_percentage": 'N/A',
                "responses": 'N/A'
            }
        },
        "typical_student_descriptions": get_typicalStudent_description(university_home_page),
    }

    soup = BeautifulSoup(university_home_page, 'html.parser')

    # Extract freshman housing
    freshman_housing_element = soup.select_one('.scalar__label:contains("Freshman Live On-Campus") + .scalar__value span')
    if freshman_housing_element:
        res["freshman_housing"]["live_on_campus_percentage"] = int(freshman_housing_element.text.strip('%'))

    # Extract day care services
    day_care_services_element = soup.select_one('.scalar__label:contains("Day Care Services") + .scalar__value span')
    if day_care_services_element:
        res["day_care_services"] = day_care_services_element.text.strip().lower() == 'yes'

    # Extract Greek life
    greek_life_element = soup.select_one('.poll__single__body:contains("Greek life is average")')
    if greek_life_element:
        parent_element = greek_life_element.find_parent(class_='poll__single__value')
        if parent_element:
            res["greek_life"]["description"] = greek_life_element.text.strip()
            res["greek_life"]["agree_percentage"] = int(parent_element.select_one('.poll__single__percent').text.strip('%'))
            res["greek_life"]["responses"] = int(greek_life_element.select_one('.poll__single__responses').text.strip().split(' ')[0])

    # Extract sports culture
    sports_culture_element = soup.select_one('.poll__single__body:contains("varsity sporting events are attended")')
    if sports_culture_element:
        parent_element = sports_culture_element.find_parent(class_='poll__single__value')
        if parent_element:
            res["sports_culture"]["description"] = sports_culture_element.text.strip()
            res["sports_culture"]["agree_percentage"] = int(parent_element.select_one('.poll__single__percent').text.strip('%'))
            res["sports_culture"]["responses"] = int(sports_culture_element.select_one('.poll__single__responses').text.strip().split(' ')[0])

    # Extract facility ratings
    athletics_element = soup.select_one('.poll__single__body:contains("highly rate the athletics/recreation facilities")')
    if athletics_element:
        parent_element = athletics_element.find_parent(class_='poll__single__value')
        if parent_element:
            res["facility_ratings"]["athletics"]["highly_rated_percentage"] = int(parent_element.select_one('.poll__single__percent').text.strip('%'))
            res["facility_ratings"]["athletics"]["responses"] = int(athletics_element.select_one('.poll__single__responses').text.strip().split(' ')[0])

    dining_element = soup.select_one('.poll__single__body:contains("highly rate the dining facilities")')
    if dining_element:
        parent_element = dining_element.find_parent(class_='poll__single__value')
        if parent_element:
            res["facility_ratings"]["dining"]["highly_rated_percentage"] = int(parent_element.select_one('.poll__single__percent').text.strip('%'))
            res["facility_ratings"]["dining"]["responses"] = int(dining_element.select_one('.poll__single__responses').text.strip().split(' ')[0])

    performing_arts_element = soup.select_one('.poll__single__body:contains("highly rate the performing arts facilities")')
    if performing_arts_element:
        parent_element = performing_arts_element.find_parent(class_='poll__single__value')
        if parent_element:
            res["facility_ratings"]["performing_arts"]["highly_rated_percentage"] = int(parent_element.select_one('.poll__single__percent').text.strip('%'))
            res["facility_ratings"]["performing_arts"]["responses"] = int(performing_arts_element.select_one('.poll__single__responses').text.strip().split(' ')[0])

    return res


def get_typicalStudent_description(university_home_page):
    res = []

    soup = BeautifulSoup(university_home_page, 'html.parser')

    # Extract typical student descriptions
    typical_student_elements = soup.select('.poll__table__result__item')
    for element in typical_student_elements:
        description_element = element.select_one('.poll__table__result__label')
        percentage_element = element.select_one('.poll__table__result__percent')
        if description_element and percentage_element:
            description = description_element.text.strip()
            percentage = int(percentage_element.text.strip('%'))
            res.append({
                "description": description,
                "percentage": percentage
            })

    return res
