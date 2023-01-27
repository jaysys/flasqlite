import os
import pandas as pd

home = os.environ.get('HOME')
os.environ.get('HOME')
#print(home)
lang = os.environ.get('LANG')
#print(lang)

try:
    db_conn = os.environ.get('DBCONN')
    print("[db]",db_conn)
except:
    pass

from sqlalchemy import create_engine
db = create_engine(db_conn)
conn = db.connect()
print("connected:",db,conn)

qry_all="select * from my_asset"

qr_each_div_sum = "select to_char(timestamp::timestamp,'YYYY/Mon/DD/HH24:MI') as date, div, round(sum(total_krw)) as total_krw from my_asset group by div, timestamp order by timestamp desc"
df = pd.read_sql(qr_each_div_sum, conn)
print(df)#.to_markdown(floatfmt=',.2f'))
print(df.head(5))

# qr_crypto = "select div, to_char(timestamp::timestamp,'YYYY/Mon/DD/HH24:MI') as date, round(sum(total_krw)) as total_krw from my_asset where div = 'CRYPTO' group by div, timestamp order by timestamp desc"
# df_crypto = pd.read_sql(qr_crypto, conn, index_col=None)

# qr_stock = "select div, to_char(timestamp::timestamp,'YYYY/Mon/DD/HH24:MI') as date, round(sum(total_krw)) as total_krw from my_asset where div = 'STOCK' group by div, timestamp order by timestamp desc"
# df_stock = pd.read_sql(qr_stock, conn, index_col=None)
# print(df_stock)#.to_markdown(floatfmt=',.2f'))

# qr_cash = "select div, to_char(timestamp::timestamp,'YYYY/Mon/DD/HH24:MI') as date, round(sum(total_krw)) as total_krw from my_asset where div = 'CASH' group by div, timestamp order by timestamp desc"
# df_cash = pd.read_sql(qr_cash, conn, index_col=None)
# print(df_each_div_sum)#.to_markdown(floatfmt=',.2f'))



'''
import matplotlib.pyplot as plt
dframe = pd.DataFrame({
    'sales': [10, 2, 3, 9, 10, 6],
    'signups': [10, 5, 6, 12, 14, 13],
    'visits': [20, 42, 28, 62, 81, 50],}, 
    index=pd.date_range(start='2018/01/01', end='2018/07/01',freq='M'))
dframe.plot.area(stacked=True) #stacked=False
plt.show()
'''



