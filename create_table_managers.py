#------------------------------------------managers and leads------------------------------------------------

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


#--------------------------------------------------------------------------------------------------------------


#------------------------------- сколько заявок создал каждый менеджер-----------------------------------------

lead_column = pd.DataFrame(pd.read_csv(url_lead))['lead_id'].tolist()
manager_of_lead_column = pd.DataFrame(pd.read_csv(url_lead))['l_manager_id'].tolist()

client_of_lead_column = pd.DataFrame(pd.read_csv(url_lead))['l_client_id'].tolist()
data_of_lead_column = pd.DataFrame(pd.read_csv(url_lead))['created_at'].tolist()


manager_and_lead = {}    # словарь менеджер - количество заявок
managers = []

 # проходим по рабочему листу
for i in range(len(lead_column)):
    if manager_of_lead_column[i] not in managers:
        managers.append(manager_of_lead_column[i])
        manager_and_lead[manager_of_lead_column[i]] = 1
    else:
        manager_and_lead[manager_of_lead_column[i]] = manager_and_lead[manager_of_lead_column[i]] + 1



#--------------------------------------------------------------------------------------------------------------


# ------------------------количество мусорных заявок (на основании заявки не создан клиент)-------------------

manager_and_lead_trash = {} # словарь менеджер - количество мусорных заявок
managers_trash = []

 # проходим по рабочему листу
for i in range(len(lead_column)):
    if client_of_lead_column[i] == '00000000-0000-0000-0000-000000000000':
        if manager_of_lead_column[i] not in managers_trash:
            managers_trash.append(manager_of_lead_column[i])
            manager_and_lead_trash[manager_of_lead_column[i]] = 1
        else:
            manager_and_lead_trash[manager_of_lead_column[i]] = manager_and_lead_trash[manager_of_lead_column[i]] + 1
    else:
        pass


#--------------------------------------------------------------------------------------------------------------

#----------------количество новых заявок (не было заявок и покупок от этого клиента раньше)-------------------

client_of_transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['l_client_id'].tolist()
data_of_transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['created_at'].tolist()



managers_and_lead_new= {}   #словарь менеджер - количество новых заявок
managers_new = []


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
        if manager_of_lead_column[i] not in managers_new:
            managers_new.append(manager_of_lead_column[i])
            managers_and_lead_new[manager_of_lead_column[i]] = 1
        else:
            managers_and_lead_new[manager_of_lead_column[i]] = managers_and_lead_new[manager_of_lead_column[i]] + 1


#--------------------------------------------------------------------------------------------------------------

# ------------------------количество покупателей (кто купил в течение недели после заявки)--------------------

client_of_transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['l_client_id'].tolist()
data_of_transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['created_at'].tolist()
transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['transaction_id'].tolist()

manager_of_client_column = pd.DataFrame(pd.read_csv(url_client_manager))['l_manager_id'].tolist()
client_of_manager_column = pd.DataFrame(pd.read_csv(url_client_manager))['client_id'].tolist()

client_manager = dict(zip(client_of_manager_column, manager_of_client_column))  #словарь клиент и какой у него менеджер




def check_lead_before_transaction(date_transaction, date_lead):   # проверим: что после заявки не прошла неделя
  if ((date_to_sec(date_transaction) - date_to_sec(date_lead)) < 604800):   # в неделе 604800 секунд
    return True
  else:
    return False


def find_date_of_lead(client):     # найдем дату заявки от этого клиента
  for i in range(len(client_of_lead_column )): # ищем клиента в листе заявок
    if client_of_lead_column[i] == client:
      return data_of_lead_column[i] 



managers_and_new_transactions= {}  # cловарь клиент - количество покупателей
managers_transactions_new = []


 # проходим по рабочему листу
for i in range(len(transaction_column)):
  if find_date_of_lead(client_of_transaction_column[i]) != None:
    if check_lead_before_transaction(data_of_transaction_column[i], find_date_of_lead(client_of_transaction_column[i])):
      manager_of_transaction = client_manager[client_of_transaction_column[i]]   # найдем менеджера транзакции (по клиенту)
      if manager_of_transaction not in managers_transactions_new:
        managers_transactions_new.append(manager_of_transaction)
        managers_and_new_transactions[manager_of_transaction] = 1
      else:
        managers_and_new_transactions[manager_of_transaction] = managers_and_new_transactions[manager_of_transaction] + 1




