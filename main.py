#!/usr/bin/env python3
import pandas as pd

from crawler import dfs_crawl

if __name__ == '__main__':
    # Set up server address and target URL.
    server_addr = 'https://brd-customer-hl_cf240944-zone-scrape_job_postings:si9klwfh7f28@brd.superproxy.io:9515'
    TARGET_URL = 'https://fieracapital.wd3.myworkdayjobs.com/Career'
    
    all_job_links, all_job_postings = dfs_crawl(server_addr, TARGET_URL, max_depth=3, max_breadth=3)

    df = pd.DataFrame(all_job_postings).drop_duplicates()

    print(df.head())
    print("Crawl complete.")
