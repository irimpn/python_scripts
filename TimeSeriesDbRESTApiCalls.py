__author__ = 'Navin'

import requests
import string
from DateUtils import *

dateData = {}

wrapperDateData = {}
dateutil  = DateUtils()

class TimeSeriesDbRESTAPICalls:


    def timeSeriesDBDataGather(self,query):
        response = requests.get(query)
        wrappedDate = None
        if (response.status_code == 200 and response.text != '[]'):
            if response.content.split("dps"):
                interStr = string.replace(string.replace(response.content.split("dps")[1], ":{\"", ""), "}}]", "")
            splitList = interStr.split(",")

            for resSplit in splitList:
                val = resSplit.split(":")
                dateData[string.replace(val[0], '\"', '')] = val[1]
                if(wrappedDate == dateutil.convertTimeStampToDate(string.replace(val[0], '\"', '') , '')) :
                    continue
                else:
                    if(wrappedDate != None):
                        wrapperDateData[wrappedDate]=dateData
                        wrappedDate = dateutil.convertTimeStampToDate(string.replace(val[0], '\"', '') , '')
            return dateData


    def timeSeriesDBDataGatherWithAgg(self,query):
        wrapperDateData = self.timeSeriesDBDataGather(query)
        return wrapperDateData
