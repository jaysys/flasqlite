
## Intro
유튜브강의링크: https://www.youtube.com/watch?v=Z1RJmh_OqeA&ab_channel=freeCodeCamp.org 

런타임 데모: https://port-0-flasqlite-1jx7m2gld1u0xx5.gksl2.cloudtype.app/



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

## Contributing

Since this is a repository for a tutorial, the code should remain the same as the code that was shown in the tutorial. Any pull requests that don't address security flaws or fixes for language updates will be automatically closed. Style changes, adding libraries, etc are not valid changes for submitting a pull request.
