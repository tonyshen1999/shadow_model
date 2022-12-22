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
        self.__accounts = []



    def get_ratio_set(self):
        return self.__ratios

    def __str__(self):
        to_return = ""
        for x in self.__accounts:
            to_return += x.__str__() + "\n"

        return to_return

    def generate_random_tb(self, starting_asset = 1000000.00):
        asset = Account("Asset", starting_asset, self.__period)
        debt_equity = asset.split_ratio(self.__ratios['debtRatio'], "Liability", "Equity")
        liability = debt_equity[0]
        equity = debt_equity[1]
        del debt_equity

        self.__accounts.append(asset)
        self.__accounts.append(liability)
        self.__accounts.append(equity)
    def generate_ratios(self,ticker):
        api_url = "https://financialmodelingprep.com/api/v3/ratios/"+ticker+"?limit=1000&apikey=e68f6ad070640ca92dbae4f9ce317086"
        response = requests.get(api_url)
        return response.json()[0]



# p = Period("CYE","2022", "01-01-2022", "12-31-2022")
# tb = TrialBalance(p)
# print(sorted(tb.get_ratio_set().keys()))

