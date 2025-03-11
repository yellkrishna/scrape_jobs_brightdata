# link_classification.py
import logging
from config import retry_with_backoff
from openai_interaction import call_openai_api
from selenium.common.exceptions import StaleElementReferenceException
import json

logger = logging.getLogger(__name__)

LINK_CLASSIFICATION_TEMPLATE = """
You are a helpful AI assistant. Determine if the following link likely leads to a job posting.
Respond ONLY with 'YES' if it is likely a job, or '' if not.

Here is the link data:
- URL: "{link_url}"
- Text: "{link_text}"
- Element Type: "{element_type}"
- Other Info: "{other_info}"
""".strip()

@retry_with_backoff(max_tries=2, backoff_factor=1)
def is_job_posting_link(link_info: dict) -> bool:
    """
    Uses OpenAI's API to determine if a given link likely leads to a job posting
    by examining its URL, text, element type, and any extra metadata.
    
    :param link_info: dict with keys like 'url', 'text', 'element_type', and 'other_info'.
    :return: True if the model responds "YES", False otherwise.
    """
    try:
        link_text = link_info.get('text', '').strip()
        link_url = link_info.get('url', '')
        element_type = link_info.get('element_type', '')
        other_info = link_info.get('other_info', {})  # Could be a dict

        # If there's neither text nor URL, skip
        if not link_text and not link_url:
            return False

        logger.debug(f"Evaluating link => url='{link_url}', text='{link_text}', "
                     f"type='{element_type}', other_info={other_info}")

        # Prepare prompt for OpenAI
        prompt = LINK_CLASSIFICATION_TEMPLATE.format(
            link_url=link_url,
            link_text=link_text,
            element_type=element_type,
            other_info=other_info
        )
        response = call_openai_api(prompt_text=prompt, model_name="gpt-4", temperature=0)
        logger.debug(f"OpenAI response => {response}")

        # If OpenAI responds exactly "YES" (case-insensitive), we treat it as True
        return response.strip().upper() == "YES"

    except StaleElementReferenceException:
        logger.warning("Stale element reference when evaluating link")
        return False
    except Exception as e:
        logger.error(f"Error evaluating link: {str(e)}")
        return False


LINK_ORDERING_TEMPLATE = """
You are a helpful AI assistant. Evaluate the following list of links extracted from a webpage. For each link, consider its URL, text, element type, and any other info. Assign a score between 0 and 100 indicating how likely the link is to lead to a job posting webpage (where 100 means very likely and 0 means not likely). Return your answer as a JSON array of numbers, where the first number corresponds to the first link, the second number to the second link, and so on. Do not include any additional text in your response.

Links:
{links_list}
""".strip()

def format_link_info(link: dict, index: int) -> str:
    link_text = link.get('text', '').strip()
    link_url = link.get('url', '')
    element_type = link.get('element_type', '')
    other_info = link.get('other_info', {})
    return (
        f"Link {index + 1}:\n"
        f"- URL: \"{link_url}\"\n"
        f"- Text: \"{link_text}\"\n"
        f"- Element Type: \"{element_type}\"\n"
        f"- Other Info: \"{other_info}\"\n"
    )

@retry_with_backoff(max_tries=2, backoff_factor=1)
def order_links_by_job_likelihood(links: list) -> list:
    """
    Uses OpenAI's API to assign a score to each link based on how likely it is to lead to a job posting webpage.
    Returns the list of links sorted from most likely (highest score) to least likely (lowest score).
    
    :param links: List of dictionaries, each containing keys like 'url', 'text', 'element_type', and 'other_info'.
    :return: Sorted list of link dictionaries, each with an added 'score' key.
    """
    try:
        if not links:
            return []
        
        # Build a string containing the information for all links
        links_list_str = "\n".join([format_link_info(link, i) for i, link in enumerate(links)])
        
        # Prepare the prompt for the LLM
        prompt = LINK_ORDERING_TEMPLATE.format(links_list=links_list_str)
        logger.debug(f"Ordering links with prompt: {prompt}")
        
        # Call the OpenAI API
        response = call_openai_api(prompt_text=prompt, model_name="gpt-4", temperature=0)
        logger.debug(f"OpenAI ordering response => {response}")
        
        # Parse the JSON array of scores from the response
        scores = json.loads(response.strip())
        
        # Ensure the response is a list with the correct number of scores
        if not isinstance(scores, list) or len(scores) != len(links):
            logger.error("Invalid response format from OpenAI API for link ordering")
            return links  # Fallback: return unsorted links
        
        # Attach the score to each link
        for link, score in zip(links, scores):
            link['score'] = score
        
        # Sort the links by score in descending order (most likely first)
        sorted_links = sorted(links, key=lambda x: x.get('score', 0), reverse=True)
        return sorted_links

    except StaleElementReferenceException:
        logger.warning("Stale element reference encountered during link ordering")
        return links
    except Exception as e:
        logger.error(f"Error ordering links: {str(e)}")
        return links
