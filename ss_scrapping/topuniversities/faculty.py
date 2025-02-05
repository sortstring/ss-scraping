from . import helper


def get_faculty_data(html_content):
    percents = get_staff_percents(html_content)
    res = helper.OrderedDict({
        "total_staff": get_staff_count(html_content),
        "composition": {
            "domestic": {
                "percentage": percents['domestic_percent']
            },
            "international": {
                "percentage": percents['international_percent']
            }
        }
    })
    return res


def get_staff_count(html_content):
    class_name = 'studstaff-subsection-count'
    tag_name = 'div'
    elements = helper.get_html_elements(html_content, tag_name, class_name)
    try:
        staff_count = elements[2].text
    except:
        staff_count = 'N/A'
    return staff_count


def get_staff_percents(html_content):
    parent_tag = 'div'
    parent_class = 'color-code-parent'
    nested_tag = 'div'

    elements = helper.get_html_elements(html_content, parent_tag, parent_class)

    try:
        domestic_percent = helper.get_innermost_nested_element(elements[4], nested_tag)
    except:
        domestic_percent = 'N/A'

    try:
        international_percent = helper.get_innermost_nested_element(elements[5], nested_tag)
    except:
        international_percent = 'N/A'

    res = {
        "domestic_percent": domestic_percent,
        "international_percent": international_percent,
    }

    return res