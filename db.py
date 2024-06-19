import mysql.connector
import datetime

username = 'pass'
host="pass"
password = "pass"
database = "pass"

def update(PO, updated_date = None, updated_qty = None, date = False,qty = False):
  mydb = mysql.connector.connect(
    username = username,
    host = host,
    password = password,
    database = database
  )
  cur = mydb.cursor()
  flag = False
  if date and updated_date != None:
    flag = update_date(PO,updated_date, cur)
  elif qty and updated_qty != None:
    flag = update_qty(PO,updated_qty, cur)

  # cur.execute("Select * from purchase_orders;")
  # print(cur.fetchall())

  mydb.commit()
  mydb.close()
  return flag
# cur.execute("Use easeworkai;")

# {updated_date.strftime('%d-%m-%Y')} 

def update_date(PO, updated_date, cur):
  try:
    query = f'UPDATE purchase_orders SET DeliveryDate = "{updated_date}" WHERE PONumber = "{PO}";'
    cur.execute(query)

    return True
  except Exception as e:
    print(e)
    return False

def update_qty(PO, updated_qty, cur):
  try:
    query = f'UPDATE purchase_orders SET Quantity = {updated_qty} WHERE PONumber = "{PO}";'
    cur.execute(query)
    return True
  except Exception as e:
    print(e)
    return False

# print(update_date("PO001", "2002-01-01"))



def update_received_docs(PO, attached_doc):
  mydb = mysql.connector.connect(
    username = username,
    host = host,
    password = password,
    database = database
  )
  cur = mydb.cursor()
  supplier_requested_docs = ["BOL" ,"PFI", "Drawings", "MQIC"]
  buyer_requested_docs = ["LOC"]

  try:
    query = f'UPDATE {"documents_received_tobuyer_bysupplier" if attached_doc in supplier_requested_docs else "documents_received_tosupplier_bybuyer" if attached_doc in buyer_requested_docs else ""} SET {attached_doc} = 1 WHERE PONumber = "{PO}";'
    # print(query)
    cur.execute(query)
    mydb.commit()
    mydb.close()
    return True
  except Exception as e:
    print(e)
    return False

def get_delivery_date():
  mydb = mysql.connector.connect(
    username = username,
    host = host,
    password = password,
    database = database
  )
  cur = mydb.cursor()
  try:
    query = f'SELECT PONumber, DeliveryDate FROM purchase_orders;'
    cur.execute(query)
    data = cur.fetchall()
    return data
    # print(data)
    # print(type(data))
    # datetime.date.today()
  except Exception as e:
    pass


def get_requestor(PO):
  mydb = mysql.connector.connect(
    username = username,
    host = host,
    password = password,
    database = database
  )
  cur = mydb.cursor()
  try:
    query = f'SELECT requestor FROM requestor_supplier WHERE PONumber = "{PO}";'
    cur.execute(query)
    data = cur.fetchall()
    # print(data)
    return data[0][0]
  except Exception as e:
    print("Error", e)
def get_supplier(PO):
  mydb = mysql.connector.connect(
    username = username,
    host = host,
    password = password,
    database = database
  )
  cur = mydb.cursor()
  try:
    query = f'SELECT supplier FROM requestor_supplier WHERE PONumber = "{PO}";'
    cur.execute(query)
    data = cur.fetchall()
    # print(data)
    return data[0][0]
  except Exception as e:
    print("Error", e)


def get_missing_docs(PO):
  mydb = mysql.connector.connect(
    username = username,
    host = host,
    password = password,
    database = database
  )
  cur = mydb.cursor()
  supplier_requested_docs = ["BOL" ,"PFI", "Drawings", "MQIC"]
  buyer_requested_docs = ["LOC"]
  s_missing = []
  b_missing = []
  try:
    query = f'SELECT BOL, PFI, Drawings, MQIC FROM documents_received_tobuyer_bysupplier WHERE PONumber = "{PO}";'
    cur.execute(query)
    data = cur.fetchall()
    for i,f in enumerate(data[0]):
      if(f == 0):
        s_missing.append((i,supplier_requested_docs[i]))
    query = f'SELECT LOC FROM documents_received_tosupplier_bybuyer WHERE PONumber = "{PO}";'
    cur.execute(query)
    data = cur.fetchall()
    for i,f in enumerate(data[0]):
      if(f == 0):
        b_missing.append((i,buyer_requested_docs[i]))
    # print(data)
    return {"s_missing": s_missing,"b_missing": b_missing}
  except Exception as e:
    print("Error", e)


def get_incharge(PO,file):
  mydb = mysql.connector.connect(
    username = username,
    host = host,
    password = password,
    database = database
  )
  cur = mydb.cursor()
  try:
    query = f'SELECT {file} FROM incharge WHERE PONumber = "{PO}"'
    cur.execute(query)
    data = cur.fetchall()
    # print(data)
    return data[0][0]
  except Exception as e:
    print("Error", e)



def get_Supplier_Name(PO):
  mydb = mysql.connector.connect(
    username = username,
    host = host,
    password = password,
    database = database
  )
  cur = mydb.cursor()
  try:
    query = f'SELECT SupplierName FROM purchase_orders WHERE PONumber = "{PO}";'
    cur.execute(query)
    data = cur.fetchall()
    # print(data)
    return data[0][0]
  except Exception as e:
    print("Error", e)


# check_missing_docs('PO002')

# print(get_requestor("PO002"))


# print(get_missing_docs("PO003"))


# print(update_received_docs("PO001","LOC"))