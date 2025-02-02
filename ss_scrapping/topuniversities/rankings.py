from . import helper


def has_ratings(html_content):
    tag_name = 'div'
    id_attr = 'p2-rankings'
    elements = helper.get_html_element_by_id(html_content, tag_name, id_attr)
    if not elements:
        return False
    return True

def get_over_all_rankings(html_content):
    tag_name = 'a'
    class_name = 'use-ajax'
    elements = helper.get_html_elements(html_content, tag_name, class_name)
    rating = 'N/A'
    qs_world_rankings = 'N/A'
    qs_subject_ranking = 'N/A'
    qs_sustainability_ranking = 'N/A'
    for element in elements:
        try:
            rating = element.find('div', class_='latest_rank').text
        except:
            continue

        if element.get('id') == 'wur-tab':
            qs_world_rankings = rating
        elif element.get('id') == 'subj-tab':
            qs_subject_ranking = rating
        elif element.get('id') == 'item-4085':
            qs_sustainability_ranking = rating

    return qs_world_rankings, qs_subject_ranking, qs_sustainability_ranking


def get_ranking_data(html_content):
    data = {
        "qs_world_rankings": {
            "2025": {
                "overall_rank": "N/A",
                "scores": {
                    "overall": "N/A",
                    "academic_reputation": "N/A",
                    "citations_per_faculty": "N/A",
                    "employment_outcomes": "N/A",
                    "employer_reputation": "N/A",
                    "faculty_student_ratio": "N/A",
                    "international_faculty_ratio": "N/A",
                    "international_research_network": "N/A",
                    "international_student_ratio": "N/A",
                    "sustainability": "N/A"
                }
            }
        },
        "other_rankings": {
            "qs_subject_ranking": 'N/A',
            "qs_sustainability_ranking": 'N/A',
        }
    }
    if not has_ratings(html_content):
        helper.logger.info("No ratings found")
        return data

    qs_world_rankings, qs_subject_ranking, qs_sustainability_ranking = get_over_all_rankings(html_content)
    data['other_rankings']['qs_subject_ranking'] = qs_subject_ranking
    data['other_rankings']['qs_sustainability_ranking'] = qs_sustainability_ranking
    data['qs_world_rankings']['2025']['overall_rank'] = qs_world_rankings

    circles = get_qs_world_rankings(html_content)
    for circle in circles:
        try:
            score = circle.find('div', class_='score').text
            value = circle.find('div', class_='itm-name').text
            value = value.lower().replace(' ', '_')
            data['qs_world_rankings']['2025']['scores'][value] = score
        except Exception as e:
            helper.logger.error(f"Error in getting QS World Rankings {e}")
    return data



def get_qs_world_rankings(html_content):
    try:
        criteria_wrap = helper.get_html_elements(html_content, 'div', 'criteria-wrap')
        circles = criteria_wrap[0].find_all('div', class_='circle')
    except Exception as e:
        helper.logger.error(f"Error in getting QS World Rankings {e}")
        circles = []

    return circles
