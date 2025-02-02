
from . import helper


def get_admission_requirements(university_home_page):
    res = {
        "acceptance_rate": 'N/A',
        "application_deadline": 'N/A',
        "application_fee": 'N/A',
        "test_scores": {
            "sat_range": {
                "min": 'N/A',
                "max": 'N/A'
            },
            "act_range": {
                "min": 'N/A',
                "max": 'N/A'
            }
        },
        "requirements": {
            "sat_act": 'N/A',
            "high_school_gpa": 'N/A',
            "early_decision": 'N/A',
            "common_app": 'N/A',
        },
        "similar_schools": []
    }

    soup = helper.BeautifulSoup(university_home_page, 'html.parser')

    # Extract acceptance rate
    acceptance_rate_element = soup.select_one('.block--admissions__application-deadline + .MuiGrid-item .scalar__value span')
    if acceptance_rate_element:
        try:
            res["acceptance_rate"] = float(acceptance_rate_element.text.strip('%')) / 100
        except:
            res["acceptance_rate"] = 'N/A'

    # Extract application deadline
    application_deadline_element = soup.select_one('.block--admissions__application-deadline .scalar__value span')
    if application_deadline_element:
        try:
            res["application_deadline"] = application_deadline_element.text.strip()
        except:
            res["application_deadline"] = 'N/A'

    # Extract application fee
    application_fee_element = soup.select_one('.scalar--three .scalar__label:contains("Application Fee") + .scalar__value span')
    if application_fee_element:
        try:
            res["application_fee"] = int(application_fee_element.text.strip('$'))
        except:
            res["application_fee"] = 'N/A'

    # Extract SAT range
    sat_range_element = soup.select_one('.scalar--three .scalar__label:contains("SAT Range") + .scalar__value span')
    if sat_range_element:
        try:
            sat_range = sat_range_element.text.strip().split('-')
            res["test_scores"]["sat_range"]["min"] = int(sat_range[0])
            res["test_scores"]["sat_range"]["max"] = int(sat_range[1])
        except:
            res["test_scores"]["sat_range"]["min"] = 'N/A'
            res["test_scores"]["sat_range"]["max"] = 'N/A'

    # Extract ACT range
    act_range_element = soup.select_one('.scalar--three .scalar__label:contains("ACT Range") + .scalar__value span')
    if act_range_element:
        try:
            act_range = act_range_element.text.strip().split('-')
            res["test_scores"]["act_range"]["min"] = int(act_range[0])
            res["test_scores"]["act_range"]["max"] = int(act_range[1])
        except:
            res["test_scores"]["act_range"]["min"] = 'N/A'
            res["test_scores"]["act_range"]["max"] = 'N/A'

    # Extract requirements
    sat_act_element = soup.select_one('.scalar--three .scalar__label:contains("SAT/ACT") + .scalar__value span')
    if sat_act_element:
        try:
            res["requirements"]["sat_act"] = sat_act_element.text.strip()
        except:
            res["requirements"]["sat_act"] = 'N/A'

    high_school_gpa_element = soup.select_one('.scalar--three .scalar__label:contains("High School GPA") + .scalar__value span')
    if high_school_gpa_element:
        try:
            res["requirements"]["high_school_gpa"] = high_school_gpa_element.text.strip()
        except:
            res["requirements"]["high_school_gpa"] = 'N/A'

    early_decision_element = soup.select_one('.scalar--three .scalar__label:contains("Early Decision/Early Action") + .scalar__value span')
    if early_decision_element:
        try:
            res["requirements"]["early_decision"] = early_decision_element.text.strip().lower() == 'yes'
        except:
            res["requirements"]["early_decision"] = 'N/A'

    common_app_element = soup.select_one('.scalar--three .scalar__label:contains("Accepts Common App") + .MuiTypography-subtitleSmall')
    if common_app_element:
        try:
            res["requirements"]["common_app"] = common_app_element.text.strip() != '—'
        except:
            res["requirements"]["common_app"] = 'N/A'

    # Extract similar schools
    similar_schools_elements = soup.select('.popular-entities-list-item .popular-entity__name a')
    for element in similar_schools_elements:
        try:
            res["similar_schools"].append(element.text.strip())
        except:
            pass

    return res


