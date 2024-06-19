from db import get_delivery_date, get_missing_docs, get_incharge, get_requestor, get_supplier
from datetime import datetime
import pytz
from send_approval_email import send_BotEmail
import json
import time
import os



def doc_request():
    today = datetime.date.today()
    dd = get_delivery_date()
    try:
        with open('times.json', 'r') as file:
            data = json.load(file)
        setDays = data[0]["days_before"]
    except Exception as e:
        print("Error", e)
        setDays = 86400

    for PO,DD in dd:
        daysRemaining = DD - today
        missing = get_missing_docs(PO)
        supplier_docNames = ["Bill Of Ladding", "Pro Forma Invoice", "Drawings", "Material Quality Inspection Certificate"]
        buyer_docNames = ["Letter of Credit"]

        supplier = get_supplier(PO)
        requestor = get_requestor(PO)
        requestTo = {supplier : "", requestor: ""}
        
        if daysRemaining.days > setDays:
            continue
        for i,j in missing["s_missing"]:
            requestTo[supplier] += "- " + supplier_docNames[i] + "\n"
        for i,j in missing["b_missing"]:
            requestTo[requestor] += "- " + buyer_docNames[i] + "\n"
        

        # print(requestTo)
        for to,missing_docs in requestTo.items():
            user = "User"
            if to == supplier:
                user = "Supplier"
            else:
                user = "Buyer"
            
            subject = f"Submit the missing documents for #{PO}"
            msg = f"""Dear {user},
Please submit your missing documents for PO order #{PO}, only {daysRemaining.days} days are left for the delivery due.
Your missing documents: \n
{missing_docs}
Please submit before the delivery due.

Best Regards,
EaseAgent

        """
            # print(to, msg, "\n\n-----")
            if missing_docs == "":
                continue
            else:
                send_BotEmail(to, subject, msg,"text")

def convert_time_to_seconds(time_string):
  hours, minutes, seconds = time_string.split(":")
  return int(hours) * 3600 + int(minutes) * 60 + int(seconds)

def check_docs():
    print("Working")
    while True:
        # utc_now = datetime.datetime.utcnow()
        # ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))  # Convert to IST timezone
        # current_time = ist_now.strftime("%H:%M:%S")
 
        # try:
        #     with open('times.json', 'r') as file:
        #         data = json.load(file)
        #     received_time = data[0]["received_time"]
        # except (FileNotFoundError, IndexError, KeyError):
        #     received_time = "00:00:00"
 
        # if current_time == received_time:
        #     print('Processing document request...')
        #     doc_request()
        #     time.sleep(1)  # Delay to prevent rapid processing

        try:
            with open('times.json', 'r') as file:
                data = json.load(file)
            received_time = data[0]["received_time"]
        except (FileNotFoundError, IndexError, KeyError):
            received_time = "24:00:00"

        t = convert_time_to_seconds(received_time)
        doc_request()
        time.sleep(t)
 
if __name__ == "__main__":
    check_docs()

# doc_request()

# import asyncio
# asyncio.run(check_docs())

# print(datetime.time.now())