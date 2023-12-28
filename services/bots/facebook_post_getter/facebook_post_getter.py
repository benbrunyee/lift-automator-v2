# A script for running the bot that will login to Facebook, go to a lifts page
# scrape the posts and then post them to a Pub/Sub topic for processing.

import argparse
import logging
import os
import re
import sys
import time
from typing import List

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from google.auth.transport import requests
from lib.FbHelpers import FbHelpers
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

parser = argparse.ArgumentParser()
parser.add_argument(
    "--debug",
    help="Enable debug logging.",
    action="store_true",
)

args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(re.sub(r"\.py$", "", sys.argv[0]) + ".log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

load_dotenv()

PAGE_TO_SCRAPE = os.getenv("PAGE_TO_SCRAPE")
POSTS_TO_SCRAPE = int(os.getenv("POSTS_TO_SCRAPE"))
RUNNING_IN_CONTAINER = os.getenv("RUNNING_IN_CONTAINER") == "true"
FACEBOOK_EMAIL = os.getenv("FACEBOOK_EMAIL")
FACEBOOK_PASSWORD = os.getenv("FACEBOOK_PASSWORD")
DATA_ENDPOINT = os.getenv("DATA_ENDPOINT")

KEY_PATH = "../service-account-key.json"

if not os.path.exists(KEY_PATH):
    logger.error("No service account key found. Exiting.")
    exit(1)

# Set the service account key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

FERNET = None
DRIVER = None
FB_HELPER = FbHelpers()

LOGGED_POSTS = {}

XPATHS = {
    # Login xpaths
    "decline_cookies": "//button[@data-testid='cookie-policy-manage-dialog-decline-button']",
    "email_login": "//input[@name='email']",
    "password_login": "//input[@name='pass']",
    "code_prompt": "//*[contains(text(), 'enter your login code')]",
    # Main page
    "main_feed": "//*[@role='main']",
    # Page xpaths
    "page_feed": "//div[@role='feed']",
    "child_post_page_inactive_link": "//div[@role='feed']//a[@href='#']",
    "child_post_page_active_link": "//div[@role='feed']//a[contains(@href, 'groups') and contains(@href, 'posts')]",
    "child_post_page_user": "//a[contains(@href, 'groups') and contains(@href, 'user')]/strong/span",
    "child_post_text": "//div[@dir='auto']//div[text()]",
    # Post page
    "post_page_post": "//div[@aria-posinset='1']",
    "post_time_inactive_parent": "//div[@aria-posinset='1']//a[@href='#']",
    "post_time_active_parent": "//div[@aria-posinset='1']//a[contains(@href, 'groups') and contains(@href, 'posts')]//span[contains(@style, 'flex')]",
}


def main():
    """
    Main function for the bot.
    """
    logger.info("Starting bot.")

    global DRIVER
    DRIVER = FB_HELPER.load_chromedriver()

    decrypted_facebook_email = decrypt_string(FACEBOOK_EMAIL)
    decrypted_facebook_password = decrypt_string(FACEBOOK_PASSWORD)
    FB_HELPER.login_to_facebook(decrypted_facebook_email, decrypted_facebook_password)

    while True:
        try:
            scrape_posts(PAGE_TO_SCRAPE)
            logger.debug("Waiting for 10 seconds.")
            time.sleep(10)
        except Exception as e:
            logger.exception(e)
            logger.error("An error occurred while scraping posts.")
        finally:
            logger.info("Waiting for 10 minutes.")
            time.sleep(600)


def decrypt_string(string: str) -> str:
    """
    Decrypt a string.
    """

    if not FERNET:
        logger.info("Loading Fernet key.")

        if not os.path.exists("./key.txt"):
            raise Exception("No Fernet key found.")

        with open("./key.txt", "rb") as f:
            key = f.read()
            FERNET = Fernet(key)

    return FERNET.decrypt(string.encode()).decode()


def load_facebook_page(page: str):
    """
    Load a page.
    """
    logger.info(f"Loading page: {page}")
    DRIVER.get(page)
    pass


def does_time_string_conform_to_format(time_string: str):
    """
    Determine whether a time string conforms to the format of a Facebook post time string
    """

    if (
        time_string == "a day ago"
        or re.match(r"\d{1,2} days ago", time_string)
        or time_string == "about an hour ago"
        or re.match(r"\d{1,2}h", time_string)
        or re.match(r"\d{1,2} hours ago", time_string)
        or re.match(r"\d{1,2}m", time_string)
        or re.match(r"\d{1,2} minutes ago", time_string)
        or re.match(r"\d{1,2}s", time_string)
        or re.match(r"\d{1,2} seconds ago", time_string)
        or time_string == "now"
    ):
        logger.info(f"Time string conforms to format: {time_string}")
        return True

    logger.warn(f"Time string does not conform to format: {time_string}")
    return False


def load_inactive_a_tag(
    inactive_element_xpath: str,
    active_element_xpath: str,
    wait_between: int = 1,
    retries: int = 10,
):
    """
    Load an inactive a tag by hovering over the element until it cannot be found.
    """

    logger.debug("Loading inactive a tag.")

    counter = 0

    while True:
        if counter > retries:
            raise Exception("Timeout waiting for inactive a tag to load.")

        try:
            FB_HELPER.hover_over(inactive_element_xpath)
            logger.debug("Inactive a tag still present.")
            time.sleep(wait_between)
            counter += 1
        except NoSuchElementException:
            logger.debug("Inactive a tag not present.")

            # Wait for the active a tag to load
            FB_HELPER.wait_for(active_element_xpath)
            logger.debug("Active a tag present.")

            break


def read_time_from_post():
    """
    Read the time from a post.
    The driver needs to be on the post's page.
    """

    # Facebook makes it difficult to get the time from a post.
    # The time is split over numerous elements and there are dummy elements to make it difficult to get the time.
    # We need to determine the elements that are the time by checking whether they have their position style set to "relative".

    logger.info("Reading time from post.")
    time_string = ""

    # Load the href by hovering over the inactive a tag
    load_inactive_a_tag(
        XPATHS["post_time_inactive_parent"], XPATHS["post_time_active_parent"]
    )

    post_time_parent = FB_HELPER.wait_for(XPATHS["post_time_parent"])
    children = post_time_parent.find_elements_by_xpath(".//*")
    for child in children:
        if child.get_attribute("style") == "position: relative;":
            character = child.text
            logger.debug(f"Found time character: {character}")
            time_string += character

    if not does_time_string_conform_to_format(time_string):
        raise Exception("Time string does not conform to format.")

    return time_string


def wait_for_page_feed_to_load(wait_between: int = 1, retries: int = 10):
    """
    Wait for the page feed to load.
    """
    logger.info("Waiting for page feed to load.")
    page_feed = FB_HELPER.wait_for(XPATHS["page_feed"])

    # The page feed loads with children but there is no data in the children.
    # We want to continue waiting until the children have data.
    # This is done by checking whether there are at least 5 children in the page feed.

    counter = 0

    while True:
        if counter > retries:
            raise Exception("Timeout waiting for page feed to load.")

        children = page_feed.find_elements(By.XPATH, ".//*")
        if len(children) > 5:
            logger.info("Page feed loaded.")
            break

        logger.debug("Page feed not loaded.")
        time.sleep(wait_between)
        counter += 1


def load_post_page(post: WebElement):
    """
    Load a post page.
    """

    logger.info("Loading post page.")

    # Load the href by hovering over the inactive a tag
    load_inactive_a_tag(
        XPATHS["child_post_page_inactive_link"],
        XPATHS["child_post_page_active_link"],
    )
    FB_HELPER.wait_for(XPATHS["child_post_page_active_link"])

    # Get the post link
    post_link = post.find_element_by_xpath(XPATHS["child_post_page_active_link"])
    post_link_href = post_link.get_attribute("href")

    # Open the post page in a new tab
    current_window_handle = DRIVER.current_window_handle
    DRIVER.execute_script(f"window.open('{post_link_href}', '_blank');")

    # Switch to the new tab
    DRIVER.switch_to.window(DRIVER.window_handles[1])

    return current_window_handle


def clean_page_feed(children: List[WebElement]) -> List[WebElement]:
    """
    Clean the page feed of children that are not posts.
    """

    # Remove the dummy elements
    identified_classes = {}

    for child in children:
        class_name = child.get_attribute("class")
        if class_name in identified_classes:
            identified_classes[class_name] += 1
        else:
            identified_classes[class_name] = 1

    logger.debug(f"Identified post classes: {identified_classes}")

    # Remove the dummy elements from the children, the elements with the lowest class count are the dummy elements.
    dummy_element_class = min(identified_classes, key=identified_classes.get)

    logger.debug(f"Removing dummy elements with class: {dummy_element_class}")
    new_children = []

    for child in children:
        if child.get_attribute("class") != dummy_element_class:
            new_children.append(child)

    return new_children


def calculate_post_time(post_time: str):
    """
    Calculate the time of a post.
    """

    logger.info(f"Calculating post time: {post_time}")

    if post_time == "a day ago":
        return time.time() - 86400
    elif re.match(r"\d{1,2} days ago", post_time):
        days = int(re.match(r"\d{1,2}", post_time).group(0))
        return time.time() - (days * 86400)
    elif post_time == "about an hour ago":
        return time.time() - 3600
    elif re.match(r"\d{1,2}h", post_time):
        hours = int(re.match(r"\d{1,2}", post_time).group(0))
        return time.time() - (hours * 3600)
    elif re.match(r"\d{1,2} hours ago", post_time):
        hours = int(re.match(r"\d{1,2}", post_time).group(0))
        return time.time() - (hours * 3600)
    elif re.match(r"\d{1,2}m", post_time):
        minutes = int(re.match(r"\d{1,2}", post_time).group(0))
        return time.time() - (minutes * 60)
    elif re.match(r"\d{1,2} minutes ago", post_time):
        minutes = int(re.match(r"\d{1,2}", post_time).group(0))
        return time.time() - (minutes * 60)
    elif re.match(r"\d{1,2}s", post_time):
        seconds = int(re.match(r"\d{1,2}", post_time).group(0))
        return time.time() - seconds
    elif re.match(r"\d{1,2} seconds ago", post_time):
        seconds = int(re.match(r"\d{1,2}", post_time).group(0))
        return time.time() - seconds
    elif post_time == "now":
        return time.time()

    raise Exception("Could not calculate post time.")


def scrape_posts(page: str):
    """
    Scrape posts from a page.
    """

    logger.info("Scraping posts.")

    # Load the page with the sorting setting set to "Recent Activity"
    page_to_load = page + "?sorting_setting=RECENT_ACTIVITY"
    load_facebook_page(page_to_load)

    # Wait for page feed to load
    wait_for_page_feed_to_load()
    page_feed = FB_HELPER.wait_for(XPATHS["page_feed"])

    # Loop through the most recent posts
    children = clean_page_feed(page_feed.find_elements(By.XPATH, ".//*"))
    for child in children:
        # Check if we have already logged this post
        post_username = child.find_elements(
            By.XPATH, XPATHS["child_post_page_user"]
        ).text
        post_text = child.find_elements(By.XPATH, XPATHS["child_post_text"]).text

        post_id = f"{post_username} {post_text}"
        if post_id in LOGGED_POSTS:
            logger.info(f"Skipping post: {post_id}")
            continue

        current_window_handle = load_post_page(child)

        post_time = read_time_from_post()
        post_actual_time = calculate_post_time(post_time)

        # Send the post to the HTTPS endpoint
        try:
            post_to_endpoint(
                {
                    "user": post_username,
                    "content": post_text,
                    "posted_at": post_actual_time,
                }
            )
        except Exception as e:
            logger.exception(e)
            logger.error("An error occurred while posting to the endpoint.")
            logger.warn("Skipping post.")
            continue

        # Add the post to the logged posts
        logger.debug("Saving post to in-memory set.")
        LOGGED_POSTS[post_id] = post_actual_time

        # Close the post page
        logger.debug("Closing post page.")
        DRIVER.close()

        # Switch back to the main page
        logger.debug("Switching back to main page.")
        DRIVER.switch_to.window(current_window_handle)


def post_to_endpoint(endpoint: str, data: object):
    """
    Post data to the HTTPS endpoint.
    """

    logger.info("Posting data to endpoint.")
    credentials = requests.service_account.Credentials.from_service_account_file(
        "./service-account-key.json"
    )
    requests.requests.post(endpoint, json=data)
    response = requests.requests.post(
        endpoint, json=data, headers={"Authorization": f"Bearer {credentials.token}"}
    )
    logger.debug(f"Response from endpoint: {response}")
    logger.info(f"Response content: {response.content}")


if __name__ == "__main__":
    main()
