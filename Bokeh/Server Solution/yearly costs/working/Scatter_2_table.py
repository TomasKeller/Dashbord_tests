import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import row, column, layout
from bokeh.models import ColumnDataSource, TableColumn, DataTable, CustomJS
from bokeh.models.widgets import PreText, Select, Slider
from bokeh.plotting import figure, show, curdoc
from bokeh.models.callbacks import CustomJS
from bokeh.charts import Area
from bokeh.client import push_session
from math import pi
# import data
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

#x = [random() for x in range(500)]
#y = [random() for y in range(500)]
x = df['dt']
y = df['Belopp']

s1 = ColumnDataSource(data=dict(x=x, y=y))
p1 = figure(plot_width=400, plot_height=400, x_axis_type='datetime', tools="lasso_select", title="Expenses")
p1.circle('x', 'y', source=s1, alpha=0.6)

p1.xaxis.major_label_orientation = -pi/4


s2 = ColumnDataSource(data=dict(x=[], y=[]))
##---
columns = [
            TableColumn(field='x',  title="Saldo"),
            TableColumn(field='y',  title="Belopp")
]
data_table = DataTable(source=s2, columns=columns, editable = True)
##---

s1.callback = CustomJS(args=dict(s2=s2,target_obj=data_table), code="""
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

layout = column(row(p1, data_table))

document = curdoc()
document.add_root(layout)
document.title = "Selection Histogram"

if __name__ == "__main__":
    print("\npress ctrl-C to exit")
    session = push_session(document)
    session.show()
    session.loop_until_closed()
