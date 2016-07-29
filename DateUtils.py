__author__ = 'Navin'

from datetime import timedelta,date
import time
import datetime

class DateUtils:
    # --------------------------------------------------------------------------------
    # Calculate the Pre-Post Start and End Dates for a given Reference Date.
    # --------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------

    def calculateDates(self,refDate, windowInDays , prePostFlag):
        if(prePostFlag == "B"):
            returnDate = refDate - timedelta(days=int(windowInDays))
        elif (prePostFlag == "A"):
            returnDate = refDate + timedelta(days=int(windowInDays))
        return returnDate

    def convertStringToDate(self,refDate , format):
        if (format == ""):
            format = '%m/%d/%Y'
        refDate = time.strptime(str(refDate), format)
        refDate = date(refDate.tm_year, refDate.tm_mon, refDate.tm_mday)
        return refDate

    def convertTimeStampToDate(self,timestamp, dateformat):
        if (dateformat == ""):
            dateformat = '%Y-%m-%d'
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime(dateformat)


    def convertTimeStampToDateWithTime(self,timestamp):
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')