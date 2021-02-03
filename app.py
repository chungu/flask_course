from flask import Flask, jsonify, request, session, render_template, g
from flask.globals import request
from flask.helpers import url_for
from werkzeug.utils import redirect
import sqlite3

app = Flask(__name__)

# config
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'Thisisasecret!'


# databse conenctions
def connect_db():
    sql = sqlite3.connect('/Users/ngolwe/Documents/dev/flask_course/data.db')
    sql.row_factory = sqlite3.Row
    return sql


def get_db():
    if not hasattr(g, 'sqlite3'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def index():
    # clear sessions
    session.pop('name', None)
    return '<h1> Hello, World </h1>'


@app.route('/home', methods=['POST', 'GET'], defaults={'name': 'Default'})
@app.route('/home/<string:name>', methods=['POST', 'GET'])
def home(name):
    session['name'] = name
    db = get_db()
    cur = db.execute('select * from users')
    results = cur.fetchall()
    return render_template('home.html', name=name, display=True,
                           mylist=["One", "two", "three", "four"], listofdictionaries=[{'name': 'Zach'}, {'name': 'Zoe'}], results=results)

# process queries


@app.route('/query', methods=['POST', 'GET'])
def query():
    name = request.args.get('name')
    location = request.args.get('location')
    return '<h1>Hi {}.You are from {}. You are on the query page </h1>'.format(name, location)


@app.route('/json')
def json():
    if 'name' in session:
        name = session['name']
    else:
        name = 'Notinsession!'

    return jsonify({'key': 'value', 'listkey': [1, 2, 3, 4, 5, 6], 'name': name})


@app.route('/theform', methods=['POST', 'GET'])
def theform():
    # capturing form input
    if request.method == 'GET':
        return render_template("form.html")
    # processing form data
    else:
        name = request.form['name']
        location = request.form['location']
        # return 'Hello {}. You are from {}. Your form was submitted successfully'.format(name, location)

        db = get_db()
        db.execute('insert into users (name, location) values (?, ?)', [
                   name, location])
        db.commit()

        return redirect(url_for('home', name=name, location=location))


# getting data throguh json objects


@app.route('/processjson', methods=['POST', 'GET'])
def processjosn():
    data = request.get_json()
    name = data['name']
    location = data['location']
    randomlist = data['randomlist']
    return jsonify({'result': 'Success!', 'name': name, 'location': location, 'randomkeyinlist': randomlist[2]})


@app.route('/viewresults')
def viewresults():
    db = get_db()
    cur = db.execute('select * from users')
    results = cur.fetchall()
    return '<h1>The ID is {}. The name is {}. The location is {}. </h1>'.format(results[2]['id'], results[2]['name'], results[2]['location'])


if __name__ == '__main__':
    app.run()
