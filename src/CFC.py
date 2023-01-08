from Account import Account, ShadowAccount
from Trialbalance import TrialBalance
from Period import Period
from AccountsTable import AccountsTable
import pandas as pd
import copy
import itertools
from Attributes import AttributesTable,Attribute
from Entity import Entity

class CFC(Entity):
    def __init__(self, name,country, currency, period, entity_type="", tb = None, accounts_table = None,atr_tb = None):
        atr = AttributesTable(period,"CFCAttributes.csv")
        super().__init__(name=name,country=country, currency=currency, period=period, entity_type="CFC", tb=tb, accounts_table=accounts_table,atr_tb = atr)
    def calculate(self):
        self.CFCTestedIncome()

    def CFCTestedIncome(self):
        if self.contains_account("TentativeTestedIncomeBeforeTaxes") == False:
            self.sec163j()
            tent_tested_income_amt = self._accounts_table["TI_EBIT"].getAmount()+self._accounts_table["InterestExpenseUtilized"].getAmount()+self._accounts_table["InterestIncomeThirdParty"].getAmount()-self._accounts_table["SubpartF_Income"].getAmount()

            tent_tested_income = self._create_account("TentativeTestedIncomeBeforeTaxes",tent_tested_income_amt)
            colct = "TestedIncome"
            tent_tested_income.account_collection=colct
            self._accounts_table.add_account(tent_tested_income)

            tested_income_etr_amt = self._accounts_table["IncomeTaxes"]/tent_tested_income_amt
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
            self._accounts_table.add_account(tested_income)
            self._accounts_table.add_account(tested_loss)

            # pro_rata_tested_income = self._create_account("ProRataTestedIncome",tested_income.getAmount() * self.ownership)
            # pro_rata_tested_loss = self._create_account("ProRataTestedLoss",tested_loss.getAmount() * self.ownership)

            # pro_rata_tested_income.account_collection=colct
            # pro_rata_tested_loss.account_collection=colct

            # self.accounts_tbl.add_account(pro_rata_tested_income)
            # self.accounts_tbl.add_account(pro_rata_tested_loss)


            qbai_amount = 0
            if tested_income.getAmount() <0 and hte_met == False:
                qbai_amount = self._accounts_table["QBAI"].getAmount()
            tested_income_qbai = self._create_account("TestedIncomeQBAI",qbai_amount)
            tested_income_qbai.account_collection=colct
            self._accounts_table.add_account(tested_income_qbai)
            

            tested_loss_qbai_amt = 0
            if tested_loss.getAmount()>0:
                tested_loss_qbai_amt = self._accounts_table["QBAI"].getAmount()*self.atr_tb["TestedLossQBAIAmount"].get_value()
            tested_loss_qbai = self._create_account("TestedLossQBAI",tested_loss_qbai_amt)
            tested_loss_qbai.account_collection=colct
            
            self._accounts_table.add_account(tested_loss_qbai)
            
            
            etr = self._create_account("TestedIncome_ETR",tested_income_etr_amt*-1)
            etr.account_collection = colct
            self._accounts_table.add_account(etr)

            tested_interest_expense_amt = self._accounts_table["InterestExpenseUtilized"].getAmount()
            tested_interest_income_amt = self._accounts_table["InterestIncomeThirdParty"].getAmount()
            # print(hte_met)
            if hte_met == True:
                
                tested_interest_expense_amt = 0
                tested_interest_income_amt = 0

            tested_interest_expense_amt = max(tested_interest_expense_amt-tested_loss_qbai_amt,0)

            tested_interest_income = self._create_account("TestedInterestIncome",tested_interest_income_amt)
            tested_interest_expense = self._create_account("TestedInterestExpense",tested_interest_expense_amt)
            
            tested_interest_income.account_collection=colct
            tested_interest_expense.account_collection=colct
            

            self._accounts_table.add_account(tested_interest_expense)
            self._accounts_table.add_account(tested_interest_income)
            
            tested_income_taxes_amt = self._accounts_table["IncomeTaxes"].getAmount()
            
            if hte_met:
                tested_income_taxes_amt = 0
            
            tested_income_taxes = self._create_account("TestedIncomeTaxes",tested_income_taxes_amt)
            tested_income_taxes.account_collection = colct

            self._accounts_table.add_account(tested_income_taxes)