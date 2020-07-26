import requests
from decimal import *
import datetime
import time
import webbrowser
import re
import simplejson as json
import bs4
import csv

def look_at_price():
    #We're going to dump this later
    company_prices = {}

    #All of the necessary markets, to be added to later
    USA = ["US", "USA", "America", "NYSE", "NASDAQ"]
    UK = ["FTSE", "FTSE100", "FTSE250", "FTSE 100", "FTSE 250", "UK", "LONDON", "LSE"]
    JPN = ["TYO", "JPX", "TOKYO", "JAPAN", "JAPANESE", "JPN", "JPX"]
    CNDA = ["TO", "TORONTO", "CANADA", "CANADIAN", "CND", "CNDA", "TSX"]
    CHINA = ["CHINA", "CHINESE", "SHANGHAI", "SSE", "HK", "HONG KONG"]


    #Any necessary inputs that we need
    market = input("What market are you viewing? (press q to exit) ")
    if market == "q":
        quit()

    company_symbol = input("Input the company symbol you wish to view: ")
    fair_price = input("What price do you feel is appropriate for this company? (In the denomination of the stock) ")


    try:
        isinstance(fair_price, Decimal)
        assert(Decimal(fair_price) > 0)
    except DecimalException:
        print("This is not a number, enter a valid number")
        look_at_price().exit()
    except AssertionError:
        print("Please enter a positive number.")
        look_at_price().exit()
    else:
        pass

    true_fair_price = Decimal(fair_price)

    if market.upper() in USA:
        pass
    elif market.upper() in UK:
        company_symbol += ".L"
    elif market.upper() in JPN:
        company_symbol += ".T"
    elif market.upper() in CNDA:
        company_symbol += ".TO"
    elif market.upper() in CHINA:
        company_symbol += ".HK"


    res = requests.get("https://finance.yahoo.com/quote/{}".format(company_symbol))


    query = bs4.BeautifulSoup(res.text, "lxml")


    price_query = str(query.find("span" ,attrs={"data-reactid": "32"}))

    price_query_2 = re.sub(r'(?!<)[^<]*(?=>)', '', price_query)

    true_price_query = Decimal(re.sub("\<\>", "", price_query_2))


    company_prices.update( {company_symbol: true_fair_price} )

    #Remember this is simplejson
    with open("company_and_price.json", "w") as json_file:
        if true_fair_price < 0:
            print("The number was invalid, so any existing price was not overwritten")
        else:
            json.dump(company_prices, json_file, use_decimal=True)


    if true_fair_price > true_price_query:
        webbrowser.open_new("https://finance.yahoo.com/quote/{}".format(company_symbol))

look_at_price()