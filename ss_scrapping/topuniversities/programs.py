from . import helper


def get_available_programs_div(html_content):
    tag_name = 'div'
    class_name = 'avail_prog'
    elements = helper.get_html_elements(html_content, tag_name, class_name)
    programs_list_id = 'aptabs'

    try:
        program_list = elements[0].find_all('ul', id=programs_list_id)
        list_elements = program_list[0].find_all('li')
        assert list_elements
    except:
        list_elements = []

    return list_elements


def get_available_programs_data(html_content):
    available_programs = []
    programs_div = get_available_programs_div(html_content)
    if not programs_div:
        return []

    for program in programs_div:
        spans = program.find_all('span')
        try:
            name = spans[0].text
        except:
            name = 'N/A'

        try:
            level = spans[1].text
        except:
            level = 'N/A'

        if name == 'N/A':
            h3s = program.find_all('h3')
            try:
                name = h3s[0].text
            except:
                name = 'N/A'

        if level == 'N/A':
            h3s = program.find_all('h3')
            try:
                level = h3s[1].text
            except:
                level = 'N/A'

        available_programs.append({
            "name": name,
            "level": level,
            "school": 'N/A'
        })

    return available_programs