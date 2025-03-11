#!/usr/bin/env python3
import pandas as pd
import logging

from crawler import dfs_crawl
from config import BRIGHT_DATA_CONFIG, setup_logging

if __name__ == '__main__':
    # Initialize logging
    logger = setup_logging(console_level=logging.INFO, file_level=logging.DEBUG)
    logger.info("Starting web crawler")
    
    # Read input data from a CSV file.
    # If using Excel, replace pd.read_csv with pd.read_excel and adjust the file name.
    input_file = 'company_data.xlsx'
    companies_df = pd.read_excel(input_file)
    
    # Ensure your CSV has the columns 'company_name' and 'target_url'
    logger.info(f"Loaded {len(companies_df)} company records from {input_file}")
    
    # Initialize an empty DataFrame to collect all job postings
    all_jobs_df = pd.DataFrame()
    
    # Get the server address from your config
    server_addr = BRIGHT_DATA_CONFIG["server_addr"]
    
    # Loop over each company record
    for index, row in companies_df.iterrows():
        company_name = row['company_name']
        target_url = row['target_url']
        logger.info(f"Processing company: {company_name} with URL: {target_url}")
        
        # Perform the crawl for this company's URL
        all_job_links, all_job_postings = dfs_crawl(server_addr, target_url, max_depth=3, max_breadth=3)
        
        # Create a DataFrame from the job postings and drop duplicates
        df = pd.DataFrame(all_job_postings).drop_duplicates()
        
        # Add the company name to every row
        df['company_name'] = company_name
        
        # Append the results to the cumulative DataFrame
        all_jobs_df = pd.concat([all_jobs_df, df], ignore_index=True)
        
        logger.info(f"Finished processing {company_name}. Found {len(df)} unique job postings.")
    
    logger.info(f"Crawl complete. Found a total of {len(all_jobs_df)} unique job postings.")
    
    # Optionally, print a summary and save the results to a CSV file.
    print(all_jobs_df.head())
    all_jobs_df.to_csv("all_job_postings.csv", index=False)
    logger.info("Saved all job postings to all_job_postings.csv")
