# REVISIT AFTER TEST MODEL WORKS TO IMPLEMENT OWN COMPILER FOR CALC SCRIPTS


from Account import Account,ShadowAccount
import pandas as pd
import copy as copy
from AccountsTable import AccountsTable
from Period import Period
from Trialbalance import TrialBalance
from Entity import Entity
from Attributes import AttributesTable,Attribute

class Calc:

    def __init__(self, script_fileName, period, atr_fileName, accounts_table = None, currency = "USD"):
        if accounts_table == None:
            accounts_table = AccountsTable()
            accounts_table.import_tables("TBFC",period)
        self.accounts = copy.deepcopy(accounts_table)
        self.script_fileName = script_fileName
        self.currency = currency
        self.atr_tbl = AttributesTable(period=period,fName=atr_fileName)
        self.period = period
        atr_accounts = self.atr_tbl.pull_account_atr()
        for x in atr_accounts:
            self.accounts.add_account(x)

        # self.calc_accounts = []
        # self.calc_accounts = set(self.calc_accounts)
        fileRead = open('CalcScripts//' +self.script_fileName, "r")

        for line in fileRead:
            
            line_list = line.strip().split("=")
            new_account = ShadowAccount(account_name=line_list[0],amount=0.00,account_period=period,currency=self.currency,sign=True,account_collection="")
            new_children = self.node_from_line(line_list[1]) ## SWITCH BACK

            for x in new_children:
                #print(x)
                new_account.set_child(x)
            
            self.accounts.add_account(new_account)
            
        
        fileRead.close()


        self.compile()


        # a = self.accounts.find_account("PBT")
        # a.to_post_fix()
        # print("children--")
        # for x in a.post_fix_children:
        #     print(x)
    def compile(self):
        for x in self.accounts:
            x.compile_post_fix()
            print(x)
            # if x.account_name == "TaxLiability":
            #     print(x)
    def node_from_line(self,line):

        node_list = []
        currWord = ""
        operators = "+-*/()"
        for c in line:
            if c in operators:
                
                acc_node = self.accounts.find_account(currWord)
                if acc_node != None:
                    node_list.append(acc_node)
                    # print(acc_node)
                    node_list.append(c)
                currWord = ""
            else:
                currWord+=c
        if len(currWord) > 0:
            acc_node = self.accounts.find_account(currWord)
            if acc_node != None:    
                node_list.append(acc_node)

        if isinstance(node_list[-1],str) and node_list[-1] in operators:
            del node_list[-1]
        return node_list

    def tag_node_from_line(self,line):
    
        node_list = []
        currWord = ""
        operators = "+-*/()"



        for c in line:

            if c in operators:
                if "[" in currWord and "]" in currWord and self.atr_tbl[currWord.replace("[","").replace("]","")] is not None:
                    currWord = self.atr_tbl[currWord.replace("[","").replace("]","")].atr_value
                    print("FOUND TAG!")
                    print(str(currWord))
                acc_node = self.accounts.find_account(currWord)
                if acc_node != None:
                    node_list.append(acc_node)
                    node_list.append(c)
                elif isinstance(currWord,int) or isinstance(currWord,float):
                    node_list.append(float(currWord))
                    node_list.append(c)
                currWord = ""
            else:
                currWord+=c
        if len(currWord) > 0:
            acc_node = self.accounts.find_account(currWord)
            if acc_node != None:    
                node_list.append(acc_node)
            elif isinstance(currWord,int) or isinstance(currWord,float):
                node_list.append(float(currWord))

        if isinstance(node_list[-1],str) and node_list[-1] in operators:
            del node_list[-1]
        return node_list

p = Period("CYE","2022", "01-01-2022", "12-31-2022")
t = TrialBalance(p)
t.generate_random_tb()
a = AccountsTable()
a.pull_tb(t)

e = Entity(name = "Foo", country = "Canada",currency = "CA",period = p,entity_type="CFC",accounts_table=a)
e.pull_accounts_csv("testing_ties.csv")


c = Calc(script_fileName="CFC_Tested_Income.txt",period=p,atr_fileName="CFCAttributes.csv",accounts_table=a,currency="USD")