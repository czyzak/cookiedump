#!/usr/bin/python3

# cookidump
# Original GitHub project:
# https://github.com/auino/cookidump

import os
import io
import argparse
import platform
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By




def scroll_down(self):
    """A method for scrolling the page."""

    # Get scroll height.
    last_height = self.driver.execute_script("return document.body.scrollHeight")

    while True:

        # Scroll down to the bottom.
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page.
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height.
        new_height = self.driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:

            break

        last_height = new_height


def getAllIds_from_page(driver, baseURL):
    """Returns ids of recipes in page number as string list"""
    ids, idsTotal, links = [], [], []
    driver.get(baseURL)
    
    while True:
            #"""A method for scrolling the page."""
        try:
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
            # Scroll down to the bottom.
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load the page.
                time.sleep(1)
            # Calculate new scroll height and compare with last scroll height.
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            time.sleep(0.5)
            driver.find_element_by_id("load-more-page").click()
        except Exception:
            break

    elems = driver.find_elements_by_css_selector('core-tile.core-tile--expanded')
#    print([elem.get_attribute('id') for elem in elems])
    for elem in elems:
        ids.append(elem.get_attribute('id'))
#    print(len(ids))    
    return ids


def getAllIds(driver):
    # set number of   categories
    k=20
    ids_cat = []
    for i in range(1,10):
        ids = getAllIds_from_page(driver, 'https://cookidoo.pl/search/pl?countries=pl&context=recipes&sortby=publishedAt&categories=VrkNavCategory-RPF-00{}'.format(i))
        ids_cat.extend(ids)
    for i in range(10,k+1):
        ids = getAllIds_from_page(driver, 'https://cookidoo.pl/search/pl?countries=pl&context=recipes&sortby=publishedAt&categories=VrkNavCategory-RPF-0{}'.format(i))
        ids_cat.extend(ids)  
    return ids_cat    

def startBrowser():
    """Starts browser with predefined parameters"""
    #chrome_driver_path = 'chromedriver.exe'

# def getRecipeBaseURL(browser):
#     """Gets the base URL to use with the recipe ID"""
#     link =  browser.find_element_by_class_name('link--alt')
#     url = link.get_attribute('href')
#     baseURL = url[0:url.find('/r', len(url)-10)+1]
#     return baseURL

def recipeToFile(browser, id, baseDir, baseURL):
    """Gets html by recipe id and saves in html file"""
    #TODO deal with locale URLs
    browser.get(baseURL+str(id))
    html = browser.page_source
    #baseDir = os.getcwd()+dir_separator+'{}'+dir_separator.format(folder)
    with io.open(baseDir+id+'.html', 'w', encoding='utf-8') as f: f.write(html)

#def appendToMarkdown(content, file):
#    baseDir = os.getcwd() + dir_separator+'recipes'+dir_separator+'{}.md'.format(file)
#    with io.open(baseDir, 'a', encoding='utf-8') as f: f.write(content + '\n')

def getFiles(mypath):
    #https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
    #mypath = os.getcwd() + dir_separator+'{}'+dir_separator.format(folder)
    fileList = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
    return fileList


def isDownloaded(fileList, id):
    try:
        fileIndex = fileList.index('{}.html'.format(id))
    except:
        fileIndex = -1
    
    if fileIndex > 0:
        answer = True
    else:
        answer = False
    return answer

def run(webdriverfile, outputdir):
    """Scraps all recipes and stores them in html"""
    print('[CD] Welcome to cookidump, starting things off...')

    #locale = input('[CD] Complete the website domain: https://cookidoo.')
    baseURL = 'https://cookidoo.pl/recipes/recipe/pl/'

    options = Options()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    #chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    idsTotal, idsDownloaded = [], [] 
    #activeFolder = 'recipes'
    #activePath = os.getcwd() + dir_separator+'{}'+dir_separator.format(activeFolder)

    #login page
    driver.get("https://cookidoo.pl/profile/pl/login?redirectAfterLogin=%2Ffoundation%2Fpl")
    driver.find_element_by_id('email').send_keys('d2314367@urhen.com')
    driver.find_element_by_id ('password').send_keys('d2314367@urhen.com')
    driver.find_element_by_id('j_submit_id').click()

    time.sleep(0.05)

    #Creating necessary folder
    #if not os.path.exists(activePath): os.makedirs(activePath)

    #Fetching all the IDs 
    idsTotal = getAllIds(driver)
    ##print(len(idsTotal))
    #Writing all the IDs to a file
    with open('ids.txt', 'w') as f: f.write(str(idsTotal))
    print('[CD] Stored ids in ids.txt file')

    #Checking which files are already downloaded
    files = getFiles(outputdir)

## for testing: 
#   idsTotal = ['r301400', 'r574051', 'r571871']

     #Downloading all the recipes
    i = 0
    j = len(idsTotal)
    for id in idsTotal:
        if not isDownloaded(files, id):
            recipeToFile(driver, id, outputdir, baseURL)
            idsDownloaded.append(id)
            i += 1
    #     print('\r[CD] {}/{} recipes processed'.format(i, j))
    
    # #Writing all the downloaded IDs to a file
    # with open('idsDownloaded.txt', 'w') as f:
    #     f.write(str(idsDownloaded))
    # print('[CD] {} ids downloaded, ids stored in IdsDownloaded.txt file'.format(len(idsDownloaded)))

    # print('[CD] Closing session\n[CD] Goodbye!')
    driver.close()

if  __name__ =='__main__':
    # parser = argparse.ArgumentParser(description='Dump Cookidoo recipes from a valid account')
    # parser.add_argument('webdriverfile', type=str, help='the path to the Chrome WebDriver file')
    # parser.add_argument('outputdir', type=str, help='the output directory')
    # args = parser.parse_args()
    run('chromedriver', '/home/ania/cookidump/recipes')
