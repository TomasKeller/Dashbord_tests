from bokeh.charts import Bar
from bokeh.models.widgets import CheckboxGroup, CheckboxButtonGroup
import numpy as np
from bokeh.layouts import row, widgetbox
from bokeh.io import curdoc


#output_notebook()
#output_file('dash.html')

import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import row, column, layout
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import PreText, Select, Slider
from bokeh.plotting import figure, show, output_file
from bokeh.models.callbacks import CustomJS
from bokeh.charts import Area
from bokeh.models.callbacks import CustomJS


# import data
fname = 'data/Export.csv'

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
# define source data
#source = ColumnDataSource(df)

#selection = ['HOUSE', 'CAR']
#bar = Bar(df[ (df['Belopp']<0) & (df['HASH'].isin(selection))], label='yearMth', values='Cost', agg='sum', stack='HASH', title="Expected Sales by year", tools = 'hover')

df = df[df['Belopp']<0]
source = ColumnDataSource(df)

#bar = Bar(source.data, label='yearMth', values='Cost', agg='sum', stack='HASH', title="Expected Sales by year", tools = 'hover')
p1 = figure(plot_width=500, plot_height=300, logo=None, toolbar_location='right', x_axis_type='datetime')
p1.line(source=source, x='yearMth', y='Cost')  # CHANGED
#cb_group = CheckboxButtonGroup(labels=['Close', 'Adj Close'],active=[0,1])

# define widgets
SEL = [x for x in sorted(set(df['HASH']))]
#cb_group = CheckboxGroup(labels = SEL, active = np.ones(len(SEL),dtype=np.int).tolist())

cb_group = CheckboxButtonGroup(labels = SEL, active = [x for x in range(len(SEL))])
y_axis = Select(title="Y:", value='HOUSE', options=['HOUSE', 'CAR', 'TOMAS'])



# select all rows selected in HASH column
def update_plot(attrname, old, new):
#    print('pl1')
    data = source.to_df()
#    print('pl1.1')
    o_data = source.to_df()
#    print('pl1.2')
    switch = cb_group.active
    print(switch)
    items = [SEL[i] for i in switch]
    for i in range(len(data['HASH'])):
        #print('pl2')
        data.drop(data.index[i])
        if (o_data['HASH'][i] in str(items)):
        #    print('pl3')
            data = pd.concat([data, o_data.iloc[[i]]])
#            data = data + o_data[i]
        #    print('pl3.1')
    print(data.shape)
    cds = ColumnDataSource(data)
    update_graph(data)

def update_graph(cds):
    print ('gr1')
    bar = Bar(cds.data, label='yearMth', values='Cost', agg='sum', stack='HASH', title="Expected Sales by year", tools = 'hover')
    print ('gr2')



combined_callback_code = """
var data = source.get('data');
var original_data = original_source.get('data');
var grp = grp_select_obj.get('value');
console.log(grp);
for (var key in original_data) {
    data[key] = [];
    for (var i = 0; i < original_data['grp'].length; ++i) {
        if (( original_data['grp'][i] === grp)) {
            data[key].push(original_data[key][i]);
        }
    }
}
source.trigger('change');
"""
generic_callback = CustomJS(
    args=dict(source=source,
              original_source=source,
              grp_select_obj=y_axis,
#              year_select_obj=year_select,
              #target_obj=data_table
              ),
    code=combined_callback_code
)

cb_group.on_change('active', update_plot)
y_axis.js_on_change('value', generic_callback)

bar2 = Bar(source.data, label='yearMth', values='Cost', agg='sum', stack='HASH', title="Expected Sales by year", tools = 'hover')

#layout=row(cb_group,y_axis,bar)
layout=row(y_axis,p1)

# initialize
#update()

curdoc().add_root(layout)
curdoc().title = "Foo"
