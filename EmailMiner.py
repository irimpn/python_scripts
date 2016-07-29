__author__ = 'Navin'


import win32com.client
import unicodedata
import string
import cStringIO
import MySQLdb


outlook=win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
inbox = outlook.GetDefaultFolder(6)
messages = inbox.Items

countDict = {}
match_field="all"
customerDetails = {}
i = 1
for message in messages:
    singleCustomerDetails={}
    body_content = unicodedata.normalize('NFKD',message.body).encode('ascii', 'ignore')
    subject= message.subject
    if string.find(subject,"InsuranceQuote") >= 0:
        print "+-------------------- NEW CUSTOMER ------------------------+"
        buf = cStringIO.StringIO(body_content)
        for line in buf.readlines():
            if(string.find(line,"Name") == 0):
                nameCol= string.split(line, ":")
                print nameCol[1]
                singleCustomerDetails["Name"]=nameCol[1]
            if(string.find(line,"Last Name ") == 0):
                nameCol= string.split(line, ":")
                print nameCol[1]
                singleCustomerDetails["LastName"]=nameCol[1]
            if(string.find(line,"Company") == 0):
                nameCol= string.split(line, ":")
                print nameCol[1]
                singleCustomerDetails["Company"]=nameCol[1]
            if(string.find(line,"State") == 0):
                nameCol= string.split(line, ":")
                print nameCol[1]
                singleCustomerDetails["State"]=nameCol[1]
            if(string.find(line,"Zip") == 0):
                nameCol= string.split(line, ":")
                print nameCol[1]
                singleCustomerDetails["Zip"]=nameCol[1]

            customerDetails[i]=singleCustomerDetails
        print "+ ---------------------------------------------------------+"
        i += 1



print customerDetails
db = MySQLdb.connect("localhost","root","","insurancedb" )
cursor = db.cursor()
cursor.execute("TRUNCATE TABLE customer")


for oneCustomer in customerDetails.values():
    name = oneCustomer["Name"].rstrip()
    lastName = oneCustomer["LastName"].rstrip()
    company = oneCustomer["Company"].rstrip()
    state = oneCustomer["State"].rstrip()
    zip = oneCustomer["Zip"].rstrip()
    sql = "INSERT customer values( 0,'" +name+ "','" +lastName+ "','" +company+ "','"+ state + "','" +zip+ "');"
    print sql

    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()

db.close()
