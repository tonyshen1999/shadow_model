from Trialbalance import TrialBalance
from Account import ShadowAccount, Account
from Period import Period
import copy
import random
import pandas as pd
import random as random
from Adjustment import Adjustment

class AccountsTable:

    def __init__(self,period):
        self.accounts = []

        if isinstance(period,Period):
            self.period = period
        else:
            raise Exception(period.__str__() + " must be type Period")
        

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
        df = self.get_accounts_df()
        df.to_csv(fName)

    def __len__(self):
        return len(self.accounts)

    def __getitem__(self,key):

        if isinstance(key,Account):
            key = key.account_name
        elif isinstance(key,str):
            acc_tbl = AccountsTable(self.period)

            for x in self.accounts:
                if x.account_name == key:
                    acc_tbl.add_account(x)
            if len(acc_tbl) == 1:
                return acc_tbl.accounts[0]
            elif len(acc_tbl) == 0:
                print("*****WARNING*****: " + key + " wasn't found!")
                return Account(account_name=key,amount=0,account_period=self.period)
            return acc_tbl
        else:
            raise Exception(key.__str__() + "must be either Account or string type")
            return AccountsTable(self.period)
    
    '''
    Only used for testing purposes, remove in production
    '''
    def force163j(self):
        self.__getitem__("InterestExpenseThirdParty").amount *= 100
       
    '''
    Only used for testing purposes, remove in production
    '''
    def convert_loss(self):
        for x in self.accounts:
            if x.account_name == "Sales":
                x.amount = 0
            elif x.account_name == "OtherIncomeThirdParty":
                x.amount = 0
            elif x.account_name == "OtherIncomeIntercompany":
                x.amount = 0
            elif x.account_name == "InterestIncomeIntercompany":
                x.amount = 0
            elif x.account_name == "IncomeTaxes":
                x.amount = 0
            elif x.account_name == "InterestIncomeThirdParty":
                x.amount *= .25
    
    '''
    Only used for testing purposes, remove in production
    '''    
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
    
    '''
    Returns number of adjustments with amounts greater than 0
    '''
    def num_active_adjustments(self):
        num_adj = 0;
        for x in self.accounts:
            num_adj += len(x.adjustments)
        return num_adj
        
    '''
    Returns number of accounts
    '''
    def num_active_accounts(self):
        num = 0
        for x in self.accounts:
            if x.amount != 0:
                num+=1
            
        return num

    def add_account(self, account):
        if isinstance(account,Account):
            self.accounts.append(account)
        else:
            raise Exception(account.__str__() + " must be Account type object")
       
    def get_accounts(self):
        return self.accounts

    def find_account(self,account):

        if isinstance(account, str):
            for x in self.accounts:
                if x.account_name == account:
                    return x
        return None
    
    def search_collection(self, colct):

        acc_tbl = AccountsTable(self.period)
        for x in self.accounts:
            if x.account_collection == colct:
                acc_tbl.add_account(x)
        return acc_tbl
    
    ## THIS IS DOING THE SAME THING AS PULL ACCOUNTS BY PERIOD
    def search_period(self, pd):
        acc_tbl = AccountsTable(self.period)
        for x in self.accounts:
            if x.account_period == pd:
                acc_tbl.add_account(x)
        return acc_tbl
    #get_adjustment_amount(self,colct,adj_cls,adj_type,pd)
    def apply_adjustments(self,acct_name, acct_colct,adj_colct,adj_cls,adj_type,pd,currency = "USD"):
        
        if self.find_account(acct_name)==None:
            amount = 0
            for x in self.accounts:
                amount += x.get_adjustment_amount(colct=adj_colct,adj_cls=adj_cls,adj_type=adj_type,pd=pd)
            # print("adj amount")
            # print(amount)

            a = ShadowAccount(account_name=acct_name,amount=amount,account_period=pd,currency=currency,account_collection=acct_colct)
            self.accounts.append(a)

    def print_adj(self):
        to_return = "Account Name,\tType,\tCollection\t,Class\t,Amount,\tCurrency,\tPercentage,\tPeriod\n"
        for x in self.accounts:
            # print(x)
            for y in x.adjustments:
                to_return += x.account_name+",\t"+y.adj_type+",\t"+y.adj_collection+",\t"+y.adj_class+",\t"+str(y.adj_amount)+",\t"+y.currency+",\t"+str(y.adj_perc)+",\t"+y.adj_period.get_pd()+"\n"
        # print(to_return)
        return to_return
    
    def append_adj(self,account,adj_amount,adj_type,adj_perc,adj_class,adj_collection,adj_period,adj_currency):
        adj = Adjustment(adj_amount=adj_amount,adj_type = adj_type,adj_class=adj_class,adj_collection=adj_collection,adj_period=adj_period,currency=adj_currency)
        account.adjustments.append(adj)

    def get_accounts_df(self):

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
            account_period.append(x.account_period.period_type + str(x.account_period.period_year))
        
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

        return df

    # USE FOR TESTING ONLY
    def generate_random_adjustments(self,acct_names):
        sign = bool(random.getrandbits(1))
        for x in acct_names:
            # print(x)

            
            acct = self.find_account(x)
            amt = acct.amount*random.random()
            if sign == True:
                amt *= -1
            # print(acct)
            self.append_adj(account=acct,adj_currency=acct.currency,adj_amount=amt,adj_type = "ForeignSchM-1Adj",adj_perc=0,adj_class="ForeignSchM-1Adj",adj_collection="",adj_period=acct.account_period)
    def get_adjustments_df(self):
        acct_names = []
        types = []
        colcts = []
        classes = []
        amts = []
        percs = []
        pds = []
        currency = []
        for x in self.accounts:
            for y in x.adjustments:
                acct_names.append(x.account_name)
                types.append(y.adj_type)
                colcts.append(y.adj_collection)
                classes.append(y.adj_class)
                amts.append(y.adj_amount)
                percs.append(y.adj_perc)
                pds.append(y.adj_period.get_pd())
                currency.append(y.currency)
        adj_set = {
            "Account Name":acct_names,
            "Adjustment Type":types,
            "Adjustment Collection":colcts,
            "Adjustment Class":classes,
            "Adjustment Amount":amts,
            "ISO Currency Code":currency,
            "Adjustment Period":pds,
            "Adjustment Percentage":percs
        }

        adj_df = pd.DataFrame(adj_set)

        return adj_df
    def export_adjustments(self, fName):
        
        adj_df = self.get_adjustments_df()
        adj_df.to_csv(fName)
    
    def import_adjustments_df(self,df):
        for index, row in df.iterrows():
            acc = self.__getitem__(key=row["Account Name"])
            adj = Adjustment(adj_amount=float(row["Adjustment Amount"]),adj_class=str(row["Adjustment Class"]),adj_collection=str(row["Adjustment Collection"]), adj_period=acc.account_period,adj_type=str(row["Adjustment Type"]),adj_perc=float(row["Adjustment Percentage"]),currency=str(row["ISO Currency Code"]))
            # print(adj.adj_class)
            acc.adjustments.append(adj)

    # modify this file for later
    def import_adjustments(self, fName):

        
        adj_df = pd.read_csv(fName)
        
        self.import_adjustments_df(adj_df)

    def import_accounts(self, fName):
        acc_df = pd.read_csv(fName)
        print(acc_df)
        for index, row in acc_df.iterrows():
            acc = ShadowAccount(account_name=row["Account Name"],amount=float(row["Amount"]),account_period=Period(period_type="",period_year=row["Period"]),currency=str(row["ISO Currency Code"]),account_collection=str(row["Collection"]),account_class=str(row["Class"]),account_data_type=str(row["Data Type"]))
            self.accounts.append(acc)
