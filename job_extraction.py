# job_extraction.py

import logging
import re
import json
import traceback
from typing import List, Dict

from config import retry_with_backoff
from openai_interaction import call_openai_api

logger = logging.getLogger(__name__)

# Example template for job extraction
JOB_POSTING_EXTRACTION_TEMPLATE = r"""
You are an expert job posting extractor.

Extract the job posting details from the text below. Only extract the following details:
- Job Title (key: "title")
- Job Description (key: "description")
- Salary Range (key: "salary_range")
- Responsibilities (key: "responsibilities")
- Location (key: "location")
- Qualification (key: "qualification")

For each job posting, if any of the above details are not present, include the key in the JSON with an empty string as its value.

Strictly ignore any partial job details that exist only in a hyperlink or as link to another page.
Return only job postings that are fully described in the visible text.

Return the job postings as a valid JSON list, where each posting is a JSON object with the keys specified above.

If there is only one job posting, return a list with exactly one JSON object.
If there are multiple postings, return a list containing multiple JSON objects.
If no job posting is found, return an empty list: [].

Output format: valid JSON only, without triple backticks or any extra text.

Text:
{dom_content}
""".strip()

# Regex pattern to remove anchor references from markdown text
LINK_PATTERN = r"\[.*?\]\(.*?\)"

@retry_with_backoff(max_tries=2, backoff_factor=1)
def extract_job_postings(dom_chunks: List[str]) -> List[Dict[str, str]]:
    """
    Given a list of DOM (markdown) chunks, extracts job postings using OpenAI API.
    Returns a concatenated list of job posting dictionaries.
    """
    all_postings = []
    logger.debug(f"Processing {len(dom_chunks)} DOM chunks")

    for chunk in dom_chunks:
        try:
            # Remove hyperlink references from chunk
            preprocessed_chunk = re.sub(LINK_PATTERN, "", chunk)

            prompt = JOB_POSTING_EXTRACTION_TEMPLATE.format(dom_content=preprocessed_chunk)
            response_text = call_openai_api(prompt_text=prompt, model_name="gpt-4", temperature=0)

            logger.debug("OpenAI extraction completed.")
            clean_response = response_text.strip()

            # Strip out possible extraneous prefixes or whitespace
            clean_response = re.sub(r"^(?:json)?\s*", "", clean_response, flags=re.IGNORECASE)
            clean_response = re.sub(r"\s*$", "", clean_response)

            try:
                postings = json.loads(clean_response)
                if isinstance(postings, dict):
                    postings = [postings]
                if isinstance(postings, list):
                    all_postings.extend(postings)
                    logger.info(f"Extracted {len(postings)} job postings.")
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing error: {str(e)}")
                # Optional fallback to regex or other heuristics here.
        except Exception as e:
            logger.error(f"Error processing chunk: {str(e)}")
            logger.debug(traceback.format_exc())

    return all_postings
