# IRS
Scripts to work with IRS 990 XML data

You can find background on the data here:
https://www.irs.gov/newsroom/irs-makes-electronically-filed-form-990-data-available-in-new-format

There are three scripts in the directory:

check_files_nicar -- downloads XML filings
parse_990_nicar --   extracts key fields from filings
diversions_nicar --  select filings where organization reported a material diversion of assets

There are two csvs:
diversion_list_2018.csv (Sample output based on data available through 2/25/18)
diversion_data_2011_17.csv (Data for 2011-2017 based on data available at end of 2017. IRS has since added some additional 2017 data.)






