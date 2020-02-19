#!/usr/bin/python3

import os
import io
import argparse
import platform
import time
import requests
import multiprocessing
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

RECIPES_DIR = 'recipes'


def downloadRecipe(q):
    while True:
        (id, token) = q.get()
        if id is None:
            return
        if os.path.isfile(f"{RECIPES_DIR}/{id}"):
            print(f":", end="", flush=True)
        else:
            try:
                r = requests.get(f"https://cookidoo.pl/recipes/recipe/pl/{id}",
                                 cookies=token)
                with open(f"{RECIPES_DIR}/{id}", 'wb') as f:
                    f.write(r.content)
                    print(".", end="", flush=True)
            except:
                print("*", end="", flush=True)
                os.remove(f"{RECIPES_DIR}/{id}")


def downloadIds(driver, categories, q):
    for category in categories:
        driver.get(
            f'https://cookidoo.pl/search/pl?query=&countries=pl&categories={category}'
        )
        token = {}
        cookies = dict([(c["name"], c["value"]) for c in driver.get_cookies()])
        token["v-token"] = cookies["v-token"]

        currentList = driver.find_elements_by_css_selector(
            "core-tile.core-tile--expanded")
        while True:
            num_start = len(currentList)
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            button = None
            try:
                button = driver.find_element_by_id("load-more-page")
            except NoSuchElementException:
                pass
            if not button is None:
                driver.execute_script("arguments[0].click();", button)
            time.sleep(0.05)
            currentList = driver.find_elements_by_css_selector(
                "core-tile.core-tile--expanded")
            num_end = len(currentList)
            if num_start == num_end:
                print(
                    f"{category} contains {len(currentList)} items. The queue will contain {len(currentList)+q.qsize()} unprocessed items."
                )
                for recipe in currentList:
                    q.put((recipe.get_attribute('id'), token))
                break


def run():
    options = Options()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)

    if not os.path.isdir(RECIPES_DIR):
        os.mkdir(RECIPES_DIR)

    q = multiprocessing.Queue()

    recipeDownloaders = [
        multiprocessing.Process(target=downloadRecipe, args=(q, ))
        for i in range(50)
    ]
    for recipeDowloader in recipeDownloaders:
        recipeDowloader.start()

    driver.get('https://cookidoo.pl/')
    login_link = driver.find_element_by_link_text("Zaloguj się")
    login_address = login_link.get_attribute('href')

    driver.get(login_address)
    login = driver.find_element_by_id("email")
    driver.execute_script("arguments[0].value = 'd2314367@urhen.com';", login)
    login = driver.find_element_by_id("password")
    driver.execute_script("arguments[0].value = 'd2314367@urhen.com';", login)
    login = driver.find_element_by_id("j_submit_id")
    driver.execute_script("arguments[0].click();", login)

    categories = [f"VrkNavCategory-RPF-0{i+1:02d}" for i in range(20)]
    categories.append("VrkNavigationCategory-rpf-000001303095")

    downloadIds(driver, categories, q)
    driver.close()

    for recipeDownloader in recipeDownloaders:
        q.put((None, {}))

    for recipeDownloader in recipeDownloaders:
        recipeDowloader.join()


if __name__ == '__main__':
    run()
