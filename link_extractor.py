#!/usr/bin/env python3
import logging
from urllib.parse import urlparse, urlunparse, urljoin
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)

def collect_link_data_from_element(element, element_type, url_attribute, text_attribute=None):
    """
    Extracts link data from a given element.
    """
    record = {
        'element_type': element_type,
        'url': element.get_attribute(url_attribute) or '',
        'text': '',
        'other_info': {}
    }
    if text_attribute == 'text':
        record['text'] = element.text.strip()
    elif text_attribute:
        record['text'] = element.get_attribute(text_attribute) or ''
    
    # Capture additional attribute (e.g. "title")
    title = element.get_attribute("title")
    if title:
        record['other_info']['title'] = title
    return record

def collect_all_links(driver):
    """
    Collect link data from multiple tag types in the page and normalize URLs.
    """
    logger.debug(f"Collecting all links from page: {driver.current_url}")
    link_data = []
    base_url = driver.current_url  # Get current URL for joining relative URLs

    # 1. <a> tags
    anchors = driver.find_elements(By.TAG_NAME, "a")
    logger.debug(f"Found {len(anchors)} anchor tags")
    anchor_count = 0
    for anchor in anchors:
        data = collect_link_data_from_element(anchor, 'a', 'href', 'text')
        if data['url']:
            data['url'] = urljoin(base_url, data['url'])
            link_data.append(data)
            anchor_count += 1
    
    # 2. <iframe> tags
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    logger.debug(f"Found {len(iframes)} iframe tags")
    iframe_count = 0
    for iframe in iframes:
        data = collect_link_data_from_element(iframe, 'iframe', 'src')
        if data['url']:
            data['url'] = urljoin(base_url, data['url'])
            link_data.append(data)
            iframe_count += 1
    
    # 3. <script> tags
    scripts = driver.find_elements(By.TAG_NAME, "script")
    logger.debug(f"Found {len(scripts)} script tags")
    script_count = 0
    for script in scripts:
        data = collect_link_data_from_element(script, 'script', 'src')
        if data['url']:
            data['url'] = urljoin(base_url, data['url'])
            link_data.append(data)
            script_count += 1
    
    # 4. <link> tags
    link_tags = driver.find_elements(By.TAG_NAME, "link")
    logger.debug(f"Found {len(link_tags)} link tags")
    link_tag_count = 0
    for link in link_tags:
        data = collect_link_data_from_element(link, 'link', 'href')
        if data['url']:
            data['url'] = urljoin(base_url, data['url'])
            link_data.append(data)
            link_tag_count += 1
    
    # 5. <object> tags
    objects = driver.find_elements(By.TAG_NAME, "object")
    logger.debug(f"Found {len(objects)} object tags")
    object_count = 0
    for obj in objects:
        data = collect_link_data_from_element(obj, 'object', 'data')
        if data['url']:
            data['url'] = urljoin(base_url, data['url'])
            link_data.append(data)
            object_count += 1
    
    # 6. <embed> tags
    embeds = driver.find_elements(By.TAG_NAME, "embed")
    logger.debug(f"Found {len(embeds)} embed tags")
    embed_count = 0
    for embed in embeds:
        data = collect_link_data_from_element(embed, 'embed', 'src')
        if data['url']:
            data['url'] = urljoin(base_url, data['url'])
            link_data.append(data)
            embed_count += 1
    
    logger.info(f"Collected {len(link_data)} total links: {anchor_count} anchors, {iframe_count} iframes, "
                f"{script_count} scripts, {link_tag_count} link tags, {object_count} objects, {embed_count} embeds")
    return link_data

def collect_header_footer_nav_links(driver):
    """
    Collect links from header, footer, or nav elements and normalize them.
    """
    logger.debug("Collecting links from header, footer, and nav elements")
    link_data = []
    base_url = driver.current_url  # Base URL for normalization
    selectors = {
        'a':        ('href', 'text'),
        'iframe':   ('src', None),
        'script':   ('src', None),
        'link':     ('href', None),
        'object':   ('data', None),
        'embed':    ('src', None),
    }
    
    for tag_name, (url_attr, text_attr) in selectors.items():
        elements = driver.find_elements(By.CSS_SELECTOR, f"header {tag_name}, footer {tag_name}, nav {tag_name}")
        logger.debug(f"Found {len(elements)} {tag_name} elements in header/footer/nav")
        for element in elements:
            data = collect_link_data_from_element(element, tag_name, url_attr, text_attr)
            if data['url']:
                data['url'] = urljoin(base_url, data['url'])
                link_data.append(data)
    
    logger.info(f"Collected {len(link_data)} links from header, footer, and nav elements")
    return link_data

def remove_fragment(href: str) -> str:
    """
    Removes the fragment part (#something) from the URL to prevent duplicates.
    """
    try:
        parsed = urlparse(href)
        # Clear out the fragment
        sanitized = parsed._replace(fragment="")
        return urlunparse(sanitized)
    except Exception as e:
        logger.warning(f"Error removing fragment from URL {href}: {str(e)}")
        return href
