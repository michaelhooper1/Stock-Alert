import requests
from decimal import Decimal
import webbrowser
import re
import json
import bs4


def look_at_price():
    company_prices = {}

    market = input("What market are you viewing? ")

    company_symbol = input("Input the company or company symbol you wish to view: ")


    fair_price = int(input("What price do you feel is appropriate for this company? "))
    try:
        assert fair_price in range(0, 2147483648)
    except ValueError:
        print("This is not an integer, enter a valid integer")
        look_at_price().exit()
    except AssertionError:
        print("Please enter a positive number.")
    else:
        pass


    if market.upper() in ["US", "USA", "America", "NYSE", "NASDAQ"]:
        pass
    elif market.upper() in ["FTSE", "FTSE100", "FTSE250", "FTSE 100", "FTSE 250", "UK", "LONDON", "LSE"]:
        company_symbol += ".L"
    elif market.upper() in ["TYO", "JPX", "TOKYO", "JAPAN", "JAPANESE"]:
        company_symbol += ".T"
    elif market.upper() in ["TO", "TORONTO", "CANADA", "CANADIAN"]:
        company_symbol += ".TO"

    res = requests.get("https://finance.yahoo.com/quote/{}".format(company_symbol))

    query = bs4.BeautifulSoup(res.text, "lxml")

    price_query = str(query.find("span" ,attrs={"data-reactid": "32"}))

    price_query_2 = re.sub(r'(?!<)[^<]*(?=>)', '', price_query)
    true_price_query = Decimal(re.sub("\<\>", "", price_query_2))

    print(true_price_query)


    company_prices.update( {company_symbol: fair_price} )


    with open("company_and_price.json", "w") as json_file:
        json.dump(company_prices, json_file)


    if fair_price > true_price_query:
        webbrowser.open_new("https://finance.yahoo.com/quote/{}".format(company_symbol))

look_at_price()
