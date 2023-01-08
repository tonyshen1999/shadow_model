from Account import Account, ShadowAccount
from Trialbalance import TrialBalance
from Period import Period
from AccountsTable import AccountsTable
import pandas as pd
import copy
import itertools
from Attributes import AttributesTable,Attribute

class Entity:

    id_obj = itertools.count()
    
    # Create an Attributes Class for each Entity type (CFC, DRE, USSH). Load Attributes pushes appropriate attribute type based on Entity type
    #
    def __init__(self, name,country, currency, period, entity_type="", tb = None, accounts_table = None,atr_tb = None):

        self.id = next(Entity.id_obj)
        self.name = name
        self.country = country
        self.type = entity_type
        self.currency = currency
        self.period = period

        self.children = {}
        self.parents = {}
        
        self._accounts_table = accounts_table
        self.atr_tb = atr_tb

        if self.atr_tb == None:
            self.atr_tb = AttributesTable(self.period)

        # if tb == None:
        #     self.__tb = TrialBalance(self.period,currency=self.currency)
        # else:
        #     self.__tb = tb
        
        if self._accounts_table == None:
            self.__tb = TrialBalance(self.period,currency=self.currency)
            self._accounts_table = AccountsTable()
            self._accounts_table.pull_tb(self.__tb)
    def __str__(self):
        # parent = self.parent
        # if parent == None:
        #     parent = "None"
        # else:
        #     parent = parent.name
        to_return = "ID: " + str(self.id) + ", Name: " + self.name + ", Type: " + self.type + ", Country: " + self.country #+ ", Parent: " + parent +", Percent Owned: " + str(self.percent_owned*100) + "%"
        return to_return
    def get_accounts_table(self):
        return self._accounts_table
    def set_accounts_table(self,acc_tbl):
        self._accounts_table = acc_tbl
    def get_tb(self):
        return self.__tb
    def set_tb(self,tb):
        self.__tb = tb
    def set_child(self,child, percent_owned):
        self.children[child] = percent_owned
        child.parents[self] = percent_owned
    def __eq__(self,other):
        if other == None:
            return False
        return (self.name,self.type) == (other.name,other.type)
    def __hash__(self):
        return hash(self.name) ^ hash(self.type)
    def __getitem__(self,key):
        
        for x in self.children.keys():
            if x.name == key:
                return x
        
        to_return = copy.deepcopy(self)
        to_return.name = key
        print("*****WARNING*****\n" + key + " DOES NOT EXIST")
        return to_return
    def search_all_children(self,to_find):
        results = []
        if isinstance(to_find,Entity):
            to_find = to_find.name
        self.__search_all_children_helper(to_find,self,results)

        if len(results) == 0:
            return None
        elif len(results) == 1:
            return results[0]
        return results

    def __search_all_children_helper(self,to_find, entity, results):
        if to_find == entity.name:
            return results.append(entity)
        else:  
            for x in entity.children:
                self.__search_all_children_helper(to_find,x,results)
            
    def pull_accounts_csv(self, fName):
        
        entity = []
        account_names = []
        account_amount = []
        account_currency = []
        account_collection = []
        account_class = []
        account_data_type = []
        account_period = []

        for x in self._accounts_table.accounts:
            entity.append(self.name)
            account_names.append(x.account_name)
            account_amount.append(x.getAmount())
            account_currency.append(x.currency)
            account_collection.append(x.account_collection)
            account_class.append(x.account_class)
            account_data_type.append(x.account_data_type)
            account_period.append(x.account_period.period_type + str(x.account_period.period_year))
        
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

    def contains_account(self,acc_name):
        for x in self._accounts_table:
            if x.account_name == acc_name:
                return True

        return False
    
    def _create_account(self,acc_name,amt = 0,collection = ""):
        a = ShadowAccount(account_name=acc_name,amount = amt, account_period=self.period,currency=self.currency,account_collection=collection)
        return a

    def EBIT(self):
        if self.contains_account("EBIT") == False:
            a = self._create_account("EBIT")

            amount = (self._accounts_table["Sales"].getAmount()+self._accounts_table["COGS"].getAmount()+self._accounts_table["OtherIncomeThirdParty"].getAmount()
            +self._accounts_table["OtherIncomeIntercompany"].getAmount()+self._accounts_table["SGA"].getAmount()+self._accounts_table["OtherDeductions"].getAmount()
            +self._accounts_table["DividendIncome"].getAmount()+self._accounts_table["NonIncomeTaxes"].getAmount()+self._accounts_table["Depreciation"].getAmount()+self._accounts_table["Amortization"].getAmount()+self._accounts_table["InterestIncomeIntercompany"].getAmount()+self._accounts_table["InterestExpenseIntercompany"].getAmount())
            a.amount = amount

            a.account_collection = "EBIT"
            self._accounts_table.add_account(a)

    def EBIT_TI(self):
        if self.contains_account("TI_EBIT") == False:
            a = self._create_account("TI_EBIT")
            self.EBIT()
            # Apply M-1 Adjustments for Taxable Income EBIT
            self._accounts_table.apply_adjustments(acct_name="M1Adjustments",acct_colct="ForeignSchM-1Adj",adj_colct="",adj_cls="ForeignSchM-1Adj",adj_type="ForeignSchM-1Adj",pd=self.period,currency = "USD")

            amount = (self._accounts_table["EBIT"]+ self._accounts_table["M1Adjustments"].getAmount())
            a.amount = amount

            a.account_collection = "TI_EBIT"
            self._accounts_table.add_account(a)
    def sec163j(self):
        if self.contains_account("TI_EBIT") == False:
            colct = "Sec163j"
            self.EBIT_TI()

            ebit_amount = self._accounts_table["EBIT"] 

            ati = self._create_account("ATI",(ebit_amount-self._accounts_table["Depreciation"].getAmount()-self._accounts_table["Amortization"].getAmount()+self._accounts_table["M1Adjustments"].getAmount()))
            ati.account_collection = colct
            self._accounts_table.add_account(ati)

            
            
            sec163_lim_amt = -1*(min(ati.getAmount()*self.atr_tb["163jLimit_Perc"].get_value(),0)+self._accounts_table["InterestIncomeThirdParty"].getAmount())
            sec163_limitation = self._create_account("Section163jLimitation", sec163_lim_amt)
            sec163_limitation.account_collection = colct
            self._accounts_table.add_account(sec163_limitation)

            py_disallowed_amt = self._accounts_table.search_period(self.period-1)["Sec163DisallowedInterestExpense"].getAmount()
            

            int_exp_util_amt = self._accounts_table["InterestExpenseThirdParty"].getAmount() + py_disallowed_amt
            int_exp_util_amt = min(int_exp_util_amt,sec163_lim_amt)
            int_exp_util = self._create_account("InterestExpenseUtilized",int_exp_util_amt)
            int_exp_util.account_collection = colct
            
            disallowed_int_exp = self._create_account("Sec163DisallowedInterestExpense",(self._accounts_table["InterestExpenseThirdParty"].getAmount()-int_exp_util_amt))
            disallowed_int_exp.account_collection = colct
            self._accounts_table.add_account(int_exp_util)
            self._accounts_table.add_account(disallowed_int_exp)

    def calculate(self):
        self.sec163j()

    def clear_accounts(self):
        self._accounts_table = AccountsTable()

class DRE(Entity):
    def calculate(self):
        pass


# p = Period("CYE","2022", "01-01-2022", "12-31-2022")
# tb = TrialBalance(p)
# tb.generate_random_tb()
# e = Entity("Acme Corp","ME","EUR",p,"CFC",tb)

# e.pull_accounts_csv("tests//Misc//accounts.csv")