def get_cost_info(university_home_page):
    res = {
        "net_price_per_year": 'N/A',
        "national_average_price": 'N/A',
        "financial_aid": {
            "average_aid_awarded": 'N/A',
            "national_average_aid": 'N/A',
            "students_receiving_aid_percentage": 'N/A',
        }
    }

    soup = helper.BeautifulSoup(university_home_page, 'html.parser')

    # Extract net price per year
    net_price_element = soup.select_one('.scalar__label:contains("Net Price") + .scalar__value span')
    if net_price_element:
        try:
            res["net_price_per_year"] = int(net_price_element.text.strip('$').replace(',', ''))
        except:
            res["net_price_per_year"] = 'N/A'

    # Extract national average price
    national_average_price_element = soup.select_one('.scalar__label:contains("Net Price") + .scalar__value .scalar__national__value')
    if national_average_price_element:
        national_average_price_text = national_average_price_element.text.strip()
        try:
            res["national_average_price"] = int(national_average_price_text.replace('National', '').strip('$').replace(',', ''))
        except:
            res["national_average_price"] = 'N/A'

    # Extract average aid awarded
    average_aid_awarded_element = soup.select_one('.scalar__label:contains("Average Total Aid Awarded") + .scalar__value span')
    if average_aid_awarded_element:
        try:
            res["financial_aid"]["average_aid_awarded"] = int(average_aid_awarded_element.text.strip('$').replace(',', ''))
        except:
            res["financial_aid"]["average_aid_awarded"] = 'N/A'

    # Extract national average aid
    national_average_aid_element = soup.select_one('.scalar__label:contains("Average Total Aid Awarded") + .scalar__value .scalar__national__value')
    if national_average_aid_element:
        national_average_aid_text = national_average_aid_element.text.strip()
        try:
            res["financial_aid"]["national_average_aid"] = int(national_average_aid_text.replace('National', '').strip('$').replace(',', ''))
        except:
            res["financial_aid"]["national_average_aid"] = 'N/A'

    # Extract students receiving aid percentage
    students_receiving_aid_percentage_element = soup.select_one('.scalar__label:contains("Students Receiving Financial Aid") + .scalar__value span')
    if students_receiving_aid_percentage_element:
        try:
            res["financial_aid"]["students_receiving_aid_percentage"] = int(students_receiving_aid_percentage_element.text.strip('%'))
        except:
            res["financial_aid"]["students_receiving_aid_percentage"] = 'N/A'

    return res


def get_academics_info(university_home_page):
    res = {
        "student_faculty_ratio": 'N/A',
        "evening_degree_programs": False,
        "professor_ratings": 'N/A',
        "student_feedback": {
            "professor_effort": {
                "agree_percentage": 'N/A',
                "total_responses": 'N/A'
            },
            "class_availability": {
                "agree_percentage": 'N/A',
                "total_responses": 'N/A'
            },
            "manageable_workload": {
                "agree_percentage": 'N/A',
                "total_responses": 'N/A'
            }
        },
        "popular_majors": get_popular_majors(university_home_page),
        "online_education": get_online_education_info(university_home_page)
    }

    soup = helper.BeautifulSoup(university_home_page, 'html.parser')

    # Extract professor ratings
    professor_ratings_element = soup.select_one('.profile-grade__label:contains("Professors") + .niche__grade')
    if professor_ratings_element:
        res["professor_ratings"] = professor_ratings_element.text.strip().replace("grade\u00a0", "")

    # Extract student faculty ratio
    student_faculty_ratio_element = soup.select_one('.scalar__label:contains("Student Faculty Ratio") + .scalar__value span')
    if student_faculty_ratio_element:
        res["student_faculty_ratio"] = student_faculty_ratio_element.text.strip()

    # Extract evening degree programs
    evening_degree_programs_element = soup.select_one('.scalar__label:contains("Evening Degree Programs") + .scalar__value span')
    if evening_degree_programs_element:
        res["evening_degree_programs"] = evening_degree_programs_element.text.strip().lower() == 'yes'

    # Extract student feedback
    professor_effort_element = soup.select_one('.poll__single__body:contains("professors put a lot of effort")')
    if professor_effort_element:
        parent_element = professor_effort_element.find_parent(class_='poll__single__value')
        if parent_element:
            try:
                res["student_feedback"]["professor_effort"]["agree_percentage"] = int(parent_element.select_one('.poll__single__percent').text.strip('%'))
            except:
                res["student_feedback"]["professor_effort"]["agree_percentage"] = 'N/A'

            try:
                res["student_feedback"]["professor_effort"]["total_responses"] = int(professor_effort_element.select_one('.poll__single__responses').text.strip().split(' ')[0])
            except:
                res["student_feedback"]["professor_effort"]["total_responses"] = 'N/A'

    class_availability_element = soup.select_one('.poll__single__body:contains("easy to get the classes they want")')
    if class_availability_element:
        parent_element = class_availability_element.find_parent(class_='poll__single__value')
        if parent_element:
            try:
                res["student_feedback"]["class_availability"]["agree_percentage"] = int(parent_element.select_one('.poll__single__percent').text.strip('%'))
            except:
                res["student_feedback"]["class_availability"]["agree_percentage"] = 'N/A'
            try:
                res["student_feedback"]["class_availability"]["total_responses"] = int(class_availability_element.select_one('.poll__single__responses').text.strip().split(' ')[0])
            except:
                res["student_feedback"]["class_availability"]["total_responses"] = 'N/A'

    manageable_workload_element = soup.select_one('.poll__single__body:contains("workload is easy to manage")')
    if manageable_workload_element:
        parent_element = manageable_workload_element.find_parent(class_='poll__single__value')
        if parent_element:
            try:
                res["student_feedback"]["manageable_workload"]["agree_percentage"] = int(parent_element.select_one('.poll__single__percent').text.strip('%'))
            except:
                res["student_feedback"]["manageable_workload"]["agree_percentage"] = 'N/A'

            try:
                res["student_feedback"]["manageable_workload"]["total_responses"] = int(manageable_workload_element.select_one('.poll__single__responses').text.strip().split(' ')[0])
            except:
                res["student_feedback"]["manageable_workload"]["total_responses"] = 'N/A'

    return res

