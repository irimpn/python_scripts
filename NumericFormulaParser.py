__author__ = 'Navin'

import re
import string

class NumericFormulaParser(object):

    def decomposeVariables(self,operand):
        varList=[]
        chars = re.escape(string.punctuation)
        variables= re.sub(r'['+chars+']', '|',operand).split("|")
        for everyVar in variables:
            regex= re.compile(r'\d*')
            match=regex.search(everyVar)
            if everyVar and not match.group():
                varList.append(everyVar)
        return varList

    def calculateOutputValue(self,numerator, denominator, counterData):
        numervalues=self.decomposeVariables(numerator)
        denomvalues=self.decomposeVariables(denominator)
        for numer in numervalues:
            numerator = str(numerator).replace(numer,counterData[numer])
        for denom in denomvalues:
            denominator= str(denominator).replace(denom,counterData[denom])
        value = self.calcDivision( numerator,denominator)
        return value

    def calcDivision(self, numerator, denominator):
        calcnumerator = format(float(eval(numerator)), '.2f')
        calcdenominator = format(float(eval(denominator)), '.2f')
        value = format((float(calcnumerator) / float(calcdenominator)), '.2f')
        return value



