# Web Crawler for Job Postings

A robust web crawler designed to extract job postings from websites based on configurable depth and breadth parameters.

## Overview

This project implements a depth-first search (DFS) web crawler that:
1. Navigates to job posting websites
2. Identifies and extracts job posting information
3. Follows job-related links to discover more postings
4. Filters out non-job-related content

The crawler uses AI-powered classification to identify job-related links and extract structured job posting data.

## Features

- **Configurable Crawling**: Set maximum depth and breadth for the crawl
- **Intelligent Link Classification**: Uses OpenAI to identify job-related links
- **Job Data Extraction**: Extracts structured job posting data (title, description, salary, etc.)
- **Robust Error Handling**: Implements retry with exponential backoff for network operations
- **Header/Footer Filtering**: Excludes navigation links to focus on content

## Requirements

- Python 3.8+
- Chrome browser
- Bright Data or similar proxy service
- OpenAI API key

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-4o-mini  # or your preferred model
   ```

## Usage

```python
from crawler import dfs_crawl

# Set up server address and target URL
server_addr = 'your_proxy_server_address'
target_url = 'https://example.com/careers'

# Run the crawler with specified depth and breadth
all_job_links, all_job_postings = dfs_crawl(server_addr, target_url, max_depth=3, max_breadth=3)

# Process the results
import pandas as pd
df = pd.DataFrame(all_job_postings).drop_duplicates()
print(df.head())
```

## Configuration

The crawler behavior can be configured by modifying the parameters in `main.py`:

- `max_depth`: Maximum depth of the crawl (how many links deep to follow)
- `max_breadth`: Maximum breadth of the crawl (how many links to follow at each level)
- `server_addr`: Address of the proxy server
- `TARGET_URL`: Starting URL for the crawl

## Project Structure

- `main.py`: Entry point for the application
- `crawler.py`: Core crawling logic
- `browser.py`: Browser connection and page loading
- `page_parser.py`: HTML parsing and text extraction
- `link_extractor.py`: Link extraction from HTML
- `link_classification.py`: AI-powered link classification
- `job_extraction.py`: AI-powered job posting extraction
- `openai_interaction.py`: OpenAI API interaction
- `config.py`: Configuration and utility functions

## License

MIT
