# OK vbar_stack
# create a dict with
# category : [value for each time event]
# time : [each timestamp]
# p.vbar_stack(category, x='time', width=0.9, color=colors, source=source,
#             legend=[x for x in category])
#
#---
import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import row, column, layout
from bokeh.models import ColumnDataSource, TableColumn, DataTable, CustomJS
from bokeh.models.widgets import PreText, Select, Slider
from bokeh.plotting import figure, show, curdoc
from bokeh.models.callbacks import CustomJS
from bokeh.charts import Area
from bokeh.client import push_session
from bokeh.core.properties import value
from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from math import pi
import numpy as np

fname = '/Users/tomas/Documents/Notebook/Dashboards/Bokeh/Server Solution/yearly costs/data/Export.csv'

#df = pd.read_csv(fname, header=1, parse_dates=['Bokforingsdatum'])
#df = data.set_index('Bokforingsdatum')
df = pd.read_csv(fname, sep=";")
#df = dfa.set_index('Bokforingsdatum')

df['dt'] = pd.to_datetime(df['Bokforingsdatum'])
# df["dt"].dt.month

df['Belopp'] = df['Belopp'].str.replace(',','.')
df['Belopp'] = pd.to_numeric(df['Belopp'])
df['Cost'] = -1*df['Belopp']
df['yearMth'] = df['dt'].map(lambda x: 100*x.year + x.month)

df = df.sort_values(by=["yearMth","HASH"])
#df = df[df['Belopp']>0]


# define source data
source = ColumnDataSource(df)

# plot all data #
#---------
# pivot data
df_pivot2 = df.pivot_table(values='Cost', index=['HASH'],aggfunc=np.sum, columns="yearMth").fillna(0)
df_pivot2 = df_pivot2.reset_index(drop=False)

#---------
category = [c for c in sorted(set(df['HASH']))]
colors = ['#1f77b4','#aec7e8','#ff7f0e','#ffbb78','#2ca02c','#98df8a','#d62728','#ff9896','#9467bd','#c5b0d5','#8c564b']
# since yearMth is index in the pivot, I'm taking the values from the original df <redo>
dates = [str(a) for a in sorted(set(df.yearMth))]

wtf = {'time' : dates}

for i in range(len(category)):
    name = df_pivot2.iloc[i:i+1,:1].get_value(i,'HASH')
    values = df_pivot2.iloc[i+0:i+1,1:].get_values()
    val = values[0,:].tolist()
    wtf.update({name : val})

#---------
sourceW = ColumnDataSource(data=wtf)
original_source = ColumnDataSource(df)

p = figure(x_range=dates, plot_height=300, title="by Year", toolbar_location=None, tools="")
p.vbar_stack(category, x='time', width=0.9, legend=[value(x) for x in category], color = colors, source=sourceW)
# format plot
p.xaxis.major_label_orientation = -pi/4
p.y_range.start = -1000
p.x_range.range_padding = 0.1
p.xgrid.grid_line_color = None
p.axis.minor_tick_line_color = None
p.outline_line_color = None
p.legend.location = "bottom_right"
p.legend.orientation = "vertical"

#p.add_layout(legend, 'right')

# widget
offset = Slider(title="offset", value=201508, start=201508, end=201712, step=1)

# plot subset data #
def update_data(attrname, old, new):
    # Get the current slider values
    b = offset.value
    df_tmp = df[df['yearMth']>=b]
#    print(df_tmp.shape)
    df_pivot3 = df_tmp.pivot_table(values='Cost', index=['HASH'],aggfunc=np.sum, columns="yearMth").fillna(0)
    df_pivot3 = df_pivot3.reset_index(drop=False)
#    print(df_pivot3.shape)
#    category = [c for c in sorted(set(df_tmp['HASH']))]
#    colors = ['#1f77b4','#aec7e8','#ff7f0e','#ffbb78','#2ca02c','#98df8a','#d62728','#ff9896','#9467bd','#c5b0d5','#8c564b']
    dates = [str(a) for a in sorted(set(df_tmp.yearMth)) if (a >= b)]
#    print (len(dates))
    wtf = {'time' : dates}

    for i in range(len(category)):
        name = df_pivot3.iloc[i:i+1,:1].get_value(i,'HASH')
        values = df_pivot3.iloc[i+0:i+1,1:].get_values()
        val = values[0,:].tolist()
        wtf.update({name : val})
#    print([len(v) for v in wtf.values()])
#   Update the x-range
    p.x_range.factors = dates
# Update data source
#    sourceW.data=wtf
    sourceW.update(data=wtf)
#    sourceW = ColumnDataSource(data=wtf)


offset.on_change('value', update_data)


layout = layout(offset, p)

document = curdoc()
document.add_root(layout)
document.title = "Selection Histogram"

if __name__ == "__main__":
    print("\npress ctrl-C to exit")
    session = push_session(document)
    session.show()
    session.loop_until_closed()
