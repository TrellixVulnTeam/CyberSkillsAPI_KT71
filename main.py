#!/usr/bin/python3

# For parsing html
from bs4 import BeautifulSoup as bs

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

def extractEventDetails(pageSoup):

    events = []

    for eventBox in pageSoup.select("div.mec-topsec"):
        currentEvent = {}
        currentEvent["imageURL"] = eventBox.select("img.wp-post-image")[0].get("src")

        eventTitle = eventBox.select("h3.mec-event-title")[0].select("a")[0]
        currentEvent["eventURL"] = eventTitle.get("href")
        currentEvent["title"] = eventTitle.text.strip('\n')

        currentEvent["description"] = eventBox.select("div.mec-event-description")[0].text.strip('\n')

        eventMetaData = eventBox.select("div.mec-event-meta")[0]
        currentEvent["date"] = eventMetaData.select("div.mec-date-details")[0].text.strip('\n')
        currentEvent["time"] = eventMetaData.select("div.mec-time-details")[0].text.strip('\n')
        currentEvent["location"] = eventMetaData.select("div.mec-venue-details")[0].text.strip('\n')

        events.append(currentEvent)

    return events
