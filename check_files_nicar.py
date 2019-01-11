# Script to download IRS 990 XML files from AWS for each year available

# The script reads data from the AWS hosted copy of IRS 990 filings
#   https://aws.amazon.com/public-datasets/irs-990/
# 1) Creates /filing_xx subdirectories
# 2) Downloads indexes for the years available (2011 to 2018)
# 3) Checks to see what (if any) filings you have already downloaded
# 4) Downloads all the missing filings for each year available

#import modules
import os, csv, urllib2, time

IRS_LISTING_URL = "https://s3.amazonaws.com/irs-form-990/"
IRS_FILE_URL = IRS_LISTING_URL + "index_"

# Downloads index for each year and builds list of filings available
def index(path, year):
    url = IRS_FILE_URL + str(year) + ".csv"
    index_file = urllib2.urlopen(url)
    return_list = []
    for line in index_file: # files are iterable
        line = line.split(",")
        return_number = line[8].strip()
        if return_number != "OBJECT_ID":  #this ignores the header role
            return_list.append(return_number)
    print "There are " + str(len(return_list)) + " items in index list for " + str(year)
    return return_list

# Function to build a list of the filings already downloaded for the given year
def files(path, year):
    file_list = [ file[:-5] for file in os.listdir(path) if file[-4:] == 'html' ]
    print "There are %s filings in the folder." % (str(len(file_list)))
    return file_list

# Function to downloads new filings
def grab(path, item, year):
    newpath = path + os.path.sep
    url = IRS_LISTING_URL + str(item) + "_public.xml"
    print url
    try:  
        response = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        time.sleep(100)
        response = urllib2.urlopen(url)
    except Exception:
        time.sleep(100)
        response = urllib2.urlopen(url)
    web_page = response.read()
    outfile = open(newpath + str(item) + ".html", 'w')
    outfile.write(web_page)
    outfile.close()


# Main program execution #
start_year = 2016  #Data starts with 2011, but you can pick a later year
end_year = 2016    #Last year data is currently available

for year in range(start_year, end_year + 1): 
    path = os.path.join(os.getcwd(), "filings_" + str(year)[2:])
    if not os.path.exists(path):
        os.makedirs(path)
    print str(year) + " data downloading to " + path # This is the year currently being checked
    return_list = index(path, year)
    file_list = files(path, year)
    for item in return_list:
        if item not in file_list and item != "93491211007003":
            try: 
                grab(path, item, year)
                print item
            except Exception as e:
                print "failed to grab " + item + " due to: " + str(e)

print "DONE"
