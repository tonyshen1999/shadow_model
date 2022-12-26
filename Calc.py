from Account import Account,ShadowAccount
import pandas as pd
import copy as copy
from AccountsTable import AccountsTable

class Calc:
    def __init__(self, script_fileName, period, accounts_table = None):
        if accounts_table == None:
            accounts_table = AccountsTable()
            accounts_table.default_tables("TBFC",period)
        self.values = copy.deepcopy(accounts_table.accounts)
        self.script_fileName = script_fileName
        with open('CalcScripts//' +self.script_fileName ) as f:
            lines = f.readlines()
            print(lines)
            
        

