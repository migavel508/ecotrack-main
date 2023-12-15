'''

    Ecotrack - by Xgen25

    
'''


# imports

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from flask import json
from random import randint
from time import gmtime,time
from flask_sqlalchemy import SQLAlchemy as _BaseSQLAlchemy


# Flask app initialization

app = Flask(__name__)

#database configuration

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://aishwinmigavel:yL7XJGTpH5ig@ep-black-fire-68996719-pooler.us-east-2.aws.neon.tech/eco_trac?sslmode=require'
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
    achievement_points = db.Column(db.Integer, nullable=False)
    goal = db.Column(db.Integer, nullable=False)
    contribution_points = db.Column(db.Integer, nullable=False)
    redeemed_points = db.Column(db.Integer, nullable=False)


# User-details

class Details(db.Model):
    phone_no = db.Column(db.String(80), unique=True, nullable=False, primary_key = True)
    username = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    lng = db.Column(db.Float, nullable=True)
    lat = db.Column(db.Float, nullable=True)
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
    Iron_box = db.Column(db.Integer,nullable=True)
    Heater = db.Column(db.Integer,nullable=True)
    Fans = db.Column(db.Integer,nullable=True)
    Lights = db.Column(db.Integer,nullable=True)
    

#Billing details

class Billing_details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_no = db.Column(db.String(80), nullable=False)
    water_consumer_no = db.Column(db.String(120), nullable=True)
    electricity_consumer_no = db.Column(db.String(120), nullable=True)
    electricity_consumption = db.Column(db.Float,nullable=True)
    electricity_bill = db.Column(db.Float,nullable=True)
    water_consumption = db.Column(db.Float,nullable=True)
    water_bill = db.Column(db.Float,nullable=True)
    water_billing_date = db.Column(db.String(10),nullable=True)
    water_board = db.Column(db.String(10), nullable=True)
    electricity_billing_date = db.Column(db.String(10),nullable=True)
    electricity_board = db.Column(db.String(10), nullable=True)

#Hourly Entries

class Hourly_entries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_no = db.Column(db.String(80), nullable=False)
    water_consumption_morning = db.Column(db.Float,nullable=True)
    water_consumption_afternoon = db.Column(db.Float,nullable=True)
    electricity_consumption_morning = db.Column(db.Float,nullable=True)
    electricity_consumption_afternoon = db.Column(db.Float,nullable=True)
    date = db.Column(db.String(10),nullable=True)

# Functions
    
# to calculate eb bill

def calculate_electricity_bill(bill):
    if bill>220 and bill<400:
        return 450 + (bill-250)*4.5
    elif bill>400:
        return 1350 + (bill-450)*6

# to calculate water bill


def calculate_water_bill(bill):
    bill=bill/1000
    return bill*40


# to initialize the database

with app.app_context():
    db.create_all()

# Routes - 

# root

@app.route('/',methods=['POST','GET'])
def home():
    if 'phone_no' not in session:
        return json.dumps({'success':False}), 401, {'ContentType':'application/json'}

