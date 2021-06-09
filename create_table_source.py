#------------------------------------------ sources-----------------------------------------------------------------

# читаем данные из рабочего листа
import pandas as pd

sheet_id = '1Ycg7zTxds9DZnDvTrFcyNNKuTUxg6Yy6WF0a8Wc02WQ'
sheet_leads_name = 'leads'
sheet_transactions_name = 'transactions'
sheet_client_manager = 'clients'
sheet_managers = 'managers'

url_lead = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_leads_name}'
url_transaction = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_transactions_name}'
url_client_manager = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_client_manager}'
url_managers = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_managers}'

lead_column = pd.DataFrame(pd.read_csv(url_lead))['lead_id'].tolist()
manager_of_lead_column = pd.DataFrame(pd.read_csv(url_lead))['l_manager_id'].tolist()

client_of_lead_column = pd.DataFrame(pd.read_csv(url_lead))['l_client_id'].tolist()
data_of_lead_column = pd.DataFrame(pd.read_csv(url_lead))['created_at'].tolist()


#--------------------------------сколько заявок создано с каждого канала---------------------------------------------

lead_column = pd.DataFrame(pd.read_csv(url_lead))['lead_id'].tolist()
source_of_lead_column = pd.DataFrame(pd.read_csv(url_lead))['d_utm_source'].tolist()


source_and_lead = {}  #  словарь источник - количество заявок
sourses = []

 # проходим по рабочему листу
for i in range(len(lead_column)):
  if str(source_of_lead_column[i]) not in sourses:
    sourses.append(str(source_of_lead_column[i]))
    source_and_lead[str(source_of_lead_column[i])] = 1
  else:
    source_and_lead[str(source_of_lead_column[i])] = source_and_lead[str(source_of_lead_column[i])] + 1
    

#--------------------------------------------------------------------------------------------------------------------

#-------------------------- количество мусорных заявок (на основании заявки не создан клиент)-----------------------

source_and_lead_trash = {}   # словарь источник - количество мусорных заявок
source_trash = []

 # проходим по рабочему листу
for i in range(len(lead_column)):
    if client_of_lead_column[i] == '00000000-0000-0000-0000-000000000000':
      if str(source_of_lead_column[i]) not in source_trash:
        source_trash.append(str(source_of_lead_column[i]))
        source_and_lead_trash[str(source_of_lead_column[i])] = 1
      else:
        source_and_lead_trash[str(source_of_lead_column[i])] = source_and_lead_trash[str(source_of_lead_column[i])] + 1
    else:
        pass


#--------------------------------------------------------------------------------------------------------------------



client_of_transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['l_client_id'].tolist()
data_of_transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['created_at'].tolist()

#---------------------- количество новых заявок (не было заявок и покупок от этого клиента раньше)--------------------

source_and_lead_new = {}   # словарь источник - количество новых заявок
source_new = []



from datetime import datetime

def date_to_sec(date):    # сколько секунд в дате
  return datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S').timestamp()

def check_older_transaction_client(client_of_transaction, data_of_transaction):    # проверим что ранее не было покупок
    for i in range(len(client_of_transaction_column)):
        if ((client_of_transaction_column[i] == client_of_transaction) and (date_to_sec(data_of_transaction_column[i]) < date_to_sec(data_of_transaction))):
            return False
    return True


def check_older_leads_client(client_of_lead, data_of_lead):    # проверим что ранее не было заявок
    for i in range(len(client_of_lead_column)):
        if ((client_of_lead_column[i] == client_of_lead) and (date_to_sec(data_of_lead_column[i]) < date_to_sec(data_of_lead))):
            return False
    return True    

 # проходим по рабочему листу
for i in range(len(lead_column)):
    if (check_older_transaction_client(client_of_transaction_column[i], data_of_transaction_column[i]) and check_older_leads_client(client_of_lead_column[i], data_of_lead_column[i])):
        if str(source_of_lead_column[i]) not in source_new:
            source_new.append(str(source_of_lead_column[i]))
            source_and_lead_new[str(source_of_lead_column[i])] = 1
        else:
            source_and_lead_new[str(source_of_lead_column[i])] = source_and_lead_new[str(source_of_lead_column[i])] + 1


#--------------------------------------------------------------------------------------------------------------------

# ----------------------количество покупателей (кто купил в течение недели после заявки)-----------------------------

client_of_transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['l_client_id'].tolist()
data_of_transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['created_at'].tolist()
transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['transaction_id'].tolist()

source_of_client_column = pd.DataFrame(pd.read_csv(url_lead))['d_utm_source'].tolist()
client_of_source_column = pd.DataFrame(pd.read_csv(url_lead))['l_client_id'].tolist()

client_source = dict(zip(client_of_source_column, source_of_client_column))  #словарь клиент и какой у него источник

def check_lead_before_transaction(date_transaction, date_lead):   # проверим: что после заявки не прошла неделя
  if ((date_to_sec(date_transaction) - date_to_sec(date_lead)) < 604800):   # в неделе 604800 секунд
    return True
  else:
    return False

def find_date_of_lead(client):     # найдем дату заявки от этого клиента
  for i in range(len(client_of_lead_column )): # ищем клиента в листе заявок
    if client_of_lead_column[i] == client:
      return data_of_lead_column[i] 


