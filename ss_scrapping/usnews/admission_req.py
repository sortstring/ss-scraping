from . import helper


def get_admission_data(html_content):
    data = {
        "acceptance_rate": "N/A",
        "application_deadline": "N/A",
        "test_scores": {
            "sat": {
                "25th_percentile": "N/A",
                "75th_percentile": "N/A",
            },
            "act": {
                "25th_percentile": "N/A",
                "75th_percentile": "N/A",
            }
        },
        "high_school_gpa": {
            "reported": "N/A",
            "value": "N/A"
        }
    }

    adm_div = get_admission_details_div(html_content)
    if not adm_div:
        helper.logger.info("No admission details found")
        return data

    text_type = adm_div.find_all('div', class_='ApplyingSection__DataLabel-sc-2strss-8')
    try:
        assert text_type and text_type[0].text == 'Application Deadline'
        data["application_deadline"] = adm_div.find_all('p', class_='ApplyingSection__DataHeader-sc-2strss-7')[0].text
    except:
        pass

    try:
        assert text_type and text_type[1].text == 'Acceptance Rate'
        data["acceptance_rate"] = adm_div.find_all('p', class_='ApplyingSection__DataHeader-sc-2strss-7')[1].text
    except:
        pass

    scores = adm_div.find_all('div', class_='ApplyingSection__StyledDataRow-sc-2strss-5')
    for score in scores:
        paragraphs = score.find_all('p', class_='Paragraph-sc-1iyax29-0')
        if not paragraphs:
            continue

        if 'SAT' in paragraphs[0].text:
            try:
                sat_range = list(map(int, paragraphs[1].text.split('-')))
            except:
                continue
            else:
                data['test_scores']['sat']['25th_percentile'] = sat_range[0]
                data['test_scores']['sat']['75th_percentile'] = sat_range[1]

        elif 'ACT' in paragraphs[0].text:
            try:
                act_range = list(map(int, paragraphs[1].text.split('-')))
            except:
                continue
            else:
                data['test_scores']['act']['25th_percentile'] = act_range[0]
                data['test_scores']['act']['75th_percentile'] = act_range[1]

        elif 'High School GPA' in paragraphs[0].text:
            data['high_school_gpa']['reported'] = True
            data['high_school_gpa']['value'] = paragraphs[1].text


    return data


def get_admission_details_div(html_content):
    h2_element = helper.get_html_element_by_id(html_content, 'h2', 'admissions')
    if h2_element:
        next_div = h2_element.find_next_sibling('div', class_='Grid-lx2f3i-0 fQYHzS')
        if next_div:
            return next_div

    return None