def get_online_education_info(university_home_page):
    res = {
        "offers_online_courses": False,
        "learning_distribution": {
            "mixed": 0,
            "on_campus": 100,
            "fully_online": 0
        },
        "online_programs": {
            "complete_programs": 0,
            "certificates": 0,
            "associates": 0,
            "bachelors": 0
        }
    }

    soup = helper.BeautifulSoup(university_home_page, 'html.parser')

    # Extract offers online courses
    offers_online_courses_element = soup.select_one('.scalar__label:contains("Offers Online Courses") + .scalar__value span')
    if offers_online_courses_element:
        res["offers_online_courses"] = offers_online_courses_element.text.strip().lower() == 'yes'

    # Extract learning distribution
    learning_distribution_elements = soup.select('.breakdown-facts .fact__table__row')
    for element in learning_distribution_elements:
        label = element.select_one('.fact__table__row__label').text.strip().lower().replace(' ', '_')
        try:
            value = int(element.select_one('.fact__table__row__value').text.strip('%'))
        except:
            value = 0
        if label in res["learning_distribution"]:
            res["learning_distribution"][label] = value

    # Extract online programs
    online_programs_elements = soup.select('.scalar__label:contains("Programs Offered Entirely Online") + .scalar__value span, .scalar__label:contains("Online Certificate Programs") + .scalar__value span, .scalar__label:contains("Online Associates Programs") + .scalar__value span, .scalar__label:contains("Online Bachelor\'s Programs") + .scalar__value span')
    for element in online_programs_elements:
        label = element.select_one('.scalar__label').text.strip().lower().replace(' ', '_').replace('\'', '') if element.select_one('.scalar__label') else 'N/A'
        try:
            value = int(element.select_one('.scalar__value span').text.strip()) if element.select_one('.scalar__value span') else 0
        except:
            value = 0
        if label in res["online_programs"]:
            res["online_programs"][label] = value

    return res

def get_popular_majors(university_home_page):
    res = []

    soup = helper.BeautifulSoup(university_home_page, 'html.parser')

    # Extract popular majors
    popular_majors_elements = soup.select('.popular-entities-list-item')
    for element in popular_majors_elements:
        name_element = element.select_one('.popular-entity__name')
        graduates_element = element.select_one('.popular-entity-descriptor')
        if name_element and graduates_element:
            name = name_element.text.strip()
            try:
                graduates = int(graduates_element.text.strip().split(' ')[0].replace(',', ''))
            except:
                graduates = 'N/A'
            res.append({
                "name": name,
                "graduates": graduates
            })

    return res