# register a new user

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':

        # Get inputs from user

        phone_no = request.json['phone_no']

        # Check if number is unique

        if User.query.filter_by(phone_no=phone_no).first() is not None:
            return json.dumps({'success':"Phone number already exists!"}), 401, {'ContentType':'application/json'}
        
        # If phone number is unique get other details

        password = request.json['password']
        firstname = request.json['firstname']
        lastname = request.json['lastname']
        fullname = firstname + " " + lastname

        # Set up time

        tm = gmtime(time())

        # for electricity, 1 month diff

        curr_month="1-"+str(tm[1])+"-"+str(tm[0])
        prev_month="1-"+str(tm[1]-1)+"-"+str(tm[0])
        last_month="1-"+str(tm[1]-2)+"-"+str(tm[0])

        # for water, 6 month diff

        water_curr_month="1-"+str(tm[1]-2)+"-"+str(tm[0])
        water_prev_month="1-"+str(tm[1]-8)+"-"+str(tm[0])
        water_last_month="1-"+str(tm[1]-2)+"-"+str(tm[0]-1)

        # Setup for electricity consumption and bill

        econsumption=randint(250,500)
        econsumption2=econsumption + econsumption*0.05
        econsumption3=econsumption + econsumption*0.025

        # Setup for water consumption and bill

        wconsumption=randint(18000,20000)
        wconsumption2=wconsumption + wconsumption*0.05
        wconsumption3=wconsumption + wconsumption*0.025

        # Setting up the values inside the database -

        # for user table

        user = User(phone_no=phone_no, password=password, fullname=fullname,achievement_points=0,goal=econsumption*0.95,redeemed_points=0,contribution_points=0)
        
        # for user_details table

        user_details = Details(phone_no=phone_no,username=fullname,water_consumer_no=None, water_board=None,electricity_consumer_no=None,electricity_board=None,Number_of_people=None,lat=None,lng=None,address=None)
        
        # for applaince_details table
        
        appliance_details = Appliances(phone_no=phone_no,Television=None,Air_conditioner=None,Refrigerator=None,Microwave=None,Washing_machine=None,Lights=None,Fans=None,Iron_box=None,Heater=None)
       
        # for Bill_details  table
       
        bill_details = Billing_details(phone_no=phone_no,water_consumer_no=None, water_board=None,electricity_consumer_no=None,electricity_board=None,electricity_billing_date=curr_month,water_billing_date=water_curr_month,water_bill=calculate_water_bill(wconsumption),electricity_bill=calculate_electricity_bill(econsumption),electricity_consumption=econsumption,water_consumption=wconsumption)
        prev_bill_details = Billing_details(phone_no=phone_no,water_consumer_no=None, water_board=None,electricity_consumer_no=None,electricity_board=None,electricity_billing_date=prev_month,water_billing_date=water_prev_month,water_bill=calculate_water_bill(wconsumption2),electricity_bill=calculate_electricity_bill(econsumption2),electricity_consumption=econsumption2,water_consumption=wconsumption2)
        last_bill_details = Billing_details(phone_no=phone_no,water_consumer_no=None, water_board=None,electricity_consumer_no=None,electricity_board=None,electricity_billing_date=last_month,water_billing_date=water_last_month,water_bill=calculate_water_bill(wconsumption3),electricity_bill=calculate_electricity_bill(econsumption3),electricity_consumption=econsumption3,water_consumption=wconsumption3)
        
        # for setting up mock data for daily entries
        
        for i in range(7):
            econsumption=randint(250,500)
            hourly_update = Hourly_entries(phone_no=phone_no,water_consumption_morning = econsumption/2,water_consumption_afternoon = econsumption/2-15,electricity_consumption_morning = econsumption/40,electricity_consumption_afternoon = econsumption/30,date=str(tm[2]-i)+"-"+str(tm[1])+"-"+str(tm[0]))
            db.session.add(hourly_update)

        # adding the data to the cloud database

        db.session.add(user)
        db.session.add(user_details)
        db.session.add(appliance_details)
        db.session.add(bill_details)
        db.session.add(prev_bill_details)
        db.session.add(last_bill_details)

        # commiting the changes

        db.session.commit()

        # reply for processing

        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    
    return json.dumps({'success':False}), 401, {'ContentType':'application/json'}

# login to acc

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':

        # Get details

        phone_no = request.json['phone_no']
        password = request.json['password']

        # check if user exists

        user = User.query.filter_by(phone_no=phone_no, password=password).first()

        # if he does, login and add it to session

        if user is not None:
            session['phone_no'] = phone_no
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        else:
            return json.dumps({'success':"user is None"}), 401, {'ContentType':'application/json'}

    return json.dumps({'success':"idk"}), 401, {'ContentType':'application/json'}

# logout of account

@app.route("/logout", methods=['GET'])
def logout():

    # remove from session
    
    session.pop('phone_no', None)
    
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

# route for adding/updating user details

@app.route("/updateuserdetails", methods=['GET','POST'])
def updateuserdetails():
    if 'phone_no' in session:
        if request.method == 'POST':

            # Getting details

            water_consumer_no = request.json['water_consumer_no']
            water_board = request.json['water_board']
            electricity_consumer_no = request.json['electricity_consumer_no']
            electricity_board = request.json['electricity_board']
            Number_of_people = request.json['Number_of_people']
            phone_no=session['phone_no']

            # update the details in the table

            user_to_update = Details.query.get_or_404(phone_no)          
            user_to_update.water_board = water_board
            user_to_update.water_consumer_no = water_consumer_no
            user_to_update.electricity_consumer_no = electricity_consumer_no
            user_to_update.electricity_board = electricity_board
            user_to_update.Number_of_people = Number_of_people

            #update the bill details in table

            details_to_update = Billing_details.query.filter_by(phone_no=session['phone_no']).all()
            for i in range(3):        
                details_to_update[i].water_board = water_board
                details_to_update[i].water_consumer_no = water_consumer_no
                details_to_update[i].electricity_consumer_no = electricity_consumer_no
                details_to_update[i].electricity_board = electricity_board

            # commit changes
                
            db.session.commit()

            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        else:
            return json.dumps({'success':False}), 401, {'ContentType':'application/json'}

