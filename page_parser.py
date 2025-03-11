#!/usr/bin/env python3
import logging
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)

def check_for_apply_button_and_extract_html(driver):
    """
    If a button or link with 'apply' is found, returns the full HTML of the page.
    """
    logger.debug("Searching for 'apply' buttons or links")
    apply_buttons = driver.find_elements(
        By.XPATH, 
        "//*[self::button or self::a][contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply')]"
    )
    if apply_buttons:
        logger.info(f"Found {len(apply_buttons)} button(s) or link(s) with 'apply' text. Extracting page HTML...")
        return driver.page_source
    logger.info("No 'apply' buttons or links found on the page")
    return None

def html_to_text(html: str) -> str:
    """
    Convert HTML content into clean plain text.
    """
    logger.debug("Converting HTML to text")
    soup = BeautifulSoup(html, "lxml")
    
    # Remove script and style elements
    script_style_count = len(soup(["script", "style"]))
    for element in soup(["script", "style"]):
        element.decompose()
    logger.debug(f"Removed {script_style_count} script and style elements")
    
    # Extract text
    text = soup.get_text(separator="\n", strip=True)
    lines = [line for line in text.splitlines() if line.strip()]
    logger.debug(f"Extracted {len(lines)} non-empty lines of text")
    return "\n".join(lines)
