__author__ = 'Navin'

detectConfigData = {}

class PrePostAverageComparisonAlgorithm(object):

    def run(self,refDt, preData, postData,detectConfigData):
        for preKey in preData.keys():
            varianceVal = format(float(preData.get(preKey)) - float(postData.get(preKey)), '.2f')
            if (abs(float(varianceVal)/float(preData.get(preKey)) * 100) >= float(detectConfigData.get("avgPercentVarianceRed"))):
                print  "Reference Date : " + str(refDt) +  " Sector Carrier : " + preKey + " :  Percentage Variation Avg Value : " +  format(abs(float(varianceVal)/float(preData.get(preKey))*100),'.2f') + " Config Data : " +  str(float(detectConfigData.get("avgPercentVarianceRed"))) + " :::: ##### &&& -- "   + "Anomaly Detected"


