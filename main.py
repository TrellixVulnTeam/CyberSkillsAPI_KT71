#!/usr/bin/python3

# For parsing html
from bs4 import BeautifulSoup as bs

# Used for dynamically scraping pages that aren't static
from selenium import webdriver

# Used for running the browser headlessly
from selenium.webdriver.firefox.options import Options

# For changing the year and month
from selenium.webdriver.support.ui import Select

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By

from pathlib import Path

import json
import time

import re

filePathPattern = re.compile('[^a-zA-Z0-9]')

mainEventPage = "https://community.cyberskills.dk/cyberskills-events/"


def writeEventsToFile(year, month, contents):
    year = filePathPattern.sub("", year)
    month = filePathPattern.sub("", month)

    fullPath = f"./events/{year};{month}.json"

    with open(Path(fullPath).resolve(), "w") as eventFile:
        json.dump(contents, eventFile)

def selectMonthAndYear(driver, month, year):

    yearSelector = Select(driver.find_element_by_id("mec_sf_year_902"))
    if year:
        yearSelector.select_by_visible_text(year)

    monthSelector = Select(wait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#mec_sf_month_902"))))
    if month:
        monthSelector.select_by_visible_text(month)

    time.sleep(3)

def loadMore(driver):
    # Will check if theres more than one title stating the month for the following content. If there is, that means that the page has already loaded the whole month, as the start of the next one is already loaded, and it can skip pressing the "Load More" button
    if not len(driver.find_elements_by_css_selector("div.mec-month-divider")) > 1:
        # Will make sure that the button is present before trying to wait for it to be click-able, as this will otherwise timeout
        if len(driver.find_elements_by_css_selector("div.mec-load-more-button")) > 0:
            # Wait for the load more button to be clickable
            loadMoreButton = wait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.mec-load-more-button")))
            # If it is present, click it
            if loadMoreButton:
                loadMoreButton.click()
                loadMore(driver)

def scrapeEventPage(url, month=None, year=None, headless=True):

    # Setting the options for running the browser driver headlessly so it doesn't pop up when running the script
    driverOptions = Options()
    driverOptions.headless = headless

    # Setup the webdriver with options
    driver = webdriver.Firefox(options=driverOptions, executable_path=Path("./geckodriver").resolve())

    driver.get(mainEventPage)

    if month and year:
        if isinstance(month, list) and isinstance(year, list):
            sourceCollection = {}
            for exactYear in year:
                for exactMonth in month:
                    print(exactYear, exactMonth)
                    selectMonthAndYear(driver, exactMonth, exactYear)
                    loadMore(driver)
                    sourceCollection[f"{exactYear};{exactMonth}"] = driver.page_source

        else:
            selectMonthAndYear(driver, month, year)
            loadMore(driver)
            sourceCollection = driver.page_source
    else:
        sourceCollection = driver.page_source

    driver.quit()

    return sourceCollection

def extractCurrentMonth(pageSoup):
    monthDividerTitles = pageSoup.select("div.mec-month-divider")
    if len(monthDividerTitles) < 2:
        return pageSoup
    else:
        secondMonthTitle = monthDividerTitles[1]
        laterEvents = secondMonthTitle.find_all_next("div")
        for event in laterEvents:
            event.decompose()

        return pageSoup

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

def listDetails():
    pageSoup = bs(scrapeEventPage(mainEventPage), "html.parser")

    detailCollection = {}

    for detailName in ["year", "month"]:
        detailCollection[detailName] = [ detail.text for detail in pageSoup.select(f"select#mec_sf_{detailName}_902")[0].select("option") if detail and detail.get("value").isnumeric() ]

    return detailCollection

def listEvents(month, year):
    pageSoup = bs(scrapeEventPage(mainEventPage, month, year, headless=True), "html.parser")

    currentMonthSoup = extractCurrentMonth(pageSoup)

    return extractEventDetails(currentMonthSoup)

def listEventsForAllTime():
    details = listDetails()

    sourceCollection = scrapeEventPage(mainEventPage, month=details["month"], year=["2021"])

    for source in sourceCollection:
        year = source.split(";")[0]
        month = source.split(";")[1]
        currentMonthSoup = extractCurrentMonth(bs(sourceCollection[source], "html.parser"))
        writeEventsToFile(year, month, extractEventDetails(currentMonthSoup))
