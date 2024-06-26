import pendulum
import time
import json
from dotenv import load_dotenv
from emailOperations import read_emails, send_emails
from agents_with_LLM import model
from get_PO import get_po

from access_token import get_or_authenticate_user
from NER import classify_email
from send_approval_email import send_approval_email
from check_response import check_approval_responses
# Load environment variables
load_dotenv()

from db import update_received_docs,update, get_requestor, get_supplier, get_incharge, get_Supplier_Name
import asyncio
# from docRequestor import check_docs
from bot_token import get_or_authenticate_bot


def check_latest_emails():
    
    while True:
        utc_now = pendulum.now('UTC')
        # try:
        #     username = get_or_authenticate_user() 
        # except Exception as e:
        #     print(f"Error while checking emails: {e}")
        #     mail = None
        try: 
            mail = read_emails()
            utc_string = mail['received']
            
            # Parse the received time
            received_timestamp_utc = pendulum.parse(utc_string, tz='UTC')
            
            # Check if the mail was received within the last 5 seconds
            if utc_now.subtract(seconds=2) < received_timestamp_utc:
                break
        except Exception as e:
            print(e)


    
    return mail

def PO(mail):


    username = get_or_authenticate_bot() 
    outputs = model(mail)
    print(outputs)
    validator = json.loads(outputs['json1'])
    categorizer = json.loads(outputs['json2'])
    PO = categorizer['PO']
    mailFrom = mail['from']['emailAddress']['address'].lower()
    supplier = get_supplier(PO).lower()



    if mailFrom != supplier and validator['Is_Supplier_Email'] == "True":
        subject = "Email is not registered."
        body = f"""
Dear {mail['from']['emailAddress']['name']},
    Sorry your email is not registered with our company's supplier records. Please send it from the registered email or contact the supplier admin for further support at {supplier}.
Yours Sincerely,
EaseAgent
        """
        message = {
            'subject': subject,
            'content': body,
            'recipient': mailFrom
        }
        send_emails(message)
    elif mailFrom == supplier and validator['Is_Supplier_Email'] == "True":
        # category_output
        draft = outputs["json3"] 
        email = json.loads(draft)
        email = email['email']

        message = {
            'subject': email["subject"] ,
            'content': email["body"] + "\n" + "EaseAgent",
            'recipient': mail["from"]['emailAddress']['address']
        }


        requestor = get_requestor(PO)   #
        if categorizer['category'] == 'change':
            ## Approval

            new_mail = f"""
Dear Requester,
The Supplier {get_Supplier_Name(PO)} has requested PO change - Please refer to supplier email below :
From: {mail['from']}
Subject: {mail['subject']}
{mail['body']}

In your service,
EaseAgent
"""

            send_approval_email(requestor, new_mail)
            all_approved = check_approval_responses()
            if all_approved == True: 
                if categorizer['change']['change_type'] == "delivery_date":
                    if update(categorizer['PO'],updated_date = categorizer['change']['changed_date'],date= True):    
                        send_emails(message)
                    else:
                        print("Error while updating database")
                elif categorizer['change']['change_type'] == "quantity":
                    if update(categorizer['PO'],updated_qty= categorizer['change']['changed_qty'], qty= True):
                        send_emails(message)
                    else:
                        print("Error while updating database")
                else:
                    print("Something went wrong!")
        else:
            send_emails(message)
    else:
        pass

def validate_response(reply_to, doc,PO):
    # Checking approval
    # approval_granted = True
    approval_granted = check_approval_responses()
    flag = False
    if approval_granted:

        #Approved message to Supplier
        message = {
            'subject': f'Document Approval for {PO}',
            'content': f'Your document:- {doc} has been approved for {PO}.',
            'recipient': reply_to
        }
        print("Sending approval email to supplier.")

        if update_received_docs(PO,doc):
            flag =True
            print("Document Received")
        #After Approval update the DB

    else:
        #rejection message to Supplier
        message = {
            'subject': 'Document Disapproval',
            'content': f'Your document: {doc} has not been approved.',
            'recipient': reply_to
        }
        print("Sending disapproval email to supplier.")

    #send_emails(supplier_email, message)
    send_emails(message)
    print(f"Email sent to {reply_to}")
    if flag:
        return True
    else:
        False


def process_attachments(mail):
    s_docs =  ["BOL" ,"PFI", "Drawings", "MQIC"]
    b_docs = ["LOC"]
    PO = get_po(mail)
    received_docs = []
    if PO == None:
        print("No PO found in the email")
        return
    for i in mail["attachments"]:
        attached_doc = ""
        if i == 'BOL':
            attached_doc = "Bill of Lading"
        if i == 'PFI':
            attached_doc = "Pro Forma Invoice"
        if i == 'Drawings':
            attached_doc = "Drawings and Design"
        if i == 'MQIC':
            attached_doc = "Material Quality Inspection Certificate"
        if i == 'LOC':
            attached_doc = "Letter of Credits"
        if i in s_docs:
            incharge = get_incharge(PO, i)
            print(incharge)
            if incharge != None:
                new_mail = f"""
Dear Document Verifier,</br>
The supplier has sent documents. Please verify and confirm the document:</br>
From: {mail['from']}</br>
Subject: {mail['subject']}</br>
{mail['body']}</br></br>
Attached Document: 
{attached_doc}
</br></br>
In your service,
EaseAgent
"""
                send_approval_email(incharge,new_mail)
                reply_to =  mail['from']['emailAddress']['address'].lower()
                if validate_response(reply_to,i,PO):
                    received_docs.append(i)
        elif i in b_docs:
            incharge = get_incharge(PO, i)
            print(incharge)
            if incharge != None:
                new_mail = f"""
Dear Document Verifier,</br>
The buyer has sent documents. Please verify and confirm the document:</br>
From: {mail['from']}</br>
Subject: {mail['subject']}</br>
{mail['body']}</br></br>
Attached Document: 
{attached_doc}
</br></br>
In your service,
EaseAgent
"""
                send_approval_email(incharge,new_mail)
                reply_to =  mail['from']['emailAddress']['address'].lower()
                if validate_response(reply_to,i,PO):
                    received_docs.append(i)
                
        print("Received Docs",received_docs)

    

def process_mail(mail):
    #approval_mail = send_approval_email(username, mail)
    most_likely_label = classify_email(str(mail))[0]
    # Check if the email is about a PO date change.
    if mail['attachments'] != []:
        process_attachments(mail)
    print(most_likely_label)
    if most_likely_label == "purchase order related":
        PO(mail)
        #print(mail)


if __name__ == "__main__":
    while True:
        # check_docs()
        
        print("[+] Checking Latest Mail [+]...")
        mail = check_latest_emails()
        # open("approval_response.json","w")

        if mail:
            open("approval_response.json","w")
            process_mail(mail)
        time.sleep(5)


# async def check_docs_loop():
#     while True:
#         await check_docs()
#         print("[+] Checking Latest Mail [+]...")
#         mail = check_latest_emails()
       
#         if mail:
#             open("approval_response.json","w")
#             process_mail(mail)
#         await asyncio.sleep(5)
 
# async def main():
#     await asyncio.gather(check_docs_loop(), asyncio.to_thread(check_docs))
 
# if __name__ == "__main__":
#     asyncio.run(main())