__author__ = 'Navin'

from itertools import islice
from NumericFormulaParser import *
import time
import datetime
import numpy

configData = {}
counterData = {}
outputFileWriter = {}
fileData = {}
sectorCarrierDict = {}
avgValues = {}
outputValueDict = {}

readConfigFile = open('C:\Work\data\config\kpi-calc-config.txt', 'r')
for configLine in readConfigFile:
    configLine = configLine.strip()
    key, value = configLine.split(":")
    configData[key] = value

for key in configData.keys():
    outputFileWriter[key] = open(key, 'w')

calc = NumericFormulaParser()

avgFile = open("company1.calldrop.stats.avg", 'w')
medianFile = open("company1.calldrop.stats.median", 'w')

with open("C:\Work\data\outputFiles\KPICounterData_Historic_16-03-2016", 'r') as readFile:
    while True:
        nextLines = list(islice(readFile, 250000))
        if not nextLines:
            break

        dataList = []
        kpiData = {}
        avgData = {}
        fileDataText = []

        for line in nextLines:
            line = line.rstrip()
            split_data = line.split("|")

            network = split_data[0]
            band = split_data[1]
            cellsite = split_data[2]
            sector = split_data[3]
            sectorCarrier = split_data[4]

            date = split_data[5]
            strDate = time.strptime(str(date), "%m/%d/%Y %H:%M:%S")
            formattedDate = time.strftime('%m/%d/%Y', strDate)
            timestamp = split_data[6]

            counterData["CDsuccessfulCalls"] = split_data[7]
            counterData["CDcounter1"] = split_data[8]
            counterData["CDcounter2"] = split_data[9]
            counterData["TTcounter1"] = split_data[10]
            counterData["TTcounter2"] = split_data[11]
            counterData["TTcounter3"] = split_data[12]
            counterData["CFRcounter1"] = split_data[13]
            counterData["CFRcounter2"] = split_data[14]

            for key in configData.keys():
                value = configData[key]
                value = str(value).strip()
                numerator, denominator = value.split("|")
                outputValue = str(calc.calculateOutputValue(numerator.strip(), denominator.strip(), counterData))

                if key == "company1.calldrop.stats":
                    if sectorCarrier in sectorCarrierDict:
                        outputValueDict = sectorCarrierDict[sectorCarrier]
                        if formattedDate in outputValueDict:
                            outputValueDict[formattedDate].append(outputValue)
                        else:
                            outputValueDict[formattedDate] = [outputValue]
                        sectorCarrierDict[sectorCarrier] = outputValueDict
                    else:
                        outputValueDict[formattedDate] = [outputValue]
                        sectorCarrierDict[sectorCarrier] = outputValueDict
                    outputValueDict = {}

                dataString = key + " " + timestamp + " " + \
                             str(outputValue) + " " + \
                             "network=" + network + " " + \
                             "band=" + band + " " + \
                             "cellSite=" + cellsite + " " + \
                             "sector=" + sector + " " + \
                             "sectorCarrier=" + sectorCarrier + "\n"

                if key in fileData.keys():
                    fileDataText = fileData[key]
                    fileDataText.append(dataString)
                    fileData[key] = fileDataText
                else:
                    fileDataText = [dataString]
                    fileData[key] = fileDataText


        for key in outputFileWriter.keys():
            fileValues = fileData[key]
            for val in fileValues:
                outputFileWriter[key].write(val)
        fileValues = []
        fileData = {}


    for sectCarr in sectorCarrierDict.keys():
        outputValueDict = sectorCarrierDict[sectCarr]
        dates = outputValueDict.keys()

        for date in sorted(dates, key=lambda x: datetime.datetime.strptime(x, '%m/%d/%Y')):
            timestampStr = int(time.mktime(datetime.datetime.strptime(date, '%m/%d/%Y').timetuple()))
            outputValues = []
            for opVal in sorted(outputValueDict[date], key=lambda x: float(x)):
                outputValues.append(float(opVal))
            avgValue = format(numpy.average(outputValues), '.2f')
            medianValue = format(numpy.median(outputValues), '.2f')

            avgString = "company1.calldrop.stats.avg" + " " + str(timestampStr) + " " + avgValue + " " + "sectorCarrier=" + sectCarr
            avgFile.write(avgString + "\n")

            medianString = "company1.calldrop.stats.median" + " " + str(timestampStr) + " " + medianValue + " " + "sectorCarrier=" + sectCarr
            medianFile.write(medianString + "\n")




    for key in outputFileWriter.keys():
        outputFileWriter[key].close()

    avgFile.close()
    medianFile.close()

readFile.close()
    # os.rename("sampleCallDropAnalysisData_RealTime.txt", "sampleCallDropAnalysisData_RealTime.txt.completed"+date)
