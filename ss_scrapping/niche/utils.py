from . import basic_info
from . import admissions
from . import students
from . import outcome_metadata


def get_basic_info(university_home_page):
    return basic_info.get_basic_info(university_home_page)

def get_niche_grades(university_home_page):
    return basic_info.get_niche_grades(university_home_page)


def get_rankings(university_home_page):
    return basic_info.get_rankings(university_home_page)

def get_admission_requirements(university_home_page):
    return admissions.get_admission_requirements(university_home_page)

def get_cost_info(university_home_page):
    return admissions.get_cost_info(university_home_page)

def get_academics_info(university_home_page):
    return admissions.get_academics_info(university_home_page)

def get_student_info(university_home_page):
    return students.get_student_info(university_home_page)

def get_outcome(university_home_page):
    return outcome_metadata.get_outcome(university_home_page)