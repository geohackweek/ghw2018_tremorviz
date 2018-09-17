"""
This module allows you to plot tremor data interactively
with the Python package altair
"""

import altair as alt
import numpy as np
import pandas as pd
#import pickle
#from datetime import datetime

def select_tremor(tremors, tbegin, tend, \
    latmin, latmax, lonmin, lonmax):
    """
    Select tremor within user-defined area and time range

    Input:
        type tremors = pandas dataframe
        tremors = {datetime, latitude, longitude, depth}
        type tbegin = datatime.datetime
        tbegin = Beginning of selected time interval
        type tend = datatime.datetime
        tend = End of selected time interval
        type latmin = float
        latmin = Southern boundary of selected region
        type latmax = float
        latmax = Northern boundary of selected region
        type latmin = float
        lonmin = Western boundary of selected region
        type latmin = float
        lonmax = Eastern boundary of selected region
    Output:
        type tremors = pandas dataframe
        tremors = {datetime, latitude, longitude, depth}
    """
    # Keep only tremors within a user-defined area
    if (latmin != None):
        tremors = tremors.loc[(tremors['latitude'] >= latmin)]
    if (latmax != None):
        tremors = tremors.loc[(tremors['latitude'] <= latmax)]
    if (lonmin != None):
        tremors = tremors.loc[(tremors['longitude'] >= lonmin)]
    if (lonmax != None):
        tremors = tremors.loc[(tremors['longitude'] <= lonmax)]
    # Keep only tremors within a user-defined time range
    if (tbegin !=None):
        mask = (tremors['datetime'] >= tbegin)
        tremors = tremors.loc[mask]
    if (tend != None):
        mask = (tremors['datetime'] <= tend)
        tremors = tremors.loc[mask]
    return tremors

def bin_tremor(tremors, nbin, winlen):
    """
    Compute the percentage of the time during which there is recorded tremor

    Input:
        type tremors = pandas dataframe
        tremors = {datetime, latitude, longitude, depth}
        type nbin = integer
        nbin = Duration of the time windows (in minutes) for which we compute
            the percentage of time with tremor
        type winlen = float
        winlen = Duration of the time windows from the tremor catalog
            (in minutes)
    Output:
        type dfInterp = pandas dataframe
        dfInterp = {datetime, latitude, longitude, depth, Time, Value}
    """
    # Bin tremor windows
    smin = str(nbin) + 'T'
    df = pd.DataFrame({'Time': tremors['datetime'], \
                       'Value': np.repeat(1, tremors.shape[0])})
    df.set_index('Time', inplace=True)
    df_group = df.groupby(pd.Grouper(level='Time', \
        freq=smin))['Value'].agg('sum')   
    df_group = df_group.to_frame().reset_index()
    df_group['Value'] = (winlen / nbin) * df_group['Value']
    # Merge datasets to keep the number of tremor windows
    dfInterp = pd.merge_asof(tremors.sort_values(by="datetime"), \
        df_group.sort_values(by="Time"), left_on="datetime", right_on="Time")
    return dfInterp

def plot_tremor(tremors):
    """
    Plot tremor location and tremor activity
    with interaction between both graphs

    Input:
        type tremors = pandas dataframe
        tremors = {datetime, latitude, longitude, depth, Time, Value}
    Output:
        type myChart = Altair chart
        myChart = tremor plot
    """
    # Selection
    brush = alt.selection(type='interval', encodings=['x'])
    # Map of tremor location
    points = alt.Chart(
    ).mark_point(
    ).encode(
        longitude = 'longitude',
        latitude = 'latitude',
        color=alt.Color('Time', \
                        legend=alt.Legend(format='%Y/%m/%d - %H:%M:%S'))
    ).transform_filter(
        brush.ref()
    ).properties(
        width=600,
        height=600
    )
    # Graph of tremor activity
    bars = alt.Chart(
    ).mark_area(
    ).encode(
        x=alt.X('Time', \
                axis=alt.Axis(format='%Y/%m/%d - %H:%M:%S', title='Time')),
        y=alt.Y('Value', \
                axis=alt.Axis(format='%', title='Percentage of tremor'))
    ).properties(
        width=600,
        height=100,
        selection=brush
    )
    # Putting graphs together
    myChart = alt.vconcat(points, bars, data=tremors)
    return myChart
    
def visualize_tremor(filename, output, nbin, winlen=1.0, \
    tbegin=None, tend=None, \
    latmin=None, latmax=None, lonmin=None, lonmax=None):
    """
    Read and plot tremor location and activity

    Input:
        type filename = string
        filename = Pickle file where tremor dataset is stored
        type output = string
        output = Name of output file containing the figure
        type nbin = integer
        nbin = Duration of the time windows (in minutes) for which we compute
            the percentage of time with tremor
        type winlen = float
        winlen = Duration of the time windows from the tremor catalog
            (in minutes)
        type tbegin = datatime.datetime
        tbegin = Beginning of selected time interval
        type tend = datatime.datetime
        tend = End of selected time interval
        type latmin = float
        latmin = Southern boundary of selected region
        type latmax = float
        latmax = Northern boundary of selected region
        type latmin = float
        lonmin = Western boundary of selected region
        type latmin = float
        lonmax = Eastern boundary of selected region
    Output:
        None
    """
    # Read dataset
    tremors = pd.read_pickle(filename)[0]
    # Select tremors
    tremors = select_tremor(tremors, tbegin, tend, \
        latmin, latmax, lonmin, lonmax)
    # Construct time line for selection
    tremors = bin_tremor(tremors, nbin, winlen)
    # Manage big datasets
    alt.data_transformers.enable('json')
    # Plot
    myChart = plot_tremor(tremors)
    # Save
    myChart.save(output + '.html')

if __name__ == '__main__':

#    filename = 'ghosh_al_2012_JGR.pkl'
    filename = 'PNSN_2009-2018_NW.pkl'
#    output = 'ghosh_al_2012_JGR'
    output = 'PNSN_2009-2018_NW'
#   winlen = 1.0
    winlen = 2.5
    nbin =  1440
    visualize_tremor(filename, output, nbin, winlen, \
        tbegin=None, tend=None, \
        latmin=None, latmax=None, lonmin=None, lonmax=None)
