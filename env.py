import os
import pandas as pd

home = os.environ.get('HOME')
os.environ.get('HOME')
#print(home)
lang = os.environ.get('LANG')
#print(lang)

try:
    db_conn = os.environ.get('DBCONN')
    print(db_conn)
except:
    pass

from sqlalchemy import create_engine
db = create_engine(db_conn)
conn = db.connect()
print("[db_connection~]",db,conn)

qry000="select * from my_asset"

qry_div_sum = "select to_char(timestamp::timestamp,'YYYY/Mon/DD/HH24:MI') as date, div, round(sum(total_krw)) as total_krw from my_asset group by div, timestamp order by timestamp desc"

qry002 = "SELECT timestamp as date, round(sum(total_krw)) as total FROM my_asset GROUP BY timestamp ORDER BY timestamp desc"

res = pd.read_sql(qry_div_sum, conn, index_col=None)
print(res)#.to_markdown(floatfmt=',.2f'))

