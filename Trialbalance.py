import copy
import datetime
import pandas as pd
import random
from datetime import datetime, timedelta
import requests
import json
from collections import defaultdict


class Account:
    def __init__(self, account_name, amount, account_period, currency="USD"):
        self.account_name = account_name
        self.amount = amount
        self.account_period = account_period
        self.currency = currency

    def __str__(self):
        to_return = "Account Name: " + self.account_name + ", Period: " + self.account_period.__str__() + \
                    ", Amount: " + str(self.amount) + self.currency

        if self.account_type != "":
            to_return += ", Account Type: " + self.account_type.__str__()
        if self.account_description != "":
            to_return += ", Account Description: " + self.account_description
        if self.account_comment != "":
            to_return += ", Account Comment: " + self.account_comment

        return to_return

    def split_ratio(self, ratio, name_a, name_b):

        to_return = []
        account_a = copy.deepcopy(self)
        account_a.account_name = name_a
        account_a.amount = round(self.amount * float(ratio),2)

        account_b = copy.deepcopy(self)
        account_b.account_name = name_b
        account_b.amount = round(self.amount - account_a.amount,2)
        to_return.append(account_a)
        to_return.append(account_b)

        return to_return

    def split_random(self, new_name="", num_accounts=random.randrange(3, 20)):

        if new_name == "":
            new_name = self.account_name
        print(new_name)
        total_amount = self.amount
        accounts = []
        base_amount = total_amount/num_accounts
        current_sum = 0
        for i in range(0, num_accounts-1):
            new_account = copy.deepcopy(self)
            new_account.amount = round(base_amount * random.random(),2)
            current_sum += new_account.amount
            new_account.account_name = new_name
            accounts.append(new_account)

        plug_account = copy.deepcopy(self)
        plug_account.amount = total_amount - current_sum
        plug_account.account_name = new_name
        accounts.append(plug_account)

        return accounts


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



p = Period("CYE","2022", "01-01-2022", "12-31-2022")
tb = TrialBalance(p)
# print(sorted(tb.get_ratio_set().keys()))