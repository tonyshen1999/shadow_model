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
        self.ownership = entity.percent_owned
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
            +self.accounts_tbl["DividendIncome"].getAmount()+self.accounts_tbl["NonIncomeTaxes"].getAmount()+self.accounts_tbl["Depreciation"].getAmount()+self.accounts_tbl["Amortization"].getAmount()+self.accounts_tbl["InterestIncomeIntercompany"].getAmount()+self.accounts_tbl["InterestExpenseIntercompany"].getAmount())
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
    def __init__(self, period, entity, atr_tb = None,sec163j = True):
        self.period = period
        self.entity = entity
        self.accounts_tbl = self.entity.get_accounts_table()

        self.atr_tb = atr_tb
        self.sec163j_calc = sec163j
        
        if self.atr_tb == None:
            self.atr_tb = AttributesTable(self.period)
        self.ownership = self.entity.percent_owned
        self.calculate()
    def __validation(self):
        if self.entity.type == "CFC":
            return True
        return False
    def calculate(self):
        if self.contains("TentativeTestedIncomeBeforeTaxes") == False and self.__validation() == True:
            if self.sec163j_calc == True:
                # print("get calc")
                Sec163j(self.period,self.entity)
            tent_tested_income_amt = self.accounts_tbl["TI_EBIT"].getAmount()+self.accounts_tbl["InterestExpenseUtilized"].getAmount()+self.accounts_tbl["InterestIncomeThirdParty"].getAmount()-self.accounts_tbl["SubpartF_Income"].getAmount()

            tent_tested_income = self._create_account("TentativeTestedIncomeBeforeTaxes",tent_tested_income_amt)
            colct = "TestedIncome"
            tent_tested_income.account_collection=colct
            self.accounts_tbl.add_account(tent_tested_income)

            tested_income_etr_amt = self.accounts_tbl["IncomeTaxes"]/tent_tested_income_amt
            hte = self.atr_tb["Section951AHighTaxElection"].atr_value
            tested_income = self._create_account("TestedIncome",0)
            tested_loss = self._create_account("TestedLoss",0)
            tested_income.account_collection = colct
            tested_loss.account_collection = colct

            hte_met = (tested_income_etr_amt*-1) > (self.atr_tb["HTETaxPercentage"].get_value()*self.atr_tb["USTaxRate"].get_value())
            # print(tested_income_etr_amt)

            if hte == False or hte_met == False:
                if tent_tested_income_amt > 0:
                    tested_loss.amount = tent_tested_income_amt
                    tested_income.amount = 0
                else:
                    tested_income.amount = tent_tested_income_amt
                    tested_loss.amount = 0
            self.accounts_tbl.add_account(tested_income)
            self.accounts_tbl.add_account(tested_loss)

            pro_rata_tested_income = self._create_account("ProRataTestedIncome",tested_income.getAmount() * self.ownership)
            pro_rata_tested_loss = self._create_account("ProRataTestedLoss",tested_loss.getAmount() * self.ownership)

            pro_rata_tested_income.account_collection=colct
            pro_rata_tested_loss.account_collection=colct

            self.accounts_tbl.add_account(pro_rata_tested_income)
            self.accounts_tbl.add_account(pro_rata_tested_loss)


            qbai_amount = 0
            if tested_income.getAmount() <0 and hte_met == False:
                qbai_amount = self.accounts_tbl["QBAI"].getAmount()
            pro_rata_qbai = self._create_account("ProRataQBAI",qbai_amount*self.ownership)
            pro_rata_qbai.account_collection=colct
            self.accounts_tbl.add_account(pro_rata_qbai)
            

            tested_loss_qbai_amt = 0
            if tested_loss.getAmount()>0:
                tested_loss_qbai_amt = self.accounts_tbl["QBAI"].getAmount()*self.ownership*self.atr_tb["TestedLossQBAIAmount"].get_value()
            tested_loss_qbai = self._create_account("TestedLossQBAI",tested_loss_qbai_amt)
            tested_loss_qbai.account_collection=colct

            self.accounts_tbl.add_account(tested_loss_qbai)
            
            etr = self._create_account("TestedIncome_ETR",tested_income_etr_amt*-1)
            etr.account_collection = colct
            self.accounts_tbl.add_account(etr)

            tested_interest_expense_amt = self.accounts_tbl["InterestExpenseUtilized"].getAmount()
            tested_interest_income_amt = self.accounts_tbl["InterestIncomeThirdParty"].getAmount()
            # print(hte_met)
            if hte_met == True:
                
                tested_interest_expense_amt = 0
                tested_interest_income_amt = 0

            tested_interest_expense_amt = max(tested_interest_expense_amt-tested_loss_qbai_amt,0)*self.ownership

            tested_interest_income = self._create_account("TestedInterestIncome",tested_interest_income_amt)
            tested_interest_expense = self._create_account("TestedInterestExpense",tested_interest_expense_amt)

            tested_interest_income.account_collection=colct
            tested_interest_expense.account_collection=colct

            self.accounts_tbl.add_account(tested_interest_expense)
            self.accounts_tbl.add_account(tested_interest_income)

            tested_income_taxes_amt = self.accounts_tbl["IncomeTaxes"].getAmount()*self.ownership
            
            if hte_met:
                tested_income_taxes_amt = 0
            
            tested_income_taxes = self._create_account("TestedIncomeTaxes",tested_income_taxes_amt)
            tested_income_taxes.account_collection = colct

            self.accounts_tbl.add_account(tested_income_taxes)

            
            

            

