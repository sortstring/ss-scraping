from . import helper

def is_scholarships_available(html_content):
    div = helper.get_html_element_by_id(html_content, 'div', 'p2-tuition-fee-and-scholarships')
    if not div:
        return False
    return True


def get_features(html_content):
    tag_name = 'p'
    class_name = 'guide-keypoints'
    elements = helper.get_html_elements(html_content, tag_name, class_name)
    features = []
    for element in elements:
        try:
            feature = element.text
        except:
            feature = 'N/A'
        features.append(feature)
    return features

def get_financial_data(html_content):
    data = {
        "scholarships": {
            "available": is_scholarships_available(html_content),
            "guide": {
                "features": get_features(html_content)
            }
        }
    }

    return data

