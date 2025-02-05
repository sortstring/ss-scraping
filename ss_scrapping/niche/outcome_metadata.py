from .helper import BeautifulSoup


def get_outcome(university_home_page):
    res = {
        "median_earnings_after_6_years": 'N/A',
        "national_median_earnings": 'N/A',
        "graduation_rate": 'N/A',
        "national_graduation_rate": 'N/A',
        "employed_after_2_years": 'N/A',
        "national_employment_rate": 'N/A'
    }

    soup = BeautifulSoup(university_home_page, 'html.parser')

    # Extract median earnings after 6 years
    median_earnings_element = soup.select_one('.scalar__label:contains("Median Earnings 6 Years After Graduation") + .scalar__value span')
    if median_earnings_element:
        res["median_earnings_after_6_years"] = int(median_earnings_element.text.strip('$').replace(',', ''))

    # Extract national median earnings
    national_median_earnings_element = soup.select_one('.scalar__label:contains("Median Earnings 6 Years After Graduation") + .scalar__value .scalar__national__value')
    if national_median_earnings_element:
        res["national_median_earnings"] = int(national_median_earnings_element.text.split('$')[-1].replace(',', ''))

    # Extract graduation rate
    graduation_rate_element = soup.select_one('.scalar__label:contains("Graduation Rate") + .scalar__value span')
    if graduation_rate_element:
        res["graduation_rate"] = int(graduation_rate_element.text.strip('%')) / 100

    # Extract national graduation rate
    national_graduation_rate_element = soup.select_one('.scalar__label:contains("Graduation Rate") + .scalar__value .scalar__national__value')
    if national_graduation_rate_element:
        res["national_graduation_rate"] = int(national_graduation_rate_element.text.strip('%').replace("National", "")) / 100

    # Extract employed after 2 years
    employed_after_2_years_element = soup.select_one('.scalar__label:contains("Employed 2 Years After Graduation") + .scalar__value span')
    if employed_after_2_years_element:
        res["employed_after_2_years"] = int(employed_after_2_years_element.text.strip('%')) / 100

    # Extract national employment rate
    national_employment_rate_element = soup.select_one('.scalar__label:contains("Employed 2 Years After Graduation") + .scalar__value .scalar__national__value')
    if national_employment_rate_element:
        res["national_employment_rate"] = int(national_employment_rate_element.text.strip('%').replace("National", "")) / 100

    return res