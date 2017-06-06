# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 10:44:33 2016

@author: RobR
Python 3
"""
import os
from glob import glob
from os.path import join
from shutil import copyfile
import pandas as pd


ic_bool=0
instr_bool=0
# Expected setup is to drop the "BasicItems" CDS file and (optionally) a
# fresh BLANK Improvement Calculator into the same directory. Then we split the
# CDS file and write it to sub-directories w/a copy of the IC.
# Working Folder contains: CDS_Spliter, CDS_Results, Improvement Calc.
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


response = 'n'
print()
response = input("Do you want to copy the Impr. Calc. into each hospital's folder? y/[n]? ")
if response.lower()!='n':
    # Get improvement calc filename. Test for !=1 copies.
    ic_file_list = glob('hiin_improvement_calculator.xlsx')
    if len(ic_file_list) == 0:
        print("No Improvement Calc file found!")
        quit()
    elif len(ic_file_list) > 1:
        print("Found multiple Improvement Calc files, please place only ONE in the directory.")
        print(ic_file_list)
        quit()
    else:
        ic_name = ic_file_list[0]
        ic_bool=1

response = 'n'
print()
response = input("Do you want to copy the Instructions into each hosp folder? y/[n]? ")
if response.lower()!='n':
    # Get improvement calc filename. Test for !=1 copies.
    ic_file_list = glob('hiin_ic_instruction_manual.pdf')
    if len(ic_file_list) == 0:
        print("No instructions found")
        quit()
    elif len(ic_file_list) > 1:
        print("Found multiple instructions please place only ONE in the directory.")
        print(ic_file_list)
        quit()
    else:
        instr = ic_file_list[0]
        instr_bool=1

# Status check.
print()
print('Current Directory: ' + cwd)
if ic_bool==1:
    print()
    print('Improvement Calc File: ' + ic_name)
print('CDS File: ' + cds_in)
print()
print('Download Date: ' + file_date)

response = 'n'
print()
response = input("Does this look right? y/[n]? ")
if response.lower()!='y':
    print("Aborting now!")
    quit()

   
# Begin processing.
print("Reading CDS Results File...")
df = pd.read_html(cds_in,header=0,parse_dates=['Start Date','End Date'])[0]

if len(df.columns)!=11:
    print("11 columns expected, we found {x}".format(x=len(df.columns)))
    print("We'll try this anyway but double check your file!")

grouped_df = df.groupby('Reporting Entity')

hospitals = list(df['Reporting Entity'].unique())

print("Making directories...")
# Nice to nest one more level so you can just select one folder and delete
# if needed.
top_dir = 'Hospital Subdirectories'

for name in hospitals:
    nice_short=name.split()[0]+'_'
    hosp_short=name.replace(' ','')
    hosp_short=hosp_short[0:8]+'_' # Using odd truncation avoid character limit
    os.makedirs(join(top_dir,name),exist_ok=True)
    out = grouped_df.get_group(name)
    out.to_excel(join(cwd,top_dir,name,(hosp_short+cds_short+'.xlsx')),sheet_name=(hosp_short+cds_short),index=False)
    if ic_bool==1:
        copyfile(join(cwd,ic_name),join(cwd,top_dir,name,(nice_short+ic_name)))
    if instr_bool==1:
        copyfile(join(cwd,instr),join(cwd,top_dir,name,instr))


quit()
