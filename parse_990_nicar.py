# Script to parse 990 XML files, one year at a time


# import modules
import xmltodict, json, requests, re, os, time, csv

#Define initial variables
year = 18  #Two Digit Year Between 11 and 18
current_path = os.getcwd()  #looks up current working directory
path = current_path + "\\filings_" + str(year) + "\\" #This is where files are stored
path = "c:/python27/nonprofit/filings_" + str(year) + "/" #This is where files are stored
path_out = os.getcwd() + "\\" #This is where the output files are stored
main_file = path_out + 'main_' + str(year) + '.csv'

#headers for output file
headers_main = ["bus_name","ein","url","address","city","state","zipcode","formation","organization","organization_flag","tax_period_begin","tax_period_end","tax_year","signature_date","return_date","amended","return_type","cy_revenue","diversion","explanation"]

# Function to create output file
def create_output_file(output_file,headers):
    with open(output_file,'wb') as csv_output:
        rowwriter = csv.writer(csv_output, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)  
        rowwriter.writerow(headers)

# Function to add info to output file
def amend_output_file(output_file,new_line):
    with open(output_file,'ab') as csv_output:
        rowwriter = csv.writer(csv_output, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)  
        rowwriter.writerow(new_line)

# Command to create output files
create_output_file(main_file,headers_main)


# Build a list of the 990 files already stored in directory
filing_list = [ i for i in os.listdir(path) if i[-4:] == 'html' ]
filings = str(len(filing_list))
print "There are " + str(filings) + " filings in the folder."

#grab text in tag
def grab_text(regex,web_page):
    match = re.search(regex,web_page)
    if match:
        tag = match.group(1)
    else:
        tag = ""
    return tag

#grab multiple pieces of text in tag
def grab_texts(regex,web_page,fields):
    match = re.search(regex,web_page)
    tags = []
    if match:
        for field in range(fields):
            tags.append(match.group(field + 1))
            tags.append(" ")
    else:
        for field in range(fields):
            tags.append("")
    return tags


# Function to grab basic filer info from 990 
def grab_filer_info(page):
    global bus_name,ein,city,state,zipcode,address,tax_period_begin,tax_period_end,signature_date,return_date,amended,return_type,tax_year
    #reset variables used in function
    bus_name = ""
    ein = ""  
    address_info =[]  #Sets up empty bucket for address info
    zipcode = ""
    state = ""
    city = ""
    address = ""
    o = xmltodict.parse(page)
    try:
    	dict= o['Return']['ReturnHeader']['Filer']['BusinessName']
    except Exception:
    	dict = o['Return']['ReturnHeader']['Filer']['Name']
    for key, value in dict.iteritems():
        bus_name += value + " "
        bus_name.replace('"', '\'')  
    ein = o['Return']['ReturnHeader']['Filer']['EIN']
    try:
        dict= o['Return']['ReturnHeader']['Filer']['USAddress']
        for key, value in dict.iteritems():
        	address_info.append(value)
    	zipcode = address_info.pop()
    	state = address_info.pop()
    	city = address_info.pop()
    	for info in address_info:
        	address += info + " "
    except KeyError:
        dict= o['Return']['ReturnHeader']['Filer']['ForeignAddress']
        address_info = ""
        for key, value in dict.iteritems():
        	address_info += value + " "
        ziocode = ""
        city = ""
        state = ""
        address = address_info
    tax_period_begin = grab_text(r'>([^<]*)</TaxPeriodBegin(?:Dt|Date)>',page)
    tax_period_end = grab_text(r'>([^<]*)</TaxPeriodEnd(?:Dt|Date)>',page)
    signature_date = grab_text(r'>([^<]*)</(Signature(?:Dt|Date)?|DateSigned)>',page)
    return_date = grab_text(r'>([^<]*)</(?:ReturnTs|Timestamp)>',page)
    amended = grab_text(r'>([^<]*)</AmendedReturn(?:Ind)?>',page)
    return_type = grab_text(r'>([^<]*)</ReturnType(?:C)?[A-z]*>',page)
    tax_year = grab_text(r'<TaxY(?:ea)?r>([^<]*)</TaxY(?:ea)?r>',page)


