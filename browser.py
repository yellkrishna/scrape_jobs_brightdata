#!/usr/bin/env python3
import time
import logging
from selenium.webdriver import Remote, ChromeOptions as Options
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection as Connection
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import retry_with_backoff

logger = logging.getLogger(__name__)

@retry_with_backoff()
def connect_to_chrome_server(server_addr):
    """
    Establish a connection to the remote Chrome server and return a WebDriver instance.
    """
    print('Connecting to Browser...')
    connection = Connection(server_addr, 'goog', 'chrome')
    driver = Remote(connection, options=Options())
    print('Connected!')
    return driver

def wait_for_page_load(driver, timeout=20):
    """
    Wait until the page's readyState is complete and the <body> element is present.
    """
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    time.sleep(1)

@retry_with_backoff()
def load_page(driver, url):
    """
    Load a page using driver.get and wait for it to load completely.
    """
    print(f'Navigating to {url}...')
    driver.get(url)
    wait_for_page_load(driver, timeout=20)
