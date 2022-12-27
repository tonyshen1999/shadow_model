from Trialbalance import TrialBalance
from Account import ShadowAccount, Account
from Period import Period
import copy
import random
import pandas as pd
class AccountsTable:
    def __init__(self):
        self.accounts = []
    
    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < len(self.accounts):
            self.n += 1
            return self.accounts[self.n-1]
        else:
            raise StopIteration

    def import_tables(self, account_collection, period, fName = "shadow_accounts.csv", currency = "USD"):
        acc_df = pd.read_csv(fName)
        for index, row in acc_df.iterrows():
            to_add = ShadowAccount(account_name = row['Account Types'],amount = 0.00, account_period = period, currency = currency,sign = row['Sign'],account_collection = account_collection)
            self.accounts.append(to_add)

    def export(self, fName):
        account_names = []
        account_amount = []
        account_currency = []
        account_collection = []
        account_class = []
        account_data_type = []
        account_period = []

        for x in self.accounts:
           
            account_names.append(x.account_name)
            account_amount.append(x.getAmount())
            account_currency.append(x.currency)
            account_collection.append(x.account_collection)
            account_class.append(x.account_class)
            account_data_type.append(x.account_data_type)
            account_period.append(x.account_period.period_type + x.account_period.period_year)
        
        accounts_dict = {
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
       
        self.accounts.append(account)
       
    def get_accounts(self):
        return self.accounts

    def find_account(self,account):

        if isinstance(account, str):
            for x in self.accounts:
                if x.account_name == account:
                    return x
        return None
# p = Period("CYE","2022", "01-01-2022", "12-31-2022")
# tb = TrialBalance(p)
# tb.generate_random_tb()

# at = AccountsTable()
# at.pull_tb(tb)
# print(at)