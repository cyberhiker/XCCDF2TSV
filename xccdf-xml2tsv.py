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
check_list = []
profile_name = "MAC-3_Sensitive"
profiles = benchmark.findall("{%s}Profile" % xmlns)
for profile in profiles:
	if profile.get("id") == profile_name:
		#<select idref="V-761" selected="true"/>
		selects = profile.findall("{%s}select" % xmlns)
		for select_tag in selects:
			if select_tag.get("selected") == "true":
				check_list.append(select_tag.get('idref'))
					
groups = benchmark.findall("{%s}Group" % xmlns)

print "ID\tVersion\tRule Title\tTitle\tSeverity\tIA Controls"
for group in groups:
	group_id = group.get("id")
	if group_id in check_list:
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
		print "%s\t%s\t%s\t%s\t%s\t%s\t" % (group_id.replace('\n', '##').replace('V-',''), version.replace('\n', '##'), rule_title.replace('\n', '##'), title.replace('\n', '##'), severity.replace('\n', '##'), iacontrols.replace('\n', '##'))
