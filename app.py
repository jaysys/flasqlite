import os
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from bokeh.embed import components
from bokeh.plotting import figure, show
from bokeh.resources import INLINE
from bokeh.models import DatetimeTickFormatter, NumeralTickFormatter
import openai

try:
    db_conn = os.environ.get('DBCONN')
    openai.api_key = os.environ.get('OPENAI')
    #print(db_conn,openai.api_key)
except:
    pass

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = db_conn  # 'postgresql://id:password@127.0.0.1:port/dbname'
with app.app_context():
    db = SQLAlchemy(app)

class Todo(db.Model):
    '''
    DB table
    '''
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.String(100), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


@app.route("/")
def index():
    return render_template('./index.html')

@app.route("/exam")
def exam():
    return render_template('exam70.html')

@app.route('/task', methods=['POST', 'GET'])
def task():
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
        return render_template('task.html', tasks=tasks)


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


@app.route('/meta')
def meta():
    return render_template('meta.html')


@app.route('/bokeh')
def bokeh():
    # init a basic bar chart:
    # http://bokeh.pydata.org/en/latest/docs/user_guide/plotting.html#bars

    fig = figure(width=600, height=400)

    # fig.vbar(
    #     x=[0,1,2,3,4,5,6],
    #     top=[11.7, 12.2, 14.6, 13.9,5,16,12] #,width=0.2, bottom=0, color='green'
    # )

    ax = [1, 2, 3, 4, 5]
    ay = [6, 7, 2, 4, 5]
    fig.circle(ax, ay , size=5, color="red", alpha=0.8)
    
    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(fig)
    html = render_template(
        'bokeh.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
    )
    return (html)
    
@app.route('/tailcss')
def tailcss():
    fig = figure(width=600, height=400)
    ax = [1, 2, 3, 4, 5]
    ay = [6, 7, 2, 4, 5]
    fig.circle(ax, ay , size=5, color="red", alpha=0.8)
    
    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(fig)
    html = render_template(
        'tailcss.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
    )
    return (html)


@app.route('/history')
def history():
    db = create_engine(db_conn)
    conn = db.connect()
    print("[db_connection]",db,conn)

    if True:
        #df_div = pd.read_sql("SELECT TO_CHAR(timestamp::timestamp,'YYYY/Mon/DD/HH24:MI') as date, div, round(sum(total_krw)) as total FROM my_asset GROUP BY timestamp, div ORDER BY timestamp desc", conn)
        df_div = pd.read_sql("SELECT TO_CHAR(timestamp::timestamp,'YYYY/Mon/DD/HH24:MI') as date, div, round(sum(total_krw)) as total FROM my_asset WHERE div != 'CASH' GROUP BY timestamp, div ORDER BY div, timestamp desc", conn)
    
    html = df_div.to_html()

    #write html to file
    with open("templates/history.html", "w") as text_file:
        text_file.write(html)

    print(df_div)#.to_markdown(floatfmt=',.2f'))
    return render_template('history.html')

@app.route('/dfbokeh')
def dfbokeh():
    db = create_engine(db_conn)
    conn = db.connect()
    print("[db_connection]",db,conn)

    if True:
        # df_div = pd.read_sql("SELECT TO_CHAR(timestamp::timestamp,'YYYY/Mon/DD/HH24:MI') as date, round(sum(total_krw)) as total FROM my_asset GROUP BY timestamp ORDER BY timestamp desc", conn)
        df_div = pd.read_sql("SELECT timestamp as date, round(sum(total_krw)) as total FROM my_asset GROUP BY timestamp ORDER BY timestamp desc", conn, index_col=None)
        df_div_stock = pd.read_sql("SELECT timestamp as date, round(sum(total_krw)) as total FROM my_asset WHERE div = 'STOCK' GROUP BY timestamp, div ORDER BY timestamp desc", conn, index_col=None)
        df_div_crypto = pd.read_sql("SELECT timestamp as date, round(sum(total_krw)) as total FROM my_asset WHERE div = 'CRYPTO' GROUP BY timestamp, div ORDER BY timestamp desc", conn, index_col=None)        
        #print(df_div)#.to_markdown(floatfmt=',.2f'))


    '''
    '''
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
 

    '''
    '''
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



    '''
    '''
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





    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(fig)
    script2, div2 = components(fig2)
    script3, div3 = components(fig3)
    html = render_template(
        'dfbokeh.html',
        plot_script=script,
        plot_script_stock=script2,
        plot_script_crypto=script3,
        plot_div=div,
        plot_div_stock = div2,
        plot_div_crypto = div3,
        js_resources=js_resources,
        css_resources=css_resources,
        total = total,
        date = date,
        total_stock = total_stock,
        date2 = date2,
        total_crypto = total_crypto,
        date3 = date3
    )
    return (html)


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

@app.route("/gpt")
def gpt():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    prompt = request.form["prompt"]
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = completions.choices[0].text
    return message



with app.test_request_context():
    print (url_for('meta'))  
    print (url_for('dfbokeh'))  



if __name__ == "__main__":
    app.run(debug=True)
