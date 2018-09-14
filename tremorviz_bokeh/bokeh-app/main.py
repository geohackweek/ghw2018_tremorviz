from os.path import join, dirname
import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import gridplot, column, widgetbox, layout
from bokeh.models import (ColumnDataSource, 
                          ResetTool, PanTool, BoxZoomTool, WheelZoomTool,
                         )
from bokeh.plotting import figure
from bokeh.tile_providers import CARTODBPOSITRON
from bokeh.models.widgets import DateSlider

def make_plot(selected_data_source, unselected_data_source):    
    tools = [ResetTool(), PanTool(), BoxZoomTool(), WheelZoomTool()]
    
    xmin, xmax = df0.merc_long.min(), df0.merc_long.max()
    ymin, ymax = df0.merc_lat.min(), df0.merc_lat.max()

    top = figure(tools=tools, plot_width=600, plot_height=500, title='Tremor locations', x_range=(xmin, xmax), y_range=(ymin, ymax),
               x_axis_type="mercator", y_axis_type="mercator")
    top.add_tile(CARTODBPOSITRON)
    top.circle('merc_long', 'merc_lat', source=unselected_data_source, color='gray', alpha=0.2)
    top.circle('merc_long', 'merc_lat', source=selected_data_source, color='red', alpha=1.0)#, view=view)

    bottom = figure(plot_width=600, plot_height=80, title=None, x_axis_type="datetime")
    bottom.line('date', 'value', source=ColumnDataSource(df0), color='red', alpha=0.8)

    p = gridplot([[top], [bottom]], toolbar_location='right')
    
    return p

def get_datasets(df):
    '''Filter based on widget
    '''
    # start with the whole dataset
    copy = df.copy()
    # narrow by selected date from the DateSlider
    selected = copy[copy['date']==pd.Timestamp(date_slider.value)]
    unselected = copy[copy['date'] < pd.Timestamp(date_slider.value)]

    return {'selected':ColumnDataSource(data=selected), 'unselected':ColumnDataSource(unselected)}
    
def update_plot():
    src = get_datasets(df)
    selected_data_source.data.update(src['selected'].data)
    unselected_data_source.data.update(src['unselected'].data)

df0 = pd.read_pickle(join(dirname(__file__), 'data', 'tremors.pkl'))
df = df0.sample(frac=0.1)


date_slider = DateSlider(start=df['date'].min(), end=df['date'].max(), step=100, value=df['date'].min())
date_slider.on_change('value', lambda attr, old, new: update_plot())

slider_box = widgetbox(children=[date_slider], width=600)

datasets_init = get_datasets(df) # get bokeh ColumnDataSource
selected_data_source = datasets_init['selected']
unselected_data_source = datasets_init['unselected']
p = make_plot(selected_data_source, unselected_data_source)

layout = layout(children=[[p],[slider_box]], sizing_mode='fixed')

curdoc().add_root(layout)