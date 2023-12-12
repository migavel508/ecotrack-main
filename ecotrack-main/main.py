'''

    Ecotrack - by Xgen25

    
'''


# imports

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from flask import json
from time import gmtime,time
from flask_sqlalchemy import SQLAlchemy as _BaseSQLAlchemy


# Flask app initialization

app = Flask(__name__)

#database configuration

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://aishwinmigavel:yiogsDCkO06x@ep-black-fire-68996719-pooler.us-east-2.aws.neon.tech/ecotrack?sslmode=require'

# class for database preperation

class SQLAlchemy(_BaseSQLAlchemy):
    def apply_pool_defaults(self, app, options):
        super(SQLAlchemy, self).apply_pool_defaults(self, app, options)
        options["pool_pre_ping"] = True

# run database

db = SQLAlchemy(app)


# secret key

app.secret_key='asdsdfsdfs13sdf_df%&'


# Database Tables - 

# User-login 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_no = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    fullname = db.Column(db.String(120), nullable=False)

# User-details

class Details(db.Model):
    phone_no = db.Column(db.String(80), unique=True, nullable=False, primary_key = True)
    username = db.Column(db.String(120), nullable=False)
    water_consumer_no = db.Column(db.String(120), nullable=True)
    water_board = db.Column(db.String(10), nullable=True)
    electricity_consumer_no = db.Column(db.String(120), nullable=True)
    electricity_board = db.Column(db.String(10), nullable=True)
    Number_of_people = db.Column(db.Integer)

# Applainces owned

class Appliances(db.Model):
    phone_no = db.Column(db.String(80), unique=True, nullable=False,primary_key = True)
    Television = db.Column(db.Integer,nullable=True)
    Refrigerator = db.Column(db.Integer,nullable=True)
    Microwave = db.Column(db.Integer,nullable=True)
    Washing_machine = db.Column(db.Integer,nullable=True)
    Air_conditioner = db.Column(db.Integer,nullable=True)

#Billing details

class Billing_details(db.Model):
    phone_no = db.Column(db.String(80), unique=True, nullable=False,primary_key = True)
    water_consumer_no = db.Column(db.String(120), nullable=True)
    electricity_consumer_no = db.Column(db.String(120), nullable=True)
    electricity_bill = db.Column(db.Integer,nullable=True)
    electricity_billing_date = db.Column(db.Date,nullable=True)
    water_bill = db.Column(db.Integer,nullable=True)
    water_billing_date = db.Column(db.Date,nullable=True)
    water_board = db.Column(db.String(10), nullable=True)
    electricity_billing_date = db.Column(db.Date,nullable=True)
    electricity_board = db.Column(db.String(10), nullable=True)


with app.app_context():
    db.create_all()

@app.route('/',methods=['POST','GET'])
def home():
    if 'phone_no' not in session:
        return json.dumps({'success':False}), 401, {'ContentType':'application/json'}

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        phone_no = request.json['phone_no']
        password = request.json['password']
        firstname = request.json['firstname']
        lastname = request.json['lastname']
        fullname = firstname + " " + lastname
        user = User(phone_no=phone_no, password=password, fullname=fullname)
        user_details = Details(phone_no=phone_no,username=fullname,water_consumer_no=None, water_board=None,electricity_consumer_no=None,electricity_board=None,Number_of_people=None)
        appliance_details = Appliances(phone_no=phone_no,Television=None,Air_conditioner=None,Refrigerator=None,Microwave=None,Washing_machine=None)
        bill_details = Billing_details(phone_no=phone_no,water_consumer_no=None, water_board=None,electricity_consumer_no=None,electricity_board=None,electricity_billing_date=None,water_billing_date=None,water_bill=None,electricity_bill=None)
        db.session.add(user)
        db.session.add(user_details)
        db.session.add(appliance_details)
        db.session.add(bill_details)
        db.session.commit()
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    return json.dumps({'success':False}), 401, {'ContentType':'application/json'}

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        phone_no = request.json['phone_no']
        password = request.json['password']
        user = User.query.filter_by(phone_no=phone_no, password=password)
        if user is not None:
            session['phone_no'] = phone_no
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        else:
            return json.dumps({'success':"user is None"}), 401, {'ContentType':'application/json'}

    return json.dumps({'success':"idk"}), 401, {'ContentType':'application/json'}

@app.route("/logout", methods=['GET'])
def logout():
    session.pop('phone_no', None)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/userdetails", methods=['GET'])
def userdetails():
    if 'phone_no' in session:
        user = Details.query.filter_by(phone_no=session['phone_no']).first()
        return json.dumps({'success':True, "phone_no":user.phone_no,"fullname":user.fullname,"electricity_consumer_no":user.electricity_consumer_no,"water_consumer_no":user.water_consumer_no}), 200, {'ContentType':'application/json'}
    else:
        return json.dumps({'success':False}), 401, {'ContentType':'application/json'}


# route for adding/updating user details

@app.route("/updateuserdetails", methods=['GET','POST'])
def updateuserdetails():
    if 'phone_no' in session:
        if request.method == 'POST':
            water_consumer_no = request.json['water_consumer_no']
            water_board = request.json['water_board']
            electricity_consumer_no = request.json['electricity_consumer_no']
            electricity_board = request.json['electricity_board']
            Number_of_people = request.json['Number_of_people']
            phone_no=session['phone_no']
            user_to_update = Details.query.get_or_404(phone_no)          
            user_to_update.water_board = water_board
            user_to_update.water_consumer_no = water_consumer_no
            user_to_update.electricity_consumer_no = electricity_consumer_no
            user_to_update.electricity_board = electricity_board
            user_to_update.Number_of_people = Number_of_people
            details_to_update = Billing_details.query.get_or_404(phone_no)          
            details_to_update.water_board = water_board
            details_to_update.water_consumer_no = water_consumer_no
            details_to_update.electricity_consumer_no = electricity_consumer_no
            details_to_update.electricity_board = electricity_board
            db.session.commit()
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        else:
            return json.dumps({'success':False}), 401, {'ContentType':'application/json'}

@app.route("/updateapplaincedetails", methods=['GET','POST'])
def updateapplaincedetails():
    if 'phone_no' in session:
        if request.method == 'POST':
            Air_conditioner = request.json['AC']
            Television = request.json['TV']
            Refrigerator = request.json['Refrigerator']
            Washing_machine = request.json['Washing_machine']
            Microwave = request.json['Microwave']
            phone_no=session['phone_no']
            appliance_to_update = Appliances.query.get_or_404(phone_no)          
            appliance_to_update.Television = Television
            appliance_to_update.Air_conditioner = Air_conditioner
            appliance_to_update.Refrigerator = Refrigerator
            appliance_to_update.Washing_machine = Washing_machine
            appliance_to_update.Microwave = Microwave
            db.session.commit()
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        else:
            return json.dumps({'success':False}), 401, {'ContentType':'application/json'}




if __name__ == '__main__':
    app.run(debug=True)