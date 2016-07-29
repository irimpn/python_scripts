__author__ = 'Navin'

class FileReader(object):

    def readFileIntoDictionary(readFile , dataDict, delimiter):
        file = open(readFile, 'r')
        for line in file:
            line=line.strip()
            key,value = line.split(delimiter)
            dataDict[key]=value
        return dataDict