# update applaince details
        
@app.route("/updateapplaincedetails", methods=['GET','POST'])
def updateapplaincedetails():
    if 'phone_no' in session:
        if request.method == 'POST':

            # Get applaince count

            Air_conditioner = request.json['AC']
            Television = request.json['TV']
            Refrigerator = request.json['Refrigerator']
            Washing_machine = request.json['Washing_machine']
            Microwave = request.json['Microwave']
            Fans = request.json['Fans']
            Lights = request.json['Lights']
            Heater = request.json['Heater']
            Iron_box = request.json['Iron_box']
            phone_no=session['phone_no']

            # update applaince count

            appliance_to_update = Appliances.query.get_or_404(phone_no)          
            appliance_to_update.Television = Television
            appliance_to_update.Air_conditioner = Air_conditioner
            appliance_to_update.Refrigerator = Refrigerator
            appliance_to_update.Washing_machine = Washing_machine
            appliance_to_update.Fans = Fans
            appliance_to_update.Lights = Lights
            appliance_to_update.Iron_box = Iron_box
            appliance_to_update.Heater = Heater
            appliance_to_update.Microwave = Microwave

            # Commit changes

            db.session.commit()

            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        else:
            return json.dumps({'success':False}), 401, {'ContentType':'application/json'}

# set goal

@app.route("/goal", methods=['GET','POST'])
def goal():
    if 'phone_no' in session:
        if request.method == 'POST':

            # get updated goal

            goal = request.json['goal']

            # find and update matching goal

            goal_to_update = User.query.filter_by(phone_no=session['phone_no']).first()        
            goal_to_update.goal = goal

            # commit
            
            db.session.commit()
            
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        else:
            return json.dumps({'success':False}), 401, {'ContentType':'application/json'}

# To get user details
        
@app.route("/userdetails", methods=['GET'])
def userdetails():
    if 'phone_no' in session:
        
        # get user details from tables

        user = Details.query.filter_by(phone_no=session['phone_no']).first()
        appl = Appliances.query.filter_by(phone_no=session['phone_no']).first()
       
        # return the data

        return json.dumps({"Applainces":{"Lights":appl.Lights,"Fans":appl.Fans,"Heater":appl.Heater,"Iron_box":appl.Iron_box,"Television":appl.Television,"Washing_machine":appl.Washing_machine,"Ac":appl.Air_conditioner,"Microwave":appl.Microwave,"Refrigerator":appl.Refrigerator},"details":{"phone_no":user.phone_no,"fullname":user.username,"address":user.address,"electricity_consumer_no":user.electricity_consumer_no,"water_consumer_no":user.water_consumer_no,"lat":user.lat,"lng":user.lng,"electricity_board":user.electricity_board,"water_board":user.water_board,"Number_of_people":user.Number_of_people}}), 200, {'ContentType':'application/json'}
    else:
        return json.dumps({'success':False}), 401, {'ContentType':'application/json'}

# To get bill details

@app.route("/billdetails", methods=['GET'])
def billdetails():
    if 'phone_no' in session:

        # get user details from tables

        user = Billing_details.query.filter_by(phone_no=session['phone_no']).all()

        # return the data

        return json.dumps([{"electricity_consumer_no":user[0].electricity_consumer_no,"water_consumer_no":user[0].water_consumer_no,"electricity_board":user[0].electricity_board,"water_board":user[0].water_board,"water_date":user[0].water_billing_date,"electricity_date":user[0].electricity_billing_date,"electricity_bill":user[0].electricity_bill,"water_bill":user[0].water_bill,"electricity_consumption":user[0].electricity_consumption,"water_consumption":user[0].water_consumption,"water_payment_status":False,"electricity_payment_status":True},{"electricity_consumer_no":user[0].electricity_consumer_no,"water_consumer_no":user[0].water_consumer_no,"electricity_board":user[0].electricity_board,"water_board":user[0].water_board,"water_date":user[1].water_billing_date,"electricity_date":user[1].electricity_billing_date,"electricity_bill":user[1].electricity_bill,"water_bill":user[1].water_bill,"electricity_consumption":user[1].electricity_consumption,"water_consumption":user[1].water_consumption,"water_payment_status":False,"electricity_payment_status":True},{"electricity_consumer_no":user[0].electricity_consumer_no,"water_consumer_no":user[0].water_consumer_no,"electricity_board":user[0].electricity_board,"water_board":user[0].water_board,"water_date":user[2].water_billing_date,"electricity_date":user[2].electricity_billing_date,"electricity_bill":user[2].electricity_bill,"water_bill":user[2].water_bill,"electricity_consumption":user[2].electricity_consumption,"water_consumption":user[2].water_consumption,"water_payment_status":False,"electricity_payment_status":True}]), 200, {'ContentType':'application/json'}
    else:
        return json.dumps({'success':False}), 401, {'ContentType':'application/json'}


