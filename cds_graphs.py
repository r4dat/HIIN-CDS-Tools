# -*- coding: utf-8 -*-
"""
Created on Mon Jun 5 18:52:18 2017

@author: RobR
"""

import argparse
from glob import glob

import matplotlib
import pandas as pd

matplotlib.use('Agg')
import matplotlib.dates as mdates
import sys
import os
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, datetime, timedelta

# Year 1 target
soft_target_dict = {'ADE': 0.93,
                    'CLABSI': 0.90,
                    'CAUTI': 0.90,
                    'CDI': 0.93,
                    'Falls': 0.93,
                    'HAPU': 0.90,
                    'PrU': 0.90,
                    'SEPSIS': 0.93,
                    'Sepsis': 0.93,
                    'SSI': 0.90,
                    'VTE': 0.93,
                    'VAE': 0.93,
                    'WS': 0.95,
                    'MRSA': 0.95,
                    'READ': 0.96}

# Project Target
proj_target_dict = {'ADE': 0.80,
                    'CLABSI': 0.80,
                    'CAUTI': 0.80,
                    'CDI': 0.80,
                    'Falls': 0.80,
                    'HAPU': 0.80,
                    'PrU': 0.80,
                    'SEPSIS': 0.80,
                    'Sepsis': 0.80,
                    'SSI': 0.80,
                    'VTE': 0.80,
                    'VAE': 0.80,
                    'WS': 0.80,
                    'MRSA': 0.80,
                    'READ': 0.88}


