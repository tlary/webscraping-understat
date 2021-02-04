import pandas as pd
from selenium import webdriver
import chromedriver_binary
import re
from datetime import datetime
from itertools import chain



def get_element(className, browser):
    """
    :param className: string - name of the class which is to be retrieved
    :param browser: browser object, initialized by initialize_browser()
    :return text of element as string
    """

    regex = re.compile(r"[\n\r\t]") # compile regular expression
    element = browser.find_element_by_class_name(className) # find element
    element = element.get_attribute("innerText") # extract html
    element = regex.sub("", element) # remove unwanted parts of the string
    return element


def get_element_xpath(xpath, browser):
    """
    :param xpath: string - xpath to the element which is to be retrieved
    :param browser: browser object, initialized by initialize_browser()
    :return: text of element as string
    """

    element = browser.find_element_by_xpath(xpath).get_attribute("innerHTML")
    return element


def get_float(xpath, browser):
    """
    :param xpath: string - xpath to the element which is to be retrieved
    :param browser: browser object, initialized by initialize_browser()
    :return: element as float object
    """
    element = get_element_xpath(xpath, browser)
    regex = re.compile(r"<[^>]+>")
    element = regex.sub("", element)
    element = float(element)
    return element


def get_date(xpath, browser):
    """
    :param xpath: string - xpath to the date element
    :param browser: browser object, initialized by initialize_browser()
    :return: date as datetime object
    """
    element = get_element_xpath(xpath, browser=browser)
    element = datetime.strptime(element, "%b %d %Y")
    return element


def scrape_match_infos(browser):
    """
    :param browser: browser object, initialized by initialize_browser()
    :return: all date for a single match from its corresponding page as a dictionary
    """
    matchData = {
        "date" : get_date("/html/body/div[1]/div[3]/ul/li[3]", browser=browser),
        "homeTeam" : get_element("progress-home.progress-over", browser=browser),
        "awayTeam" : get_element("progress-away", browser=browser),
        "homeGoals" : int(get_element_xpath("/html/body/div[1]/div[3]/div[2]/div[1]/div/div[4]/div[3]/div[2]/div", browser=browser)),
        "awayGoals" : int(get_element_xpath("/html/body/div[1]/div[3]/div[2]/div[1]/div/div[4]/div[3]/div[3]/div", browser=browser)),
        "xgHome" : get_float("/html/body/div[1]/div[3]/div[2]/div[1]/div/div[4]/div[4]/div[2]/div", browser=browser),
        "xgAway" : get_float("/html/body/div[1]/div[3]/div[2]/div[1]/div/div[4]/div[4]/div[3]/div", browser=browser),
        "shotsHome" : int(get_element_xpath("/html/body/div[1]/div[3]/div[2]/div[1]/div/div[4]/div[5]/div[2]/div", browser=browser)),
        "shotsAway" : int(get_element_xpath("/html/body/div[1]/div[3]/div[2]/div[1]/div/div[4]/div[5]/div[3]/div", browser=browser)),
        "shotsOnTargetHome" : int(get_element_xpath("/html/body/div[1]/div[3]/div[2]/div[1]/div/div[4]/div[6]/div[2]/div", browser=browser)),
        "shotsOnTargetAway" : int(get_element_xpath("/html/body/div[1]/div[3]/div[2]/div[1]/div/div[4]/div[6]/div[3]/div", browser=browser)),
        "deepHome" : int(get_element_xpath("/html/body/div[1]/div[3]/div[2]/div[1]/div/div[4]/div[7]/div[2]/div", browser=browser)),
        "deepAway" : int(get_element_xpath("/html/body/div[1]/div[3]/div[2]/div[1]/div/div[4]/div[7]/div[3]/div", browser=browser)),
        "ppdaHome" : get_float("/html/body/div[1]/div[3]/div[2]/div[1]/div/div[4]/div[8]/div[2]/div", browser=browser),
        "ppdaAway" : get_float("/html/body/div[1]/div[3]/div[2]/div[1]/div/div[4]/div[8]/div[3]/div", browser=browser),
        "xptsHome" : get_float("/html/body/div[1]/div[3]/div[2]/div[1]/div/div[4]/div[9]/div[2]/div", browser=browser),
        "xptsAway" : get_float("/html/body/div[1]/div[3]/div[2]/div[1]/div/div[4]/div[9]/div[3]/div", browser=browser)
    }
    return matchData


def scrape_page(browser):
    """
    :param browser: browser object, initialized by initialize_browser()
    :return: data for all matches from a "week overview" page
    """
    # initialize empty list for match data and links
    dicts = []
    links = []
    # get all matches from a page and save links
    matches = browser.find_elements_by_class_name("match-info")
    for m in range(len(matches)):
        links.append(matches[m].get_attribute("href"))
    for link in links:
        browser.get(link)
        matchInfos = scrape_match_infos(browser=browser)
        dicts.append(matchInfos)
    return dicts


def initialize_browser(headless=True):
    """
    :param headless: bool, should chrome run in headless mode, i.e. in background
    :return: browser object used for all other functions
    """

    # set chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")

    if headless:
        chrome_options.add_argument("--headless")

    # Initialize a new browser
    browser = webdriver.Chrome(options=chrome_options)
    return browser

def scrape_season(league, season, browser):
    """
    :param league: string - name of the league for which data is to be retrieved;
                   one out of ["EPL", "La_liga", "Bundesliga", "Serie_A", "Ligue_1", "RFPL"]
    :param season: list - seasons for which data should be collected
                    possible values: [2014, 2015, 2016, 2017, 2018, 2019]
    :param browser: browser object, initialized by initialize_browser()
    :return:
    """

    print("Getting data for {}: Season {}.".format(league, season))

    # initialize empty list for data storage
    allMatches = []

    # define url
    url = "https://understat.com/league/" + league + "/" + season
    print(url)

    # open landing page
    browser.get(url)

    # find button for previous week and next week
    prev_week = browser.find_element_by_class_name("calendar-prev")

    # go to the first week and store the number of pages per season
    numOfPages = 1
    while prev_week.is_enabled():
        numOfPages += 1
        prev_week.click()

    # scrape all the pages
    while numOfPages >= 1:
        browser.get(url)
        prev_week = browser.find_element_by_class_name("calendar-prev")
        for n in range(1, numOfPages):
            prev_week.click()
        matchday = scrape_page(browser=browser)
        allMatches.append(matchday)
        numOfPages -= 1

    allMatches = list(chain.from_iterable(allMatches))
    allMatches = pd.DataFrame(allMatches)
    allMatches["season"] = season
    allMatches["league"] = league
    return allMatches


def scrape_league(league, browser, seasons=[2014, 2015, 2016, 2017, 2018, 2019]):
    """
    :param league: string - name of the league for which data is to be retrieved;
                   one out of ["EPL", "La_liga", "Bundesliga", "Serie_A", "Ligue_1", "RFPL"]
    :param browser: browser object, initialized by initialize_browser()
    :param seasons: list - seasons for which data should be collected
                    possible values: [2014, 2015, 2016, 2017, 2018, 2019]
    :return:
    """

    # convert elements in season list to string
    seasons = [str(season) for season in seasons]

    leagueData = []
    for season in seasons:
        seasonDat = scrape_season(league=league, season=season, browser=browser)
        leagueData.append(seasonDat)

    # combine dataframes to single dataframe
    leagueDF = pd.concat(leagueData)

    return leagueDF