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
    ids = []
    driver.get(baseURL)
    
    while True:
        #A method for scrolling the page.
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
        ids = getAllIds_from_page(driver, f'https://cookidoo.pl/search/pl?countries=pl&context=recipes&sortby=publishedAt&categories={cat}')
        ids_cat.extend(ids)
    return ids_cat 

def recipeToFile(browser, id, baseDir, baseURL):
    browser.get(baseURL+str(id))
    html = browser.page_source
    with open(baseDir+id+'.html', 'w', encoding='utf-8') as f: f.write(html)

def getFiles(mypath):
    fileList = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
    return fileList

def isDownloaded(fileList, id):
    try:
        fileIndex = fileList.index(f'recipes{id}.html')
    except:
        fileIndex = -1
    
    if fileIndex > 0:
        answer = True
    else:
        answer = False
    return answer

def run(webdriverfile, outputdir):
    print('Welcome to cookidump! Our goal is to download all new recipes from cookidoo site.')
    # Setting our regional cookidoo site:
    baseURL = 'https://cookidoo.pl/recipes/recipe/pl/'
    options = Options()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    
    idsTotal, idsDownloaded = [], [] 

    #login page
    driver.get("https://cookidoo.pl/profile/pl/login?redirectAfterLogin=%2Ffoundation%2Fpl")
    driver.find_element_by_id('email').send_keys('d2314367@urhen.com')
    driver.find_element_by_id ('password').send_keys('d2314367@urhen.com')
    driver.find_element_by_id('j_submit_id').click()

    time.sleep(0.05)

    #Fetching all the IDs 
    idsTotal = getAllIds(driver)
    #Writing all the IDs to a file
    with open('ids.txt', 'w') as f: f.write(str(idsTotal))

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
    print(f'{i} recipes have been downloaded.\n Goodbye!')
    driver.close()


## Run the program
run('chromedriver', 'recipes/')
