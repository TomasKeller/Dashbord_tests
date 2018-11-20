
from bokeh.plotting import Figure, output_file, show
from bokeh.models import CustomJS
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn, Toggle
from bokeh.layouts import row, column, layout

from bokeh.io import curdoc
from bokeh.layouts import row, column, layout
from bokeh.models import ColumnDataSource, TableColumn, DataTable, CustomJS
from bokeh.models.widgets import PreText, Select, Slider
from bokeh.plotting import figure, show, curdoc
from bokeh.models.callbacks import CustomJS
from bokeh.charts import Area
from bokeh.client import push_session

from random import randint
import pandas as pd

output_file("data_table_subset_example.html")

data = dict(
        x=[randint(0, 100) for i in range(10)],
        y=[randint(0, 100) for i in range(10)],
        z=['some other data'] * 10
    )
df = pd.DataFrame(data)
#filtering dataframes with pandas keeps the index numbers consistent
filtered_df = df[df.x < 80]

#Creating CDSs from these dataframes gives you a column with indexes
s1 = ColumnDataSource(df)
s2 = ColumnDataSource(filtered_df)

fig1 = Figure(plot_width=200, plot_height=200, tools='lasso_select')
fig1.circle(x='x', y='y', source=s1)

fig2 = Figure(plot_width=200, plot_height=200, tools='lasso_select')
fig2.circle(x='x', y='y', source=s2)

columns = [
        TableColumn(field="x", title="X"),
        TableColumn(field="z", title="Text"),
    ]
data_table = DataTable(source=s2, columns=columns, width=400, height=280)

button = Toggle(label="Select")
button.callback = CustomJS(args=dict(s1=s1, s2=s2), code="""
        var inds_in_source2 = s2.get('selected')['1d'].indices;
        var d = s2.get('data');
        var inds = []

        if (inds_in_source2.length == 0) { return; }

        for (i = 0; i < inds_in_source2.length; i++) {
            inds.push(d['index'][i])
        }

        s1.get('selected')['1d'].indices = inds
        s1.trigger('change');
    """)

s1.callback = CustomJS(args=dict(s2=s2), code="""
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

    """)

layout = row(fig1, fig2, data_table, button)

document = curdoc()
document.add_root(layout)
document.title = "Selection Histogram"

if __name__ == "__main__":
    print("\npress ctrl-C to exit")
    session = push_session(document)
    session.show()
    session.loop_until_closed()
