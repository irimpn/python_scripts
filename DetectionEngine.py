__author__ = 'Navin'

import requests
import datetime
import time
from datetime import date,timedelta
from NumericFormulaParser import *
from readFile import *
from PrePostAverageComparisonAlgorithm import *
from TimeSeriesDbRESTApiCalls import *
from TrendDetectionAlgorithm import *

# ----------------------------------------
# Initialize Data Structures & Variables
# ----------------------------------------
# ----------------------------------------

preData = {}
postData = {}
detectConfigData = {}
userInputData={}
sectCarrConfigData = {}
prePostDataGathered = {}

valueList=[]
refDtList=[]
baseUrl = 'http://192.168.1.31:4242/api/query?'


calc = NumericFormulaParser()
restAPIs= TimeSeriesDbRESTAPICalls()
avgAlgo = PrePostAverageComparisonAlgorithm()
trendAlgo = TrendDetectionAlgorithm()

# ----------------------------------------
# Read Config & Input Files
# ----------------------------------------
# ----------------------------------------

startTime=  time.localtime()


fileReader = FileReader()

readDetectConfigFile = open('C:\Work\data\config\detection-config.txt', 'r')
for configLine in readDetectConfigFile:
    configLine=configLine.strip()
    key,value = configLine.split("|")
    detectConfigData[key]=value


readDetectUserInputFile = open('C:\Work\data\config\detection-user-input.txt', 'r')
for userInputLine in readDetectUserInputFile:
    userInputLine=userInputLine.strip()
    key,value = userInputLine.split("|")
    userInputData[key]=value
print userInputData

readhierarchyConfFile = open('C:\Work\data\config\\tsgen-config.txt', 'r')
for hierConfLine in readhierarchyConfFile:
    hierConfLine=hierConfLine.strip()
    key,order, value = hierConfLine.split(",")
    if(key=="hierarchyConfig"):
        sectCarrConfigData[order]=value


# -------------------------------------------------------------------------------
# Flatten out the list of Sector Carriers (ideally from Reference Data)
# For now this is done using a number sequence logic used in the Data Generation.
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
def prepareSectCarrierList():
    hierarchy = userInputData["hierarchy"]
    startStr = ""

    bandCount = 0
    cellSiteCount = 0
    sectorCount = 0
    sectorCarrierCount = 0

    for scConf in sorted(sectCarrConfigData.keys()):
        hier,count = sectCarrConfigData[scConf].split("|")
        if(hierarchy==hier):
            startStr = string.replace(userInputData["detectEntity"], hierarchy,"")
            continue
        elif(startStr != ""):
            if (hier == "band" ):
                bandCount = count
            if (hier == "cellSite"):
                cellSiteCount=count
            if (hier == "sectors"):
                sectorCount=count
            if (hier == "sectorCarrier"):
                sectorCarrierCount=count
        else:
            continue

    for band in range (int(bandCount)):
       for cellSite in range (int(cellSiteCount)):
            for sector in range(int(sectorCount)):
                for sectCarr in range(int(sectorCarrierCount)):
                    valueList.append("sectorCarr" + startStr + str(band + 1) + str (cellSite + 1) + str(sector + 1) + str(sectCarr + 1))


    print valueList
prepareSectCarrierList();


# --------------------------------------------------------------------------------
# Calculate the Pre-Post Start and End Dates for a given Reference Date.
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------

def calculateDates(refDate, windowInDays , prePostFlag):
    if(prePostFlag == "B"):
        returnDate = refDate - timedelta(days=int(windowInDays))
    elif (prePostFlag == "A"):
        returnDate = refDate + timedelta(days=int(windowInDays))
    return returnDate


def convertStringToDate(refDate):
    refDate = time.strptime(str(refDate), '%m/%d/%Y')
    refDate = date(refDate.tm_year, refDate.tm_mon, refDate.tm_mday)
    return refDate


# --------------------------------------------------------------------------------
# Gather the Pre-Post data for given Pre-Post Start and End Dates
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------

def gatherPrePostAvgData(startDt, endDt):
    for sc in valueList:
        queryString = "start=" + str(startDt) + "&end=" + str(endDt) + "&m=max:company1.calldrop.stats.avg{sectorCarrier=" + sc + "}&json"
        dateAvgData = {}
        queryString = baseUrl+queryString
        dateAvgData = restAPIs.timeSeriesDBDataGather(queryString)
        prePostDataGathered[sc] = dateAvgData



