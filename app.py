import os
import openai
import pandas as pd
import psycopg2
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import create_engine, text
from bokeh.embed import components
from bokeh.plotting import figure, show
from bokeh.resources import INLINE
from bokeh.models import DatetimeTickFormatter, NumeralTickFormatter
from web3 import Web3

try:
    db_conn_string = os.environ.get('DBCONN')
    openai.api_key = os.environ.get('OPENAI')
    my_address = os.environ.get('ADDRS')
except:
    pass

app = Flask(__name__)

@app.route("/")
def index():
    # if 'username' in session:
        username = session['username']
        return render_template('index.html', username=username)
    # else:
    #     return redirect(url_for('login'))



'''
login function
'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = psycopg2.connect(app.config['SQLALCHEMY_DATABASE_URI'])
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    else:
        return render_template('login.html')



'''
log out
'''
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


'''
reister new user
'''
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        conn = psycopg2.connect(app.config['SQLALCHEMY_DATABASE_URI'])
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        if user:
            cur.close()
            conn.close()
            return render_template('register.html', error='Username already exists')
        else:
            cur.execute('INSERT INTO users (username, password, email) VALUES (%s, %s, %s)', (username, password,email))
            conn.commit()
            cur.close()
            conn.close()
            session['username'] = username
            return redirect(url_for('index'))
    else:
        return render_template('register.html')



'''
sample html pages
'''
@app.route('/tailcss')
def tailcss():
    html = render_template(
        'tailcss.html'
    )
    return (html)

@app.route("/exam")
def exam():
    return render_template('exam70.html') #통신

@app.route("/exam2")
def exam2():
    return render_template('exam02.html') #건축




'''
postgresql DB connect & crud web page excercise 
'''
app.config['SECRET_KEY'] = db_conn_string #'mysecretkey' - 일단같은걸로해서...
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = db_conn_string  #'postgresql://id:pwd@ip:port/dbname'
    
with app.app_context():
    db = SQLAlchemy(app)

class Todo(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.String(100), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


@app.route('/task', methods=['POST', 'GET'])
def task():
    if 'username' in session:
        username = session['username']
        #accessible only when logged in
        if request.method == 'POST':
            task_content = request.form['content']
            task_completed = request.form['completed']
            new_task = Todo(content=task_content, completed=task_completed)

            try:
                db.session.add(new_task)
                db.session.commit()
                return redirect('/task')
            except:
                return 'There was an issue adding your task'
        else:
            tasks = Todo.query.order_by(Todo.date_created).all()
            return render_template('task.html', tasks=tasks, username=username)
    else:
        return redirect(url_for('login'))

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/task')
    except:
        return 'There was a problem deleting that task'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']
        task.completed = request.form['completed']

        try:
            db.session.commit()
            return redirect('/task')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=task)



'''
chatGPT excercise
'''
@app.route("/gpt")
def gpt():
    if 'username' in session:
        username = session['username']
        #accessible only when logged in
        return render_template("chat.html", username=username)
    else:
        return redirect(url_for('login'))


@app.route("/chat", methods=["POST"])
def chat():
    prompt = request.form["prompt"]
    print(prompt)
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = completions.choices[0].text
    # aa = message.replace("\n","<br />\n")
    # ans = aa.replace("\t","&nbsp&nbsp&nbsp&nbsp")
    print(message)
    ans = message
    return ans


   
'''
dataframe & bokeh combination excercise
'''
@app.route('/dfbokeh')
def dfbokeh():   

    engine = create_engine(db_conn_string)
    conn = engine.connect()

    query = text("SELECT timestamp as date, round(sum(total_krw)) as total FROM my_asset GROUP BY timestamp ORDER BY timestamp desc")
    result = conn.execute(query)
    df_div = pd.DataFrame(result.fetchall())

    query = text("SELECT timestamp as date, round(sum(total_krw)) as total FROM my_asset WHERE div = 'STOCK' GROUP BY timestamp, div ORDER BY timestamp desc")
    result = conn.execute(query)
    df_div_stock = pd.DataFrame(result.fetchall())

    query = text("SELECT timestamp as date, round(sum(total_krw)) as total FROM my_asset WHERE div = 'CRYPTO' GROUP BY timestamp, div ORDER BY timestamp desc")
    result = conn.execute(query)
    df_div_crypto = pd.DataFrame(result.fetchall())

    query = text("SELECT timestamp as date, round(sum(total_krw)) as total FROM my_asset WHERE div = 'CASH' GROUP BY timestamp, div ORDER BY timestamp desc")
    result = conn.execute(query)
    df_div_cash = pd.DataFrame(result.fetchall())

    conn.close()

    ### ---
    rows = df_div.shape[0]
    cols = df_div.shape[1]
    total = '{:,}'.format(df_div['total'][0])   #'{:,}'.format(value)
    date = (df_div['date'][0])
    print(">>total>>",rows,cols,date,total, "<<<")
    fig = figure(width=1000, height=500 ) #, tools=[HoverTool()], tooltips="@x == @y",)
    ax = pd.to_datetime(df_div["date"])
    ay = df_div['total'] 
    #fig.circle(ax, ay , size=1, color="black", alpha=1)#, x_axis_type="datetime")
    fig.line(ax, ay, color="green", alpha=1)#, x_axis_type="datetime")
    fig.yaxis[0].formatter = NumeralTickFormatter(format="0,0")
    fig.xaxis[0].formatter = DatetimeTickFormatter(months="%F")
    #fig.xgrid.grid_line_color = "olive"
    fig.ygrid.band_fill_color = "olive"
    fig.ygrid.band_fill_alpha = 0.1
    #fig.sizing_mode = 'scale_width'
 

    ### ---
    rows = df_div_stock.shape[0]
    cols = df_div_stock.shape[1]
    total_stock = '{:,}'.format(df_div_stock['total'][0])   #'{:,}'.format(value)
    date2 = (df_div_stock['date'][0])
    print(">>stock_total>>",rows,cols,date,total_stock, "<<<")
    fig2 = figure(width=1000, height=500 ) #, tools=[HoverTool()], tooltips="@x == @y",)
    ax2 = pd.to_datetime(df_div_stock["date"])
    ay2 = df_div_stock['total'] 
    #fig2.circle(ax, ay , size=1, color="black", alpha=1)#, x_axis_type="datetime")
    fig2.line(ax2, ay2, color="green", alpha=1)#, x_axis_type="datetime")
    fig2.yaxis[0].formatter = NumeralTickFormatter(format="0,0")
    fig2.xaxis[0].formatter = DatetimeTickFormatter(months="%F")
    #fig2.xgrid.grid_line_color = "olive"
    fig2.ygrid.band_fill_color = "olive"
    fig2.ygrid.band_fill_alpha = 0.1
    #fig2.sizing_mode = 'scale_width'


    ### ---
    rows = df_div_crypto.shape[0]
    cols = df_div_crypto.shape[1]
    total_crypto = '{:,}'.format(df_div_crypto['total'][0])   #'{:,}'.format(value)
    date3 = (df_div_crypto['date'][0])
    print(">>stock_crypto>>",rows,cols,date3,total_crypto, "<<<")
    fig3 = figure(width=1000, height=500 ) #, tools=[HoverTool()], tooltips="@x == @y",)
    ax3 = pd.to_datetime(df_div_crypto["date"])
    ay3 = df_div_crypto['total'] 
    #fig2.circle(ax3, ay3 , size=1, color="black", alpha=1)#, x_axis_type="datetime")
    fig3.line(ax3, ay3, color="green", alpha=1)#, x_axis_type="datetime")
    fig3.yaxis[0].formatter = NumeralTickFormatter(format="0,0")
    fig3.xaxis[0].formatter = DatetimeTickFormatter(months="%F")
    #fig3.xgrid.grid_line_color = "olive"
    fig3.ygrid.band_fill_color = "olive"
    fig3.ygrid.band_fill_alpha = 0.1
    #fig3.sizing_mode = 'scale_width'

    ### ---
    rows = df_div_cash.shape[0]
    cols = df_div_cash.shape[1]
    total_cash = '{:,}'.format(df_div_cash['total'][0])   #'{:,}'.format(value)
    date4 = (df_div_cash['date'][0])
    print(">>stock_cash>>",rows,cols,date3,total_cash, "<<<")
    fig4 = figure(width=1000, height=500 ) #, tools=[HoverTool()], tooltips="@x == @y",)
    ax4 = pd.to_datetime(df_div_cash["date"])
    ay4 = df_div_cash['total'] 
    #fig4.circle(ax3, ay3 , size=1, color="black", alpha=1)#, x_axis_type="datetime")
    fig4.line(ax4, ay4, color="green", alpha=1)#, x_axis_type="datetime")
    fig4.yaxis[0].formatter = NumeralTickFormatter(format="0,0")
    fig4.xaxis[0].formatter = DatetimeTickFormatter(months="%F")
    #fig4.xgrid.grid_line_color = "olive"
    fig4.ygrid.band_fill_color = "olive"
    fig4.ygrid.band_fill_alpha = 0.1
    #fig4.sizing_mode = 'scale_width'

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(fig)
    script2, div2 = components(fig2)
    script3, div3 = components(fig3)
    
    script4, div4 = components(fig4)
    html = render_template(
        'dfbokeh.html',
        plot_script=script,
        plot_script_stock=script2,
        plot_script_crypto=script3,
        plot_script_cash=script4,

        plot_div=div,
        plot_div_stock = div2,
        plot_div_crypto = div3,
        plot_div_cash = div4,
        
        js_resources=js_resources,
        css_resources=css_resources,
        total = total,
        date = date,
        total_stock = total_stock,
        date2 = date2,
        total_crypto = total_crypto,
        date3 = date3,
        total_cash = total_cash,
        date4 = date4
    )
    return (html)


'''
pandas dataframe to_html() excercise
'''
# Function to format number with commas
def format_with_commas(number):
    return "{:,}".format(number)

@app.route('/snapshot')
def snapshot():
    if 'username' in session:
        username = session['username']

        engine = create_engine(db_conn_string)
        conn = engine.connect()

        query = text("select to_char(timestamp::timestamp,'YYYY/Mon/DD/HH24:MI') as date, asset_note, round(sum(total_krw)) as total_krw from my_asset group by asset_note, timestamp order by timestamp desc, total_krw desc limit 14")
        result = conn.execute(query)
        
        df_div = pd.DataFrame(result.fetchall())
        df_div.columns = result.keys()
        conn.close()

        df_div['total_krw'] = df_div['total_krw'].apply(format_with_commas)
        html_table = df_div.to_html(classes='dfmystyle') #####!

        #write html to file
        # with open("templates/history_t.html", "w") as text_file:
        #     text_file.write(html_table)

        html = render_template('snapshot.html', tab = html_table, username=username)
        return (html)
    else:
        return redirect(url_for('login'))



'''
paginated data browsing
'''
# Define the database connection
engine = create_engine(db_conn_string)
# Set the number of rows to show per page
ROWS_PER_PAGE = 25

@app.route('/transaction')
def transaction():
    if 'username' in session:
        username = session['username']

        # Get the page number from the request arguments
        page = request.args.get('page', default=1, type=int)

        # Calculate the starting index and ending index for the page
        start_index = (page - 1) * ROWS_PER_PAGE
        end_index = start_index + ROWS_PER_PAGE

        engine = create_engine(db_conn_string)
        conn = engine.connect()

        query = text("SELECT div, asset, to_char(qty,'9,999,999,999.999') as qty, to_char(total_krw,'9,999,999,999.9') as total_krw, asset_note, timestamp  FROM my_asset WHERE total_krw > 1000 ORDER BY timestamp DESC, asset_note, total_krw DESC LIMIT :rows_per_page OFFSET :start_index")

        result = conn.execute(query, {"rows_per_page": ROWS_PER_PAGE, "start_index": start_index})
        df = pd.DataFrame(result.fetchall())
        df.columns = result.keys()
        conn.close()

        # Check if there are any more rows to display
        has_next_page = len(df) == ROWS_PER_PAGE

        # Disable previous button on first page
        has_prev_page = page > 1

        # Render the template with the data
        return render_template('transaction.html', transactions=df.to_dict('records'), 
                            has_next_page=has_next_page, has_prev_page=has_prev_page,
                            next_page=page + 1, prev_page=page - 1, username=username)
    
    else:
        return redirect(url_for('login'))


'''
bokeh excercise
'''
@app.route('/bokeh')
def bokeh():
    # init a basic bar chart:
    # http://bokeh.pydata.org/en/latest/docs/user_guide/plotting.html#bars
    fig = figure(width=600, height=400)
    ax = [1, 2, 3, 4, 5]
    ay = [6, 7, 2, 4, 5]
    fig.circle(ax, ay , size=5, color="red", alpha=0.8)
    # fig.vbar( x=[0,1,2,3,4,5,6], top=[11.7, 12.2, 14.6, 13.9,5,16,12] ,width=0.2, bottom=0, color='green')

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(fig)
    html = render_template(
        'bokeh.html',
        plot_script = script,
        plot_div = div,
        js_resources = js_resources,
        css_resources = css_resources,
    )
    return (html)
 


'''
typescript sample page
'''
@app.route('/tyscript', methods=["GET"]) #
def tyscript():
    # Create or load a dataframe
    df = pd.DataFrame()
    df['name'] = ['Celo', 'Jake', 'Eth', 'Glyp', 'Ada']
    df['num'] = list(range(5))
    df['score'] = list(range(12,17))

    # Send values as list of lists
    data = df.values.tolist()
    print(data)

    return render_template('tyscript.html', data=data)



'''
metamask connect & query balance
'''
@app.route('/meta')
def meta():
    return render_template('meta.html')


'''
crypto unit price query
'''
@app.route('/price', methods=['GET', 'POST'])
def price():
    coin = None
    price = None
    if request.method == 'POST':
        coin = request.form['coin']
        price = crypto_unit_price(coin)
        print(price)
    else:
        price = None
    return render_template('price.html', coin=coin.upper() if coin else None, price=price)

def crypto_unit_price(coin):
    param = coin
    api_endpoint = "https://cryptoprices.cc/"

    try:
        response = requests.get(api_endpoint+param.upper(), timeout=5)
        response.raise_for_status()
        price = response.text.strip()
        return float(price)

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        return -1.0

    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
        return -1.0

    except requests.exceptions.Timeout as e:
        print(f"Request timed out: {e}")
        return -1.0

    except Exception as e:
        print(f"An error occurred: {e}")
        return -1.0


'''
ethereum network
'''
def ethereum_eth_balance():
    '''
    ETH
    '''
    # Connect to the network using an RPC endpoint
    w3 = Web3(Web3.HTTPProvider('https://ethereum-mainnet-rpc.allthatnode.com'))
    # Convert the Ethereum address to checksum format
    address = w3.toChecksumAddress(my_address)
    # Get the balance of the address on the network
    eth_bal = w3.eth.get_balance(address)
    # Convert the balance values to decimal units
    eth_bal = Web3.fromWei(eth_bal, 'ether')
    eth_unit_price = crypto_unit_price("ETH")
    print(f"eth:{eth_unit_price}, balance:{eth_bal}")
    return(eth_unit_price, eth_bal)




'''
polygon network
'''
def polygon_matic_balance():
    '''
    MATIC
    '''
    # Connect to the network using an RPC endpoint
    w3 = Web3(Web3.HTTPProvider('https://rpc-mainnet.maticvigil.com/'))
    # Convert the Ethereum address to checksum format
    address = w3.toChecksumAddress(my_address)
    # Get the balance of the address on the network
    matic_bal = w3.eth.get_balance(address)
    # Convert the balance values to decimal units
    matic_bal = Web3.fromWei(matic_bal, 'ether')
    matic_unit_price = crypto_unit_price("MATIC")
    print(f"matic:{matic_unit_price}, balance:{matic_bal}")
    return(matic_unit_price, matic_bal)

'''
gmx on arbitrum
'''
def gmx_balance():
    '''
    GMX
    '''
    w3 = Web3(Web3.HTTPProvider('https://arb1.arbitrum.io/rpc'))
    gmx_contract_address = '0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a'
    gmx_contract_address = Web3.toChecksumAddress(gmx_contract_address)
    with open('static/abi/abi_gmx.json', 'r') as f:
        abi = json.load(f)
    gmx_contract = w3.eth.contract(address=gmx_contract_address, abi=abi)
    gmx_bal = gmx_contract.functions.balanceOf(my_address).call() / 1000000000000000000
    print(f'GMX balance is {gmx_bal}')

    '''
    sbfGMX
    '''
    w3 = Web3(Web3.HTTPProvider('https://arb1.arbitrum.io/rpc'))
    sbfgmx_contract_address = '0xd2d1162512f927a7e282ef43a362659e4f2a728f'
    sbfgmx_contract_address = Web3.toChecksumAddress(sbfgmx_contract_address)
    with open('static/abi/abi_gmx.json', 'r') as f:
        abi = json.load(f)
    sbfgmx_contract = w3.eth.contract(address=sbfgmx_contract_address, abi=abi)
    sbfgmx_bal = sbfgmx_contract.functions.balanceOf(my_address).call() / 1000000000000000000
    print(f'sbfGMX balance is {sbfgmx_bal}')

    return(gmx_bal, sbfgmx_bal)



'''
WFLR, WSGB on flare/songbird network
'''
def wrapped_flare_balance():
    '''
    WFLR
    '''
    # Replace with your own node endpoint URL
    w3 = Web3(Web3.HTTPProvider('https://flare-api.flare.network/ext/C/rpc'))
    # WrappedFLR contract address
    wflr_contract_address = '0x1D80c49BbBCd1C0911346656B529DF9E5c2F783d'
    # wflr_contract_address = Web3.toChecksumAddress(wflr_contract_address)
    with open('static/abi/abi_wflr.json', 'r') as f:
        abi = json.load(f)
    _contract = w3.eth.contract(address=wflr_contract_address, abi=abi)
    wflr_bal = _contract.functions.balanceOf(my_address).call() / 1000000000000000000
    print(f'WFLR balance is {wflr_bal}')

    '''
    WSGB
    '''
    w3 = Web3(Web3.HTTPProvider('https://sgb.ftso.com.au/ext/bc/C/rpc'))
    wsgb_contract_address = "0x02f0826ef6ad107cfc861152b32b52fd11bab9ed"
    wsgb_contract_address = Web3.toChecksumAddress(wsgb_contract_address)
    with open('static/abi/abi_wsgb.json', 'r') as f:
        abi = json.load(f)
    _contract = w3.eth.contract(address=wsgb_contract_address, abi=abi)
    wsgb_bal = _contract.functions.balanceOf(my_address).call() / 1000000000000000000
    print(f'WSGB balance is {wsgb_bal}')

    return(wflr_bal, wsgb_bal)


'''
Web3 connect 
'''
@app.route("/web3")
def web3start():
    print(my_address[:6]+".......(web3)")

    if 'username' in session:
        username = session['username']
        print(my_address[:6]+".......")

        eth_price, eth_bal = ethereum_eth_balance()
        matic_price, matic_bal = polygon_matic_balance()

        #arbitrum
        # Connect to the Arbitrum network using an RPC endpoint
        arbitrum = Web3(Web3.HTTPProvider('https://arb1.arbitrum.io/rpc'))
        # Convert the Ethereum address to checksum format
        address = Web3.toChecksumAddress(my_address)
        # Get the balance of the address on the Arbitrum network
        balance = arbitrum.eth.get_balance(address)
        # Convert the balance values to decimal units
        aeth_balance = Web3.fromWei(balance, 'ether')
        gmx_bal, sbfgmx_bal = gmx_balance()
        gmx = crypto_unit_price("GMX")
        eth = crypto_unit_price("ETH")

        #flare&sgb
        # Connect to the Flare and Songbird networks using Web3
        flare = Web3(Web3.HTTPProvider('https://flare-api.flare.network/ext/C/rpc'))
        songbird = Web3(Web3.HTTPProvider('https://sgb.ftso.com.au/ext/bc/C/rpc'))
        address = Web3.toChecksumAddress(my_address)
        # Get the balance of Flare and Songbird coins for the specified address
        flare_balance = flare.eth.getBalance(address)
        songbird_balance = songbird.eth.getBalance(address)
        # Convert the balance values to decimal units
        flare_balance = Web3.fromWei(flare_balance, 'ether')
        songbird_balance = Web3.fromWei(songbird_balance, 'ether')
        wflr_bal, wsgb_bal = wrapped_flare_balance()
        flr = crypto_unit_price("FLR")
        sgb = crypto_unit_price("SGB")

        return render_template('web3.html', address=address[:6]+"......", 
                            eth="{:,.3f}".format(eth), gmx="{:,.3f}".format(gmx), 
                            flr="{:,.3f}".format(flr), sgb="{:,.3f}".format(sgb),
                            eth_price="{:,.3f}".format(eth_price), eth_bal="{:,.3f}".format(eth_bal), eth_total="{:,.2f}".format(float(str(eth_bal))*float(str(eth_price))),
                            matic_price="{:,.3f}".format(matic_price), matic_bal="{:,.3f}".format(matic_bal), matic_total="{:,.2f}".format(float(str(matic_bal))*float(str(matic_price))),
                            aeth_balance="{:,.3f}".format(aeth_balance), 
                            aeth_total="{:,.2f}".format(float(str(aeth_balance))*float(str(eth))),
                            gmx_balance="{:,.3f}".format(gmx_bal), 
                            gmx_total="{:,.2f}".format(float(str(gmx_bal))*float(str(gmx))),
                            sbfgmx_balance="{:,.3f}".format(sbfgmx_bal), 
                            sbfgmx_total="{:,.2f}".format(float(str(gmx))*float(str(sbfgmx_bal))),
                            flare_balance="{:,.3f}".format(flare_balance), 
                            flr_total="{:,.2f}".format(float(str(flare_balance))*float(str(flr))),
                            songbird_balance="{:,.3f}".format(songbird_balance), 
                            sgb_total="{:,.2f}".format(float(str(sgb))*float(str(songbird_balance))),
                            flare_staked="{:,.3f}".format(wflr_bal), 
                            wflr_total="{:,.2f}".format(float(str(wflr_bal))*float(str(flr))),
                            sgb_staked="{:,.3f}".format(wsgb_bal), 
                            wsgb_total="{:,.2f}".format(float(str(wsgb_bal))*float(str(sgb))),
                            username=username)
    else:
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)