class USSH951AInclusion(Calculation):
    def __validation(self):
        if self.entity.type == "USSH":
            return True
        return False
    def calculate(self):
        if self.__validation():
            cfcs = self.entity.children
            cfc_atr = AttributesTable(self.period,"CFCAttributes.csv")
            # ussh_atr = AttributesTable(self.period)
            agg_cfc_tested_income_amt = 0
            agg_cfc_tested_loss_amt = 0
            qbai_amt = 0
            agg_tested_interest_inc_amt = 0
            agg_tested_interest_exp_amt = 0
            agg_tested_income_tax_amt = 0
            qbai_perc = cfc_atr["QBAIPerc"].get_value()
            colct = "USSH951A"
            for x in cfcs:
                CFCTestedIncome(self.period,x,cfc_atr)
                cfc_acc_tbl = x.get_accounts_table()
                agg_cfc_tested_income_amt += cfc_acc_tbl["ProRataTestedIncome"].getAmount()
                agg_cfc_tested_loss_amt += cfc_acc_tbl["ProRataTestedLoss"].getAmount()
                net_cfc_tested_income_amt = agg_cfc_tested_income_amt+agg_cfc_tested_loss_amt
                qbai_amt += cfc_acc_tbl["ProRataQBAI"].getAmount()
                agg_tested_interest_inc_amt += cfc_acc_tbl["TestedInterestIncome"].getAmount()
                agg_tested_interest_exp_amt += cfc_acc_tbl["TestedInterestExpense"].getAmount()
                agg_tested_income_tax_amt += cfc_acc_tbl["TestedIncomeTaxes"].getAmount()
            

            agg_cfc_tested_income = self._create_account("AggregateCFCTestedIncome",agg_cfc_tested_income_amt)
            agg_cfc_tested_loss = self._create_account("AggregateCFCTestedLoss",agg_cfc_tested_loss_amt)
            net_cfc_tested_income = self._create_account("NetCFCTestedIncome",net_cfc_tested_income_amt)
            qbai = self._create_account("AggregateQBAI",qbai_amt)
            agg_tested_interest_inc = self._create_account("AggregateTestedInterestIncome",agg_tested_interest_inc_amt)
            agg_tested_interest_exp = self._create_account("AggregateTestedInterestExpnese",agg_tested_interest_exp_amt)
            agg_tested_income_tax = self._create_account("AggregateTestedIncomeTax",agg_tested_income_tax_amt)



            specified_interest_exp_amt = max(agg_tested_interest_inc+agg_tested_interest_exp,0)
            dtir = max((qbai*qbai_perc)-specified_interest_exp_amt,0)
            gilti_amt = (-1*net_cfc_tested_income_amt)-dtir
            gilti = self._create_account("GILTI",gilti_amt)
            specified_interest_exp = self._create_account("SpecifiedInterestExpense",specified_interest_exp_amt)

            inclusion_perc = self._create_account("GILTIInclusionPercentage",(gilti_amt/net_cfc_tested_income_amt))
            sec78grossup = self._create_account("Sec78GrossUpOnGILTI",((gilti_amt/net_cfc_tested_income_amt)*agg_tested_income_tax_amt))


            agg_cfc_tested_income.account_collection = colct
            agg_cfc_tested_loss.account_collection = colct
            net_cfc_tested_income.account_collection = colct
            qbai.account_collection = colct
            agg_tested_interest_inc.account_collection = colct
            agg_tested_interest_exp.account_collection = colct
            agg_tested_income_tax.account_collection = colct
            inclusion_perc.account_collection = colct
            sec78grossup.account_collection = colct
            gilti.account_collection = colct
            specified_interest_exp.account_collection = colct

            self.accounts_tbl.add_account(agg_cfc_tested_income)
            self.accounts_tbl.add_account(agg_cfc_tested_loss)
            self.accounts_tbl.add_account(qbai)
            self.accounts_tbl.add_account(net_cfc_tested_income)
            self.accounts_tbl.add_account(agg_tested_interest_inc)
            self.accounts_tbl.add_account(agg_tested_interest_exp)
            self.accounts_tbl.add_account(agg_tested_income_tax)
            self.accounts_tbl.add_account(inclusion_perc)
            self.accounts_tbl.add_account(sec78grossup)
            self.accounts_tbl.add_account(gilti)
            self.accounts_tbl.add_account(specified_interest_exp)

# p = Period("CYE",2022, "01-01-2022", "12-31-2022")
# t = TrialBalance(p)
# t.generate_random_tb()
# a = AccountsTable()
# a.pull_tb(t)
# a.generate_random_adjustments(["OtherDeductions"])
# a.print_adj()
# a.export_adjustments("test_adj.csv")
# e = Entity(name = "Foo", country = "Canada",currency = "CA",period = p,entity_type="CFC",accounts_table=a)
# # e.pull_accounts_csv("testing_ties.csv")
# # print(e.get_accounts_table())
# atr = AttributesTable(p,"CFCAttributes.csv")
# c = CFCTestedIncome(p,e,atr)
# # c.calculate()
# # print("-------------------")
# print(e.get_accounts_table())
# e.pull_accounts_csv("tests//Misc//163jCalc.csv")