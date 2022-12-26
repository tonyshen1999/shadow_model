from Account import Account, ShadowAccount
from Trialbalance import TrialBalance
from Period import Period
from AccountsTable import AccountsTable

class Entity:


    
    # Create an Attributes Class for each Entity type (CFC, DRE, USSH). Load Attributes pushes appropriate attribute type based on Entity type
    #
    def __init__(self, name,country, currency, period, entity_type, tb = None):

        self.name = name
        self.country = country
        self.type = entity_type
        self.currency = currency
        self.period = period

        self.children = []
        self.parent = None
        self.percent_owned = 100

        if tb == None:
            self.__tb = TrialBalance(self.period,currency=self.currency)
        else:
            self.__tb = tb
        
        self.__accounts_table = AccountsTable()
        self.__accounts_table.pull_tb(self.__tb)

    def get_accounts_table(self):
        return self.__accounts_table
    def get_tb(self):
        return self.__tb
    
    def set_child(self,child, percent_owned):
        child.parent = self
        child.percent_owned = percent_owned
        self.children.append(child)


