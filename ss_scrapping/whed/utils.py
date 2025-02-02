from . import general_info
from . import degrees

def get_general_info(html_content, topic_1, university_name, parent_university_name):
    return general_info.get_general_info(html_content, topic_1, university_name, parent_university_name)


def get_divisions(html_content, topic_1):
    return general_info.get_divisions(html_content, topic_1)


def get_degrees_info(html_content, topic_1):
    return degrees.get_degrees_info(html_content, topic_1)