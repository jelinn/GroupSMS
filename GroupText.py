#!/usr/bin/python
from __future__ import with_statement
from flask import Flask, request, g, render_template, redirect
from sqlite3 import dbapi2 as sqlite3
from twilio.rest import TwilioRestClient

#GroupText.py
#Flask app that uses Twilio to allows users to text a single number and have it sent to a group of phone numbers via SMS. 
#Stores each SMS message sent in an sqlite3 database and displays them to a webpage.
#Input varaiables marked by comments below. 1)Database sqlite file(line 14) 2)Twilio account sid and auth_token(lines 17/18) 3)Group that you want to send the SMS messages to(line 22) 4)Twilio phone number(line 50)



#Database (sqlite3) file information here.
DATABASE=''
PER_PAGE=30
#Twillio account information here
account_sid=""
auth_token=""

#Input phone numbers as a hash. 
#Format {"+15554443333":"Friend1","+12224445555":"Friend2"}
Users={"",""}

app=Flask(__name__)
#app.debug=True

def connect_db():
	return sqlite3.connect(DATABASE)

@app.before_request
def before_request():
	g.db = connect_db()
	 
@app.teardown_request
def teardown_request(exception):
	if hasattr(g, 'db'):
		g.db.close()

@app.route("/")
def TextProxy():
	from_number=request.args.get('From',None)
	Message=request.args.get('Body',None)
	sender=Users[from_number]
	TextMessageBody=Users[from_number]+": "+Message
	client=TwilioRestClient(account_sid, auth_token)
	g.db.execute('INSERT INTO entries (ID, SMS) values (NULL,?)', [TextMessageBody])
	g.db.commit()		
	for user in Users:
		#Add twilio phone number to from=""
		SMS=client.sms.messages.create(to=user,from_="",body=TextMessageBody)	
	return "Success"

@app.route("/recent", methods=['POST','GET'])
def status():
	cur= g.db.execute('select SMS from entries order by ID desc')
	entries = [dict(text=row[0]) for row in cur.fetchall()]
	return render_template('recent.html', entries=entries)	

if __name__=="__main__":
	app.run(host="0.0.0.0")
