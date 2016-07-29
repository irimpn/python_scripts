__author__ = 'Navin'

from TimeSeriesDbRESTApiCalls import *
from datetime import date,timedelta
from DateUtils import *
import time
import numpy

baseUrl = 'http://192.168.1.31:4242/api/query?'

restAPI = TimeSeriesDbRESTAPICalls()
allData = {}
refData = {}
detectConfigData = {}
userInputData= {}
dateutil = DateUtils()

class TrendDetectionAlgorithm:

    global dataExtractStartDt
    global dataExtractEndDt


    def calculateDates(self,refDate, windowInDays , prePostFlag):
        if(prePostFlag == "B"):
            returnDate = refDate - timedelta(days=int(windowInDays))
        elif (prePostFlag == "A"):
            returnDate = refDate + timedelta(days=int(windowInDays))
        return returnDate


    def convertStringToDate(self,refDate):
        refDate = time.strptime(str(refDate), '%m/%d/%Y')
        refDate = date(refDate.tm_year, refDate.tm_mon, refDate.tm_mday)
        return refDate


    def prepareDatesForDataExtraction(self, year):
        print self.userInputData
        refStartDate = self.userInputData["refStartDate"]
        refEndDate = self.userInputData["refEndDate"]

        if(year != ''):
            refStartDate = string.replace(refStartDate,'2015','2014')
            refEndDate = string.replace(refEndDate,'2015','2014')

        print refStartDate , refEndDate
        refEndDate = self.calculateDates(self.convertStringToDate(refEndDate),self.userInputData["trendWindow"],"B")
        dataExtractStartDt= self.calculateDates(self.convertStringToDate(refStartDate),self.userInputData["trendWindow"],"B")
        dataExtractEndDt  = self.calculateDates(refEndDate,self.userInputData["trendWindow"],"A")
        print dataExtractStartDt, dataExtractEndDt
        return dataExtractStartDt , dataExtractEndDt


    def gatherDataForAlgorithm(self,sectCarrList , type):
        year = ''
        if(type == 'REF'):
            year = '2014'

        dataExtractStartDt , dataExtractEndDt = self.prepareDatesForDataExtraction(year)
        dataExtractStartDtTS = int(time.mktime(datetime.datetime.strptime(str(dataExtractStartDt), '%Y-%m-%d').timetuple()))
        dataExtractEndDtTS   = int(time.mktime(datetime.datetime.strptime(str(dataExtractEndDt), '%Y-%m-%d').timetuple()))

        for sectCarr in sectCarrList:
            queryString = baseUrl + "start=" + str(dataExtractStartDtTS) + "&end=" + str(dataExtractEndDtTS) + "&m=max:company1.calldrop.stats{sectorCarrier=" + sectCarr + "}&json"
            extractedData = restAPI.timeSeriesDBDataGatherWithAgg(queryString)
            if extractedData == None:
                continue

            dateSampleData = {}
            sampleList=[]
            prevDay = '2010-01-01'
            prevDayTS   = int(time.mktime(datetime.datetime.strptime(str(prevDay), '%Y-%m-%d').timetuple()))

            for day in sorted(extractedData.keys()):
                if(dateutil.convertTimeStampToDate(prevDayTS,'') ==  dateutil.convertTimeStampToDate(day,'')):
                    sampleValue= extractedData[day]
                    sampleList.append(float(sampleValue))
                    prevDayTS = day
                elif (sampleList != []):
                    medianvalue = numpy.median(sampleList)
                    dateSampleData[dateutil.convertTimeStampToDate(day,'')] = format(float(medianvalue),'.2f')
                    prevDayTS = day
                else:
                    prevDayTS = day
            if(type == 'REF'):
                refData[sectCarr] = dateSampleData
            else:
                allData[sectCarr] = dateSampleData

        print "NEW DATA"
        print allData
        print "REF DATA"
        print refData

    def initialize(self,detectConfigData,userInputData,sectCarrList):
        self.detectConfigData = detectConfigData
        self.userInputData = userInputData
        self.gatherDataForAlgorithm(sectCarrList,'')
        self.gatherDataForAlgorithm(sectCarrList, 'REF')


    def run(self,refDt):
        print "Inside RUN"
        self.computeTrend(refDt)

    def computeTrend(self,refDt):
        trendDict = {}
        deltaPercent = self.userInputData["trendVariancePercentLimit"]
        deltaCountPercent = self.userInputData["trendVarianceCountPercent"]
        for sectCarKey in allData.keys():
            latestDataPoints =  allData[sectCarKey]
            if (sectCarKey not in refData.keys()):
                continue
            varianceList = []
            referenceDataPoints =  refData[sectCarKey]
            for latKey in latestDataPoints.keys():
                refKey = dateutil.convertStringToDate(latKey,'%Y-%m-%d')
                refKey = string.replace(str(refKey),'2015','2014')
                if(refKey in referenceDataPoints.keys()):
                   if(float(referenceDataPoints[refKey]) <= 0.0):
                       continue
                   varianceList.append((float(latestDataPoints[latKey]) - float(referenceDataPoints[refKey]))*100/(float(referenceDataPoints[refKey])))
            trendDict[sectCarKey] = varianceList

        print trendDict
        for trendKey in trendDict.keys():
            varianList = trendDict[trendKey]
            #print trendKey
            i = 0
            for delta in varianList:
                if (float(delta) > float(deltaPercent)):
                    #print "DELTA " + "DELTA PERCENT"
                    #print  delta   ,  deltaPercent
                    i = i + 1
            #print i
            if ( float(i * 100)/ float(len(varianList))  > float(deltaCountPercent)):
                print "Actual Calculated Percent :" +   " Configured Percent :"
                print "------------------------- "  +   ' ------------------'
                print  str(format(float(i * 100)/ float(len(varianList)), '.3f')) + "       " +  str(format(float(deltaCountPercent), '.3f'))
                print "Trend Anomaly Detected ::  Sector Carrier --- " + str(trendKey)