# this function parses body of 990
def parse_990(page,url):
    grab_filer_info(page)
    match = re.search(r'>([^<]*)</Organization501c3(?:Ind)?>',page)
    match2 = re.search(r'<Organization501cInd\s*organization501cTypeTxt=\"(\d*)\">([^<]*)</Organization501cInd>',page)
    match3 = re.search(r'<Organization501c3(?:Ind)?[^>]*>([^<]*)</Organization501c3(?:Ind)?>',page)
    match4 = re.search(r'<Organization4947a1NotPF(?:Ind)?>([^<]*)</Organization4947a1NotPF(?:Ind)?>',page)
    match5 = re.search(r'<Organization501c\s*typeOf501cOrganization=\"(\d*)\">([^<]*)</Organization501c>',page)
    if match:
        organization = "501c3"
        organization_flag = match.group(1)
    elif match2:
        organization = "501c" + match2.group(1)
        organization_flag = match2.group(2)
    elif match3:
        organization = "501c3" 
        organization_flag = match3.group(1)
    elif match4:
        organization = "4947a1"
        organization_flag = match4.group(1)
    elif match5:
        organization = "501c" + match5.group(1)
        organization_flag = match5.group(2)
    else:
        organization = ""
        organization_flag = ""


   # This section grabs several key fields from forms. You can easily add others
    formation = grab_text(r'>([^<]*)</(?:YearFormation|Formation(?:Yr|Year))>',page)
    domicile_state = grab_text(r'>([^<]*)</(?:StateLegalDomicile|LegalDomicileState[A-z]*)>',page)
    cy_revenue =grab_text(r'>([^<]*)</(?:CYTotalRevenueAmt|TotalRevenueCurrentYear)',page)
    match = re.search(r'>([^<]*)</MaterialDiversionOrMisuse(?:Ind)?>',page)


    # This ugly section hunts for any text explaining material diversion of assets in the free-text supplements of the form
    # Note: The material diversion of assets is Part VI, Line 5 of the form
    # It could be condensed by creating a function
    explanation = ""
    if match:
        diversion = match.group(1)
        if diversion == "1" or diversion.upper() == "TRUE":
            regex = ur"<SupplementalInformationDetail>\s*<FormAndLineReferenceDesc>([^<]*)</FormAndLineReferenceDesc>\s*<ExplanationTxt>([^<]*)</ExplanationTxt>\s*</SupplementalInformationDetail>"
            supplementals = re.findall(regex, page)
            for supp in supplementals:
                if "LINE 5" in supp[0].upper() or "QUESTION 5" in supp[0].upper():
                    if " VI" in supp[0] or "PART VI" in supp[0].upper() or "PART 6" in supp[0].upper():
                        explanation += supp[1] + " "
                        explanation.replace('"', '\'')
            if explanation == "":
                regex = ur"<GeneralExplanation>\s*<Identifier>([^<]*)</Identifier>\s*(?:<ReturnReference>[^<]*</ReturnReference>\s*)?<Explanation>([^<]*)</Explanation>\s*</GeneralExplanation>"
                supplementals = re.findall(regex, page)
                for supp in supplementals:
                    if "LINE 5" in supp[0].upper()  or "QUESTION 5" in supp[0].upper():
                        if " VI" in supp[0] or "PART VI" in supp[0].upper() or "PART 6" in supp[0].upper():
                            explanation += supp[1] + " "
                            explanation.replace('"', '\'')
            if explanation == "":
                regex = ur"<ReturnReference>\s*([^<]*)</ReturnReference>\s*<Explanation>([^<]*)\s*</Explanation>"
                supplementals = re.findall(regex, page)
                for supp in supplementals:
                    if "LINE 5" in supp[0].upper() or "QUESTION 5" in supp[0].upper():
                        if " VI" in supp[0] or "PART VI" in supp[0].upper() or "PART 6" in supp[0].upper():
                            explanation += supp[1] + " "
                            explanation.replace('"', '\'')
            if explanation == "":
                regex = ur">\s*([^<]*)</Identifier>\s(?:<ReturnReference>\s*[^<]*</ReturnReference>)?\s*<Explanation>([^<]*)\s*</Explanation>"
                supplementals = re.findall(regex, page)
                for supp in supplementals:
                    if "diversion" in supp[0].upper():
                        explanation += supp[1] + " "
                        explanation.replace('"', '\'')
            if explanation == "":
                regex = ur"<Explanation>([^<]*)\s*</Explanation>"
                supplementals = re.findall(regex, page)
                for supp in supplementals:
                    if "diversion" in supp[0].upper() or " stole" in supp[0].upper() or "embezzle" in supp[0].upper() or "misappropriate" in supp[0].upper() or " diverted" in supp[0].upper():
                        explanation += supp + " "
                        explanation.replace('"', '\'')                 
    else:       
        diversion = ""    
    row_main = []
    for header in headers_main:
        row_main.append(eval(header))  #add every field in heards to new row

    amend_output_file(main_file,row_main) #save new row to output file


#Main part of program
#Loops through each filing in folder
#Only gathers data from the traditional 990 form.
#Ignores 990PFs and 990EZs because those don't contain the question about material diversion of assets


for filing in filing_list:
    infile = open(path + filing)
    web_page = infile.read()
    url = "https://s3.amazonaws.com/irs-form-990/" + filing[:-5] + "_public.xml"
    print url
    match = re.search(r'<ReturnType(?:Cd)?>([^<]*)</ReturnType(?:Cd)?>',web_page)
    if match:
        ReturnTypeCd = match.group(1)
        if ReturnTypeCd in ('990','990EO','990O'):
            parse_990(web_page,url)
        else:
            pass
