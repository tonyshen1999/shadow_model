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
import itertools
import xml.etree.ElementTree as ET

class TrialBalance:

    def __config(self,xml_node,account_node):

        account_node.account_name = xml_node.tag
        parent_debit = xml_node.attrib['debit']
        if parent_debit == "False":
            account_node.sign = False
        else:
            account_node.sign = True

        for x in xml_node:
            
            child_debit = x.attrib['debit']
            if child_debit == "False":
                child_debit  = False
            else:
                child_debit = True
            account_child = Account(x.tag,0,self.__period, sign = child_debit)
            account_node.set_child(account_child)
            self.__config(x,account_child)

    def __init__(self, period, currency = "USD"):
        self.__period = period

        config_tree = ET.parse('tb_config.xml')
        self.__header = Account("Header",0,self.__period)
        self.__config(config_tree.getroot(),self.__header)
        self.update_currency(currency)
        
    def buildXML(self,root):
        tree = ET.parse('tb_config.xml')
        self.__buildXMLHelper(root,tree.getroot())
        tree.write("tb_config.xml")

    def __buildXMLHelper(self,account_node,xml_node):

        xml_node.tag = account_node.account_name
        for x in account_node.children:
            xml_node_child = ET.SubElement(xml_node,x.account_name)
            self.__buildXMLHelper(x,xml_node_child)

    def getRatioMap(self):

        return self.__ratio_map
    

    def __str__(self):

        to_return = ""

        for x in self.__header.children:
            to_return += x.parse_tree()



        return to_return
    
    def find_account(self,account_node,account_name):
        results = []
        self.__find_account_helper(account_node,account_name,results)
        return results

    def __find_account_helper(self, account_node,account_name,results):

        if account_node.account_name == account_name:
            results.append(account_node)
        for x in account_node.children:
            self.__find_account_helper(x,account_name, results)

    def define_accounts(self):

        self.__assets = self.find_account(self.__header,"Asset")[0]
        self.__liabs = self.find_account(self.__header,"Liability")[0]
        self.__equity = self.find_account(self.__header,"Equity")[0]
        self.__non_current_liab = self.find_account(self.__header,"NonCurrentLiability")[0]
        self.__current_liab = self.find_account(self.__header,"CurrentLiability")[0]
        self.__current_assets = self.find_account(self.__header,"CurrentAsset")[0]
        self.__non_current_assets = self.find_account(self.__header,"NonCurrentAsset")[0]
        self.__common_stock = self.find_account(self.__header,"CommonStock")[0]
        self.__retained_earnings = self.find_account(self.__header,"RetainedEarnings")[0]
        self.__other_equity = self.find_account(self.__header,"OtherEquity")[0]
        self.__net_income = self.find_account(self.__header,"NetIncome")[0]
        self.__dividends = self.find_account(self.__header,"Dividends")[0]
        self.__re_begin = self.find_account(self.__header,"RetainedEarningsBeginning")[0]
        self.__cash = self.find_account(self.__header,"Cash")[0]
        self.__non_cash = self.find_account(self.__header,"NonCash")[0]
        self.__sales = self.find_account(self.__header,"Sales")[0]
        self.__ppe = self.find_account(self.__header,"PPE")[0]
        self.__intangible = self.find_account(self.__header,"Intangible")[0]
        self.__other_assets = self.find_account(self.__header,"OtherNonCurrentAssets")[0]
        self.__cogs = self.find_account(self.__header,"COGS")[0]
        self.__other_expense = self.find_account(self.__header,"OtherExpense")[0]
        self.__other_income = self.find_account(self.__header,"OtherIncome")[0]
        self.__interest_income = self.find_account(self.__header,"InterestIncome")[0]
        self.__dividend_income = self.find_account(self.__header,"DividendIncome")[0]
        self.__interest_expense = self.find_account(self.__header,"InterestExpense")[0]
        self.__tax = self.find_account(self.__header,"IncomeTaxExpense")[0]
        self.__depreciation = self.find_account(self.__header,"Depreciation")[0]
        self.__amortization = self.find_account(self.__header,"Amortization")[0]

    def generate_random_tb(self,starting_asset  = 1000000000.00,ticker="AAPL"):

        self.set_ratios(ticker)
        self.define_accounts()
        while True:
            self.push_random_tb(starting_asset)
            if self.verify_accounts() == True:
                break
            else:
                self.randomize_ratios()



    def push_random_tb(self, starting_asset):

        # print("pushing accounts...")

        self.__assets.amount = round(starting_asset)
        self.__liabs.amount = round(self.__ratio_map["debtRatio"]*self.__assets.amount)
        self.__equity.amount = round(self.__assets.amount - self.__liabs.amount)
        self.__non_current_liab.amount = round(self.__ratio_map["debtToAsset"]*self.__assets.amount)
        self.__current_liab.amount = self.__liabs.amount - self.__non_current_liab.amount
        self.__current_assets.amount = round(self.__non_current_liab.amount * self.__ratio_map["currentRatio"])
        self.__non_current_assets.amount = self.__assets.amount - self.__current_assets.amount
        self.__common_stock.amount = round(self.__equity.amount*self.__ratio_map["commonToRetainedEarnings"])
        self.__retained_earnings.amount = round(self.__equity.amount - self.__common_stock.amount - self.__other_equity.amount)
        self.__other_equity.amount = 0
        self.__net_income.amount = round(self.__assets.amount * self.__ratio_map["returnOnAssets"])
        self.__dividends.amount = round(self.__net_income.amount * self.__ratio_map["payoutRatio"])
        self.__re_begin.amount = round(self.__retained_earnings.amount - self.__net_income.amount + self.__dividends.amount)
        self.__cash.amount = round(self.__current_liab.amount * self.__ratio_map["cashRatio"])
        self.__non_cash.amount = round(self.__current_assets.amount - self.__cash.amount)
        self.__sales.amount = round(self.__net_income.amount * self.__ratio_map["netProfitMargin"])
        self.__ppe.amount = round(self.__sales.amount/self.__ratio_map["fixedAssetTurnover"])
        self.__intangible.amount = round(self.__assets.amount-(self.__net_income.amount/self.__ratio_map["returnOnTangibleAssets"]))
        self.__other_assets.amount = self.__non_current_assets.amount - self.__ppe.amount - self.__intangible.amount

        if self.__non_current_assets.amount - (self.__ppe.amount + self.__intangible.amount) < 0:
            self.__intangible.amount = self.__non_current_assets.amount - self.__ppe.amount

        self.__cogs.amount = round(self.__sales.amount - (self.__ratio_map["grossProfitMargin"]*self.__sales.amount))
        ebit = round(self.__ratio_map["ebitPerRevenue"]*self.__sales.amount)
        self.__other_expense.amount = round((self.__sales.amount-self.__cogs.amount-ebit) * self.__ratio_map["otherExpenseIncome"])
        self.__other_income.amount = round(self.__net_income.amount - ebit - self.__other_expense.amount)
        self.__interest_income.amount = round(self.__other_income.amount * self.__ratio_map["otherIncome"])
        self.__dividend_income.amount = 0
        # da = (self.__liabs.amount - self.__cash.amount)/self.__ratio_map["netDebtToEbitda"] - ebit
        # self.__amortization.amount = round(da * self.__ratio_map["amortizationRatio"])
        # self.__depreciation.amount = round(da - self.__amortization.amount)
        self.__interest_expense.amount = round((ebit/self.__ratio_map["interestCoverage"]))
        self.__tax.amount = -self.__net_income.amount + (self.__sales.amount - self.__cogs.amount - self.__other_expense.amount + self.__other_income.amount + self.__dividend_income.amount - self.__interest_expense.amount + self.__interest_income.amount)
        # self.split_leaf_accounts()

    def split_leaf_accounts(self):
        self.__split_leaf_helper(self.__assets)
        self.__split_leaf_helper(self.__liabs)
        self.__split_leaf_helper(self.__equity)
        
    
    def __split_leaf_helper(self, node):

        if len(node.children) == 0:
            new_leaves = node.split_random()
            for x in new_leaves:
                node.set_child(x)
        else:
            for x in node.children:
                self.__split_leaf_helper(x)
    

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

        self.__random_ratios = []
        generated_ratios = self.generate_ratios(ticker)

        gen_keys = generated_ratios.keys()

        for x in ratios:
            if x in gen_keys:
                self.__ratio_map[x]=generated_ratios[x]
            else:
                random_perc = random.random()
                self.__ratio_map[x] = random_perc
                self.__random_ratios.append(x)

    def randomize_ratios(self):
        print("generating random ratios:")
        for x in self.__random_ratios:
            self.__ratio_map[x] = random.random()
        
    def verify_accounts(self):

        accounts = [
            self.__assets,
            self.__liabs,
            self.__equity,
            self.__non_current_liab,
            self.__current_liab,
            self.__current_assets,
            self.__non_current_assets,
            self.__common_stock,
            self.__dividends,
            self.__cash,
            self.__non_cash,
            self.__ppe,
            self.__intangible,
            self.__other_assets
        ]

        for x in accounts:
            if x.amount < 0:
                return False
        return True

    def to_csv(self, fname):

        account_names = []
        account_amount = []
        account_id = []
        account_description = []
        
        self.__parse_accounts_helper(account_names,account_amount,account_id,account_description, self.__assets)
        self.__parse_accounts_helper(account_names,account_amount,account_id,account_description, self.__liabs)
        self.__parse_accounts_helper(account_names,account_amount,account_id,account_description, self.__equity)

        d = {"Account ID":account_id,'Account Names':account_names,"Account Amount":account_amount,"Account Description":account_description}
        df = pd.DataFrame(data = d)
        df.to_csv(fname)

        print("saved to " + fname)

    def __parse_accounts_helper(self, account_names,account_amount,account_id,account_description, node):
        
        if len(node.children) == 0:
            account_names.append(node.account_name)
            account_amount.append(node.getAmount())
            account_description.append(node.parent.account_name)
            account_id.append(1)
        else:
            for x in node.children:
                self.__parse_accounts_helper(account_names,account_amount,account_id,account_description,x)

    def check_difference(self, acceptable_diff = 2.0):

        results = {}
        self.__check_difference_helper(self.__header,results, acceptable_diff)
        return results

    def __check_difference_helper(self, node, results, acceptable_diff):

        if len(node.children) > 0:
            children_total = 0
            for x in node.children:
                children_total += x.getAmount()
            
            if abs(children_total-node.getAmount()>acceptable_diff):
                results[node] = children_total-node.getAmount()
            
            for x in node.children:
                self.__check_difference_helper(x, results, acceptable_diff)

    def update_currency(self, currency):
        self.__update_currency_helper(currency,self.__header)

    def __update_currency_helper(self, currency, node):

        node.currency = currency

        for x in node.children:
            self.__update_currency_helper(currency,x)

p = Period("CYE","2022", "01-01-2022", "12-31-2022")
tb = TrialBalance(p)

# print(tb.generate_ratios("AAPL"))
# print("-----------------")
for x in range(0,1):
    tb.generate_random_tb()

    tb.to_csv("test1.csv")
    print(tb)