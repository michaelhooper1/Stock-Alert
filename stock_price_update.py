import requests
from decimal import *
import webbrowser
import re

import bs4
import asyncio
import smtplib
import os
from datetime import datetime

#Raw package
import numpy as np
import pandas as pd


#Data Source
import yfinance as yf

#Data vizualisation
import plotly.graph_objs as go



os.environ["EMAIL_ADDRESS"] = "mhooperjnr1995@hotmail.co.uk"
os.environ["EMAIL_PASSWORD"] = "Everton123456789"

USA = ["US", "USA", "America", "NYSE", "NASDAQ"]
UK = ["FTSE", "FTSE100", "FTSE250", "FTSE 100", "FTSE 250", "UK", "LONDON", "LSE"]
JPN = ["TYO", "JPX", "TOKYO", "JAPAN", "JAPANESE", "JPN", "JPX"]
CNDA = ["TO", "TORONTO", "CANADA", "CANADIAN", "CND", "CNDA", "TSX"]
CHINA = ["CHINA", "CHINESE", "SHANGHAI", "SSE", "HK", "HONG KONG"]

def price_search(company_symbol, mark):

    if "." in company_symbol:
        pass
    elif mark.upper() in USA:
        pass
    elif mark.upper() in UK:
        company_symbol += ".L"
    elif mark.upper() in JPN:
        company_symbol += ".T"
    elif mark.upper() in CNDA:
        company_symbol += ".TO"
    elif mark.upper() in CHINA:
        company_symbol += ".HK"

    res = requests.get("https://finance.yahoo.com/quote/{}".format(company_symbol))

    query = bs4.BeautifulSoup(res.text, "lxml")

    price_query = str(query.find("span", attrs={"data-reactid": "32"}))

    price_query_2 = re.sub(r'(?!<)[^<]*(?=>)', '', price_query)

    true_price_query = (re.sub("\<\>|,", "", price_query_2))
    
    return Decimal(true_price_query)

def send_email_notification(symbol, market, user_email):
    with smtplib.SMTP("smtp.outlook.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(os.environ.get("EMAIL_ADDRESS"), os.environ.get("EMAIL_PASSWORD"))

        subject = "{} in the {} market has fallen below your desired price".format(symbol, market)

        body = "This occured at: {}".format(datetime)

        message = "Subject: {} \n\n {}".format(subject,body)

        smtp.sendmail(os.environ.get("EMAIL_ADDRESS"), user_email, message)

async def look_at_price(symb, mark, pri):
    


    #Any necessary inputs that we need
    market = mark
    company_symbol = symb
    fair_price = pri



    true_fair_price = Decimal(fair_price)



    price_search(company_symbol, market)

    if mark.upper() in USA:
        pass
    elif mark.upper() in UK:
        company_symbol += ".L"
    elif mark.upper() in JPN:
        company_symbol += ".T"
    elif mark.upper() in CNDA:
        company_symbol += ".TO"
    elif mark.upper() in CHINA:
        company_symbol += ".HK"

  
    while true_fair_price < price_search(company_symbol,market):
        price_search(company_symbol, market)
        await asyncio.sleep(0.00000001)
        

    

    if true_fair_price > price_search(company_symbol,market):
        webbrowser.open_new("https://finance.yahoo.com/quote/{}".format(company_symbol))
        #send_email_notification(company_symbol, market, email)

        return 0


def all_stat_lookup(symb, mark):
    company_symbol = symb

    if mark.upper() in USA:
        pass
    elif mark.upper() in UK:
        company_symbol += ".L"
    elif mark.upper() in JPN:
        company_symbol += ".T"
    elif mark.upper() in CNDA:
        company_symbol += ".TO"
    elif mark.upper() in CHINA:
        company_symbol += ".HK"


    res = requests.get("https://finance.yahoo.com/quote/{}".format(company_symbol))
    prof = requests.get("https://finance.yahoo.com/quote/{}/profile?p={}".format(company_symbol,company_symbol))

    query = bs4.BeautifulSoup(res.text, "lxml")
    profile = bs4.BeautifulSoup(prof.text, "lxml")

    name_1 = str(query.find("h1", attrs= {"class": "D(ib) Fz(18px)", "data-reactid":"7"}))
    name_2 = re.sub(r'(?!<)[^<]*(?=>)', '', name_1)
    name = re.sub("\<\>", "", name_2)

    market_1 = str(query.find("div", attrs={"class": "C($tertiaryColor) Fz(12px)", "data-reactid": "8"}))
    market_2 = re.sub(r'(?!<)[^<]*(?=>)', '', market_1)
    market =  re.sub("\<\>", "", market_2)

    price_query = str(query.find("span", attrs={"data-reactid": "32"}))
    price_query_2 = re.sub(r'(?!<)[^<]*(?=>)', '', price_query)
    true_price_query = re.sub("\<\>", "", price_query_2)

  
    
    info_1 = profile.find("p", attrs={"class": "D(ib) Va(t)"})
    info_data = info_1.findChildren("span", attrs={"class": "Fw(600)"}, recursive = False)
    info_data_string = [str(x) for x in info_data]
    info_titles = [x for x in info_1.findChildren("span") if x not in info_data]
    
    
    info_data_2 = [re.sub(r'(?!<)[^<]*(?=>)', '', x) for x in info_data_string]
    info_data_3 = [re.sub("\<\>", " ", y) for y in info_data_2]
    true_info_data = [re.sub("\&amp;", "&", a) for a in info_data_3]

    
    
    
    


    query_dict = {"name": name, "market": market, "price": true_price_query, "info": true_info_data}

    return query_dict

async def main(lst, price):
    loop_list = []
    for a in range(len(lst)):
        loop_list.append(asyncio.create_task(look_at_price(lst[a][1], lst[a][2], price[a])))
        
    
    await asyncio.gather(*loop_list)
    

    