# Plot monitoring performance vs. baseline & target if available.
def plot_perf_data(output_dir, dat, measure):
    hosp_name = dat['Reporting Entity'].values[0]
    hosp_name.replace('Hospital ', '')  # Shorten hospital titles for the label
    clean_hosp_name = ''.join(c for c in hosp_name if c.isalnum())  # Remove special chars

    out_filename = ''.join(clean_hosp_name + '_' + measure + ".png")
    out_filepath = os.path.join(output_dir, out_filename)

    baseline = dat[dat['Timeframe'] == 'Baseline']['Measure Rate'].values[0]

    measure_token = measure.split(sep='-')[1]

    rdx_target = baseline * proj_target_dict.get(measure_token)
    sft_rdx_target = baseline * soft_target_dict.get(measure_token)

    axislbl = 'Rate'
    width_inches = 5
    height_inches = 2
    measure_type = dat['Measure Type'].values[0]

    fig_size = (width_inches, height_inches)
    params = {
        'axes.labelsize': 4,
        'font.size': 4,
        'legend.fontsize': 4,
        'text.usetex': False,  # True causes issues with multiproc.
        'figure.figsize': fig_size,
        'font.family': 'serif',
        'axes.linewidth': 0.5,
        'xtick.labelsize': 3,
        'ytick.labelsize': 4}
    plt.rcParams.update(params)

    perfchart = plt.figure()
    perfchart.clf()

    # Baseline rate plot
    # Create empty dataframe to fill to eval period
    fill_list = []
    for y in range(2016, 2017 + 1):
        for m in range(1, 12 + 1):
            fill_list.append((date(y, m, 1), np.NaN))

    fill_dat = pd.DataFrame(data=fill_list, columns=['Start Date', 'Rate'])
    fill_dat.set_index('Start Date', drop=False, inplace=True)
    dat.sort_values(by='Start Date', inplace=True)
    dat.set_index('Start Date', drop=False, inplace=True)
    dat = dat.combine_first(fill_dat)
    try:
        dat.sort_values(by='Start Date', inplace=True)
    except TypeError:
        # Issue where one facility-measure has a datetime, and the rest have dates.
        dat['Start Date'] = pd.to_datetime(dat['Start Date'])
        dat.sort_values(by='Start Date', inplace=True)

    datecond = dat['Start Date'] >= date(2016, 10, 1)
    measure_cond = dat['HRET_MeasureID'] == measure
    dat = dat[datecond & measure_cond]

    plt.plot(dat[dat['Start Date'] >= date(2016, 10, 1)]['Start Date'].values,
             dat[dat['Start Date'] >= date(2016, 10, 1)]['Measure Rate'],
             color='#FFA500',
             linewidth=2,
             marker='o',
             markersize=4,
             markeredgewidth=1,
             markerfacecolor='#FFA500',
             markeredgecolor='w',
             clip_on=False,
             label=hosp_name)

    try:
        plt.axhline(y=baseline, color='black', linestyle=':', linewidth=.5, label='Facility Baseline')
    except TypeError:
        print('Baseline error? Not required.')
        print(baseline)

    ax = plt.gca()
    ax.axes.xaxis.set_major_formatter(mdates.DateFormatter('%b-%Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    perfchart.autofmt_xdate()
    plt.ylim(ymin=0)
    plt.ylabel(axislbl.replace('%', '\\%'))
    yax = ax.get_ylim()
    ymin = yax[0]
    ymax = (yax[1] * 1.05)
    ax.set_ylim(ymin, ymax)
    xmin = date(2016, 10, 1)
    xmax = (datetime.now().date().replace(day=1) - timedelta(1)).replace(day=1)
    ax.set_xlim(xmin, xmax)

    if measure_type == 'Outcome' or measure in ("HIIN-CAUTI-3a", "HIIN-CLABSI-3a", "HIIN-CAUTI-3b", "HIIN-CLABSI-3b"):
        try:
            datebool = (dat['Start Date'] >= xmin) & (dat['Start Date'] <= xmax)
            x = dat['Start Date'].values
            ax.fill_between(x, 0, rdx_target, where=datebool, facecolor='green', alpha=0.2, label='Target')
            ax.fill_between(x, 0, sft_rdx_target, where=datebool, facecolor='green', alpha=0.1)
        except TypeError:
            print('Target zone shading error.')
            print('Target value causing error was: ' + str(rdx_target))

    print("\tMaking plot " + str(out_filename))

    legend = plt.legend(loc='upper center', bbox_to_anchor=(0., 1.22, 1., .0122),
                        mode="expand", ncol=3, handlelength=4)
    legend.get_frame().set_edgecolor('white')
    plt.savefig(out_filepath, dpi=300, bbox_extra_artists=[legend], bbox_inches='tight')
    # Clear figure so next plot is empty.
    plt.clf()
    plt.close(perfchart)

    return out_filename, out_filepath


def plot_comp_data(output_dir, dat, measure):
    hosp_name = dat['Reporting Entity'].values[0]
    hosp_name.replace('Hospital ', '')  # Shorten hospital titles for the label
    clean_hosp_name = ''.join(c for c in hosp_name if c.isalnum())  # Remove special chars

    datecond = dat['Start Date'] >= date(2016, 10, 1)
    measure_cond = dat['HRET_MeasureID'] == measure
    dat = dat[datecond & measure_cond]

    plot_title = dat['Measure'].values[0]
    plot_title = ''.join(c for c in plot_title if c.isalnum())

    out_filename = ''.join(clean_hosp_name + '_comp_' + measure + plot_title + ".png")
    out_filepath = os.path.join(output_dir, out_filename)


    axislbl = 'Rate'
    width_inches = 5
    height_inches = 2

    fig_size = (width_inches, height_inches)
    params = {
        'axes.labelsize': 4,
        'font.size': 4,
        'legend.fontsize': 4,
        'text.usetex': False,  # True causes issues with multiproc.
        'figure.figsize': fig_size,
        'font.family': 'serif',
        'axes.linewidth': 0.5,
        'xtick.labelsize': 3,
        'ytick.labelsize': 4}
    plt.rcParams.update(params)

    compchart = plt.figure()
    compchart.clf()

    dat['fac_rate_isfinite'] = np.isfinite(dat['Rate'].astype(np.double))
    dat['state_rate_isfinite'] = np.isfinite(dat['All State Organizations Rate'].astype(np.double))
    dat['HRET_rate_isfinite'] = np.isfinite(dat['All Project Organizations Rate'].astype(np.double))

    plt.plot(dat[(dat['HRET_rate_isfinite']) & datecond]['Start Date'].values,
             dat[(dat['HRET_rate_isfinite']) & datecond]['All Project Organizations Rate'],
             marker='s', markersize=1, markerfacecolor='#078F33', markeredgecolor='w',
             color='#078F33',
             linewidth=1,
             label='CDC Strive')
    plt.plot(dat[dat['state_rate_isfinite'] & datecond]['Start Date'].values,
             dat[dat['state_rate_isfinite'] & datecond]['All State Organizations Rate'],
             color='#A5998C',
             linewidth=1,
             label='Kansas Strive')

    datecond = dat['Start Date'] >= date(2016, 10, 1)
    dat = dat[datecond]

    ax = plt.gca()  # gets current axes.
    ax.axes.xaxis.set_major_formatter(mdates.DateFormatter('%b-%Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    compchart.autofmt_xdate()
    plt.ylim(ymin=0)
    plt.ylabel(axislbl.replace('%', '\\%'))
    yax = ax.get_ylim()
    ymin = yax[0]
    ymax = (yax[1] * 1.05)
    ax.set_ylim(ymin, ymax)
    xmin = date(2016, 10, 1)
    if date(2017, 8, 10) > datetime.now().date():
        xmax = date(2017, 6, 1)
    else:
        xmax = datetime.now().date()
    ax.set_xlim(xmin, xmax)

    legend = plt.legend(loc='lower center', bbox_to_anchor=(0., -0.25, 1., .0122),
                        mode="expand", ncol=4, handlelength=5)
    legend.get_frame().set_edgecolor('white')
    plt.savefig(out_filepath, dpi=300, bbox_extra_artists=[legend], bbox_inches='tight')
    # Clear figure so that the next plot is clean
    plt.clf()
    plt.close(compchart)

    return out_filename, out_filepath


if __name__ == '__main__':

    # In practice the output dir should be required and no default.
    parser = argparse.ArgumentParser(description='Plot data in parallel')
    parser.add_argument('-o', '--outputDir', required=False, default=r"C:\temp",
                        help='The directory to which plot files should be saved')
    parser.add_argument('--numProcessors', required=False, type=int,
                        default=multiprocessing.cpu_count(),
                        help='Number of processors to use. ' + \
                             "Default for this machine is %d" % (
                                 multiprocessing.cpu_count(),))
    args = parser.parse_args()

    if not os.path.isdir(args.outputDir) or not os.access(args.outputDir,os.W_OK):
        sys.exit("Unable to write to output directory %s" % (args.outputDir,))

    if args.numProcessors < 1:
        sys.exit('Number of processors to use must be greater than 0')

    # Get result filename, test for != 1 result file
    cwd = os.getcwd()
    cds_file_list = glob('CDS_Results*.xls')

    if len(cds_file_list) == 0:
        sys.exit("No CDS file found!")
    elif len(cds_file_list) > 1:
        sys.exit("Found multiple CDS files, please place only ONE in the directory.")
    else:
        cds_in = cds_file_list[0]

    # Begin processing.
    # Read_html returns a list of dataframes (assuming multiple tables per page) so we have to get index 0.
    print("Reading CDS Results File...")
    try:
        df = pd.read_html(cds_in, header=0, parse_dates=['Start Date', 'End Date'])[0]
    except IOError:
        sys.exit("Error reading file.")

    hospitals = list(df['Reporting Entity'].unique())


    pool = multiprocessing.Pool(args.numProcessors)

    print("Making plots for %d hospitals" %
          (len(hospitals)))

    # Task list. Set up a Queue if directly using multiproc.
    tasks = []
    while hospitals:
        sub_df = df[df['Reporting Entity'] == (hospitals.pop())]
        measures = list(sub_df['HRET_MeasureID'].unique())
        while measures:
            sub_msr = measures.pop()
            tasks.append((args.outputDir, sub_df, sub_msr))


    results = [pool.apply_async(plot_perf_data, t) for t in tasks]


    for result in results:
        (plot_filename, plot_filepath) = result.get()
        print("Result: plot written to %s" % plot_filename)

    pool.close()
    pool.join()
