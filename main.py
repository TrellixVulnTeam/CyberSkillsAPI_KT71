#!/usr/bin/python3

# Used for dynamically scraping pages that aren't static
from selenium import webdriver

# Used for running the browser headlessly
from selenium.webdriver.firefox.options import Options

from pathlib import Path

mainEventPage = "https://community.cyberskills.dk/cyberskills-events/"

def scrapeEventPage(url, headless=True):

    # Setting the options for running the browser driver headlessly so it doesn't pop up when running the script
    driverOptions = Options()
    driverOptions.headless = headless

    # Setup the webdriver with options
    driver = webdriver.Firefox(options=driverOptions, executable_path=Path("./geckodriver").resolve())

    driver.get(mainEventPage)

    pageSource = driver.page_source

    driver.quit()

    return pageSource

