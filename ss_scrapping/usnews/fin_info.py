from . import helper

def has_info(html_content):
    tag_name = 'h2'
    id_attr = 'cost'
    element = helper.get_html_element_by_id(html_content, tag_name, id_attr)
    if not element:
        return False
    return True


def get_financial_data(html_content):
    data = {
        "tuition_and_fees": 'N/A',
        "room_and_board": 'N/A',
        "books_and_supplies": 'N/A',
        "financial_aid": {
            "students_receiving_aid": 'N/A',
            "avg_need_based_aid": 'N/A',
            "avg_need_met": 'N/A',
        }
    }

    fin_div = get_financial_details_div(html_content)
    inner_divs = fin_div.find_all('div', class_='ContentSection__StyledDataRow-sc-699pa9-4')
    for div in inner_divs:
        paragraphs = div.find_all('p', class_='Paragraph-sc-1iyax29-0')
        if not paragraphs or len(paragraphs) < 2:
            continue

        if 'Tuition' in paragraphs[0].text:
            data['tuition_and_fees'] = paragraphs[1].text
        elif 'Food & Housing' in paragraphs[0].text:
            data['room_and_board'] = paragraphs[1].text
        elif 'Average Need-Based Aid Package' in paragraphs[0].text:
            data['financial_aid']['avg_need_based_aid'] = paragraphs[1].text

    return data


def get_financial_details_div(html_content):
    h2_element = helper.get_html_element_by_id(html_content, 'h2', 'cost')
    if h2_element:
        next_div = h2_element.find_next_sibling('div', class_='Grid-lx2f3i-0 ContentSection__StyledGrid-sc-699pa9-1 fQYHzS eWFIVC sm-hide')
        if next_div:
            return next_div.find('div', class_='ContentSection__StyledCell-sc-699pa9-3')

    return None