# To get points details

@app.route("/pointsdetails", methods=['GET'])
def pointsdetails():
    if 'phone_no' in session:
        
        # get points details from tables

        user = User.query.filter_by(phone_no=session['phone_no']).first()

        # return the data

        return json.dumps({"Achievement_points":user.achievement_points,"Redeemed_points":user.redeemed_points,"Contributed_points":user.contribution_points,}), 200, {'ContentType':'application/json'}
    else:
        return json.dumps({'success':False}), 401, {'ContentType':'application/json'}

# To get goal details

@app.route("/goaldetails", methods=['GET'])
def goaldetails():
    if 'phone_no' in session:

        # get goal details from tables

        entries = User.query.filter_by(phone_no=session['phone_no']).first()

        # return the data

        return json.dumps({"goal":entries.goal}), 200, {'ContentType':'application/json'}
    else:
        return json.dumps({'success':False}), 401, {'ContentType':'application/json'}    

@app.route("/leaderdetails", methods=['GET'])
def leaderdetails():
    if 'phone_no' in session:

        # get leaderboard from tables

        details=[]
        user = User.query.all()
        for i in user:
            consumption = Billing_details.query.filter_by(phone_no=i.phone_no).first()
            each_entry = {"phone_no":i.phone_no,"username":i.fullname,"achievement_points":i.achievement_points,"water_consumption":consumption.water_consumption,"electricity_consumption":consumption.electricity_consumption}
            details.append(each_entry)

        # return the combined data
        
        return json.dumps(details), 200, {'ContentType':'application/json'}
    else:
        return json.dumps({'success':False}), 401, {'ContentType':'application/json'}

# To get hourly entry details

@app.route("/hourlydetails", methods=['GET'])
def hourlydetails():
    if 'phone_no' in session:

        # get hourly entries from tables

        details=[]
        entries = Hourly_entries.query.filter_by(phone_no=session['phone_no']).all()
        for i in entries:
            each_entry = {"water_consumption_morning":i.water_consumption_morning,"water_consumption_afternoon":i.water_consumption_afternoon,"electricity_consumption_morning":i.electricity_consumption_morning,"electricity_consumption_afternoon":i.electricity_consumption_afternoon,"date":i.date}
            details.append(each_entry)

        # return the data
        
        return json.dumps(details), 200, {'ContentType':'application/json'}
    else:
        return json.dumps({'success':False}), 401, {'ContentType':'application/json'}

# To compare electricity bill

@app.route("/electricitybillcomparison", methods=['GET'])
def electricitybillcomparison():
    if 'phone_no' in session:
        
        #get the electricity bill from the table

        user = Billing_details.query.filter_by(phone_no=session['phone_no']).all()

        #compare the bill of last and current month

        comp = user[0].electricity_consumption-user[1].electricity_consumption

        # return the data

        return json.dumps({"electricity_date_1":user[0].electricity_billing_date,"electricity_bill_1":user[0].electricity_bill,"electricity_consumption_1":user[0].electricity_consumption,"electricity_date_2":user[1].electricity_billing_date,"electricity_bill_2":user[1].electricity_bill,"electricity_consumption_2":user[1].electricity_consumption,"electricity_consumption_comparison":comp,"electricity_comparison_average":((comp/user[1].electricity_consumption)*100)}), 200, {'ContentType':'application/json'}
    else:
        return json.dumps({'success':False}), 401, {'ContentType':'application/json'}
    
# To compare water bill

@app.route("/waterbillcomparison", methods=['GET'])
def waterbillcomparison():
    if 'phone_no' in session:

        #get the water bill from the table

        user = Billing_details.query.filter_by(phone_no=session['phone_no']).all()

        #compare the bill of last and current month

        comp = user[0].water_consumption-user[1].water_consumption

        # return the data

        return json.dumps({"water_date_1":user[0].water_billing_date,"water_bill_1":user[0].water_bill,"water_consumption_1":user[0].water_consumption,"water_date_2":user[1].water_billing_date,"water_bill_2":user[1].water_bill,"water_consumption_2":user[1].water_consumption,"water_consumption_comparison":comp,"water_comparison_average":((comp/user[1].water_consumption)*100)}), 200, {'ContentType':'application/json'}
    else:
        return json.dumps({'success':False}), 401, {'ContentType':'application/json'}
   
# start the app

if __name__ == '__main__':
    app.run(debug=True)

  
