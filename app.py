#!/usr/bin/env python
from datetime import date

import sqlalchemy
from flask import *

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from model import STIG, Finding, Base


engine = create_engine('sqlite:///db.dat', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


app = Flask(__name__)

def getChecksByProfile(stig, profile):
	global session
	checks = {}
	for check in getattr(stig, profile).split(','):
		finding = session.query(Finding).filter_by(findingid=check).first()
		checks[finding.findingid.strip()] = finding
	return checks

@app.route("/")
def default():
	#display linked list of stigs

@app.route("/stig/<stigid>/<profile>")
def getStig(stigid, profile):
	s = session.query(STIG).filter_by(pkid=stigid).first()
	checks = getChecksByProfile(s, profile)
	
	content = "You asked for %s" % s.title
	
	for check in checks:
		ret = "<br><hr>%s: %s" % (checks[check].findingid, checks[check].title)
		content = content + ret
	return content
@app.route("/check/<checkid>")
def getCheck(checkid):
	return "You asked for %s" % checkid

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=8080)
