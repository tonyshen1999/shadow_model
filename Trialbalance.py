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
        self.__other_equity = Account("Other Equity",0,period)

        self.__equity.set_child(self.__common_stock)
        self.__equity.set_child(self.__retained_earnings)
        self.__equity.set_child(self.__other_equity)

        # Tier 3

        self.__cash = Account("Cash",0,period)
        self.__non_cash = Account("Non Cash",0,period)

        self.__current_assets.set_child(self.__cash)
        self.__current_assets.set_child(self.__non_cash)

        self.__ppe = Account("PPE",0, period)
        self.__intangible = Account("Intangible", 0, period)
        self.__other_assets = Account("Other Non Current Assets" ,0, period)

        self.__non_current_assets.set_child(self.__ppe)
        self.__non_current_assets.set_child(self.__intangible)
        self.__non_current_assets.set_child(self.__other_assets)

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

        self.__tier1 = {
            "Assets":self.__assets,
            "Liabilities":self.__liabs,
            "Equity":self.__equity
        }
        self.__tier2 = {
            "Current Assets":self.__current_assets,
            "Non Current Assets":self.__non_current_assets,
            "Current Liabilities":self.__current_liab,
            "Non Current Liabilities":self.__non_current_liab,
            "Common Stock":self.__common_stock,
            "Retained Earnings":self.__retained_earnings,
            "Other Equity":self.__other_equity
        }
        self.__tier3 = {
            "Cash":self.__cash,
            "Non Cash": self.__non_cash,
            "PPE": self.__ppe,
            "Intangible":self.__intangible,
            "Other Non Current Assets":self.__other_assets,
            "Retained Earnings Beginning":self.__re_begin,
            "Net Income":self.__net_income,
            "Dividends":self.__dividends
        }
        self.__tier4 = {
            "Sales":self.__sales,
            "COGS":self.__cogs,
            "Other Income":self.__other_income,
            "Interest Income":self.__interest_income,
            "Dividend Income":self.__dividend_income,
            "Depreciation":self.__depreciation,
            "Amortization":self.__amortization,
            "Interest Expense":self.__interest_expense,
            "Income Tax Expense":self.__tax,
            "Other Expense":self.__other_expense
        }
        

    def getRatioMap(self):

        return self.__ratio_map
    

    def __str__(self):

        to_return = ""

        to_return += self.__assets.parse_tree()
        to_return += self.__liabs.parse_tree()
        to_return += self.__equity.parse_tree()



        return to_return
    

  
    def generate_random_tb(self, starting_asset = 1000000000.00, ticker = "AAPL"):

        self.set_ratios(ticker)

        self.__assets.amount = round(starting_asset)
        self.__liabs.amount = round(self.__ratio_map["debtRatio"]*self.__assets.amount)
        self.__equity.amount = round(self.__assets.amount - self.__liabs.amount)
        self.__non_current_liab.amount = round(self.__ratio_map["debtToAsset"]*self.__assets.amount)
        self.__current_liab.amount = self.__liabs.amount - self.__non_current_liab.amount
        self.__current_assets.amount = round(self.__non_current_liab.amount * self.__ratio_map["currentRatio"])
        self.__non_current_assets.amount = self.__assets.amount - self.__current_assets.amount
        self.__common_stock.amount = round(self.__equity.amount*self.__ratio_map["commonToRetainedEarnings"])
        self.__retained_earnings.amount = round(self.__equity.amount - self.__retained_earnings.amount - self.__other_equity.amount)
        self.__other_equity.amount = 0
        self.__net_income.amount = round(self.__assets.amount * self.__ratio_map["returnOnAssets"])
        self.__dividends.amount = round(self.__net_income.amount * self.__ratio_map["payoutRatio"])
        self.__re_begin.amount = round(self.__retained_earnings.amount - self.__net_income.amount - self.__dividends.amount)
        self.__cash.amount = round(self.__current_liab.amount * self.__ratio_map["cashRatio"])
        self.__non_cash.amount = round(self.__current_assets.amount - self.__cash.amount)
        self.__sales.amount = round(self.__net_income.amount * self.__ratio_map["netProfitMargin"])
        self.__ppe.amount = round(self.__sales.amount/self.__ratio_map["fixedAssetTurnover"])
        self.__intangible.amount = round(self.__assets.amount-(self.__net_income.amount/self.__ratio_map["returnOnTangibleAssets"]))
        self.__other_assets.amount = self.__non_current_assets.amount - self.__ppe.amount - self.__intangible.amount

        if self.__non_current_assets.amount - self.__ppe.amount - self.__intangible.amount < 0:
            self.__intangible.amount = self.__non_current_assets.amount - self.__ppe.amount

        self.__cogs.amount = round(self.__sales.amount - (self.__ratio_map["grossProfitMargin"]*self.__sales.amount))
        ebit = round(self.__ratio_map["ebitPerRevenue"]*self.__sales.amount)
        self.__other_expense.amount = round((self.__net_income.amount - ebit) * self.__ratio_map["otherExpenseIncome"])
        self.__other_income.amount = round(self.__net_income.amount - ebit - self.__other_expense.amount)
        self.__interest_income.amount = round(self.__other_income.amount * self.__ratio_map["otherIncome"])
        self.__dividend_income.amount = 0
        # da = (self.__liabs.amount - self.__cash.amount)/self.__ratio_map["netDebtToEbitda"] - ebit
        # self.__amortization.amount = round(da * self.__ratio_map["amortizationRatio"])
        # self.__depreciation.amount = round(da - self.__amortization.amount)
        self.__interest_expense.amount = round((ebit/self.__ratio_map["interestCoverage"]))
        self.__tax.amount = self.__net_income.amount - ebit - self.__interest_expense.amount
        self.split_leaf_accounts()

    def split_leaf_accounts(self):
        self.split_leaf_helper(self.__assets)
        self.split_leaf_helper(self.__liabs)
        self.split_leaf_helper(self.__equity)
        
    
    def split_leaf_helper(self, node):

        if len(node.children) == 0:
            new_leaves = node.split_random()
            for x in new_leaves:
                node.set_child(x)
        else:
            for x in node.children:
                self.split_leaf_helper(x)
    

    def generate_ratios(self,ticker):
        api_url = "https://financialmodelingprep.com/api/v3/ratios/"+ticker+"?limit=1000&apikey=e68f6ad070640ca92dbae4f9ce317086"
        response = requests.get(api_url)
        return response.json()[0]

    def set_ratios(self, ticker):


        ratios = [
            "debtRatio",
            "debtToAsset",
            "currentRatio",
            "commonToRetainedEarnings",
            "returnOnAssets",
            "payoutRatio",
            "returnOnTangibleAssets",
            "cashRatio",
            "fixedAssetTurnover",
            "netProfitMargin",
            "grossProfitMargin",
            "ebitPerRevenue",
            "otherExpenseIncome",
            "otherIncome",
            "netDebtToEbitda",
            "amortizationRatio",
            "interestCoverage"
        ]

        self.__ratio_map = {}

        for x in ratios:
            self.__ratio_map[x] = random.random()
        
        generated_ratios = self.generate_ratios(ticker)
        gen_keys = generated_ratios.keys()
        for x in self.__ratio_map.keys():
            if x in gen_keys:
                self.__ratio_map[x]=generated_ratios[x]

p = Period("CYE","2022", "01-01-2022", "12-31-2022")
tb = TrialBalance(p)
# print(tb.generate_ratios("AAPL"))
# print("-----------------")
tb.generate_random_tb()
print(tb)