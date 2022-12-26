from Account import Account,ShadowAccount
import pandas as pd
import copy as copy
from AccountsTable import AccountsTable
from Period import Period
class Calc:
    def __init__(self, script_fileName, period, accounts_table = None):
        if accounts_table == None:
            accounts_table = AccountsTable()
            accounts_table.default_tables("TBFC",period)
        self.accounts = copy.deepcopy(accounts_table)
        self.script_fileName = script_fileName
        fileRead = open('CalcScripts//' +self.script_fileName, "r")
        for line in fileRead:
            line = line.split("=")
            # create calc node and set children


    def node_from_line(self,line):

        node_list = []
        currWord = ""
        operators = "+-*/()[]"
        for c in line:
            if c in operators:
                print("found op")
                acc_node = self.accounts.find_account(currWord)
                if acc_node == None:
                    raise Exception(currWord + " is not a valid account value")
                
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
c = Calc("CFC_Tested_Income.txt",p)
node_list = c.node_from_line("Sales+COGS")


for x in node_list:
    print(x)