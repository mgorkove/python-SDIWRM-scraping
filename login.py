import requests
from lxml import html, etree, cssselect 
import sys, os
from selenium import webdriver
 



login_url = "http://irwm.rmcwater.com/sd/login.php"
links_page_url = "http://irwm.rmcwater.com/sd/reports_result.php?rpt_id=844"
download_dir = "allData2.csv" 
base_href = "http://irwm.rmcwater.com/sd/"
browser = webdriver.Chrome() 
csv = open(download_dir, "w")


def main():
	login()
	getData()

def login():
	browser.get(login_url) 

	username = browser.find_element_by_id("email") 
	password = browser.find_element_by_id("pass")

	username.send_keys("my_username")
	password.send_keys("my_password")

	browser.find_element_by_id("login_submit").click() #submit button

	
	


def getData():
	download_links = []
	result = requests.Session().get(links_page_url, allow_redirects = False)
	doc = html.document_fromstring(result.content)
	writeCsvColLabels()
	for element, attribute, link, pos in doc.iterlinks():
		if "prj_master.php" in link: 
			downloadHref = base_href + link 
			downloadHref = downloadHref.replace("review", "preview")
			getPageContent(downloadHref)
		

def writeCsvColLabels():
	#date, round, summary, description, links w other projects, lead agency, co-sponsoring agencies, grant funding requested
	#watershed, local matching %
	#csv.write( "Project Name," + "Date," + "Round," + "Project Summary," + "Project Description," + 
	#"Links with other projects," + "Lead Agency," + "Co-sponsoring Agencies," +
	#"Grant Funding Requested," + "Watershed," + "Local Matching %," + "\n")
	csv.write("Project Name," + "Lead Agency," + "Project Location," + "Project Acreage,"+ 
	"Latitude," + "Longitude," + "Project Partners," + "Partnerships with Tri-County FACC or International Organizations," +
	"Functional Area," + "Project Type," + "Project Category," + "Primary Water Management Strategy," + 
	"Quantifiable Benefit 1," + "Units for Benefit 1," + "Quantifiable Benefit 2," + "Units for Benefit 2," + 
	"Affected Hydrologic Unit(s)," + "Affected Groundwater Basin(s)," + 
	"Affected Inland Surface Waters," + "Affected Coastal Waters," + "Beneficial Uses," + 
	"Does project provide a water-related benefit to a DAC," + "\n")

def getPageContent(link):
	try:
		browser.get(link) 
	except:
		print(link)
		return
	try:
		innerHTML = browser.execute_script("return document.body.innerHTML")
	except:
		print(link)
		return
	data = html.document_fromstring(innerHTML)
	writeToCsv(data)
	
def addToCsv(field):
	field = field.replace("\"", "")
	field = field.replace("\n", "")
	field = "\"" + field + "\""
	try:
		csv.write(field + ",")
	except:
		print("couldn't write something") #for debugging
		return

def writeDate():
	date = ""
	addToCsv(date)
	return 

def writeSummary(data):
	fdescription = data.get_element_by_id("fsetdesc")
	allTxt = fdescription.text_content()
	summary = allTxt.split("Project Description")[1]
	summary = summary.replace("Project Summary", "")
	summary = summary.replace("*", "")
	summary = summary.replace("(2-3 Paragraphs)", "")
	addToCsv(summary)
	return allTxt

def writeDescription(allTxt):
	restOfTxt = allTxt.split("Project Description")[2]
	description = restOfTxt.split("Identify Linkages with Other Projects")[0]
	description = description.replace("*", "")
	description = description.replace("(1 page)", "")
	addToCsv(description)
	return restOfTxt

def writeLinkages(restOfTxt):
	try:
		linkages = restOfTxt.split("Identify Linkages with Other Projects")[1]
	except:
		linkages = ""
	addToCsv(linkages)

def writeLeadOrg(data):
	leadOrg = data.get_element_by_id("tx_Organization").value
	addToCsv(leadOrg)

