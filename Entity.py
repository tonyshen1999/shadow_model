from Account import Account, ShadowAccount
from Trialbalance import TrialBalance
from Period import Period
from AccountsTable import AccountsTable
import pandas as pd
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
    def set_tb(self,tb):
        self.__tb = tb
    def set_child(self,child, percent_owned):
        child.parent = self
        child.percent_owned = percent_owned
        self.children.append(child)
    
    def pull_accounts_csv(self, fName):
        
        entity = []
        account_names = []
        account_amount = []
        account_currency = []
        account_collection = []
        account_class = []
        account_data_type = []
        account_period = []

        for x in self.__accounts_table.accounts:
            entity.append(self.name)
            account_names.append(x.account_name)
            account_amount.append(x.getAmount())
            account_currency.append(x.currency)
            account_collection.append(x.account_collection)
            account_class.append(x.account_class)
            account_data_type.append(x.account_data_type)
            account_period.append(x.account_period.period_type + x.account_period.period_year)
        
        accounts_dict = {
            "Entity":entity,
            "Account Name":account_names,
            "Amount":account_amount,
            "ISO Currency Code":account_currency,
            "Period":account_period,
            "Collection":account_collection,
            "Class":account_class,
            "Data Type":account_data_type
        }

        df = pd.DataFrame(accounts_dict)
        df.to_csv(fName)


p = Period("CYE","2022", "01-01-2022", "12-31-2022")
tb = TrialBalance(p)
tb.generate_random_tb()
e = Entity("Acme Corp","ME","EUR",p,"CFC",tb)

e.pull_accounts_csv("accounts.csv")