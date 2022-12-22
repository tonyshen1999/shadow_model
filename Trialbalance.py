import copy
import datetime
import pandas as pd
import random
from datetime import datetime, timedelta
import requests
import json
from collections import defaultdict
import Account

class Period:
    def __init__(self, period_type, period_year, begin_date, end_date):

        self.period_year = period_year
        self.period_type = period_type
        self.begin_date = pd.to_datetime(begin_date)
        self.end_date = pd.to_datetime(end_date)
        # self.prior_period = Period(self.period_type, self.period_year - 1, begin_date - pd.DateOffset(years=1),
        #                            end_date - pd.DateOffset(years=1))
        # self.future_period = Period(self.period_type, self.period_year - 1, begin_date + pd.DateOffset(years=1),
        #                             end_date + pd.DateOffset(years=1))

    def __eq__(self,other):

        return isinstance(other, Period) and (self.period_type, self.period_year) == (other.period_type, other.period_year)

    def __str__(self):
        to_return = self.period_type + str(
            self.period_year) + ", Begin: " + self.begin_date.__str__() + ", End: " + self.end_date.__str__()
        return to_return


class TrialBalance:
    def __init__(self, period, file_name="", ticker="AAPL"):
        self.__period = period
        self.__fName = file_name
        self.__accounts = []
        self.__ratios = self.generate_ratios(ticker)
        if file_name == "":
            print("generating random trial balance...")
            self.generate_random_tb()

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