def writeCoOrgs(data):
	coOrgs = data.cssselect("[name=div_prtnrList]")[0].text_content() 
	addToCsv(coOrgs)

def writeNum(data, id1):
	fundReq = data.get_element_by_id(id1).value
	fundReq = fundReq.replace("$", "")
	fundReq = fundReq.replace(",", "")
	addToCsv(fundReq)
	return fundReq

def writeLocPct(fundReq, locMatch):
	locPct = 0
	if (float(fundReq) != 0.00): locPct = float(locMatch)/float(fundReq)
	addToCsv(str(locPct))

def writeWatershed():
	date = ""
	addToCsv(date)
	return 

def writeName(data):
	name = data.get_element_by_id("tx_ProjectTitle").value
	addToCsv(name)

def writeInput(data, id1):
	inp = data.get_element_by_id(id1).value
	addToCsv(inp)

def writeLocation(data): #not done 
	fset = data.get_element_by_id("fsetloc")
	loc = fset.find_class("plain-text")[0].text_content()
	addToCsv(loc)

def writePartnerships(data):
	checked = browser.execute_script("return document.getElementById(\"cb_prtnrFACC\").checked")
	addToCsv(str(checked))

def getSelect(data, id1):
	select = data.get_element_by_id(id1)
	if select.multiple:
		sv = ""
		for elem in select.value:
			cssSl = "[value=\"" + str(elem) + "\"]"
			sv += data.cssselect(cssSl)[0].text_content() + ", "
		addToCsv(sv)
	else:
		if str(select.value) == "None": 
			addToCsv("")
		else:
			cssSl = "[value=\"" + str(select.value) + "\"]"
			sv = data.cssselect(cssSl)[0].text_content()
			addToCsv(sv)

		



def writeToCsv(data):
	
	#I did this in 2 parts; the commented-out part below was not 
	#used for the second part
	"""
	writeDate()
	allTxt = writeSummary(data)
	restOfTxt = writeDescription(allTxt)
	writeLinkages(restOfTxt)
	writeLeadOrg(data)
	writeCoOrgs(data)
	fundReq = writeNum(data, "autcTotalGrantReq")
	writeWatershed()
	locMatch = writeNum(data, "autcTotalFundMatch")
	writeLocPct(fundReq, locMatch)
	"""
	#I separated them out like this, instead of just using for loops,
	#because I wanted to remember which ID corresponds to which data
	writeInput(data, "tx_ProjectTitle") # name
	writeInput(data, "tx_Organization") #lead org
	writeLocation(data)
	writeNum(data, "locAcreage") #acreage
	writeNum(data, "lt_LatLong") #latitude 
	writeNum(data, "ln_LatLong") #longitude
	writeCoOrgs(data)
	writePartnerships(data)
	getSelect(data, "FunctionalArea") # functional area
	getSelect(data, "ProjectType") # project type
	getSelect(data, "prjCategory") # project category
	getSelect(data, "strgPullDown") # primary water management strategy 
	writeInput(data, "tx_Readiness_ImpBenefits_1") # benefit 1
	writeInput(data, "tx_Readiness_ImpBenefits_unit_1") # benefit 1 units 
	writeInput(data, "tx_Readiness_ImpBenefits_2") # benefit 2
	writeInput(data, "tx_Readiness_ImpBenefits_unit_2") # benefit 2 units 
	getSelect(data, "slctHydroUnits") # affected hydrological units 
	getSelect(data, "slctGroundWater") # affected groundwater basins 
	getSelect(data, "slctInlandSrfcWtr") # affected inland surface water
	getSelect(data, "slctCoastalWaters") # affected coastal waters
	getSelect(data, "slctAffectedBeneficialUse") # affected beneficial uses
	getSelect(data, "CriticalWaterQuality") # does it benefit a dac
	csv.write("\n")



main()


