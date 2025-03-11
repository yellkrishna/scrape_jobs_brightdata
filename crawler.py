#!/usr/bin/env python3
import time

from browser import connect_to_chrome_server, load_page
from page_parser import check_for_apply_button_and_extract_html, html_to_text
from link_extractor import collect_all_links, collect_header_footer_nav_links, remove_fragment
from link_classification import is_job_posting_link, order_links_by_job_likelihood
from job_extraction import extract_job_postings

def scrape_page(driver, url):
    """
    Visit a page, extract job postings, and gather job-related links.
    """
    print(f'Navigating to {url}...')
    load_page(driver, url)
    time.sleep(3)  # Wait for page to load
    # Check for an "apply" button and extract HTML if found.
    extracted_html = check_for_apply_button_and_extract_html(driver)
    job_postings = []
    if extracted_html:
        extracted_text = html_to_text(extracted_html)
        job_postings = extract_job_postings([extracted_text])
        print(f"\nExtracted {len(job_postings)} job posting(s):")
        for i, posting in enumerate(job_postings, start=1):
            print(f"Posting #{i}: {posting}")
    else:
        print("No HTML extracted, so no job postings extracted.")

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
    ordered_links = order_links_by_job_likelihood(job_posting_links)
    print("\n=== Job Posting Links ===")
    for link_info in ordered_links:
        print(link_info)
    
    return ordered_links, job_postings

def dfs_crawl(server_addr, url, max_depth, max_breadth, visited=None):
    """
    Recursively crawl pages in a depth-first manner.
    """
    if visited is None:
        visited = set()
    if url in visited or max_depth < 0:
        return []
    visited.add(url)
    
    print(f"Crawling: {url} (depth remaining: {max_depth})")
    
    try:
        driver = connect_to_chrome_server(server_addr)
        job_links, job_postings = scrape_page(driver, url)
        print(f"Found {len(job_links)} job links on {url}.")
        print(job_postings)
        driver.quit()
        results = job_links[:] 
        postings = job_postings[:] 
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []
    
    if max_depth == 0:
        return results, postings

    # Recursively crawl discovered job posting links
    for link_info in job_links[:max_breadth]:
        link_url = link_info['url']
        if link_url not in visited:
            rec_links, rec_postings = dfs_crawl(server_addr, link_url, max_depth - 1, max_breadth, visited)
            results.extend(rec_links)
            postings.extend(rec_postings)
    
    return results, postings
