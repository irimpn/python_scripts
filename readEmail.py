import win32com.client
import unicodedata
import string
import imaplib


outlook=win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
folders = outlook.Folders
print folders


messages = []
for folder in folders:
    print folder
    if(str(folder) == 'careers@idatalytics.com'):
        inbox = outlook.GetDefaultFolder(6)
        for ib in inbox.Items:
            messages.append(ib)

countDict = {}

print messages
for message in messages:
    body_content = unicodedata.normalize('NFKD',message.body).encode('ascii', 'ignore')
    if string.find(body_content,'Hadoop') >= 0:
        if 'Hadoop' in countDict:
            countDict['Hadoop'] += 1
        else:
            countDict['Hadoop'] = 1

    if string.find(body_content,'TechFetch') >= 0:
        if 'TechFetch' in countDict:
            countDict['TechFetch'] += 1
        else:
            countDict['TechFetch'] = 1


print countDict
