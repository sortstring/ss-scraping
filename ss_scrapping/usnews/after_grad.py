from . import helper


def data_exists(html_content):
    try:
        h2_element = helper.get_html_element_by_id(html_content, 'h2', 'aftercollege')
        assert h2_element
    except:
        return False
    return True


def get_median_earnings_6_years(html_content):
    median_earnings_6_years = 'N/A'
    try:
        h2_element = helper.get_html_element_by_id(html_content, 'h2', 'aftercollege')
        if h2_element:
            next_div = h2_element.find_next_sibling('div', class_='Grid-lx2f3i-0 ContentSection__StyledGrid-sc-699pa9-1 fQYHzS eWFIVC sm-hide')
            if next_div:
                median_earnings_6_years = next_div.find('p', class_='AfterCollegeSection__DataHeader-czoza-1 iYbKOL').text.lstrip('$')
    except:
        pass
    return median_earnings_6_years


def get_student_debt_div(html_content):
    try:
        h2_element = helper.get_html_element_by_id(html_content, 'h2', 'aftercollege')
        if h2_element:
            next_div = h2_element.find_next_sibling('div', class_='Grid-lx2f3i-0 ContentSection__StyledGrid-sc-699pa9-1 fQYHzS eWFIVC sm-hide')
            if next_div:
                return next_div.find('div')
    except:
        return 'N/A'

def get_after_graduation_data(html_content):
    data = {
        "salary_stats": {
            "median_earnings_6_years": 'N/A',
            "median_earnings_10_years": "N/A",
        },
        "employment_stats": {
            "employment_rate_2_years": "N/A",
        },
        "grad_school_stats": {
            "grad_school_attendance_rate": "N/A",
        },
        "student_debt": {
            "graduates_with_debt": "N/A",
            "avg_debt_at_graduation": "N/A",
            "loan_default_rate": "N/A",
        }
    }

    if not data_exists(html_content):
        return data

    data["salary_stats"]["median_earnings_6_years"] = get_median_earnings_6_years(html_content)

    student_debt_div = get_student_debt_div(html_content)
    student_debt_divs = student_debt_div.find_all('div')
    # print(student_debt_divs)

    try:
        paragraphs = student_debt_divs[1].find_all('p')
        if paragraphs and len(paragraphs) >= 2:
            data["student_debt"]["graduates_with_debt"] = paragraphs[1].text.rstrip('%')
    except:
        pass

    try:
        paragraphs = student_debt_divs[2].find_all('p')
        if paragraphs and len(paragraphs) >= 2:
            data["student_debt"]["avg_debt_at_graduation"] = paragraphs[1].text.lstrip('$')
    except:
        pass
    return data