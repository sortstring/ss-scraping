from . import helper


def get_admission_data(html_content):
    data = {
        "undergraduate": {
            "sat_score": 'N/A',
            "toefl_score": 'N/A',
        },
        "graduate": {
            "gmat_score": 'N/A',
            "ielts_score": 'N/A',
            "toefl_score": 'N/A',
        }
    }
    tag_name = 'a'
    id_attr = 'admission_Tab'
    elements = helper.get_html_element_by_id(html_content, tag_name, id_attr)
    if not elements:
        data

    tag_name = 'div'
    class_name = 'univ-subsection-full-width'
    elements = helper.get_html_elements(html_content, tag_name, class_name)

    undergrad_index = -1
    grad_index = -1
    for index in range(len(elements)):
        if 'Bachelor' in elements[index].text:
            undergrad_index = index
        if 'Master' in elements[index].text:
            grad_index = index

    if undergrad_index != -1:
        undergrad_div = elements[undergrad_index]
        outer_div = undergrad_div.find_all('div')
        inner_nested_div = outer_div[0].find_all('div')
        for index, item in enumerate(inner_nested_div):
            if 'SAT' in item.text:
                try:
                    sat_score_div = inner_nested_div[index+1]
                    data['undergraduate']['sat_score'] = sat_score_div.text
                except:
                    pass

            if 'TOEFL' in item.text:
                try:
                    toefl_score_div = inner_nested_div[index+1]
                    data['undergraduate']['toefl_score'] = toefl_score_div.text
                except:
                    pass

    if grad_index != -1:
        grad_div = elements[grad_index]
        outer_div = grad_div.find_all('div')
        inner_nested_div = outer_div[0].find_all('div')
        for index, item in enumerate(inner_nested_div):
            if 'GMAT' in item.text:
                try:
                    gmat_score_div = inner_nested_div[index+1]
                    data['graduate']['gmat_score'] = gmat_score_div.text
                except:
                    pass

            if 'IELTS' in item.text:
                try:
                    ielts_score_div = inner_nested_div[index+1]
                    data['graduate']['ielts_score'] = ielts_score_div.text
                except:
                    pass

            if 'TOEFL' in item.text:
                try:
                    toefl_score_div = inner_nested_div[index+1]
                    data['graduate']['toefl_score'] = toefl_score_div.text
                except:
                    pass

    return data


