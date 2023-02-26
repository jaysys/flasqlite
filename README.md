
## Intro
유튜브링크: https://www.youtube.com/watch?v=Z1RJmh_OqeA&ab_channel=freeCodeCamp.org 


```
CREATE TABLE todo (
	id serial PRIMARY KEY,
	content VARCHAR (500),
	completed VARCHAR(50),
	date_created TIMESTAMP 
);
```

## Flask & Bokeh, Pandas, Dataframe to html
This repo has been updated to work with `Python v3.8` and up.

## How To Run
1. Install `virtualenv`:
```
$ pip install virtualenv
```

2. Open a terminal in the project root directory and run:
```
$ virtualenv env
```

3. Then run the command:
```
$ .\env\Scripts\activate
```

4. Then install the dependencies:
```
$ (env) pip install -r requirements.txt
```

5. Finally start the web server:
```
$ (env) python app.py
```

This server will start on port 5000 by default. You can change this in `app.py` by changing the following line to this:

```python
if __name__ == "__main__":
    app.run(debug=True, port=<desired port>)
```