def generateDateList(startDt, endDt,tsFlag, strformat):
    dateList=[]
    postWindow = userInputData["postWindow"]

    if(strformat==""):
        endDt = time.strptime(str(endDt),'%m/%d/%Y')
        startDt = time.strptime(str(startDt),'%m/%d/%Y')
    else:
        endDt = time.strptime(str(endDt),strformat)
        startDt = time.strptime(str(startDt),strformat)

    startDt = date(startDt.tm_year,startDt.tm_mon, startDt.tm_mday)
    endDt = date(endDt.tm_year,endDt.tm_mon, endDt.tm_mday)

    if(tsFlag=='N'):
        endDt = endDt - timedelta(days=int(postWindow))

    dayCount = (endDt-startDt).days + 1

    for dt in (startDt + timedelta(n) for n in range(dayCount)):
        if(tsFlag=="Y"):
            dateList.append(int(time.mktime(datetime.datetime.strptime(str(dt), '%Y-%m-%d').timetuple())))
        else:
            dateList.append(dt)
    return dateList


# --------------------------------------------------------------------------------
# Make OpenTSDB calls to gather Data for the whole Pre-Post window
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------



def prepareUrlRequests():
    refStartDate = userInputData["refStartDate"]
    refEndDate = userInputData["refEndDate"]

    refDtList = generateDateList(refStartDate,refEndDate,'N','')

    preWindowInDays = userInputData["preWindow"]
    postWindowInDays = userInputData["postWindow"]


    dataGatherStartDate = calculateDates(convertStringToDate(refStartDate), preWindowInDays , "B")
    dataGatherEndDate = calculateDates(convertStringToDate(refEndDate), postWindowInDays , "A")
    dataGatherStartDateTS = int(time.mktime(datetime.datetime.strptime(str(dataGatherStartDate), '%Y-%m-%d').timetuple()))
    dataGatherEndDateTS   = int(time.mktime(datetime.datetime.strptime(str(dataGatherEndDate), '%Y-%m-%d').timetuple()))

    gatherPrePostAvgData(dataGatherStartDateTS, dataGatherEndDateTS)
    return refDtList




def populatePrePostDataStructures(preDateList,postDateList):
    print "Inside pre post data structs"

    for key in prePostDataGathered.keys():
        avgData = prePostDataGathered[key]
        avgValList = []
        if (avgData != None):
            for pre in preDateList:
                avgVal = avgData[str(pre)]
                if(avgVal != ""):
                    avgValList.append(avgVal)
                else:
                    continue
            preData[key] = format(float(reduce(lambda x, y: float(x) + float(y), avgValList))/float(len(avgValList)),'.3f')
            avgValList = []
            for post in postDateList:
                avgVal = avgData[str(post)]
                if(avgVal != ""):
                    avgValList.append(avgVal)
                else:
                    continue
            postData[key]= format(float(reduce(lambda x, y: float(x) + float(y), avgValList))/float(len(avgValList)),'.3f')


# --------------------------------------------------------------------------------
# Detecting Anomalies . We will use multiple algorithms here ,
# however the code is now only for a specific one.
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------

def detectAnomalies():
    preWindowInDays = userInputData["preWindow"]
    postWindowInDays = userInputData["postWindow"]
    refDtList = prepareUrlRequests()

    trendAlgo.initialize(detectConfigData, userInputData, valueList)


    for refDt in refDtList:
        print "Reference Date : "
        print  refDt
        preStartDate = calculateDates(refDt, preWindowInDays , "B")
        postEndDate = calculateDates(refDt, postWindowInDays , "A")
        # print "Pre Start Date  " +  " Post End Date "
        # print "=============== " +  " =============="
        # print  str(preStartDate)  +"    ,    "  +  str(postEndDate)
        preDateList= generateDateList(preStartDate, refDt, 'Y', '%Y-%m-%d')
        postDateList = generateDateList(refDt, postEndDate, 'Y', '%Y-%m-%d')
        postDateList.pop(0)
        # print "Pre Date List " + " Post Date List"
        # print "============= " + " =============="
        # print  preDateList
        # print  postDateList
        populatePrePostDataStructures(preDateList, postDateList)
        # print " PRE AVG DATA "
        # print preData
        # print " POST AVG DATA "
        # print postData
        #avgAlgo.run(refDt,preData,postData,detectConfigData)
        trendAlgo.run(refDt)

detectAnomalies()


endTime= time.localtime()
print "Time Taken for the Detection Engine Execution : "
print (time.mktime(endTime) - time.mktime(startTime))