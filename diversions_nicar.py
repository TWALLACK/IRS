# Script to create a new spreadsheet with organizations that checkmarked the diversion box

# NOTE: You might have to adjust the program depending on how many files you have created

# Import results from multiple years
# Select records where organizations checkmarked the diversion box
# Dump results into new 

# Import modules
import pandas as pd
import numpy as np
import os

# Set Variables
current_path = os.getcwd()  #looks up current working directory

# Selects results where organization checkmarked diversion box
def filter(dataframe):
	dataframe2 = dataframe[(dataframe['diversion'] == "1") | (dataframe['diversion'] == "true")]
	return(dataframe2)

# Load in the results from each year
df0 =filter(pd.read_csv(current_path + '\\main_18.csv'))
df1 =filter(pd.read_csv(current_path + '\\main_17.csv'))
df2 =filter(pd.read_csv(current_path + '\\main_16.csv'))
df3 =filter(pd.read_csv(current_path + '\\main_15.csv'))
df4 =filter(pd.read_csv(current_path + '\\main_14.csv'))
df5 =filter(pd.read_csv(current_path + '\\main_13.csv'))
df6 =filter(pd.read_csv(current_path + '\\main_12.csv'))
df7 =filter(pd.read_csv(current_path + '\\main_11.csv'))

#combine files
df8 = pd.concat([df0,df1,df2,df3,df4,df5,df6,df7])


#df8 =df8[df8.state == "MA"] # Select results from a single state

df8.to_csv(current_path + '\\diversion_list.csv', index=False)
print "the end"