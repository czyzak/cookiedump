#!/usr/bin/python3

## The program read all html files of recipes and return the excel file with all informations.

from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re


def name(soup):
    r_name = soup.find('title').getText()
    r_name = r_name.split('- Cookidoo')[0]
    return r_name

def ingredients(soup):
    r_ingredients = []
    ingr = soup.find('div',{"id": "ingredients"})

    tags= ingr.find_all('li')
    for tag in tags:
        #print(tag.getText())
        r_ingredients.append(tag.getText())
    
    df = pd.DataFrame(r_ingredients)
    df['Quantity'] = df.iloc[:,0].apply(lambda x: x.split('\n')[1])
    df['Ingredient'] = df.iloc[:,0].apply(lambda x: x.split('\n')[-1])
    df.drop(df.columns[0], axis=1,inplace=True)
    
    return df

def nutrition(soup):
    nutr = soup.find('div',{'class': 'nutritions'})
    names = nutr.find_all('dt')
    val = nutr.find_all('dd')

    r_nutr = {}
    for i,j in zip(names, val):
#       print((i.getText(),j.getText()))
        r_nutr[i.getText()]= j.getText()
    
    del r_nutr['Wartości odżywcze']
    r_nutrition = {key: value.split('\n')[-2] for key,value in r_nutr.items()}
    r_nutrition = {key: re.search(r"\d+.*",value)[0] for key,value in r_nutrition.items()}
    
    return r_nutrition

    

def difficulty(soup):
    r_difficulty = soup.find('label', {"id": "rc-icon-difficulty-text"}).getText()
    r_difficulty = r_difficulty.split(' ')[2]
    return r_difficulty

def prep_time(soup):
    r_time = soup.find('label', {"id": "rc-icon-active-time-text"}).getText()
    r_time = r_time.split(' ')[2]
    return r_time

def rating(soup):
    r_rating = soup.find('span', {"class": "core-rating__counter"}).getText()
    return r_rating

def rating_nr(soup):
    r_rating_nr = soup.find('span', {"class": "core-rating__label"}).getText()
    return r_rating_nr

def tags(soup):
    tags1 = soup.find('div',{'class': 'core-tags-wrapper__tags-container'})
    tags1 = tags1.find_all('a')
    tags2 = []
    tagsAll=""
    for tag in tags1:
        t = re.search(r"(?<=#).*", tag.getText()).group(0)
        tags2.append(t)
        tagsAll = tagsAll +', '+t        
    return tags2, tagsAll


def description(soup):
    tag = soup.find('div',{'class': 'preparation-steps'})
    tags = tag.find_all('li')
    text = ""
    for tag in tags:
        text =text + tag.getText() +'\n\n'
    return text


def make_df(idList):
    n = len(idList)
    # we will store our data in pandas data frame. Define column names
    col_names1 = ['Id','Name','Difficulty','Preparation_time','Rating','Number of votes','Tags']
    col_names1.extend(nutr_list) 
    col_names1.extend(['Ingredients','Description'])
    dict1 = {}

    for r_id in idList:
        page = open('recipes/recipesr{}.html'.format(r_id), "r", encoding='utf-8')
        page = BeautifulSoup(page, 'html.parser')
        r_name = name(page)
        try:
            r_nutr = nutrition(page)              
            r_kcal = r_nutr.get(nutr_list[-1])  
            r_carbohydrates = r_nutr.get(nutr_list[0])
            r_fibre = r_nutr.get(nutr_list[2])
            r_sodium = r_nutr.get(nutr_list[3])
            r_fat2 = r_nutr.get(nutr_list[4])
            r_cholesterol =r_nutr.get(nutr_list[5])
            r_fat1 = r_nutr.get(nutr_list[6])
            r_protein = r_nutr.get(nutr_list[7])
        except:
            break

        r_ingr = ingredients(page)        
        try:
            r_diffi = difficulty(page)
        except:
            r_diffi = 'brak_danych'
        
        try:        
            r_time = prep_time(page)
        except:
            r_time = 0
        r_rating = rating(page)
        r_rating_nr = rating_nr(page) 
        try:
        #    tags(page)
            r_tags = tags(page)[1]
        except:
            r_tags = 'brak_danych'

        r_description = description(page)

# Putting our data into DataFrame
        dict1[r_id] = [r_id,r_name,r_diffi,r_time,r_rating,r_rating_nr,r_tags, r_kcal, r_carbohydrates,r_fibre,
        r_sodium,r_fat2,r_cholesterol,r_fat1,r_protein, r_ingr, r_description]
 
    df_base=pd.DataFrame.from_dict(dict1, orient='index', columns=col_names1)
    df_base.rename(columns = {'Węglowodany':'Carbohydrates', 'Błonnik':'Fiber', 'Sód':'Sodium',
    'Tłuszcz nasycony': 'Saturated Fat', 'Białko':'Protein','Tłuszcz':'Fat','Kalorie':'Calories'},inplace=True)
    return df_base




print('Welcome to read-and-write recipes. We will read all recipes from html files and converti it to the excel file.\n It can take few minutes...')

## Reading all ids into a list
f = open('ids.txt', 'r')
idsList = f.read().split(",")
f.close()
idsList = [int(re.findall(r"\d+",l)[0]) for l in idsList]


## Finding all possible nutritions:
# nutrition_set=set()
# for r_id in idsList:
#     page = open('/home/ania/cookidump/recipes/recipesr{}.html'.format(r_id), "r", encoding='utf-8')
#     page = BeautifulSoup(page, 'html')
#     try:
#         nutrition_set = nutrition_set.union(nutrition(page))     
#     except:
#         break        
# nutr_list = list(nutrition_set)
nutr_list = ['Węglowodany', 'Błonnik', 'Sód', 'Tłuszcz nasycony', 'Cholesterol', 'Białko', 'Tłuszcz', 'Kalorie']

a = make_df(idsList)
a_export_excel = a.to_excel('recipee_base.xlsx', index = None, header=True, encoding='utf-8') 

print('All recipes was downloaded to the recipee_base.xlsx file.')

#base_pickle = a.to_pickle('recepee_base.pkl')





