#!/usr/bin/env python

###
# (C) 2010 Adam Crosby
# Licensed under:
#  http://creativecommons.org/licenses/by-nc-sa/3.0/
##

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import xml.etree.ElementTree as ET
xmlns = "http://checklists.nist.gov/xccdf/1.1"

if len(sys.argv) != 2:
	print "  XCCDF-xml2tsv converts XCCDF XML documents (such as DISA STIGs)"
	print "    into easier to use Tab-Separated documents."
	print "  Please run as '%s' <filename> and redirect output as needed." % sys.argv[0]
	print "  Files should open easily in Excel."
	print "  E.g.:\n\t %s U_Perimeter_Router_v8R2_manual.xccdf.xml > output.tsv" % sys.argv[0]
	sys.exit(0)
try:
	xml = ET.parse(sys.argv[1])
except Exception,e:
	print "Error, unable to parse XML document.  Are you sure that's XCCDF?"
	sys.exit(-1)

benchmark = xml.getroot()

groups = benchmark.findall("{%s}Group" % xmlns)

print "Version\tTitle\tSeverity\tIA Controls"
for group in groups:
	group_id = group.get("id")
	title = group.find("{%s}title" % xmlns).text
	severity = group.find("{%s}Rule" % xmlns).get("severity")
	version = group.find("{%s}Rule/{%s}version" % (xmlns, xmlns)).text
	rule_title = group.find("{%s}Rule/{%s}title" % (xmlns, xmlns)).text
	desctag = "{%s}Rule/{%s}description" % (xmlns, xmlns)
	descriptiontext = group.find(desctag).text
	encodedDesc = descriptiontext.replace("&gt;", ">").replace("&lt;", "<").replace("&", "&amp;")
	innerXML = "<desc>%s</desc>" % format(encodedDesc)
	xml = ET.XML(innerXML)
	iacontrols = xml.find("IAControls").text

	print "%s\t%s\t%s\t%s\t%s\t%s\t" % (group_id, version, rule_title, title, severity, iacontrols)