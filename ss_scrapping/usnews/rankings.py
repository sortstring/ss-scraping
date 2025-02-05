from . import helper


def has_ratings(html_content):
    tag_name = 'h2'
    id_attr = 'rankings'
    elements = helper.get_html_element_by_id(html_content, tag_name, id_attr)
    if not elements:
        return False
    return True

def get_over_all_rankings(html_content):
    tag_name = 'ul'
    class_name = 'RankList__List-sc-2xewen-0 ciVlaM util__RankList-sc-1kd04gx-3 dteFWJ'
    elements = helper.get_html_elements(html_content, tag_name, class_name)
    national_universities_rank = "N/A"
    best_value_schools_rank = "N/A"
    business_programs_rank = "N/A"
    other_ratings_url = "N/A"
    other_types = []

    for li in elements[0]:
        a_tag = li.find('a')
        div = a_tag.find('div')
        rank_div = div.find('strong')
        if not rank_div:
            continue
        rank = rank_div.text

        types = a_tag.find_all('strong')
        other_types = []

        for type in types:
            if 'National Universities' in type.text:
                national_universities_rank = rank

            elif "Best Value Schools" in type.text:
                best_value_schools_rank = rank

            elif "Business Programs" in type.text:
                business_programs_rank = rank
            elif type.text != rank:
                other_types.append(f"{rank} in {type.text}")

        other_ratings_url = get_other_ratings_url(html_content)

    return (
        national_universities_rank,
        best_value_schools_rank,
        business_programs_rank,
        other_types,
    )


def get_other_ratings_url(html_content):
    tag_name = 'a'
    class_name = 'Anchor-byh49a-0 cXNfar'
    elements = helper.get_html_elements(html_content, tag_name, class_name)
    for element in elements:
        if element.get('data-tracking-placement') == 'Rankings':
            return element['href']
    return None


def get_ranking_data(html_content):
    data = {
        "national_universities_rank": "N/A",
        "best_value_schools_rank": "N/A",
        "business_programs_rank": "N/A",
        "other_rankings": ['N/A'],
    }
    if not has_ratings(html_content):
        helper.logger.info("No ratings found")
        return data

    national_universities_rank, best_value_schools_rank, business_programs_rank, \
        other_rankings = get_over_all_rankings(html_content)

    data['national_universities_rank'] = national_universities_rank
    data['best_value_schools_rank'] = best_value_schools_rank
    data['business_programs_rank'] = business_programs_rank
    data['other_rankings'] = other_rankings

    return data



# def get_qs_world_rankings(html_content):
#     try:
#         criteria_wrap = helper.get_html_elements(html_content, 'div', 'criteria-wrap')
#         circles = criteria_wrap[0].find_all('div', class_='circle')
#     except Exception as e:
#         helper.logger.error(f"Error in getting QS World Rankings {e}")
#         circles = []

#     return circles
