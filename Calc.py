from Account import Account,ShadowAccount
import pandas as pd
import copy as copy
from AccountsTable import AccountsTable
from Period import Period
from Trialbalance import TrialBalance
from Entity import Entity

class Calc:

    def __init__(self, script_fileName, period, accounts_table = None, currency = "USD"):
        if accounts_table == None:
            accounts_table = AccountsTable()
            accounts_table.default_tables("TBFC",period)
        self.accounts = copy.deepcopy(accounts_table)
        self.script_fileName = script_fileName
        self.currency = currency
        fileRead = open('CalcScripts//' +self.script_fileName, "r")

        for line in fileRead:
            line = line.split("=")
            new_account = ShadowAccount(account_name=line[0],amount=0.00,account_period=period,currency=self.currency,sign=True,account_collection="")
            new_children = self.node_from_line(line[1])
            for x in new_children:
                new_account.set_child(x)
            
            new_account.compile_post_fix()
            print(new_account.amount)
            self.accounts.add_account(new_account)
        

    def node_from_line(self,line):

        node_list = []
        currWord = ""
        operators = "+-*/()[]"
        for c in line:
            if c in operators:
                
                acc_node = self.accounts.find_account(currWord)
                if acc_node != None:
                    node_list.append(acc_node)
                    node_list.append(c)
                currWord = ""
            else:
                currWord+=c
        if len(currWord) > 0:
            acc_node = self.accounts.find_account(currWord)
            if acc_node == None:
                raise Exception(currWord + " is not a valid account value")
            node_list.append(acc_node)
        
        return node_list

p = Period("CYE","2022", "01-01-2022", "12-31-2022")
t = TrialBalance(p)
t.generate_random_tb()
a = AccountsTable()
a.pull_tb(t)

e = Entity(name = "Foo", country = "Canada",currency = "CA",period = p,entity_type="CFC",accounts_table=a)
e.pull_accounts_csv("testing_ties.csv")


c = Calc("CFC_Tested_Income.txt",p,a,"USD")