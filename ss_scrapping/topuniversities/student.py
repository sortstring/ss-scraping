from . import helper


def get_student_data(html_content):
    students, international_students = get_student_count(html_content)
    percents = get_student_percents(html_content)
    res = helper.OrderedDict({
        "total_students": students,
        "undergraduate": {
            "percentage": percents['ug_percent'],
            "international_students": {
                "percentage": percents['ug_intr_percent'],
            }
        },
        "graduate": {
            "percentage": percents['pg_percent'],
            "international_students": {
                "percentage": percents['pg_intr_percent'],
            }
        },
        "total_international_students": international_students,
    })
    return res


def get_student_count(html_content):
    class_name = 'studstaff-subsection-count'
    tag_name = 'div'
    elements = helper.get_html_elements(html_content, tag_name, class_name)
    try:
        students = elements[0].text
    except:
        students = 'N/A'

    try:
        international_students = elements[1].text
    except:
        international_students = 'N/A'

    return students, international_students


def get_student_percents(html_content):
    parent_tag = 'div'
    parent_class = 'color-code-parent'
    nested_tag = 'div'

    elements = helper.get_html_elements(html_content, parent_tag, parent_class)

    try:
        ug_percent = helper.get_innermost_nested_element(elements[0], nested_tag)
    except:
        ug_percent = 'N/A'

    try:
        pg_percent = helper.get_innermost_nested_element(elements[1], nested_tag)
    except:
        pg_percent = 'N/A'

    try:
        ug_intr_percent = helper.get_innermost_nested_element(elements[2], nested_tag)
    except:
        ug_intr_percent = 'N/A'

    try:
        pg_intr_percent = helper.get_innermost_nested_element(elements[3], nested_tag)
    except:
        pg_intr_percent = 'N/A'

    res = {
        "ug_percent": ug_percent,
        "pg_percent": pg_percent,
        "ug_intr_percent": ug_intr_percent,
        "pg_intr_percent": pg_intr_percent
    }

    return res


