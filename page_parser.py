#!/usr/bin/env python3
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

def check_for_apply_button_and_extract_html(driver):
    """
    If a button or link with 'apply' is found, returns the full HTML of the page.
    """
    apply_buttons = driver.find_elements(
        By.XPATH, 
        "//*[self::button or self::a][contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply')]"
    )
    if apply_buttons:
        print("Found button or link with 'apply' text. Extracting page HTML...")
        return driver.page_source
    return None

def html_to_text(html: str) -> str:
    """
    Convert HTML content into clean plain text.
    """
    soup = BeautifulSoup(html, "lxml")
    for element in soup(["script", "style"]):
        element.decompose()
    
    text = soup.get_text(separator="\n", strip=True)
    lines = [line for line in text.splitlines() if line.strip()]
    return "\n".join(lines)
