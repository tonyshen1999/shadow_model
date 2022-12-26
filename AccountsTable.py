from Trialbalance import TrialBalance
from Account import ShadowAccount, Account
from Period import Period
import copy
import random
import pandas as pd
class AccountsTable:
    def __init__(self):
        self.accounts = []
    #  def __init__(self, account_name, amount, account_period, currency="USD", sign = True, account_collection = "TBFC", account_class = "", account_data_type = "", adjustment = None):
    def default_tables(self, account_collection, period, currency = "USD"):
        acc_df = pd.read_csv("shadow_accounts.csv")
        for index, row in acc_df.iterrows():
            to_add = ShadowAccount(account_name = row['Account Types'],amount = 0.00, account_period = period, currency = currency,sign = row['Sign'],account_collection = account_collection)
            self.accounts.append(to_add)

    # Update this to be able to identify third party and intercompany from TB. This is only done this way for TESTING PURPOSES
    def pull_tb(self, tb, split_party = True):

        if isinstance(tb, TrialBalance) == False:
            raise Exception("Must import TrialBalance object")
        net_income_node = tb.find_account(tb.get_header_node(),"NetIncome")
        ppe_node = tb.find_account(tb.get_header_node(),"PPE")
        split_ratio = 0

        if split_party:
            split_ratio = random.random()
        

        for x in net_income_node[0].children:
            if x.account_name == "InterestExpense" or x.account_name == "InterestIncome" or x.account_name == "OtherIncome":
                og_amount = x.amount
                interco = copy.deepcopy(x)
                interco.account_name += "Intercompany"
                thirdp = copy.deepcopy(x)
                thirdp.account_name += "ThirdParty"
                interco.amount = round(og_amount * split_ratio)
                thirdp.amount = round(og_amount - interco.amount)
                self.accounts.append(thirdp.convert_shadow_account())
                self.accounts.append(interco.convert_shadow_account())
            elif x.account_name == "IncomeTaxExpense":
                tax = copy.deepcopy(x)
                tax.account_name = "IncomeTaxes"
                self.accounts.append(tax.convert_shadow_account())
            elif x.account_name == "OtherExpense":
                tax = copy.deepcopy(x)
                tax.account_name = "OtherDeductions"
                self.accounts.append(tax.convert_shadow_account())                
            else:
                self.accounts.append(x.convert_shadow_account())
        
        qbai = ppe_node[0]
        qbai.account_name = "QBAI"
        self.accounts.append(qbai.convert_shadow_account())

    def __str__(self):

        to_return = "Name,\tCollection,\tCurrency,\tClass,\tAmount,\tPeriod\n"

        for x in self.accounts:
            to_return += x.__str__() + "\n"

        return to_return


    def add_account(self, account):
        if isinstance(account, ShadowAccount):
            self.accounts.append(account)
        else:
            raise Exception("Added wrong account type")
    def get_accounts(self):
        return self.accounts

    def find_account(self,account):

        if isinstance(account, str):
            for x in self.accounts:
                if x.account_name == account:
                    return x
        return None
p = Period("CYE","2022", "01-01-2022", "12-31-2022")
tb = TrialBalance(p)
tb.generate_random_tb()

at = AccountsTable()
at.pull_tb(tb)
print(at)