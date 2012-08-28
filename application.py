#!/usr/bin/env python
from datetime import date

from flask import *
from flask.ext.sqlalchemy import SQLAlchemy
from search import getSearchResults

application = Flask(__name__)
app = application
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.dat'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/db.dat'
db = SQLAlchemy(app)

from model import STIG, Finding

def getChecksByProfile(stig, profile):
	checks = {'low':[], 'medium':[], 'high':[]}
	for check in getattr(stig, profile).split(','):
		finding = Finding.query.filter_by(findingid=check).first()
		checks[finding.severity].append(finding)
	return checks

@app.route("/")
def default():
	stigs = STIG.query.order_by(STIG.date.desc()).limit(10).all()
	return render_template('index.html', stigs=stigs)

@app.route("/stigs")
def stigs():
	#display hyper-linked list of stigs
	stigs = STIG.query.all()
	return render_template('stiglist.html', stigs=stigs)

@app.route("/checks")
@app.route("/checks/<severity>")
def checks(severity=None):
	#display hyper-linked list of checks
	if severity in ['high', 'medium', 'low']:
		checks = Finding.query.filter_by(severity=severity).all()
		return render_template('checkseveritydetail.html', checks=checks)
	elif severity == 'all':
		checks = Finding.query.all()
		return render_template('checkseveritydetail.html', checks=checks)
	else:

		highchecks = Finding.query.filter_by(severity='high').count()
		mediumchecks = Finding.query.filter_by(severity='medium').count()
		lowchecks = Finding.query.filter_by(severity='low').count()
		checkstats = {'high': highchecks, 'medium': mediumchecks, 'low': lowchecks}
		return render_template('checkoverview.html', checkstats=checkstats)

@app.route("/stig/<stigid>/")
def getStigOverview(stigid):
	s = STIG.query.filter_by(pkid=stigid).first()
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

@app.route("/stig/<stigid>/<profile>/")
def getStig(stigid, profile):
	s = STIG.query.filter_by(pkid=stigid).first()
	checkprofiles = getChecksByProfile(s, profile)
		# Some checks had no <description tag> - Patched for now, fix in import!
	for key in checkprofiles.keys():
		for check in checkprofiles[key]:
			if check.description == None:
				check.description = ""
	return render_template('stigprofiledetail.html', checks=checkprofiles, stig=s, profile=profile)

@app.route("/stig/<stigid>/<profile>/excel")
def getStigExcel(stigid, profile):
	#s = session.query(STIG).filter_by(pkid=stigid).first()
	s = STIG.query.filter_by(pkid=stigid).first()
	checks = getChecksByProfile(s, profile)
		# Some checks had no <description tag> - Patched for now, fix in import!
	checkprofiles = getChecksByProfile(s, profile)
	for key in checkprofiles.keys():
		for check in checkprofiles[key]:
			if check.description == None:
				check.description = ""
	response = make_response(render_template('stigprofiledetail.csv', checks=checkprofiles, stig=s))
	response.headers['Content-Disposition'] = 'attachment; filename="%s - %s.csv"' % (s.title, profile)
	response.headers['Content-Type'] = 'text/csv; name="%s - %s.csv"' % (s.title, profile)
	response.mimetype = 'text/comma-separated-values'
	return response

@app.route("/check/<checkid>")
def getCheck(checkid):
	s = Finding.query.filter_by(findingid=checkid).first()
	return render_template('checkdetail.html', check=s)


@app.route("/search")
def search():
	query = request.args.get('q')
	
	if query == "" or query == None:
		return render_template('nosearchresults.html', query=False)
	
	searchResults = getSearchResults(query)
	if searchResults == False:
		return render_template('nosearchresults.html', query=query)
	else:
		return render_template('searchresults.html', results = searchResults, environ=request.environ, query=query)

@app.route("/emailsub", methods=['POST'])
def email():
	print request.form['email']
	return redirect(url_for('default'))

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