source_and_new_transactions = {}   #  словарь источник - количество покупателей
source_transactions_new = []


 # проходим по рабочему листу
for i in range(len(transaction_column)):
  if find_date_of_lead(client_of_transaction_column[i]) != None:
    if check_lead_before_transaction(data_of_transaction_column[i], find_date_of_lead(client_of_transaction_column[i])):
      sourse_of_transaction = str(client_source[client_of_transaction_column[i]])   # найдем source (по клиенту)
      if sourse_of_transaction not in source_transactions_new:
        source_transactions_new.append(str(sourse_of_transaction))
        source_and_new_transactions[str(sourse_of_transaction)] = 1
      else:
        source_and_new_transactions[str(sourse_of_transaction)] = source_and_new_transactions[str(sourse_of_transaction)]+ 1


#--------------------------------------------------------------------------------------------------------------------

#-------------количество новых покупателей (кто купил в течение недели после заявки, и не покупал раньше)------------

client_of_transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['l_client_id'].tolist()
data_of_transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['created_at'].tolist()
transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['transaction_id'].tolist()

source_of_client_column = pd.DataFrame(pd.read_csv(url_lead))['d_utm_source'].tolist()
client_of_source_column = pd.DataFrame(pd.read_csv(url_lead))['l_client_id'].tolist()

client_source = dict(zip(client_of_source_column, source_of_client_column))  #словарь клиент и какой у него источник



def check_no_transactions_before(date_of_transaction, client):  # проверим не было ли покупок до этого
  for i in range(len(data_of_transaction_column)):
    if client == client_of_transaction_column[i]:
      if (date_to_sec(data_of_transaction_column[i]) < date_to_sec(date_of_transaction)):
        return False
  return True



source_and_new_transactions_week_after_lead = {}    # словарь источник - количество новых покупателей 
source_transactions_new_week_after_lead = []

 # проходим по рабочему листу
for i in range(len(transaction_column)):  

  if find_date_of_lead(client_of_transaction_column[i]) != None:

    if (check_lead_before_transaction(data_of_transaction_column[i], find_date_of_lead(client_of_transaction_column[i])) and (check_no_transactions_before(data_of_transaction_column[i], client_of_transaction_column[i]))):

      source_of_transaction = client_source[client_of_transaction_column[i]]   # найдем source (по клиенту)

      if source_of_transaction not in source_transactions_new_week_after_lead:

        source_transactions_new_week_after_lead.append(source_of_transaction)

        source_and_new_transactions_week_after_lead[source_of_transaction] = 1

      else:

        source_and_new_transactions_week_after_lead[source_of_transaction] = source_and_new_transactions_week_after_lead[source_of_transaction] + 1


#--------------------------------------------------------------------------------------------------------------------

#--------------------------------------------доход от покупок новых покупателей-------------------------------------

client_of_transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['l_client_id'].tolist()
data_of_transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['created_at'].tolist()
transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['transaction_id'].tolist()
transaction_amount_column = pd.DataFrame(pd.read_csv(url_transaction))['m_real_amount'].tolist()
source_of_client_column = pd.DataFrame(pd.read_csv(url_lead))['d_utm_source'].tolist()
client_of_source_column = pd.DataFrame(pd.read_csv(url_lead))['l_client_id'].tolist()

client_source = dict(zip(client_of_source_column, source_of_client_column))  #словарь клиент и какой у него источник




source_and_new_transactions_amount = {}    # словарь источник - оход от покупок новых покупателей
source_transactions_new_amount = []

 # проходим по рабочему листу
for i in range(len(transaction_column)):  

  if find_date_of_lead(client_of_transaction_column[i]) != None:

    if (check_lead_before_transaction(data_of_transaction_column[i], find_date_of_lead(client_of_transaction_column[i])) and (check_no_transactions_before(data_of_transaction_column[i], client_of_transaction_column[i]))):

      source_of_transaction = client_source[client_of_transaction_column[i]]   # найдем source (по клиенту)

      if source_of_transaction not in source_transactions_new_amount:

        source_transactions_new_amount.append(source_of_transaction)

        source_and_new_transactions_amount[source_of_transaction] = transaction_amount_column[i]

      else:

        source_and_new_transactions_amount[source_of_transaction] += transaction_amount_column[i]



#--------------------------------------------------------------------------------------------------------------------




#-----------------------------------------запись в CSV---------------------------------------------------------


import csv
csv_file = open("./source.csv", "w")

writer = csv.writer(csv_file)


writer.writerow(['dimension', 'количество заявок', 'количество мусорных заявок', 'количество новых заявок', 'количество покупателей', 'количество новых покупателей ', 'доход от покупок новых покупателей'])

spisok_tblte = [source_and_lead_trash , 
                source_and_lead_new, 
                source_and_new_transactions,
                source_and_new_transactions_week_after_lead,
                source_and_new_transactions_amount]

for key, value in source_and_lead.items():
    row_list = []
    if key == "nan":
      key = "нет источника"
    row_list.append(key)
    row_list.append(value)
    for x in spisok_tblte:
        if key in x:
            row_list.append(x[key])
        else:
            row_list.append(0)

    writer.writerow(row_list)  
  

csv_file.close()


#--------------------------------------------------------------------------------------------------------------
