from . import helper


def get_notable_features(html_content, about_us_paragraph):
    data = {
        "specialized_programs": [
            helper.get_answer(
                "What are the names of the highly ranked graduate programs at the university?",
                about_us_paragraph

            )
        ],
        "research": get_faculty_resesrch(html_content),
        "notable_alumni": [
            helper.get_answer(
                "Who are some of the notable alumni of the university?",
                about_us_paragraph
            )
        ]
    }

    return data
#

def get_faculty_resesrch(html_content):
    research = {
        "research_expenditures": 'N/A',
        "bibliometric_rank": 'N/A',
        "total_papers": 'N/A',
        "citations_per_publication": 'N/A',
        "field_weighted_citation_impact": 'N/A',
    }

    research_div = helper.get_html_elements(html_content, 'div', 'FacultyResearchImpact__StyledDataRow-ewzxnx-2')
    if research_div and len(research_div) > 0:
        for div in research_div:
            paragraphs = div.find_all('p')
            if paragraphs and len(paragraphs) >= 2:
                key = paragraphs[0].text
                value = paragraphs[1].text

                if key == "Bibliometric Rank":
                    research["bibliometric_rank"] = value
                if "Total Papers published" in key:
                    research["total_papers"] = value
                if key == "Citations Per Publication":
                    research["citations_per_publication"] = value
                if key == "Field Weighted Citation Impact":
                    research["field_weighted_citation_impact"] = value

    return research