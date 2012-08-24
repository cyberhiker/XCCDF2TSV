#!/usr/bin/env python

import sys, sqlalchemy
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from model import STIG, Finding, Base

# Fixup for handling UTF8 XML documents properly
reload(sys)
sys.setdefaultencoding('utf-8')
import xml.etree.ElementTree as ET

#global, cuz I gotta use it A LOT
xmlns = "http://checklists.nist.gov/xccdf/1.1"
totalfindings = 0
dupes = 0

def setupDB():
	""" Returns a sqlalchemy session - call session.add/query/etc and then session.commit"""
	engine = create_engine('sqlite:///db.dat', echo=False)
	Base.metadata.create_all(engine)
	Session = sessionmaker(bind=engine)
	session = Session()
	return session

#xmlns = "http://checklists.nist.gov/xccdf/1.1"
#adstig = STIG(id=1, title='ACtive Directory STIG', version='35v3a', description="""OH YEAH
#	SON""")
def parseProfiles(profile):
	check_list = []
	selects = profile.findall("{%s}select" % xmlns)
	for select_tag in selects:
		if select_tag.get("selected") == "true":
			check_list.append(select_tag.get('idref'))
	return check_list

def parseHeader(benchmark):
	stig = {}
	datestr = benchmark.find("{%s}status" % xmlns).get("date")
	if datestr:
		year, month, day = [int(x) for x in datestr.split('-')]
		stig['date'] = date(year, month, day)
	else:
		stig['date'] = None
	stig['title'] = benchmark.find("{%s}title" % xmlns).text
	try:
		stig['desc'] = benchmark.find("{%s}description" % xmlns).text
		stig['version'] = benchmark.find("{%s}version" % xmlns).text
	except Exception, e:
		stig['desc'] = "None"
		stig['version'] = "None"
		sys.exc_clear()
		pass

	profiles = benchmark.findall("{%s}Profile" % xmlns)
	for profile in profiles:
		if profile.get("id") == "MAC-1_Public":
			stig['MAC1Public'] = parseProfiles(profile)
		elif profile.get("id") == "MAC-1_Sensitive":
			stig['MAC1Sensitive'] = parseProfiles(profile)
		elif profile.get("id") == "MAC-1_Classified":
			stig['MAC1Classified'] = parseProfiles(profile)
		elif profile.get("id") == "MAC-2_Public":
			stig['MAC2Public'] = parseProfiles(profile)
		elif profile.get("id") == "MAC-2_Sensitive":
			stig['MAC2Sensitive'] = parseProfiles(profile)
		elif profile.get("id") == "MAC-2_Classified":
			stig['MAC2Classified'] = parseProfiles(profile)
		elif profile.get("id") == "MAC-3_Public":
			stig['MAC3Public'] = parseProfiles(profile)
		elif profile.get("id") == "MAC-3_Sensitive":
			stig['MAC3Sensitive'] = parseProfiles(profile)
		elif profile.get("id") == "MAC-3_Classified":
			stig['MAC3Classified'] = parseProfiles(profile)
	return stig

def parseDescTag(group):
	desc = str(group.find("{%s}Rule/{%s}description" % (xmlns, xmlns)).text)
	desc = desc.replace(u"&", u"&amp;").replace("<", u"&lt;").replace(">", u"&gt;")
	encodedDesc = desc.replace("&lt;VulnDiscussion&gt;", u"<VulnDiscussion>").replace("&lt;/VulnDiscussion&gt;", u"</VulnDiscussion>")
	encodedDesc = encodedDesc.replace("&lt;IAControls&gt;", u"<IAControls>").replace("&lt;/IAControls&gt;", u"</IAControls>")
	innerXML = "<desc>%s</desc>" % format(encodedDesc)  # <desc> is needed, because the xml doc needs a root element
	try:
		xml = ET.XML(innerXML)
		desc = xml.find("VulnDiscussion").text
	except Exception, e:
		print "InnerXML Decoding Error"
	#	print "*"*80
	#	print innerXML
	#	print "*"*80
	
	try:
		iacontrols = xml.find("IAControls").text
	except Exception, e:
		iacontrols = None
		sys.exc_clear()
		pass
	return desc, iacontrols


def parseFindings(benchmark):
	findings = []
	groups = benchmark.findall("{%s}Group" % xmlns)
	for group in groups:
		finding = {}
		finding['id'] = group.get("id")
		finding['ruleID'] = group.find("{%s}Rule" % xmlns).get("id")
		finding['severity'] = group.find("{%s}Rule" % xmlns).get("severity")
		finding['version'] = group.find("{%s}Rule/{%s}version" % (xmlns, xmlns)).text
		finding['title'] = group.find("{%s}Rule/{%s}title" % (xmlns, xmlns)).text

		# The Below Try/Except statements are because DISA can't follow a goddamn standard consistently
		try:
			finding['fixtext'] = group.find("{%s}Rule/{%s}fixtext" % (xmlns, xmlns)).text
			finding['fixid'] = group.find("{%s}Rule/{%s}fixtext" % (xmlns, xmlns)).get('fixref')
		except Exception, e:
			finding['fixtext'] = "None"
			finding['fixid'] = "None"
			sys.exc_clear()
			pass
		try:	
			finding['checktext'] = group.find("{%s}Rule/{%s}check" % (xmlns, xmlns)).get('system')
			finding['checkid'] = group.find("{%s}Rule/{%s}check/{%s}check-content" % (xmlns, xmlns, xmlns)).text
		except Exception, e:	
			finding['checktext'] = "None"
			finding['checkid'] = "None"
			sys.exc_clear()
			pass
		# Easy ones done, now to get stuff out of the embedded XML inside.
		finding['desc'], finding['iacontrols'] = parseDescTag(group)
		findings.append(finding)
	return findings

def parseStig(xccdf):
	""" Parses the XCCDF file and passes portions to functions to store in SQL """
	benchmark = xccdf.getroot()
	stigHeader = parseHeader(benchmark)
	findings = parseFindings(benchmark)
	return stigHeader, findings

def persist(stig, findings):
		global dupes, totalfindings
		session = setupDB()
		try:

			s = STIG(stig)
			session.add(s)
			session.commit()
			
			#print "Imported STIG successfully."
		except IntegrityError, i:
#			print "This STIG has already been imported!"
#			print "Skipping STIG, but checking individual Findings."
			
			session.rollback()
			sys.exc_clear()
			pass

		for finding in findings:
			try:
				f = Finding(finding)
				session.add(f)	
				# commit each finding individuallly, as there is a 'unique' constraint
				# and you don't want ot not import all the other findings if there's a single
				# one that is a duplicate!
				session.commit()
				totalfindings = totalfindings + 1  	
				#print "Imported Finding (%s) successfully." % finding['id']
			except IntegrityError, i:
				dupes = dupes + 1
				#print "This Finding (%s) has already been imported!" % finding['id']
				session.rollback()
				sys.exc_clear()
				pass
		session.commit()

if __name__ == '__main__':


	if len(sys.argv) != 2:
		print "Error: Please supply a document to parse."
		sys.exit(-1)
	try:
#		print "Parsing %s" % sys.argv[1]
		xccdf = ET.parse(sys.argv[1])
		stig, findings = parseStig(xccdf)
		persist(stig, findings)


	except Exception,e:
		print "Error: Unable to parse XML document.  Are you sure that's XCCDF?"
		print "Error was %s" % e
		sys.exit(-1)

#	print "STIG:\t%s\tFindings:\t%s\tDuplicates:\t%s" % (stig['title'], totalfindings, dupes)
