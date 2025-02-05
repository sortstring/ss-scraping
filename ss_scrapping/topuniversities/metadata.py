from . import helper


def get_metadata(html_content, last_updated):
    content = helper.get_html_element_by_id(html_content, 'p', 'wur-content')

    year = 'N/A'
    data_source = 'QS World University Rankings'
    if content and data_source in content.text:
        year = extract_year(content.text) or 'N/A'
    else:
        data_source = 'N/A'

    return {
        "data_source": data_source,
        "last_updated": last_updated,
        "ranking_year": year
    }

def extract_year(text):
    match = helper.re.search(r'QS World University Rankings (\d{4})', text)
    if match:
        return match.group(1)
    return None