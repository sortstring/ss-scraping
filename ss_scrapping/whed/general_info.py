from . import helper


def get_general_info(html_content, topic_1, university_name, parent_university_name):
    data = {
        "Address": {
            "Street": 'N/A',
            "City": 'N/A',
            "Province": 'N/A',
            "PostCode": 'N/A',
            "Website": 'N/A',
            "college_name": university_name,
            "university_name": parent_university_name,
        },
        "InstitutionFunding": 'N/A',
        "History": 'N/A',
        "AcademicYear": 'N/A',
        "AdmissionRequirements": [],
        "Languages": [],
        "StudentBody": 'N/A',
    }

    section = helper.get_html_content_by_id(html_content, 'section', 'contenu')
    if not section:
        return data

    h3_elements = section.find_all('h3')
    for h3 in h3_elements:
        if h3.text.strip() == topic_1:
            divs = h3.find_all_next('div', class_='dl')
            if divs:
                for div in divs:
                    inner_text = None
                    if div.find('span', class_='dt'):
                        inner_text = (div.find('span', class_='dt').text).strip() or None

                    if inner_text:

                        if inner_text == "Address":
                            paragraphs = div.find('div', class_='dd').find_all('p')
                            for paragraph in paragraphs:
                                if paragraph.find('span', class_='libelle') and 'street' in paragraph.find('span', class_='libelle').text.lower():
                                    data["Address"]["Street"] = paragraph.find('span', class_='contenu').text

                                if paragraph.find('span', class_='libelle') and 'city' in paragraph.find('span', class_='libelle').text.lower():
                                    data["Address"]["City"] = paragraph.find('span', class_='contenu').text

                                if paragraph.find('span', class_='libelle') and 'province' in paragraph.find('span', class_='libelle').text.lower():
                                    data["Address"]["Province"] = paragraph.find('span', class_='contenu').text

                                if paragraph.find('span', class_='libelle') and 'post code' in paragraph.find('span', class_='libelle').text.lower():
                                    data["Address"]["PostCode"] = paragraph.find('span', class_='contenu').text

                                if paragraph.find('span', class_='libelle') and 'www' in paragraph.find('span', class_='libelle').text.lower():
                                    data["Address"]["Website"] = paragraph.find('span', class_='contenu').text

                            if data["Address"]["Website"] == 'N/A':
                                spans = div.find('div', class_='dd').find_all('span')
                                for index, span in enumerate(spans):
                                    if 'www' in span.text.strip().lower():
                                        data["Address"]["Website"] = spans[index+1].text.strip()
                                        break

                            if data["Address"]["Street"] == 'N/A':
                                spans = div.find('div', class_='dd').find_all('span')
                                for index, span in enumerate(spans):
                                    if 'street' in span.text.strip().lower():
                                        data["Address"]["Street"] = spans[index+1].text.strip()
                                        break

                            if data["Address"]["City"] == 'N/A':
                                spans = div.find('div', class_='dd').find_all('span')
                                for index, span in enumerate(spans):
                                    if 'city' in span.text.strip().lower():
                                        data["Address"]["City"] = spans[index+1].text.strip()
                                        break

                            if data["Address"]["Province"] == 'N/A':
                                spans = div.find('div', class_='dd').find_all('span')
                                for index, span in enumerate(spans):
                                    if 'province' in span.text.strip().lower():
                                        data["Address"]["Province"] = spans[index+1].text.strip()
                                        break

                            if data["Address"]["PostCode"] == 'N/A':
                                spans = div.find('div', class_='dd').find_all('span')
                                for index, span in enumerate(spans):
                                    if 'post code' in span.text.strip().lower():
                                        data["Address"]["PostCode"] = spans[index+1].text.strip()
                                        break

                            # try:
                            #     data["Address"]["Street"] = paragraphs[0].find('span', class_='contenu').text
                            # except:
                            #     pass
                            # try:
                            #     data["Address"]["City"] = paragraphs[1].find('span', class_='contenu').text
                            # except:
                            #     pass
                            # try:
                            #     data["Address"]["Province"] = paragraphs[2].find('span', class_='contenu').text
                            # except:
                            #     pass
                            # try:
                            #     data["Address"]["PostCode"] = paragraphs[3].find('span', class_='contenu').text
                            # except:
                            #     pass
                            # try:
                            #     data["Address"]["Website"] = paragraphs[4].find('span', class_='contenu').text
                            # except:
                            #     pass

                        if inner_text == "Institution Funding":
                            paragraphs = div.find('div', class_='dd').find_all('p')
                            # join all paragraph elements
                            data["InstitutionFunding"] = ' '.join([paragraph.text for paragraph in paragraphs])

                        if inner_text == "History":
                            paragraphs = div.find('div', class_='dd').find_all('p')
                            data["History"] = ' '.join([paragraph.text for paragraph in paragraphs])

                        if inner_text == "Academic Year":
                            paragraphs = div.find('div', class_='dd').find_all('p')
                            data["AcademicYear"] = ' '.join([paragraph.text for paragraph in paragraphs])

                        if inner_text == "Admission Requirements":
                            paragraphs = div.find('div', class_='dd').find_all('p')
                            data["AdmissionRequirements"] = list(map(lambda x: x.strip(), paragraphs[0].text.split('.')))

                        if inner_text == "Language(s)":
                            paragraphs = div.find('div', class_='dd').find_all('p')
                            languages = paragraphs[0].text
                            data["Languages"] = languages.split(';')

                        if inner_text == 'Student Body':
                            paragraphs = div.find('div', class_='dd').find_all('p')
                            data["StudentBody"] = ' '.join([paragraph.text for paragraph in paragraphs])
                    else:
                        break


            break
    return data



def get_divisions(html_content, topic_1):
    section = helper.get_html_content_by_id(html_content, 'section', 'contenu')
    if not section:
        return 'N/A'

    h3_elements = section.find_all('h3')
    divisions = []

    for h3 in h3_elements:
        if h3.text.strip() == topic_1:
            divs = h3.find_all_next('div', class_='dl')
            if divs:
                for div in divs:
                    if div.find('div', class_='dd'):
                        paragraphs = div.find('div', class_='dd').find_all('p', class_='principal')
                        for paragraph in paragraphs:
                            college = None
                            field_of_study = None
                            more_details = None

                            try:
                                college = paragraph.text.split(':')[-1].strip()
                            except:
                                pass

                            try:
                                next_paragraph = paragraph.find_next_sibling('p')
                                assert next_paragraph
                                assert next_paragraph.class_ != 'principal'
                                field_of_study = next_paragraph.find('span', class_='contenu').text
                            except:
                                pass
                            else:
                                try:
                                    next_paragraph = next_paragraph.find_next_sibling('p')
                                    assert next_paragraph
                                    assert next_paragraph.class_ != 'principal'
                                    more_details = next_paragraph.find('span', class_='contenu').text
                                except:
                                    pass

                            divisions.append({
                                "College": college.split(':')[-1].strip() if college else 'N/A',
                                "FieldsOfStudy": list(map(lambda x: x.strip(), field_of_study.split(',')))
                                                                            if field_of_study else 'N/A',
                                "Details": more_details if more_details else 'N/A'
                            })
                    if div.find_next_sibling('h3'):
                        break

    return divisions
