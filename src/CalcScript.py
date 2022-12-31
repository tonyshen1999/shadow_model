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

        self.atr_tb = atr_tb

        if self.atr_tb == None:
            self.atr_tb = AttributesTable(self.period)

        

        self.calculate()
    def __validation(self):
        return True
    def calculate(self):
        pass
    
    def _create_account(self,acc_name,amt = 0,collection = ""):
        a = ShadowAccount(account_name=acc_name,amount = amt, account_period=self.period,currency=self.entity.currency,account_collection=collection)
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

            amount = (self.accounts_tbl["Sales"].getAmount()+self.accounts_tbl["COGS"].getAmount()+self.accounts_tbl["OtherIncomeThirdParty"].getAmount()
            +self.accounts_tbl["OtherIncomeIntercompany"].getAmount()+self.accounts_tbl["SGA"].getAmount()+self.accounts_tbl["OtherDeductions"].getAmount()
            +self.accounts_tbl["DividendIncome"].getAmount()+self.accounts_tbl["NonIncomeTaxes"].getAmount())
            a.amount = amount

            a.account_collection = "EBIT"
            self.accounts_tbl.add_account(a)


class TI_EBIT(Calculation):
    def calculate(self):
        if self.contains("TI_EBIT") == False:
            a = self._create_account("TI_EBIT")
            EBIT(period=self.period,entity=self.entity)
            # Apply M-1 Adjustments for Taxable Income EBIT
            self.accounts_tbl.apply_adjustments(acct_name="M1Adjustments",acct_colct="ForeignSchM-1Adj",adj_colct="",adj_cls="ForeignSchM-1Adj",adj_type="ForeignSchM-1Adj",pd=self.period,currency = "USD")

            amount = (self.accounts_tbl["EBIT"]+ self.accounts_tbl["M1Adjustments"].getAmount())
            a.amount = amount

            a.account_collection = "TI_EBIT"
            self.accounts_tbl.add_account(a)


class Sec163j(Calculation):

    def calculate(self):
        if self.contains("TI_EBIT") == False:
            colct = "Sec163j"
            TI_EBIT(self.period,self.entity)
            ebit_amount = self.accounts_tbl["EBIT"] 

            ati = self._create_account("ATI",(ebit_amount-self.accounts_tbl["Depreciation"].getAmount()-self.accounts_tbl["Amortization"].getAmount()+self.accounts_tbl["M1Adjustments"].getAmount()))
            ati.account_collection = colct
            self.accounts_tbl.add_account(ati)

            sec163_lim_amt = 0
            if ati.getAmount() < 0:
                sec163_lim_amt = ati.getAmount()*self.atr_tb["163jLimit_Perc"].get_value()+self.accounts_tbl["InterestIncomeThirdParty"].getAmount()
                sec163_lim_amt *= -1
            sec163_limitation = self._create_account("Section163jLimitation", sec163_lim_amt)
            sec163_limitation.account_collection = colct
            self.accounts_tbl.add_account(sec163_limitation)

            py_disallowed_amt = self.accounts_tbl.search_period(self.period-1)["Sec163DisallowedInterestExpense"].getAmount()
            

            int_exp_util_amt = self.accounts_tbl["InterestExpenseThirdParty"].getAmount() + py_disallowed_amt
            int_exp_util_amt = min(int_exp_util_amt,sec163_lim_amt)
            int_exp_util = self._create_account("InterestExpenseUtilized",int_exp_util_amt)
            int_exp_util.account_collection = colct
            
            disallowed_int_exp = self._create_account("Sec163DisallowedInterestExpense",(self.accounts_tbl["InterestExpenseThirdParty"].getAmount()-int_exp_util_amt))
            disallowed_int_exp.account_collection = colct
            self.accounts_tbl.add_account(int_exp_util)
            self.accounts_tbl.add_account(disallowed_int_exp)

class CFCTestedIncome(Calculation):
    def __validation(self):
        if self.entity.type == "CFC":
            return True

    def calculate(self):
        if self.contains("TentativeTestedIncome") == False and self.__validation() == True:
            Sec163j(self.period,self.entity)
            tent_tested_income_amt = self.accounts_tbl["TI_EBIT"].getAmount()+self.accounts_tbl["InterestExpenseUtilized"].getAmount()
            +self.accounts_tbl["InterestExpenseIntercompany"].getAmount()+self.accounts_tbl["InterestIncomeThirdParty"].getAmount()
            +self.accounts_tbl["InterestIncomeIntercompany"].getAmount()-self.accounts_tbl["SubpartF_Income"].getAmount()

            tent_tested_income = self._create_account("TentativeTestedIncome",tent_tested_income_amt)
            colct = "TestedIncome"
            tent_tested_income.account_collection=colct
            self.accounts_tbl.add_account(tent_tested_income)

            tested_income_etr_amt = self.accounts_tbl["IncomeTaxes"]/tent_tested_income_amt
            hte = self.atr_tb["Section951AHighTaxElection"].atr_value
            tested_income = self._create_account("TestedIncome",0)
            tested_loss = self._create_account("TestedLoss",0)
            tested_income.account_collection = colct
            tested_loss.account_collection = colct
            print(tested_income_etr_amt)
            if hte == False or (tested_income_etr_amt*-1) < (self.atr_tb["HTETaxPercentage"].get_value()*self.atr_tb["USTaxRate"].get_value()):
                if tent_tested_income_amt > 0:
                    tested_loss.amount = tent_tested_income_amt
                    tested_income.amount = 0
                else:
                    tested_income.amount = tent_tested_income_amt
                    tested_loss.amount = 0
            self.accounts_tbl.add_account(tested_income)
            self.accounts_tbl.add_account(tested_loss)
            
            self.accounts_tbl.add_account(self._create_account("TestedIncome_ETR",tested_income_etr_amt*-1))

class USSH951AInclusion(Calculation):
    def __validation(self):
        if self.entity.type == "USSH":
            return True
    def calculate(self):
        cfcs = self.entity.children
        cfc_atr = AttributesTable(p,"CFCAttributes.csv")
        ussh_atr = AttributesTable(p)
        
        for x in cfcs:
            CFCTestedIncome(self.period,x,cfc_atr)

            




p = Period("CYE",2022, "01-01-2022", "12-31-2022")
t = TrialBalance(p)
t.generate_random_tb()
a = AccountsTable()
a.pull_tb(t)
a.generate_random_adjustments(["OtherDeductions"])
a.print_adj()
a.export_adjustments("test_adj.csv")
e = Entity(name = "Foo", country = "Canada",currency = "CA",period = p,entity_type="CFC",accounts_table=a)
# e.pull_accounts_csv("testing_ties.csv")
# print(e.get_accounts_table())
atr = AttributesTable(p,"CFCAttributes.csv")
c = CFCTestedIncome(p,e,atr)
# c.calculate()
# print("-------------------")
print(e.get_accounts_table())
e.pull_accounts_csv("tests//Misc//163jCalc.csv")