#--------------------------------------------------------------------------------------------------------------


#-----------количество новых покупателей (кто купил в течение недели после заявки, и не покупал раньше)--------

client_of_transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['l_client_id'].tolist()
data_of_transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['created_at'].tolist()
transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['transaction_id'].tolist()

manager_of_client_column = pd.DataFrame(pd.read_csv(url_client_manager))['l_manager_id'].tolist()
client_of_manager_column = pd.DataFrame(pd.read_csv(url_client_manager))['client_id'].tolist()

client_manager = dict(zip(client_of_manager_column, manager_of_client_column))  #словарь клиент и какой у него менеджер



def check_no_transactions_before(date_of_transaction, client):  # проверим не было ли покупок до этого
  for i in range(len(data_of_transaction_column)):
    if client == client_of_transaction_column[i]:
      if (date_to_sec(data_of_transaction_column[i]) < date_to_sec(date_of_transaction)):
        return False
  return True



managers_and_new_transactions_week_after_lead= {}    # словарь менеджер - количество новых покупателей
managers_transactions_new_week_after_lead = []

 # проходим по рабочему листу
for i in range(len(transaction_column)):  
  if find_date_of_lead(client_of_transaction_column[i]) != None:
    if (check_lead_before_transaction(data_of_transaction_column[i], find_date_of_lead(client_of_transaction_column[i])) and (check_no_transactions_before(data_of_transaction_column[i], client_of_transaction_column[i]))):
      manager_of_transaction = client_manager[client_of_transaction_column[i]]   # найдем менеджера транзакции (по клиенту)
      if manager_of_transaction not in managers_transactions_new_week_after_lead:
        managers_transactions_new_week_after_lead.append(manager_of_transaction)
        managers_and_new_transactions_week_after_lead[manager_of_transaction] = 1
      else:
        managers_and_new_transactions_week_after_lead[manager_of_transaction] = managers_and_new_transactions_week_after_lead[manager_of_transaction] + 1


#--------------------------------------------------------------------------------------------------------------

#-----------------------------------доход от покупок новых покупателей-----------------------------------------

client_of_transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['l_client_id'].tolist()
data_of_transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['created_at'].tolist()
transaction_column = pd.DataFrame(pd.read_csv(url_transaction))['transaction_id'].tolist()
transaction_amount_column = pd.DataFrame(pd.read_csv(url_transaction))['m_real_amount'].tolist()

manager_of_client_column = pd.DataFrame(pd.read_csv(url_client_manager))['l_manager_id'].tolist()
client_of_manager_column = pd.DataFrame(pd.read_csv(url_client_manager))['client_id'].tolist()

client_manager = dict(zip(client_of_manager_column, manager_of_client_column))  #словарь клиент и какой у него менеджер





managers_and_new_transactions_amount= {}   # словарь менеджер - доход от покупок новых покупателей
managers_transactions_new_amount = []


# проходим по рабочему листу
for i in range(len(transaction_column)):
  if find_date_of_lead(client_of_transaction_column[i]) != None:
    if (check_lead_before_transaction(data_of_transaction_column[i], find_date_of_lead(client_of_transaction_column[i])) and (check_no_transactions_before(data_of_transaction_column[i], client_of_transaction_column[i]))):
      manager_of_transaction = client_manager[client_of_transaction_column[i]]   # найдем менеджера транзакции (по клиенту)
      if manager_of_transaction not in managers_transactions_new_amount:
        managers_transactions_new_amount.append(manager_of_transaction)
        managers_and_new_transactions_amount[manager_of_transaction] = transaction_amount_column[i]      
      else:        
        managers_and_new_transactions_amount[manager_of_transaction] += transaction_amount_column[i]


#--------------------------------------------------------------------------------------------------------------



#-----------------------------------------запись в CSV---------------------------------------------------------


import csv
csv_file = open("./manager.csv", "w")

writer = csv.writer(csv_file)


writer.writerow(['dimension', 'количество заявок', 'количество мусорных заявок', 'количество новых заявок', 'количество покупателей', 'количество новых покупателей ', 'доход от покупок новых покупателей'])

spisok_tblte = [manager_and_lead_trash, 
                managers_and_lead_new,
                managers_and_new_transactions,
                managers_and_new_transactions_week_after_lead,
                managers_and_new_transactions_amount]

for key, value in manager_and_lead.items():
    row_list = []
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
