import pandas as pd
from sqlalchemy import create_engine 
import psycopg2
import os

'''
Sample Dataframe data
'''
data = {'name': ['John', 'Bick', 'Cherry'],
		'age' : [   212,     211,     214] }


'''
DB connection
''' 
try:
    conn_string = os.environ.get('DBCONN')  # export DBCONN='postgresql://aaa:pwd@0.0.0.0:8888/mydb'
    print(conn_string)
except:
    pass
# connect - sqlachmey use case
db = create_engine(conn_string)
conn = db.connect()
print(db,conn)


'''
Store & Read DataFrame 
'''
df = pd.DataFrame(data)
# write
df.to_sql('pandas_data', con=conn, if_exists='replace',index=True)  #replace , append
# read 
df_rs = pd.read_sql("SELECT * FROM pandas_data", conn)
print(df_rs) 
conn.close()

'''
Read by Rraw_sql_query with psycopg2
'''
# connect - psycopg2 use case
conn_string = 'postgresql://jaysys:234567@svc.gksl2.cloudtype.app:32023/mydb'
conn2 = psycopg2.connect(conn_string)
conn2.autocommit = True

# read
cursor = conn2.cursor()
sql1 = '''select * from pandas_data;'''
cursor.execute(sql1)
print("[1]")
for i in cursor.fetchall():
	print(i)

# insert
sql2 = '''INSERT INTO pandas_data(index, name, age) VALUES (0, 'Hong', 23);'''
cursor.execute(sql2)
conn2.commit()
cursor.execute(sql1)
print("[2]")
for i in cursor.fetchall():
	print(i)

# update
sql3 = '''UPDATE pandas_data SET name = 'CHONG', age = 39  WHERE index = 0;'''
cursor.execute(sql3)
conn2.commit()
cursor.execute(sql1)
print("[3]")
for i in cursor.fetchall():
	print(i)

# delete
sql4 = '''DELETE from pandas_data WHERE index = 0;'''
cursor.execute(sql4)
conn2.commit()
cursor.execute(sql1)
print("[4]")
for i in cursor.fetchall():
	print(i)

print("Thanks")
conn2.close()





'''
====================================
pd.read_sql
'''
db = create_engine(conn_string)
conn = db.connect()
df_rs = pd.read_sql("SELECT * FROM pandas_data", conn)
conn.close()
print(df_rs) 
