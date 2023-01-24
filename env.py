import os

home = os.environ.get('HOME')
os.environ.get('HOME')
print(home)

lang = os.environ.get('LANG')
print(lang)

try:
    db_conn = os.environ.get('DBCONN')
    print(db_conn)
except:
    pass
