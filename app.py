import sqlite3

import flask
import flask_wtf
import wtforms
from flask import Flask, g, render_template, request, redirect, url_for

app = Flask('Oderman', template_folder="templates", static_folder="static")
DATABASE = 'oderman_db.db'

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = "Vlad"


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        create_order_table(db)
        create_feedback_table(db)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


class FeedBackForm(flask_wtf.FlaskForm):
    name = wtforms.StringField("Name")
    feedback_type = wtforms.RadioField("Feedback Type")
    mark = wtforms.RadioField("Mark")
    comment = wtforms.StringField("Comment")
    submit = wtforms.SubmitField("Send")


def create_order_table(db):
    db.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        address TEXT NOT NULL,
        pizza_type TEXT NOT NULL
    )
    ''')
    db.commit()


def create_feedback_table(db):
    db.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        feedback_type TEXT NOT NULL,
        mark INTEGER NOT NULL,
        comment TEXT NOT NULL
    )
    ''')
    db.commit()


menu_items = [
    {"name": "Маргарита", "description": "Томатний соус, моцарела, базилік", "price": 100},
    {"name": "Пепероні", "description": "Томатний соус, пепероні, моцарела", "price": 120},
    {"name": "Гавайська", "description": "Томатний соус, курка, ананас, моцарела", "price": 130},
    {"name": "Чотири сири", "description": "Томатний соус, гауда, пармезан, дор-блю, моцарела", "price": 150},
    {"name": "Вегетаріанська", "description": "Томатний соус, гриби, перець, помідор, моцарела", "price": 110},
]


@app.route('/')
@app.route('/index')
def index():
    pizza_name = "Oderman"
    return render_template("index.html", pizza_name=pizza_name)


@app.route('/menu')
def menu():
    return render_template("menu.html", menu_items=menu_items)


@app.route('/aboutUs')
def about_us():
    return render_template('about_us.html', title='Про нас', header='Інформація про нас')


@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        phone_number = request.form.get('phone_number', '')
        address = request.form.get('address', '')
        pizza_type = request.form.get('pizza_type', '')

        if first_name and last_name and phone_number and address and pizza_type:
            db = get_db()
            db.execute(
                'INSERT INTO orders (first_name, last_name, phone_number, address, pizza_type) VALUES (?, ?, ?, ?, ?)',
                (first_name, last_name, phone_number, address, pizza_type))
            db.commit()

            return redirect(url_for('orders'))

    return render_template('order_form.html')


@app.route('/orders')
def orders():
    db = get_db()
    cur = db.execute('SELECT * FROM orders ORDER BY id DESC')
    orders = cur.fetchall()
    return render_template('orders.html', orders=orders)


@app.route('/feedback/', methods=["GET", "POST"])
def feedback_form():
    form = FeedBackForm()
    form.feedback_type.choices = [("Feedback", "Feedback"), ("Complaint", "Complaint")]
    form.mark.choices = [("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")]

    if flask.request.method == "POST":
        name = form.name.data
        feedback_type = form.feedback_type.data[0]
        mark = form.mark.data
        comment = form.comment.data

        if name and feedback_type and mark and comment:
            db = get_db()
            db.execute(
                'INSERT INTO feedback (name, feedback_type, mark, comment) VALUES (?, ?, ?, ?)',
                (name, feedback_type, mark, comment))
            db.commit()

            return redirect(url_for('feedback_page'))

    return render_template("feedback.html", form=form)


@app.route("/feedback_page/")
def feedback_page():
    db = get_db()
    cur = db.execute('SELECT * FROM feedback ORDER BY id DESC')
    feedbacks = cur.fetchall()
    return render_template("feedback_page.html", feedbacks=feedbacks)


if __name__ == "__main__":
    with app.app_context():
        get_db()
    app.run(debug=True)
