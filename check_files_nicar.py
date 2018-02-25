# Script to download 990 XML files for each year available

# The script 
# 1) Creates subdirectoies
# 2) Downloads indexes for the years available (2011 to 2018)
# 3) Checks to see what (if any) filings you have already downloaded
# 4) Downloads all the missing filings for each year available

#import modules
import os, csv, urllib2, time

#define variables
path = os.getcwd()  #looks up current working directory
start_year = 2011  #Data starts with 2011, but you can pick a later year
end_year = 2018    #Last year data is currently available
file_list = []
return_list = []

# Creates list of file names fbrom online IRS index 
# Need to feed in the year you want (from 2011 to 2017) The 2018 index has yet to be created (as of Jan 8, 2018)

# Creates new folders (sub directories)
def new_folders(year):
    newpath = path + "\\filings_" + str(year)[2:]
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    #print path
    #print newpath    


# Downloads index for each year and builds list of filings available
def index(year):
    url = "https://s3.amazonaws.com/irs-form-990/index_" + str(year) + ".csv"
    return_list = []
    index_file = urllib2.urlopen(url) 
    for line in index_file: # files are iterable
        line = line.split(",")
        return_number = line[8].strip()
        if return_number != "OBJECT_ID":  #this ignores the header role
            return_list.append(return_number)
    print "There are " + str(len(return_list)) + " items in index list for " + str(year)
    return return_list

# Function to build a list of the filings already downloaded for the given year
def files(year):
    newpath = path + "\\filings_" + str(year)[2:]
    file_list = [ file[:-5] for file in os.listdir(newpath) if file[-4:] == 'html' ]
    filings = str(len(file_list))
    print "There are %s filings in the folder." % (filings)
    return file_list

# Function to downloads new filings
def grab(item,year):
    newpath = path + "\\filings_" + str(year)[2:] + "/"
    url = "https://s3.amazonaws.com/irs-form-990/" + str(item) + "_public.xml"
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
    outfile = open(newpath+str(item)+".html", 'w')
    outfile.write(web_page)
    outfile.close()


# Create new folders (if they don't already exist)
for year in range(start_year,end_year+1):
    new_folders(year)

for year in range(start_year,end_year+1): 
    print year # This is the year currently being checked
    return_list = index(year)
    file_list = files(year)
    for item in return_list:
        if item not in file_list and item != "93491211007003":
            try: 
                grab(item, year)
                print item
            except Exception:
                print "failed to grab "+ item
