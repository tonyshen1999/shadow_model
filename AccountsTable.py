from Trialbalance import TrialBalance
from Account import ShadowAccount, Account
from Period import Period
import copy
import random
class AccountsTable:
    def __init__(self):
        self.__accounts = []

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
                interco.account_name += "(Intercompany)"
                thirdp = copy.deepcopy(x)
                thirdp.account_name += "(ThirdParty)"
                interco.amount = round(og_amount * split_ratio)
                thirdp.amount = round(og_amount - interco.amount)
                self.__accounts.append(thirdp.convert_shadow_account())
                self.__accounts.append(interco.convert_shadow_account())
            elif x.account_name == "IncomeTaxExpense":
                tax = copy.deepcopy(x)
                tax.account_name = "IncomeTaxes"
                self.__accounts.append(tax.convert_shadow_account())
            elif x.account_name == "OtherExpense":
                tax = copy.deepcopy(x)
                tax.account_name = "OtherDeductions"
                self.__accounts.append(tax.convert_shadow_account())                
            else:
                self.__accounts.append(x.convert_shadow_account())
        
        qbai = ppe_node[0]
        qbai.account_name = "QBAI"
        self.__accounts.append(qbai.convert_shadow_account())

    def __str__(self):

        to_return = "Name,\tCollection,\tCurrency,\tClass,\tAmount,\tPeriod\n"

        for x in self.__accounts:
            to_return += x.__str__() + "\n"

        return to_return


    def add_account(self, account):
        if isinstance(account, ShadowAccount):
            self.__accounts.append(account)
        else:
            raise Exception("Added wrong account type")
    def get_accounts(self):
        return self.__accounts


p = Period("CYE","2022", "01-01-2022", "12-31-2022")
tb = TrialBalance(p)
tb.generate_random_tb()

at = AccountsTable()
at.pull_tb(tb)
print(at)