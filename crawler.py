#!/usr/bin/env python3
import time
import logging

from browser import connect_to_chrome_server, load_page
from page_parser import check_for_apply_button_and_extract_html, html_to_text
from link_extractor import collect_all_links, collect_header_footer_nav_links, remove_fragment
from link_classification import is_job_posting_link, order_links_by_job_likelihood
from job_extraction import extract_job_postings

logger = logging.getLogger(__name__)

def scrape_page(driver, url):
    """
    Visit a page, extract job postings, and gather job-related links.
    """
    logger.info(f'Navigating to {url}...')
    load_page(driver, url)
    time.sleep(3)  # Wait for page to load
    # Check for an "apply" button and extract HTML if found.
    extracted_html = check_for_apply_button_and_extract_html(driver)
    job_postings = []
    if extracted_html:
        logger.debug("HTML extracted successfully, converting to text")
        extracted_text = html_to_text(extracted_html)
        job_postings = extract_job_postings([extracted_text])
        logger.info(f"Extracted {len(job_postings)} job posting(s)")
        for i, posting in enumerate(job_postings, start=1):
            logger.debug(f"Posting #{i}: {posting}")
    else:
        logger.info("No HTML extracted, so no job postings extracted")

    # 1) Gather all link data and remove URL fragments
    all_link_data = collect_all_links(driver)
    for link_dict in all_link_data:
        link_dict['url'] = remove_fragment(link_dict['url'])
    
    # 2) Exclude header/footer/nav links
    excluded_link_data = collect_header_footer_nav_links(driver)
    for link_dict in excluded_link_data:
        link_dict['url'] = remove_fragment(link_dict['url'])
    excluded_urls = {rec['url'] for rec in excluded_link_data}
    filtered_link_data = [rec for rec in all_link_data if rec['url'] not in excluded_urls]

    # 3) Identify and order job posting links
    job_posting_links = [link_info for link_info in filtered_link_data if is_job_posting_link(link_info)]
    logger.debug(f"Identified {len(job_posting_links)} potential job posting links")
    ordered_links = order_links_by_job_likelihood(job_posting_links)
    logger.info(f"Ordered {len(ordered_links)} job posting links by likelihood")
    for i, link_info in enumerate(ordered_links, start=1):
        logger.debug(f"Link #{i}: {link_info}")
    
    return ordered_links, job_postings

def dfs_crawl(server_addr, url, max_depth, max_breadth, visited=None):
    """
    Recursively crawl pages in a depth-first manner.
    """
    if visited is None:
        visited = set()
    if url in visited or max_depth < 0:
        logger.debug(f"Skipping {url}: already visited or max depth reached")
        return [], []
    visited.add(url)
    
    logger.info(f"Crawling: {url} (depth remaining: {max_depth})")
    
    try:
        logger.debug(f"Connecting to Chrome server at {server_addr}")
        driver = connect_to_chrome_server(server_addr)
        job_links, job_postings = scrape_page(driver, url)
        logger.info(f"Found {len(job_links)} job links and {len(job_postings)} job postings on {url}")
        driver.quit()
        results = job_links[:] 
        postings = job_postings[:] 
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}", exc_info=True)
        return [], []
    
    if max_depth == 0:
        return results, postings

    # Recursively crawl discovered job posting links
    for i, link_info in enumerate(job_links[:max_breadth]):
        link_url = link_info['url']
        if link_url not in visited:
            logger.debug(f"Recursively crawling link {i+1}/{min(len(job_links), max_breadth)}: {link_url}")
            rec_links, rec_postings = dfs_crawl(server_addr, link_url, max_depth - 1, max_breadth, visited)
            results.extend(rec_links)
            postings.extend(rec_postings)
    
    return results, postings
