import time
import requests
import pandas as pd
import json
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select

sites = {}
option = Options()
option.headless = False
driver = webdriver.Chrome(ChromeDriverManager().install())

def getFromBuscape(searchCriteria):
    url = "https://www.buscape.com.br"
    driver.get(url)

    driver.find_element_by_xpath("//div[@class='search-bar']//input[@class='react-autosuggest__input search-bar__text-box']").send_keys(searchCriteria)
    driver.find_element_by_xpath("//div[@class='search-bar']//button[@class='search-bar__submit-button']").click()
    time.sleep(2)

    select = Select(driver.find_element_by_id('orderBy'))
    select.select_by_visible_text("Menor preço")
    time.sleep(3)
    
    element = driver.find_element_by_xpath("//div[@class='row']//div[@class='SearchPage_SearchList__HL7RI col']")
    html_content = element.get_attribute('outerHTML')

    #Parsear conteudo html
    soup = BeautifulSoup(html_content,'html.parser')
    divs = soup.find_all('div', attrs={'class':'priceWrapper'})
    
    cols = ['title','link','value']
    individualData = []
    data = np.array([['titulo','link','valor']])
    i = 0
    for div in divs:
        if(i <= 5):
            element_found = div.find('a',attrs={'class':'price'})
            valueMain = element_found.find('span',attrs={'class':'mainValue'})
            valueCents = element_found.find('span',attrs={'class':'centsValue'})
            value = valueMain.text+valueCents.text
            title = element_found.get('title').replace('Ver ofertas para ','')
            link = url + element_found.get('href')
            individualData = [[title,link,value]]
            if data.size == 0:
                data = np.append(data,individualData)
            else:
                data = np.append(data,individualData, axis = 0)
            i = i +1
    toPandas(data, cols,'buscape')
    time.sleep(3)
    driver.quit()
    saveToJson()
    

def getFromMagalu(searchCriteria):
    url = "https://www.magazineluiza.com.br"
    driver.get(url)
    driver.find_element_by_id('inpHeaderSearch').send_keys(searchCriteria)
    driver.find_element_by_id('btnHeaderSearch').click()
    time.sleep(2)

    selectElement = driver.find_element_by_xpath("//select[@class='select-box order']")
    select = Select(selectElement)
    select.select_by_visible_text("menor preço")
    time.sleep(3)

    element = driver.find_element_by_xpath("//ul[@class='productShowCase big']")
    html_content = element.get_attribute('outerHTML')
    #Parsear conteudo html
    soup = BeautifulSoup(html_content,'html.parser')
    lis = soup.find_all('li', attrs={'class':'product'})

    cols = ['title','link','value']
    individualData = []
    data = np.array([['titulo','link','valor']])
    i = 0
    for li in lis:
        if(i <= 5):
            price = li.find('span',attrs={'class':'price'}).text
            title = li.find('h3',attrs={'class':'productTitle'}).text
            link = url + li.find('a',attrs={'class':'product-li'}).get('href')
            individualData = [[title,link,price]]
            if data.size == 0:
                data = np.append(data,individualData)
            else:
                data = np.append(data,individualData, axis = 0)
            i = i + 1
    toPandas(data, cols,'magalu')
    time.sleep(3)
    driver.quit()
    saveToJson()

def getFromAmazon(searchCriteria):
    url = "https://www.amazon.com.br"
    driver.get(url)
    driver.find_element_by_id('twotabsearchtextbox').send_keys(searchCriteria)
    driver.find_element_by_id('nav-search-submit-button').click()
    time.sleep(2)

    select = Select(driver.find_element_by_id('s-result-sort-select'))
    select.select_by_visible_text("Preço: baixo a alto")
    time.sleep(3)

    element = driver.find_element_by_xpath("//div[@class='s-main-slot s-result-list s-search-results sg-row']")
    html_content = element.get_attribute('outerHTML')
    #Parsear conteudo html
    soup = BeautifulSoup(html_content,'html.parser')
    divs = soup.find_all('div', attrs={'class':'sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col sg-col-4-of-20'})
    
    cols = ['title','link','value']
    individualData = []
    data = np.array([['titulo','link','valor']])
    i = 0
    for div in divs:
        if(i <= 5):
            element_found = div.find('div',attrs={'class':'s-expand-height s-include-content-margin s-border-bottom s-latency-cf-section'})
            aTag = element_found.find('a',attrs={'class':'a-link-normal s-no-outline'})
            valueWhole = element_found.find('span',attrs={'class':'a-price-whole'})
            if(valueWhole != None):
                valueCents = element_found.find('span',attrs={'class':'a-price-fraction'})
                valueSeparator = element_found.find('span',attrs={'class':'a-price-decimal'})
                value = valueWhole.text+valueSeparator.text+valueCents.text
                value = value.replace(",","",1) 
                title = element_found.find('span',attrs={'class':'a-size-base-plus a-color-base a-text-normal'}).text
                link = url+aTag.get('href')
                individualData = [[title,link,value]]
                if data.size == 0:
                    data = np.append(data,individualData)
                else:
                    data = np.append(data,individualData, axis = 0)
                i = i + 1
    toPandas(data, cols,'amazon')
    time.sleep(3)
    driver.quit()
    saveToJson()

def toPandas(data,cols,name):
    #pandas
    df_full = pd.DataFrame(data=data,columns=cols)
    #dicionario colocar variavel global
    sites[name] = df_full.to_dict('records')

def saveToJson():
    js = json.dumps(sites)
    fp = open('sites.json','w')
    fp.write(js)
    fp.close()
