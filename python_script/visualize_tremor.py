"""
This module allows you to plot tremor data
interactively with the altair library
"""

import altair as alt
import numpy as np
import pandas as pd
import pickle
from datetime import datetime

def select_tremor(tremors, tbegin, tend, \
    latmin, latmax, lonmin, lonmax):
    """
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
    # Keep only tremors within a user-defined date range
    if (tbegin !=None):
        mask = (tremors['datetime'] >= tbegin)
        tremors = tremors.loc[mask]
    if (tend != None):
        mask = (tremors['datetime'] <= tend)
        tremors = tremors.loc[mask]
    return tremors

def bin_tremor(tremors, nbin, winlen):
    """
    """
    # Bin tremor windows
    smin = str(nbin) + 'T'
    df = pd.DataFrame({'Time': tremors['datetime'], 'Value': np.repeat(1, tremors.shape[0])})
    df.set_index('Time', inplace=True)
    df_group = df.groupby(pd.Grouper(level='Time', freq=smin))['Value'].agg('sum')   
    df_group = df_group.to_frame().reset_index()
    df_group['Value'] = (winlen / nbin) * df_group['Value']
    # Merge datasets to keep the number of tremor windows
    dfInterp = pd.merge_asof(tremors.sort_values(by="datetime"), df_group.sort_values(by="Time"), \
        left_on="datetime",right_on="Time")
    return dfInterp

def plot_tremor(tremors):
    """
    """
    brush = alt.selection(type='interval', encodings=['x'])
    points = alt.Chart().mark_point().encode(
        longitude = 'longitude',
        latitude = 'latitude',
        color=alt.Color('Time', legend=alt.Legend(format='%Y/%m/%d - %H:%M:%S'))
    ).transform_filter(
        brush.ref()
    ).properties(
        width=600,
        height=600
    )
    bars = alt.Chart().mark_area().encode(
        x=alt.X('Time', axis=alt.Axis(format='%Y/%m/%d - %H:%M:%S', title='Time')),
        y=alt.Y('Value', axis=alt.Axis(format='%', title='Percentage of tremor'))
    ).properties(
        width=600,
        height=100,
        selection=brush
    )
    myChart = alt.vconcat(points, bars, data=tremors)
    return myChart
    
def visualize_tremor(filename, output, nbin, winlen=1.0, \
    tbegin=None, tend=None, \
    latmin=None, latmax=None, lonmin=None, lonmax=None):
    """
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

    filename = 'tremors.pkl'
    output = 'big_map'
    winlen = 1.0
    nbin =  1440
    visualize_tremor(filename, output, nbin, winlen, \
        tbegin=None, tend=None, \
        latmin=None, latmax=None, lonmin=None, lonmax=None)
