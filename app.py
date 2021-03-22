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
from flask import Flask, render_template, request


sites = {}
bestPrice = {
    "site":None,
    "title":None,
    "value":None,
    "link":None
    }
option = Options()
#option.headless = True
driver = webdriver.Chrome(ChromeDriverManager().install(),options=option)

cols = ['site','title','link','value']


app = Flask(__name__)

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
    
    individualData = []
    data = np.array([['site','titulo','link','0']])
    i = 0
    for div in divs:
        if(i <= 5):
            element_found = div.find('a',attrs={'class':'price'})
            valueMain = element_found.find('span',attrs={'class':'mainValue'})
            valueCents = element_found.find('span',attrs={'class':'centsValue'})
            value = valueMain.text+valueCents.text
            value = priceTreatment(value)
            title = element_found.get('title').replace('Ver ofertas para ','')
            link = url + element_found.get('href')
            setBestPrice('Buscape',title,link,value)
            individualData = [['Buscape',title,link,value]]
            if data.size == 0:
                data = np.append(data,individualData)
            else:
                data = np.append(data,individualData, axis = 0)
            i = i +1
    toPandas(data, cols,'buscape')
    time.sleep(3)
    #driver.quit()
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

    individualData = []
    data = np.array([['site','titulo','link','0']])
    i = 0
    for li in lis:
        if(i <= 5):
            price = li.find('span',attrs={'class':'price'}).text
            price = priceTreatment(price)
            title = li.find('h3',attrs={'class':'productTitle'}).text
            link = url + li.find('a',attrs={'class':'product-li'}).get('href')
            setBestPrice('Buscape',title,link,price)
            individualData = [['Magalu',title,link,price]]
            if data.size == 0:
                data = np.append(data,individualData)
            else:
                data = np.append(data,individualData, axis = 0)
            i = i + 1
    toPandas(data, cols,'magalu')
    time.sleep(3)
    #driver.quit()
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
    
    individualData = []
    data = np.array([['site','titulo','link','0']])
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
                value = priceTreatment(value)
                title = element_found.find('span',attrs={'class':'a-size-base-plus a-color-base a-text-normal'}).text
                link = url+aTag.get('href')
                setBestPrice('Buscape',title,link,value)
                individualData = [['Amazon',title,link,value]]
                if data.size == 0:
                    data = np.append(data,individualData)
                else:
                    data = np.append(data,individualData, axis = 0)
                i = i + 1
    toPandas(data, cols,'amazon')
    time.sleep(3)
    #driver.quit()
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

def priceTreatment(price):
    price = price.rstrip()
    price = price.replace('\n','')
    price = price.replace('R$','')
    price = price.replace('à vista','')
    price = price.replace(',','.')
    price = float(price)
    return price

def setBestPrice(site,title,link,price):
    #print(float(bestPrice['value']))
    #print(float(price))
    #print(float(bestPrice['value']) > float(price))
    if (bestPrice['value'] == None) or (float(bestPrice['value']) > float(price)):
        bestPrice['site'] = site
        bestPrice['title'] = title
        bestPrice['value'] = price
        bestPrice['link'] = link

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == "POST":
        global sites
        criteria = request.form['criteria']
        getFromBuscape(criteria)
        getFromMagalu(criteria)
        getFromAmazon(criteria)
        sites = dict(sites) 
        sites['magalu'] = sorted(sites['magalu'], key=lambda x : float(x['value']), reverse=False)
        sites['buscape'] = sorted(sites['buscape'], key=lambda x : float(x['value']), reverse=False)
        sites['amazon'] = sorted(sites['amazon'], key=lambda x : float(x['value']), reverse=False)
        return render_template('index.html',results=sites,best=bestPrice)
    return render_template('index.html',results={},best={})

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')
