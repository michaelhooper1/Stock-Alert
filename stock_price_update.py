import requests
from decimal import *
import webbrowser
import re
import simplejson as json
import bs4
import _asyncio


USA = ["US", "USA", "America", "NYSE", "NASDAQ"]
UK = ["FTSE", "FTSE100", "FTSE250", "FTSE 100", "FTSE 250", "UK", "LONDON", "LSE"]
JPN = ["TYO", "JPX", "TOKYO", "JAPAN", "JAPANESE", "JPN", "JPX"]
CNDA = ["TO", "TORONTO", "CANADA", "CANADIAN", "CND", "CNDA", "TSX"]
CHINA = ["CHINA", "CHINESE", "SHANGHAI", "SSE", "HK", "HONG KONG"]

def price_search(company_symbol, mark):

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

    query = bs4.BeautifulSoup(res.text, "lxml")

    price_query = str(query.find("span", attrs={"data-reactid": "32"}))

    price_query_2 = re.sub(r'(?!<)[^<]*(?=>)', '', price_query)

    true_price_query = (re.sub("\<\>", "", price_query_2))
    
    return true_price_query



def look_at_price(symb, mark, pri):
    


    #Any necessary inputs that we need
    market = mark
    company_symbol = symb
    fair_price = pri



    true_fair_price = Decimal(fair_price)



    price_search(company_symbol, market)

    company_prices.update( {company_symbol: true_fair_price} )

    

  
    while true_fair_price < price_search(company_symbol):
        price_search(company_symbol, market)


    webbrowser.open_new("https://finance.yahoo.com/quote/{}".format(company_symbol))


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

def main():
    look_at_price()

if __name__ == "__main__":
    main()