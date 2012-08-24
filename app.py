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
	checks = []
	for check in getattr(stig, profile).split(','):
		finding = session.query(Finding).filter_by(findingid=check).first()
		checks.append(finding)
	return checks

@app.route("/")
def default():
	#display welcome page
	return render_template('index.html')

@app.route("/stigs")
def stigs():
	#display hyper-linked list of stigs
	stigs = session.query(STIG).all()
	return render_template('stiglist.html', stigs=stigs)

@app.route("/checks")
@app.route("/checks/<severity>")
def checks(severity=None):
	#display hyper-linked list of checks
	if severity:
		checks = session.query(Finding).filter_by(severity=severity).all()
		return render_template('checkseveritydetail.html', checks=checks)
	else:
		highchecks = session.query(Finding).filter_by(severity='high').count()
		mediumchecks = session.query(Finding).filter_by(severity='medium').count()
		lowchecks = session.query(Finding).filter_by(severity='low').count()
		checkstats = {'high': highchecks, 'medium': mediumchecks, 'low': lowchecks}
		return render_template('checkoverview.html', checkstats=checkstats)

@app.route("/stig/<stigid>/<profile>/excel")
@app.route("/stig/<stigid>/<profile>/Excel")
def getStigExcel(stigid, profile):
	s = session.query(STIG).filter_by(pkid=stigid).first()
	checks = getChecksByProfile(s, profile)
	response = make_response(render_template('stigprofiledetail.csv', checks=checks, stig=s))
	response.headers['Content-Disposition'] = 'attachment; filename="%s - %s.csv"' % (s.title, profile)
	response.headers['Content-Type'] = 'text/csv; name="%s - %s.csv"' % (s.title, profile)
	response.mimetype = 'text/comma-separated-values'
	return response

@app.route("/stig/<stigid>/")
@app.route("/stig/<stigid>/<profile>/")
def getStig(stigid, profile=None):
	if profile:
		s = session.query(STIG).filter_by(pkid=stigid).first()
		checks = getChecksByProfile(s, profile)
		return render_template('stigprofiledetail.html', checks=checks, stig=s, profile=profile)
	else:
		s = session.query(STIG).filter_by(pkid=stigid).first()
		profiles = {'mac1public': len(s.MAC1PublicProfile.split(',')), 
					'mac1sensitive':len(s.MAC1SensitiveProfile.split(',')), 
					'mac1classified':len(s.MAC1ClassifiedProfile.split(',')),
					'mac2public':len(s.MAC2PublicProfile.split(',')),
					'mac2sensitive':len(s.MAC2SensitiveProfile.split(',')),
					'mac2classified':len(s.MAC2ClassifiedProfile.split(',')),
					'mac3public':len(s.MAC3PublicProfile.split(',')), 
					'mac3sensitive':len(s.MAC3SensitiveProfile.split(',')), 
					'mac3classified':len(s.MAC3ClassifiedProfile.split(','))}
		return render_template('stigoverview.html', stig=s, profiles = profiles)

@app.route("/check/<checkid>")
def getCheck(checkid):
	return "You asked for %s" % checkid

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=8080)
