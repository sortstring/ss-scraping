from . import helper
from . import institution
from . import student
from . import admission_req
from . import programs
from . import rankings
from . import fin_info
from . import after_grad
from . import metadata
from . import features




def get_about_us_paragraph(university_home_page):
    return helper.get_about_us_paragraph(university_home_page)

def get_institution_data(university_home_page, university_name, about_us_paragraph):
    return institution.get_institution_data(university_home_page, university_name, about_us_paragraph)

def get_student_data(university_home_page, about_us_paragraph):
    return student.get_student_data(university_home_page, about_us_paragraph)

def get_admission_data(university_home_page):
    return admission_req.get_admission_data(university_home_page)

def get_available_programs_data(university_home_page):
    return programs.get_available_programs_data(university_home_page)

def get_ranking_data(university_home_page):
    return rankings.get_ranking_data(university_home_page)

def get_financial_data(university_home_page):
    return fin_info.get_financial_data(university_home_page)

def get_after_graduation_data(university_home_page):
    return after_grad.get_after_graduation_data(university_home_page)

def get_metadata(university_home_page, last_updated):
    return metadata.get_metadata(university_home_page, last_updated)

def get_answer_in_list(question, about_us_paragraph):
    return helper.get_answer_in_list(question, about_us_paragraph)

def get_answer(question, about_us_paragraph):
    return helper.get_answer(question, about_us_paragraph)

def get_notable_features(university_home_page, about_us_paragraph):
    return features.get_notable_features(university_home_page, about_us_paragraph)