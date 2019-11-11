# -*- coding: utf-8 -*-
"""
Created on 2019-01-14 14:04:33

@author: Johannes Johansson

"""

from bokeh.plotting import figure
from bokeh.io import output_notebook, push_notebook, show

output_notebook()

plot = figure()
plot.circle([1,2,3], [4,6,5])

handle = show(plot, notebook_handle=True)

# Update the plot title in the earlier cell
plot.title.text = "New Title"
push_notebook(handle=handle)