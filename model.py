#!/usr/bin/env python

from sqlalchemy import Column, Integer, String, Date, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import UniqueConstraint
import uuid
from hashlib import sha1

Base = declarative_base()

class STIG(Base):
	__tablename__ = 'stig'
	pkid = Column(String, primary_key=True)
	documentReference = Column(String) # URL to PDF or other non-XML document for clarity
	title = Column(String)  
	date = Column(Date)
	description = Column(Text)
	version = Column(String)
	# These attributes are CSV list of Finding.id's that are applicable to this profile
	MAC1PublicProfile = Column(String)  
	MAC1SensitiveProfile = Column(String)
	MAC1ClassifiedProfile = Column(String)
	MAC2PublicProfile = Column(String)
	MAC2SensitiveProfile = Column(String)
	MAC2ClassifiedProfile = Column(String)
	MAC3PublicProfile = Column(String)
	MAC3SensitiveProfile = Column(String)
	MAC3ClassifiedProfile = Column(String)
	fingerprint = Column(Text, unique=True)

	def __init__(self, stigDict=None):
		if stigDict:
			self.documentReference = stigDict.get('documentReference')
			self.date = stigDict['date']
			self.title = stigDict['title']
			self.description = stigDict['desc']
			self.version = stigDict['version']
			self.MAC1PublicProfile = ','.join(stigDict['MAC1Public'])  
			self.MAC1SensitiveProfile = ','.join(stigDict['MAC1Sensitive'])
			self.MAC1ClassifiedProfile = ','.join(stigDict['MAC1Classified'])
			self.MAC2PublicProfile = ','.join(stigDict['MAC2Public'])
			self.MAC2SensitiveProfile = ','.join(stigDict['MAC2Sensitive'])
			self.MAC2ClassifiedProfile = ','.join(stigDict['MAC2Classified'])
			self.MAC3PublicProfile = ','.join(stigDict['MAC3Public'])
			self.MAC3SensitiveProfile = ','.join(stigDict['MAC3Sensitive'])
			self.MAC3ClassifiedProfile = ','.join(stigDict['MAC3Classified'])
		self.pkid = uuid.uuid4().hex
		self.fingerprint = sha1(str(self.date) + str(self.title) + str(self.version)).hexdigest()


	def __repr__(self):
		return "<STIG('%s' - version %s)>" % (self.title, self.version)


	
class Finding(Base):
	__tablename__ = 'finding'
	findingid = Column(String, primary_key=True)  # XCCDF Group.id ('V-8538')
	ruleID = Column(String)	# XCCDF Rule.id ('SV-9035r3_rule')
	severity = Column(Enum('low', 'medium', 'high', name='ruleseverity'))
	version = Column(String)
	title = Column(Text)
	description = Column(Text)
	fixtext = Column(Text) 
	fixid = Column(String)	# XCCDF fix.id ('F-8065r2_fix')
	checktext = Column(Text)
	checkid = Column(String) # XCCDF check.id ('C-7700r2_chk')
	iacontrols = Column(String) # CSV separated list of IA controls
	def __init__(self, findingDict=None):
		if findingDict:
			self.findingid = findingDict['id']
			self.ruleID = findingDict['ruleID']
			self.severity = findingDict['severity']
			self.version = findingDict['version']
			self.title = findingDict['title']
			self.description = findingDict['desc']
			self.fixtext = findingDict['fixtext']
			self.fixid = findingDict['fixid']
			self.checktext = findingDict['checktext']
			self.checkid = findingDict['checkid']
			self.iacontrols = findingDict['iacontrols']


