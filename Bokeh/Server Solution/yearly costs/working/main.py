# 3 Oct 2017
# Working but needs big clean up
#---
import pandas as pd
import numpy as np
from math import pi
from bokeh.io import curdoc, show, output_file
from bokeh.layouts import row, column, layout
from bokeh.models import ColumnDataSource, TableColumn, DataTable, CustomJS, PrintfTickFormatter, DateFormatter
from bokeh.models.widgets import PreText, Select, Slider
from bokeh.models.callbacks import CustomJS
from bokeh.charts import Area
from bokeh.client import push_session
from bokeh.core.properties import value
from bokeh.plotting import figure, show, curdoc


# read data
fname = '/Users/tomas/Documents/Notebook/Dashboards/Bokeh/Server Solution/yearly costs/data/Export.csv'
df = pd.read_csv(fname, sep=";")

df['dt'] = pd.to_datetime(df['Bokforingsdatum'])
df['Belopp'] = df['Belopp'].str.replace(',','.')
df['Belopp'] = pd.to_numeric(df['Belopp'])
df['Cost'] = -1*df['Belopp']
df['yearMth'] = df['dt'].map(lambda x: 100*x.year + x.month)
df.rename(columns={'HASH': 'CATEGORY'}, inplace=True)

df = df.sort_values(by=["yearMth","CATEGORY"])

# width
stat_width = 300
bar_width = 800
sctr_width = 700
datat_width = 400



# plot all data #
#---------
# pivot data
df_pivot = df.pivot_table(values='Cost', index=['CATEGORY'],aggfunc=np.sum, columns="yearMth").fillna(0)
df_pivot = df_pivot.reset_index(drop=False)

#---------
category = [c for c in sorted(set(df['CATEGORY']))]
colors = ['#1f77b4','#aec7e8','#ff7f0e','#ffbb78','#2ca02c','#98df8a','#d62728','#ff9896','#9467bd','#c5b0d5','#8c564b']
# since yearMth is index in the pivot, I'm taking the values from the original df <redo>
dates = [str(a) for a in sorted(set(df.yearMth))]

dict_pivot = {'time' : dates}

for i in range(len(category)):
    name = df_pivot.iloc[i:i+1,:1].get_value(i,'CATEGORY')
    values = df_pivot.iloc[i+0:i+1,1:].get_values()
    val = values[0,:].tolist()
    dict_pivot.update({name : val})

#---------
s_pivot = ColumnDataSource(data=dict_pivot)
original_source = ColumnDataSource(df)

p_bar = figure(x_range=dates, plot_height=400, plot_width=bar_width, title="by Year", toolbar_location=None, tools="")
p_bar.vbar_stack(category, x='time', width=0.4, legend=[value(x) for x in category], color = colors, source=s_pivot)
# format plot
p_bar.xaxis.major_label_orientation = -pi/4
p_bar.y_range.start = -1000
p_bar.x_range.range_padding = 0.5
p_bar.xgrid.grid_line_color = None
p_bar.axis.minor_tick_line_color = None
p_bar.outline_line_color = None
p_bar.legend.location = "bottom_right"
p_bar.legend.orientation = "vertical"
p_bar.legend.label_text_font_size = '6pt'

p_bar.background_fill_color = "white"
p_bar.background_fill_alpha = 0.25

p_bar.border_fill_color = "whitesmoke"
p_bar.min_border_left = 80
#p.add_layout(legend, 'right')

# widget
offset = Slider(title="offset", value=201508, start=201508, end=201712, step=1)

# plot subset data #
def update_data(attrname, old, new):
    # Get the current slider values
    b = offset.value
    df_tmp = df[df['yearMth']>=b]
    df_pivot2 = df_tmp.pivot_table(values='Cost', index=['CATEGORY'],aggfunc=np.sum, columns="yearMth").fillna(0)
    df_pivot2 = df_pivot2.reset_index(drop=False)
#    category = [c for c in sorted(set(df_tmp['CATEGORY']))]
#    colors = ['#1f77b4','#aec7e8','#ff7f0e','#ffbb78','#2ca02c','#98df8a','#d62728','#ff9896','#9467bd','#c5b0d5','#8c564b']
    dates = [str(a) for a in sorted(set(df_tmp.yearMth)) if (a >= b)]
    dict_pivot = {'time' : dates}

    for i in range(len(category)):
        name = df_pivot2.iloc[i:i+1,:1].get_value(i,'CATEGORY')
        values = df_pivot2.iloc[i+0:i+1,1:].get_values()
        val = values[0,:].tolist()
        dict_pivot.update({name : val})
#    print([len(v) for v in dict_pivot.values()])
#   Update the x-range
    p_bar.x_range.factors = dates
# Update data source
#    s_pivot.data=dict_pivot
    s_pivot.update(data=dict_pivot)
#    s_pivot = ColumnDataSource(data=dict_pivot)

#---------------------------------------------
x = df['dt']
y = df['Belopp']

s_xy = ColumnDataSource(data=dict(x=x, y=y))
p_sctr = figure(plot_width=sctr_width, plot_height=400, x_axis_type='datetime', tools="lasso_select, reset", title="Expenses")
p_sctr.circle('x', 'y', source=s_xy, alpha=0.5, size = 6)

p_sctr.background_fill_color = "white"
p_sctr.background_fill_alpha = 0.25

p_sctr.border_fill_color = "whitesmoke"
p_sctr.min_border_left = 80
p_sctr.xaxis.axis_label = "Date"
p_sctr.yaxis.axis_label = "Cost"
p_sctr.yaxis[0].formatter = PrintfTickFormatter(format="%5.0f kr")
p_sctr.xaxis.major_label_orientation = -pi/4
p_sctr.xgrid.visible = False
p_sctr.ygrid.visible = False


s_xy2 = ColumnDataSource(data=dict(x=[], y=[]))
##---
#datefmt = DateFormatter(format="ddMyy")

columns = [
            TableColumn(field='x',  title="Date", formatter = DateFormatter(format='m/d/yy')),
            TableColumn(field='y',  title="Belopp")
]
data_table = DataTable(source=s_xy2, columns=columns, width = datat_width, editable = True)
##---

s_xy.callback = CustomJS(args=dict(s2=s_xy2,target_obj=data_table), code="""
        var inds = cb_obj.selected['1d'].indices;
        var d1 = cb_obj.data;
        var d2 = s2.data;
        d2['x'] = []
        d2['y'] = []
        for (i = 0; i < inds.length; i++) {
            d2['x'].push(d1['x'][inds[i]])
            d2['y'].push(d1['y'][inds[i]])
        }
        s2.change.emit();
        target_obj.trigger('change');
    """)

#---------------------------------------------
# print statistics
stats = PreText(text='', width=stat_width)
df['year'] = df['dt'].dt.year
stats.text = str((pd.crosstab(df.CATEGORY, df.year, df.Cost, aggfunc = "sum")/12).round(0))
p.outline_line_width = 7
p.outline_line_alpha = 0.3
p.outline_line_color = "navy"
#---------------------------------------------

offset.on_change('value', update_data)

layout = layout(column(row(p_sctr, data_table),row(stats, column(offset, p_bar))))

document = curdoc()
document.add_root(layout)
document.title = "Yearly Costs"

if __name__ == "__main__":
    print("\npress ctrl-C to exit")
    session = push_session(document)
    session.show()
    session.loop_until_closed()
