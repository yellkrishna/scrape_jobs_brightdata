#!/usr/bin/env python3
import pandas as pd

from crawler import dfs_crawl
from config import BRIGHT_DATA_CONFIG

if __name__ == '__main__':
    # Set up server address and target URL.
    server_addr = BRIGHT_DATA_CONFIG["server_addr"]
    TARGET_URL = 'https://fieracapital.wd3.myworkdayjobs.com/Career'
    
    all_job_links, all_job_postings = dfs_crawl(server_addr, TARGET_URL, max_depth=3, max_breadth=3)

    df = pd.DataFrame(all_job_postings).drop_duplicates()

    print(df.head())
    print("Crawl complete.")
