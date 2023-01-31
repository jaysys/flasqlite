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

'''
how-to set environ on Win(PS) & Mac
>> $env:DBCONN="postgresql://~~~~ @~:~/mydb"
>> export = ""
'''

from sqlalchemy import create_engine
db = create_engine(db_conn)
conn = db.connect()
print("connected:",db,conn)

qry_all="select * from my_asset"

qr_each_div_sum = "select to_char(timestamp::timestamp,'YYYY/Mon/DD/HH24:MI') as date, div, round(sum(total_krw)) as total_krw from my_asset group by div, timestamp order by timestamp asc"

qr_each_div_sum2 = "select timestamp::timestamp as date, div, round(sum(total_krw)) as total_krw from my_asset group by div, timestamp order by timestamp asc"

'''
pandas 이용한 query
'''
# df = pd.read_sql(qr_each_div_sum, conn)
# print(df)

'''
raw sql query
'''
from pprint import pprint
crypto = []
stock = []
cash = []
date = []
with db.connect() as con:
    rs = con.execute(qr_each_div_sum2)
    for row in rs:
        if row[1] == 'CRYPTO':
            date.append(row[0])
            crypto.append(row[2])
        elif row[1] == 'STOCK':
            stock.append(row[2])
        elif row[1] == 'CASH':
            cash.append(row[2])
        else:
            pass
    

import matplotlib.pyplot as plt
dframe = pd.DataFrame({
    'crypto': crypto,
    'stock': stock,
    'cash': cash,}, 
    index=date)
print(dframe)


'''
1.판다스&맷플랏 이용한 데이터프레임 누적영역라인 출력
'''
# dframe.plot.area(stacked=True) #stacked=False
# plt.show()


'''
2.보케 누적영역라인
'''
from bokeh.palettes import brewer
from bokeh.palettes import Spectral11
from bokeh.plotting import figure, show, output_notebook
n = dframe.shape[1]
p = figure(width=1000, height=600, x_axis_type='datetime')
p.varea_stack(stackers=dframe.columns, 
            x='index', 
            source=dframe, 
            color=brewer['Spectral'][n])
show(p)


'''
3.보케 멀티싱글라인
'''
numlines = len(dframe.columns)
mypalette = Spectral11[0:numlines]
p = figure(width=1000, height=600, x_axis_type="datetime") 
p.multi_line(xs = [dframe.index.values]*numlines,
            ys = [dframe[name].values for name in dframe],
            line_color = mypalette,
            line_width = 1.5)
show(p)


# qr_crypto = "select div, to_char(timestamp::timestamp,'YYYY/Mon/DD/HH24:MI') as date, round(sum(total_krw)) as total_krw from my_asset where div = 'CRYPTO' group by div, timestamp order by timestamp desc"
# df_crypto = pd.read_sql(qr_crypto, conn, index_col=None)

# qr_stock = "select div, to_char(timestamp::timestamp,'YYYY/Mon/DD/HH24:MI') as date, round(sum(total_krw)) as total_krw from my_asset where div = 'STOCK' group by div, timestamp order by timestamp desc"
# df_stock = pd.read_sql(qr_stock, conn, index_col=None)
# print(df_stock)#.to_markdown(floatfmt=',.2f'))

# qr_cash = "select div, to_char(timestamp::timestamp,'YYYY/Mon/DD/HH24:MI') as date, round(sum(total_krw)) as total_krw from my_asset where div = 'CASH' group by div, timestamp order by timestamp desc"
# df_cash = pd.read_sql(qr_cash, conn, index_col=None)
# print(df_each_div_sum)#.to_markdown(floatfmt=',.2f'))


'''
raw sql query
'''
# st_quiry = "select * from todo order by date_created desc"
# with db.connect() as con:
#     rs = con.execute(st_quiry)
#     for row in rs:
#         print (row)


'''
insert data
'''
# from sqlalchemy.sql import text
# from datetime import datetime
# with db.connect() as con:
#     data = ( { "id": 101, "content": "The Hobbit", "date_created": datetime.now() },
#              { "id": 102, "content": "The Silmarillion", "date_created": datetime.now() },
#     )
#     statement = text("""INSERT INTO todo(id, content, date_created) VALUES(:id, :content, :date_created)""")
#     for line in data:
#         con.execute(statement, **line)

