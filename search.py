#!/usr/bin/env
#from flask import *
#from flask.ext.sqlalchemy import SQLAlchemy
import urllib
from model import STIG, Finding
HARD_LIMIT = 25

def searchSTIGNames(query):
	return STIG.query.filter(STIG.title.ilike(query)).all()
	
def searchSTIGDescriptions(query):
	return STIG.query.filter(STIG.description.ilike(query)).all()

def searchFindingName(query):
	return Finding.query.filter(Finding.title.ilike(query)).all()

def searchFindingVersion(query):
	return Finding.query.filter(Finding.version.ilike(query)).all()

def searchFindingIAControls(query):
	return Finding.query.filter(Finding.iacontrols.ilike(query)).all()

def searchFindingRuleID(query):
	return Finding.query.filter(Finding.ruleID.ilike(query)).all()

def searchFindingDescription(query):
	return Finding.query.filter(Finding.description.ilike(query)).all()

def searchFindingCheckText(query):
	return Finding.query.filter(Finding.checktext.ilike(query)).all()

def searchFindingFixText(query):
	return Finding.query.filter(Finding.fixtext.ilike(query)).all()

def searchFindingCheckID(query):
	return Finding.query.filter(Finding.checkid.ilike(query)).all()

def searchFindingFixID(query):
	return Finding.query.filter(Finding.fixid.ilike(query)).all()

def getSearchResults(query):
	query = query.replace("%", "")
	results = {'findings':[], 'stigs':[]}
	sql_query = '%%%s%%' % query # So it can be used in 'like' searchs properly

	results['stigs'] = searchSTIGNames(sql_query)
	results['stigs'] = results['stigs'] + searchSTIGDescriptions(sql_query)

	results['findings'] = searchFindingRuleID(sql_query)
	results['findings'] = results['findings'] + searchFindingName(sql_query)
	results['findings'] = results['findings'] + searchFindingVersion(sql_query)
	results['findings'] = results['findings'] + searchFindingIAControls(sql_query)
	results['findings'] = results['findings'] + searchFindingDescription(sql_query)
	results['findings'] = results['findings'] + searchFindingCheckText(sql_query)
	results['findings'] = results['findings'] + searchFindingCheckID(sql_query)
	results['findings'] = results['findings'] + searchFindingFixText(sql_query)
	results['findings'] = results['findings'] + searchFindingFixID(sql_query)

	results['stigs'] = list(set(results['stigs'])) # Eliminate duplicates
	results['findings'] = list(set(results['findings'])) # Eliminate duplicates

	# Some checks had no <description tag> - Patched for now, fix in import!
	for result in results['findings']:
		if result.description == None:
			result.description = ""
	if (len(results['stigs']) > 0) or (len(results['findings']) > 0):
		return results
	else:
		return False


