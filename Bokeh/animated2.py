import pandas as pd
import numpy as np

from bokeh.io import curdoc, vform, output_file, show, output_server
#from bokeh.io import curdoc, output_file, show, output_server
from bokeh.layouts import row, column, widgetbox, layout
from bokeh.models import ColumnDataSource, DateFormatter
from bokeh.models.widgets import Slider, TextInput, Panel, Tabs, CheckboxGroup, Div
from bokeh.models.widgets import Toggle, DataTable, DateFormatter, TableColumn, Button
from bokeh.plotting import figure



output_server('test2')


files = ['planning_0904.csv']
names = ['URL Visits', 'Searches', 'Unique Users', 'In-Tab Users']

def create_panels(files, names):

	tab_list = []

	for i in range(len(files)):

		df = pd.read_csv('reports/{}'.format(files[i]), sep=';')
		col1 = df.columns[0]
		col2 = df.columns[1]

		if col1 == 'month':
			df['month'] = pd.to_datetime(df['month'])

			# create a new plot with a datetime axis type
			p = figure(width=800, height=350, x_axis_type="datetime")

			# create 30 day rolling average if plotting dates
			window_size = 30
			window = np.ones(window_size)/float(window_size)
			avg = np.convolve(df[col2], window, 'same')

			source = ColumnDataSource(df)
			#add renderers
			p.line(source.data[col1], avg, color='navy', legend='avg')
			p.circle(source.data[col1], source.data[col2], size=4, color='darkgrey', alpha=0.2, legend='{}'.format(names[i]))
			
			p.title.text = "One-Month Average of {}".format(names[i])

		else:

			p = figure(width=800, height=350)
			source = ColumnDataSource(df)
		    #add renderers
			p.line(source.data[col1], source.data[col2], line_width=2)
			p.circle(source.data[col1], source.data[col2], fill_color="white", size=8)
			p.title.text = "Count of {}".format(names[i])

		# NEW: customize by setting attributes
		p.legend.location = "top_left"
		p.grid.grid_line_alpha=0
		p.xaxis.axis_label = '{}'.format(col1)
		p.yaxis.axis_label = '{}'.format(names[i])
		p.ygrid.band_fill_color="olive"
		p.ygrid.band_fill_alpha = 0.1

		columns = [
	        TableColumn(field=c, title=c, formatter=DateFormatter(format='m/d/yy') if np.issubdtype(df[c].dtype, np.datetime64) else None) for c in df.columns
	        ]

		data_table = DataTable(source=source, columns=columns, width=400, height=280)

		div = Div(text="""<h2>Quick Info:</h2>
							<ul>
							<li>Number of observations: {}</li>
							<li>Max: {}</li>
							<li>Min: {}</li>
							</ul>
							""".format(df.shape[0], df[col2].max(), df[col2].min()),
					width=400, height=100)

		info = row(data_table, div) 

		tab_list.append(Panel(child= column(p, info), title=names[i]))

	return tab_list


# # Set up widgets
text = TextInput(title="Title", value='One-Month Average')
windowsize = Slider(title="Window Size", value=30, start=0, end=60, step=2)

# Set up callbacks
def update_title(attrname, old, new):
    p1.title.text = text.value

def update_window(attrname, old, new):

    # Get the current slider values
    window_size = windowsize.value

    # re calculate average and re-draw line
    window = np.ones(window_size)/float(window_size)
    avg = np.convolve(source.data[col2], window, 'same')
    p1.line(source.data[col1], avg, color='navy', legend='avg')



checkbox_group = CheckboxGroup(
        labels=["Option 1", "Option 2", "Option 3"], active=[0, 1])
button = Button(label="Foo", button_type="success")

text.on_change('value', update_title)
windowsize.on_change('value', update_window)


tabs = Tabs(tabs=create_panels(files, names), width=800)
inputs = widgetbox(text, windowsize, checkbox_group, button)#, amplitude, phase, freq)



curdoc().add_root(row(inputs, tabs))
curdoc().title = "Dashboard"



