"""
This file contains helper functions for interacting with Facebook/Chrome.
"""

import logging
import os
import random
import time

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

XPATHS = {
    # Login xpaths
    "decline_cookies": "//button[@data-testid='cookie-policy-manage-dialog-decline-button']",
    "email_login": "//input[@name='email']",
    "password_login": "//input[@name='pass']",
    "code_prompt": "//*[contains(text(), 'enter your login code')]",
}


class FbHelpers:
    driver = None

    def __init__(self, driver=None) -> None:
        if driver is not None:
            self.driver = driver

    def set_driver(self, driver):
        self.driver = driver

    def js_click(self, xpath: str, with_wait: bool = True):
        """
        Click an element using javascript.
        """

        if with_wait:
            self.wait_for(xpath)

        self.driver.execute_script(
            "arguments[0].click();", self.driver.find_element(By.XPATH, xpath)
        )

    def hover_over(self, xpath: str, with_wait: bool = True):
        """
        Hover over an element.
        """

        if with_wait:
            self.wait_for(xpath)

        self.driver.execute_script(
            "arguments[0].hover();", self.driver.find_element(By.XPATH, xpath)
        )

    def input_text_to_element(
        self, xpath: str, text: str, with_wait: bool = True, random_delay: bool = True
    ):
        """
        Input text to an element.
        """

        if with_wait:
            self.wait_for(xpath)

        element = self.driver.find_element(By.XPATH, xpath)

        if not random_delay:
            element.send_keys(text)
            return

        for char in text:
            element.send_keys(char)
            # Sleep for a random amount of time between 0.1 and 0.3 seconds.
            time.sleep(random.randint(1, 3) / 10)

    def wait_for(self, xpath: str, timeout: int = 10, log_error: bool = True):
        """
        Wait for an element to appear on the page.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return self.driver.find_element(By.XPATH, xpath)
        except NoSuchElementException as e:
            if log_error:
                logger.error(f"Could not find element with xpath: {xpath}")
            raise e

    def load_chromedriver(self, running_in_container: bool = False):
        # Get all chromedrivers in "./chromedrivers" and add them to the path, if it exists
        chromedrivers_path = "../chromedrivers"
        if not os.path.exists(chromedrivers_path):
            logger.info("No chromedrivers found.")
        else:
            logger.info("Loading chromedrivers.")
            for file in os.listdir(chromedrivers_path):
                if file.endswith(".exe"):
                    logger.debug(f"Adding chromedriver to path: {file}")
                    os.environ[
                        "PATH"
                    ] += f";{os.path.join(os.getcwd(), chromedrivers_path, file)}"

        # Set the driver parameters
        parameters = [
            "--start-maximized"
            "--disable-popup-blocking"
            "--disable-extensions"
            "--incognito"
            "--disable-infobars"
        ]

        container_parameters = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
        ]

        # If we are running in a container, we need to use a virtual display
        if running_in_container:
            logger.info("Running in container.")
            logger.info("Starting virtual display.")
            display = Display(visible=0, size=(800, 600))
            display.start()
            logger.info("Virtual display started.")

        options = webdriver.ChromeOptions()

        for parameter in parameters:
            logger.debug(f"Adding parameter: {parameter}")
            options.add_argument(parameter)

        if running_in_container:
            for parameter in container_parameters:
                logger.debug(f"Adding parameter: {parameter}")
                options.add_argument(parameter)

        logger.info("Loading chromedriver.")
        self.driver = webdriver.Chrome(
            options=options,
        )
        return self.driver

    def login_to_facebook(self, email: str, password: str, wait_for_2fa: bool = True):
        """
        Login to Facebook.
        """

        logger.info("Logging in to Facebook.")

        facebook_login_url = "https://www.facebook.com/login"
        logger.info(f"Loading {facebook_login_url}")
        self.driver.get(facebook_login_url)

        self.input_text_to_element(XPATHS["email_login"], email)
        self.input_text_to_element(XPATHS["password_login"], password + "\n")

        self.wait_for_authentication(wait_for_2fa)

    def wait_for_authentication(self, wait_for_2fa: bool = True):
        """
        Wait for the user to authenticate the login attempt.
        """

        logger.info("Waiting for authentication.")

        # Wait for the code prompt to appear.
        waiting_for_code_prompt = False
        try:
            self.wait_for(XPATHS["code_prompt"])
            logger.info("2FA required.")

            if not wait_for_2fa:
                raise Exception("2FA required.")

            waiting_for_code_prompt = True
        except NoSuchElementException:
            logger.info("No 2FA required.")

        message_printed = False

        if waiting_for_code_prompt:
            logger.info("Waiting for authentication.")
            # Wait for the user to authenticate the login attempt.
            while True:
                try:
                    self.wait_for(XPATHS["code_prompt"], timeout=1)
                    if not message_printed:
                        logger.info("Waiting for 2FA.")
                        message_printed = True
                except NoSuchElementException:
                    logger.info("2FA successful.")
                    break

        # Wait for the main feed to appear.
        self.wait_for(XPATHS["main_feed"])
        logger.info("Login successful.")
