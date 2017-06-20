# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 16:33 2017

@author: RobR
Python 3
"""
import os
from glob import glob
from os.path import join
import pandas as pd

# Expected setup is to drop the "BasicItems" CDS file into the same directory.
# Then we split the CDS file and write it to the current directory.
#

cwd = os.getcwd()

# Get result filename, test for != 1 result file
cds_file_list = glob('CDS_BasicItems*.xls')


if len(cds_file_list) == 0:
    print("No CDS file found!")
    quit()
elif len(cds_file_list) > 1:
    print("Found multiple CDS files, please place only ONE in the directory.")
    print(cds_file_list)
    quit()
else:
    cds_in = cds_file_list[0]
    file_date = cds_in[-12:-4]
    cds_short = cds_in[:-4]

# Begin processing.
print("Reading CDS Results File...")
df = pd.read_html(cds_in,header=0,parse_dates=['Start Date','End Date'])[0]

if len(df.columns)!=11:
    print("11 columns expected, we found {x}".format(x=len(df.columns)))
    print("We'll try this anyway but double check your file!")

hospitals = list(df['Reporting Entity'].unique())
total = len(hospitals)

loop = 1
while hospitals:
    hosp_sub_list = hospitals[0:10]
    df[df['Reporting Entity'].isin(hosp_sub_list)].to_excel(join(cwd,(str(loop)+'_'+cds_in)))
    hospitals = [name for name in hospitals if name not in hosp_sub_list]
    proc = round( (((10*loop)/total)*100),0)
    if proc>=100:
        proc = 100
    loop += 1
    print("Processed " + str(int(proc)) +r"%; Remaining: " + str(len(hospitals)))