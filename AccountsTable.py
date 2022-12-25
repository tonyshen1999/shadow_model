from Trialbalance import TrialBalance
from Account import ShadowAccount, Account
from Period import Period

class AccountsTable:
    def __init__(self):
        self.__accounts = []

    def pull_tb(self, tb):

        if isinstance(tb, TrialBalance) == False:
            raise Exception("Must import TrialBalance object")
        net_income_node = tb.find_account(tb.get_header_node(),"NetIncome")
        ppe_node = tb.find_account(tb.get_header_node(),"PPE")

        for x in net_income_node[0].children:
            self.__accounts.append(x.convert_shadow_account())
        self.__accounts.append(ppe_node.convert_shadow_account())

    def __str__(self):

        to_return = ""

        for x in self.__accounts:
            to_return += x.__str__

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