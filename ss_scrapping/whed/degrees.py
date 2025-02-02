from . import helper


def get_degrees_info(html_content, topic_1):
    data = {
        "Undergraduate": {
            "CertificateOrDiploma": [],
            "Bachelor'sDegree": []
        },
        "Postgraduate": {
            "PostBachelor'sDiplomaOrCertificate": [],
            "Master'sDegree": [],
            "Doctor'sDegrees": [],
            "ResearchScholarship": [],
            "EducationSpecialistDegree": []
        }
    }

    degrees = get_degrees(html_content, topic_1)
    if degrees == 'N/A':
        return data

    for degree in degrees:
        key = degree['course']
        value = degree['subjects']

        if 'certificate' in key.lower() or 'diploma' in key.lower():
            if 'post-bachelor' in key.lower() or 'graduate' in key.lower():
                data['Postgraduate']['PostBachelor\'sDiplomaOrCertificate'] = value
            else:
                data['Undergraduate']['CertificateOrDiploma'] = value

        elif 'bachelor' in key.lower():
            data['Undergraduate']["Bachelor'sDegree"] = value

        elif 'post-bachelor' in key.lower():
            data['Postgraduate']['PostBachelor\'sDiplomaOrCertificate'] = value

        elif 'master' in key.lower():
            data['Postgraduate']["Master'sDegree"] = value

        elif 'doctor' in key.lower():
            if "research" in key.lower() or "scholarship" in key.lower():
                data['Postgraduate']["ResearchScholarship"] = value
            else: # "practice" in key.lower() or "profession" in key.lower():
                data['Postgraduate']["Doctor'sDegrees"] = value

        elif 'education' in key.lower():
            data['Postgraduate']["EducationSpecialistDegree"] = value


    return data

def to_camel_case(text):
    # Split the text by spaces
    words = text.split()

    # Capitalize the first letter of each word and join them
    camel_case_text = ''.join(word.capitalize() for word in words)

    return camel_case_text

def get_degrees(html_content, topic_1):
    section = helper.get_html_content_by_id(html_content, 'section', 'contenu')
    if not section:
        return 'N/A'

    h3_elements = section.find_all('h3')
    degrees = []

    for h3 in h3_elements:
        if h3.text.strip() == topic_1:
            divs = h3.find_all_next('div', class_='dl')
            if divs:
                for div in divs:
                    if div.find('div', class_='dd'):
                        paragraphs = div.find('div', class_='dd').find_all('p', class_='principal')
                        for paragraph in paragraphs:
                            course = None
                            subjects = None

                            try:
                                course = paragraph.text.split(':')[-1].strip()
                            except:
                                pass

                            try:
                                next_paragraph = paragraph.find_next_sibling('p')
                                assert next_paragraph
                                assert next_paragraph.class_ != 'principal'
                                subjects = next_paragraph.find('span', class_='contenu').text
                            except:
                                pass

                            degrees.append({
                                "course": course.split(':')[-1].strip() if course else 'N/A',
                                "subjects": list(map(lambda x: x.strip(), subjects.split(',')))
                                                                            if subjects else 'N/A'
                            })
                    if div.find_next_sibling('h3'):
                        break

    return degrees
