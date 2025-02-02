from . import helper


def get_metadata(html_content, last_updated):
    try:
        data_source = helper.get_html_elements(html_content, 'span', 'Span-sc-19wk4id-0 Info__Copyright-sc-1vdhah7-9 lmLXYM jAudCl')[0]
        data_source = data_source.text
        data_source = data_source.split('©')[-1]
    except:
        data_source = 'N/A'

    return {
        "last_updated": last_updated,
        "data_source": data_source,
        "source_url": '',
        "scraping_timestamp": helper.get_current_time_stamp(),
    }

