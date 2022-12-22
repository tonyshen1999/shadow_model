import copy
import datetime
import pandas as pd
import random
from datetime import datetime, timedelta
import requests
import json
from collections import defaultdict
from Account import Account
from Period import Period

class TrialBalance:
    def __init__(self, period):
        self.__period = period

        # Tier 1
        self.__assets = Account("Asset",0,period)
        self.__liabs = Account("Liability",0,period)
        self.__equity = Account("Equity",0,period)

        # Tier 2
        self.__current_assets = Account("Current Asset",0,period)
        self.__non_current_assets = Account("Non Current Asset", 0, period)

        self.__assets.set_child(self.__current_assets)
        self.__assets.set_child(self.__non_current_assets)

        self.__current_liab = Account("Current Liability" , 0, period)
        self.__non_current_liab = Account("Non Current Liability" , 0, period)

        self.__liabs.set_child(self.__current_liab)
        self.__liabs.set_child(self.__non_current_liab)

        self.__common_stock = Account("Common Stock" , 0, period)
        self.__retained_earnings = Account("Retained Earnings",0, period)
        self.__other = Account("Other Equity",0,period)

        self.__equity.set_child(self.__common_stock)
        self.__equity.set_child(self.__retained_earnings)
        self.__equity.set_child(self.__other)

        # Tier 3

        self.__cash = Account("Cash",0,period)
        self.__non_cash = Account("Non Cash",0,period)

        self.__current_assets.set_child(self.__cash)
        self.__current_assets.set_child(self.__non_cash)

        self.__ppe = Account("PPE",0, period)
        self.__intangible = Account("Intangible", 0, period)
        self.__other = Account("Other Non Current Assets" ,0, period)

        self.__non_current_assets.set_child(self.__ppe)
        self.__non_current_assets.set_child(self.__intangible)
        self.__non_current_assets.set_child(self.__other)

        self.__re_begin = Account("Retained Earnings Beginning",0,period)
        self.__net_income = Account("Net Income",0,period)
        self.__dividends = Account("Dividends",0,period)
        
        self.__retained_earnings.set_child(self.__re_begin)
        self.__retained_earnings.set_child(self.__net_income)
        self.__retained_earnings.set_child(self.__dividends)

        # Tier 4

        self.__sales = Account("Sales",0,period)
        self.__cogs = Account("COGS",0,period)
        self.__other_income = Account("Other Income",0,period)
        self.__interest_income = Account("Interest Income",0,period)
        self.__dividend_income = Account("Dividend Income",0,period)
        self.__depreciation = Account("Depreciation",0,period)
        self.__amortization = Account("Amoritization",0,period)
        self.__interest_expense = Account("Interest Expense",0,period)
        self.__tax = Account("Income Tax Expense",0,period)
        self.__other_expense = Account("Other Expense",0,period)

        self.__net_income.set_child(self.__sales)
        self.__net_income.set_child(self.__cogs)
        self.__net_income.set_child(self.__other_income)
        self.__net_income.set_child(self.__interest_income)
        self.__net_income.set_child(self.__dividend_income)
        self.__net_income.set_child(self.__depreciation)
        self.__net_income.set_child(self.__amortization)
        self.__net_income.set_child(self.__interest_expense)
        self.__net_income.set_child(self.__tax)
        self.__net_income.set_child(self.__other_expense)


    def __str__(self):

        to_return = ""

        to_return += self.__assets.parse_tree()
        to_return += self.__liabs.parse_tree()
        to_return += self.__equity.parse_tree()



        return to_return
    

  
    # def generate_random_tb(self, starting_asset = 1000000.00):
    #     asset = Account("Asset", starting_asset, self.__period)
    #     debt_equity = asset.split_ratio(self.__ratios['debtRatio'], "Liability", "Equity")
    #     liability = debt_equity[0]
    #     equity = debt_equity[1]
    #     del debt_equity

    #     self.__accounts.append(asset)
    #     self.__accounts.append(liability)
    #     self.__accounts.append(equity)
    def generate_ratios(self,ticker):
        api_url = "https://financialmodelingprep.com/api/v3/ratios/"+ticker+"?limit=1000&apikey=e68f6ad070640ca92dbae4f9ce317086"
        response = requests.get(api_url)
        return response.json()[0]



p = Period("CYE","2022", "01-01-2022", "12-31-2022")
tb = TrialBalance(p)
print(tb)