import os
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.models import DatetimeTickFormatter, NumeralTickFormatter
from bokeh.models import HoverTool

try:
    db_conn = os.environ.get('DBCONN')
    print(db_conn)
except:
    pass

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = db_conn  # 'postgresql://id:password@127.0.0.1:port/dbname'

with app.app_context():
    db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
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
    
@app.route('/pandas')
def pandas():
    #create dataframe
    df_marks = pd.DataFrame({'name': ['Somu', 'Kiku', 'Amol', 'Lini'],
        'physics': [68, 74, 77, 78],
        'chemistry': [84, 56, 73, 69],
        'algebra': [78, 88, 82, 87]})

    #render dataframe as html
    html = df_marks.to_html(classes=["table-bordered", "table-striped", "table-hover"])

    #write html to file
    text_file = open("templates/pandas.html", "w")
    text_file.write(html)
    text_file.close()
    return render_template('pandas.html')

@app.route('/history')
def histroy():
    db = create_engine(db_conn)
    conn = db.connect()
    print("[db_connection]",db,conn)

    if True:
        #df_div = pd.read_sql("SELECT TO_CHAR(timestamp::timestamp,'YYYY/Mon/DD/HH24:MI') as date, div, round(sum(total_krw)) as total FROM my_asset GROUP BY timestamp, div ORDER BY timestamp desc", conn)
        df_div = pd.read_sql("SELECT TO_CHAR(timestamp::timestamp,'YYYY/Mon/DD/HH24:MI') as date, round(sum(total_krw)) as total FROM my_asset GROUP BY timestamp ORDER BY timestamp desc", conn)
        print(df_div)#.to_markdown(floatfmt=',.2f'))
    
    html = df_div.to_html()

    #write html to file
    text_file = open("templates/history.html", "w")
    text_file.write(html)
    text_file.close()
    return render_template('history.html')

@app.route('/dfbokeh')
def dfbokeh():
    db = create_engine(db_conn)
    conn = db.connect()
    print("[db_connection]",db,conn)

    if True:
        # df_div = pd.read_sql("SELECT TO_CHAR(timestamp::timestamp,'YYYY/Mon/DD/HH24:MI') as date, round(sum(total_krw)) as total FROM my_asset GROUP BY timestamp ORDER BY timestamp desc", conn)
        df_div = pd.read_sql("SELECT timestamp as date, round(sum(total_krw)) as total FROM my_asset GROUP BY timestamp ORDER BY timestamp desc", conn)
        #print(df_div)#.to_markdown(floatfmt=',.2f'))

    rows = df_div.shape[0]
    cols = df_div.shape[1]
    print(rows,cols)

    from datetime import datetime, timedelta
    '''
    dates = [(datetime.now() + timedelta(day * 7)) for day in range(0, 2)]
    print(dates)
    '''
    fig = figure(width=1200, height=500 ) #, tools=[HoverTool()], tooltips="@x == @y",)

    # fig.vbar(
    #     x= list(range(rows)),
    #     top= df_div['total'] 
    # )

    #ax = list(range(rows))
    ax = pd.to_datetime(df_div["date"])
    ay = df_div['total'] 
    print(ay)

    fig.circle(ax, ay , size=1, color="black", alpha=1)#, x_axis_type="datetime")
    fig.yaxis[0].formatter = NumeralTickFormatter(format="0,0")
    fig.xaxis[0].formatter = DatetimeTickFormatter(months="%F")
    #fig.xgrid.grid_line_color = "olive"
    fig.ygrid.band_fill_color = "olive"
    fig.ygrid.band_fill_alpha = 0.1  
    #fig.sizing_mode = 'scale_width'
 
    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(fig)
    html = render_template(
        'dfbokeh.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
    )
    return (html)



if __name__ == "__main__":
    app.run(debug=True)
