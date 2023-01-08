from Account import Account, ShadowAccount
from Trialbalance import TrialBalance
from Period import Period
from AccountsTable import AccountsTable
import pandas as pd
import copy
import itertools
from Attributes import AttributesTable,Attribute
from Entity import Entity

class USSH(Entity):
    def calculate(self):
        self.USSH951A()
    def USSH951A(self):
        cfcs = self.children
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
        for x in cfcs.keys():
            x.calculate()
            cfc_acc_tbl = x.get_accounts_table()
            agg_cfc_tested_income_amt += cfc_acc_tbl["TestedIncome"].getAmount()*cfcs[x]
            agg_cfc_tested_loss_amt += cfc_acc_tbl["TestedLoss"].getAmount()*cfcs[x]
            net_cfc_tested_income_amt = agg_cfc_tested_income_amt+agg_cfc_tested_loss_amt
            qbai_amt += cfc_acc_tbl["TestedIncomeQBAI"].getAmount()*cfcs[x]
            agg_tested_interest_inc_amt += cfc_acc_tbl["TestedInterestIncome"].getAmount()*cfcs[x]
            agg_tested_interest_exp_amt += cfc_acc_tbl["TestedInterestExpense"].getAmount()*cfcs[x]
            agg_tested_income_tax_amt += cfc_acc_tbl["TestedIncomeTaxes"].getAmount()*cfcs[x]
        

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

        inclusion_perc = self._create_account("GILTIInclusionPercentage",(gilti_amt/agg_cfc_tested_income_amt))
        sec78grossup = self._create_account("Sec78GrossUpOnGILTI",((gilti_amt/agg_cfc_tested_income_amt)*agg_tested_income_tax_amt))


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

        self._accounts_table.add_account(agg_cfc_tested_income)
        self._accounts_table.add_account(agg_cfc_tested_loss)
        self._accounts_table.add_account(qbai)
        self._accounts_table.add_account(net_cfc_tested_income)
        self._accounts_table.add_account(agg_tested_interest_inc)
        self._accounts_table.add_account(agg_tested_interest_exp)
        self._accounts_table.add_account(agg_tested_income_tax)
        self._accounts_table.add_account(inclusion_perc)
        self._accounts_table.add_account(sec78grossup)
        self._accounts_table.add_account(gilti)
        self._accounts_table.add_account(specified_interest_exp)