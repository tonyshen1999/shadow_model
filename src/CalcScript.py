from Account import Account,ShadowAccount
from Trialbalance import TrialBalance
from Period import Period
from AccountsTable import AccountsTable
from Entity import Entity
from Attributes import Attribute,AttributesTable

class Calculation:
    def __init__(self, period, entity, atr_tb = None):
        self.period = period
        self.entity = entity
        self.accounts_tbl = self.entity.get_accounts_table()

        self.calculate()
    def calculate(self):
        pass
    
    def _create_account(self,acc_name,amt = 0):
        a = ShadowAccount(account_name=acc_name,amount = amt, account_period=self.period,currency=self.entity.currency)
        return a
    
    def __getitem__(self,key):
        return self.accounts_tbl[key]

    def contains(self,acc_name):
        for x in self.accounts_tbl:
            if x.account_name == acc_name:
                return True

        return False

class EBIT(Calculation):
    def calculate(self):
        if self.contains("EBIT") == False:
            a = self._create_account("EBIT")
            amount = (self.accounts_tbl["Sales"].amount+self.accounts_tbl["COGS"].amount+self.accounts_tbl["OtherIncomeThirdParty"].amount
            +self.accounts_tbl["OtherIncomeIntercompany"].amount+self.accounts_tbl["SGA"].amount+self.accounts_tbl["OtherDeductions"].amount
            +self.accounts_tbl["DividendIncome"].amount)
            a.amount = amount
            self.accounts_tbl.add_account(a)


class Sec163j(Calculation):

    def calculate(self):
        if self.contains("EBIT") == False:
            ebit_calc = EBIT(self.period,self.entity)
            ebit_amount = ebit_calc["EBIT"] 

            ati = self._create_account("ATI",(ebit_amount-self.accounts_tbl["Deprecation"].amount-self.accounts_tbl["Amortization"].amount))
            self.accounts_tbl.add_account(ati)
            print(ati)

p = Period("CYE","2022", "01-01-2022", "12-31-2022")
t = TrialBalance(p)
t.generate_random_tb()
a = AccountsTable()
a.pull_tb(t)

e = Entity(name = "Foo", country = "Canada",currency = "CA",period = p,entity_type="CFC",accounts_table=a)
e.pull_accounts_csv("testing_ties.csv")
print(e.get_accounts_table())
c = Sec163j(p,e)
c.calculate()
print("-------------------")
print(e.get_accounts_table())