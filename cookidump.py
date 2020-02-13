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





def getAllIds_from_page(driver, baseURL):
    """Returns ids of recipes in page number as string list"""
    ids = []
    driver.get(baseURL)
    
    while True:
            #"""A method for scrolling the page."""
        try:
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
            # Scroll down to the bottom.
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load the page.
                time.sleep(0.2)
            # Calculate new scroll height and compare with last scroll height.
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            time.sleep(0.2)
            driver.find_element_by_id("load-more-page").click()
        except Exception:
            break

    elems = driver.find_elements_by_css_selector('core-tile.core-tile--expanded')
    for elem in elems:
        ids.append(elem.get_attribute('id'))
   
    return ids


def getAllIds(driver):
    #Set number of categories
    k=20
    categories = [f'VrkNavCategory-RPF-{i:03}' for i in range(1,k+1)]
    categories.append('VrkNavigationCategory-rpf-000001303095')

    ids_cat=[]
    for cat in categories:
        ids = getAllIds_from_page(driver, 'https://cookidoo.pl/search/pl?countries=pl&context=recipes&sortby=publishedAt&categories={}'.format(cat))
        ids_cat.extend(ids)
    return ids_cat
  

def recipeToFile(browser, id, baseDir, baseURL):
    """Gets html by recipe id and saves in html file"""
    #TODO deal with locale URLs
    browser.get(baseURL+str(id))
    html = browser.page_source
    #baseDir = os.getcwd()+dir_separator+'{}'+dir_separator.format(folder)
    with io.open(baseDir+id+'.html', 'w', encoding='utf-8') as f: f.write(html)

def getFiles(mypath):
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
    #Writing all the IDs to a file
    with open('ids.txt', 'w') as f: f.write(str(idsTotal))
    print('[CD] Stored ids in ids.txt file')

    #Checking which files are already downloaded
    files = getFiles(outputdir)

     #Downloading all the recipes
    i = 0
    j = len(idsTotal)
    for id in idsTotal:
        if not isDownloaded(files, id):
            recipeToFile(driver, id, outputdir, baseURL)
            idsDownloaded.append(id)
            i += 1
        print('\r[CD] {}/{} recipes processed'.format(i, j))
    
    print('[CD] Closing session\n[CD] Goodbye!')
    driver.close()

if  __name__ =='__main__':
    # parser = argparse.ArgumentParser(description='Dump Cookidoo recipes from a valid account')
    # parser.add_argument('webdriverfile', type=str, help='the path to the Chrome WebDriver file')
    # parser.add_argument('outputdir', type=str, help='the output directory')
    # args = parser.parse_args()
    run('chromedriver', '/home/ania/cookiedump/recipes')
