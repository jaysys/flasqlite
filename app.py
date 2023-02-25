import os
import openai
import pandas as pd
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session
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
    #print(db_conn_string,openai.api_key)
except:
    pass

app = Flask(__name__)

app.config['SECRET_KEY'] = db_conn_string #'mysecretkey' - 일단같은걸로해서...
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = db_conn_string  #'postgresql://id:pwd@ip:port/dbname'
    
'''
postgresql DB connect & crud web page excercise 
'''

with app.app_context():
    db = SQLAlchemy(app)

class Todo(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.String(100), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


@app.route("/")
def index():
    if 'username' in session:
        username = session['username']
        return render_template('index.html', username=username)
    else:
        return redirect(url_for('login'))

    # return render_template('index.html',username = 'aa')


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
metamask crypto web3 connect & query balance
'''
@app.route('/meta')
def meta():
    return render_template('meta.html')



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

        # Query the database for the rows to display on this page
        # query = text("SELECT div, asset, to_char(qty,'9,999,999,999.999') as qty, to_char(total_krw,'9,999,999,999.9') as total_krw, asset_note, timestamp  FROM my_asset WHERE total_krw > 1000 ORDER BY timestamp DESC, asset_note, total_krw DESC LIMIT :rows_per_page OFFSET :start_index")
        # df = pd.read_sql(query, engine, params={"rows_per_page": ROWS_PER_PAGE, "start_index": start_index})
        # with engine.connect() as conn:
        #     df = pd.read_sql(query, conn)

        # Query the database for the rows to display on this page
        # query = text("SELECT div, asset, to_char(qty,'9,999,999,999.999') as qty, to_char(total_krw,'9,999,999,999.9') as total_krw, asset_note, timestamp  FROM my_asset WHERE total_krw > 1000 ORDER BY timestamp DESC, asset_note, total_krw DESC LIMIT :rows_per_page OFFSET :start_index")
        # df = pd.read_sql(query, engine, params={"rows_per_page": ROWS_PER_PAGE, "start_index": start_index})

        engine = create_engine(db_conn_string)
        conn = engine.connect()
        query = text("SELECT div, asset, to_char(qty,'9,999,999,999.999') as qty, to_char(total_krw,'9,999,999,999.9') as total_krw, asset_note, timestamp  FROM my_asset WHERE total_krw > 1000 ORDER BY timestamp DESC, asset_note, total_krw DESC LIMIT :rows_per_page OFFSET :start_index")
        result = conn.execute(query, {"rows_per_page": ROWS_PER_PAGE, "start_index": start_index})
        df = pd.DataFrame(result.fetchall())
        df.columns = result.keys()
        conn.close()

        # Query the database for the rows to display on this page
        # query = f"SELECT div, asset, to_char(qty,'9,999,999,999.999') as qty, to_char(total_krw,'9,999,999,999.9') as total_krw, asset_note, timestamp  FROM my_asset WHERE total_krw > 1000 ORDER BY timestamp DESC, asset_note, total_krw DESC LIMIT {ROWS_PER_PAGE} OFFSET {start_index}"
        # df = pd.read_sql(query, engine)

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
flare
'''
@app.route("/flare")
def flarebalance():
    # print(my_address)
    # return redirect(url_for('index'))
    if 'username' in session:
        username = session['username']
        print(my_address)

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

        # Render the template with the balance values
        return render_template('flare.html', address=address, 
                               flare_balance=flare_balance, 
                               songbird_balance=songbird_balance, username=username)
    else:
        return redirect(url_for('login'))  


'''
flare
'''
@app.route("/arbi")
def arbitrumbalance():
    if 'username' in session:
        username = session['username']
        print(my_address)

        # Connect to the Arbitrum network using an RPC endpoint
        arbitrum = Web3(Web3.HTTPProvider('https://arb1.arbitrum.io/rpc'))

        # Convert the Ethereum address to checksum format
        address = Web3.toChecksumAddress(my_address)

        # Get the balance of the address on the Arbitrum network
        balance = arbitrum.eth.get_balance(address)

        # Convert the balance values to decimal units
        balance = Web3.fromWei(balance, 'ether')

        # Render the template with the balance values
        return render_template('arbi.html', address=address, balance=balance, username=username)
    else:
        return redirect(url_for('login'))



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
