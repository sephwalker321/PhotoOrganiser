"""============================================================================
Python Dashboard produced to monitor timeseries data with high periodicity and search for anomlous regions in the data. 

Dashboard largely developed based on tutorial located at https://realpython.com/python-dash/ and inspired by https://dash-gallery.plotly.host/dash-manufacture-spc-dashboard/.

Contents: 

Author: Joseph Walker j.j.walker@durham.ac.uk
============================================================================"""

################################################################################################################
# Imports and Set Up
################################################################################################################

#Required Dash Libraries
#Initalization
import dash 
#Interactive components
from dash import dcc
#HTML tags
from dash import html
#Bootstrap components cols and rows
import dash_bootstrap_components as dbc
#Callback functions
from dash.dependencies import Output, Input, State
#from dash_extensions.enrich import Dash, Input, State, Output, html, dcc

#Pandas for data import and management
import pandas as pd
import numpy as np


#Image plotting
#import plotly.express as px
import plotly.graph_objects as go
from skimage import data
from PIL import Image

#For moving data around as child
import json

#Command lines
import sys, getopt
import os
import time
import glob
from datetime import date

import easygui

#######################
# Local Parameters
#######################

#Timing for periodic refreshes
dt_small = 1 
dt_mid = 5 
dt_big = 5

#######################
# Hyperparameter Loading
#######################

metaTemplateDefault = {
	#"path" : "photos"+os.sep+"input"+os.sep,
	"path" : "/home/joseph/Desktop/Photos"+os.sep,
	"filename" : "",
	"code" : "",
	
	"title": "",
	"date": "",
	"caption": "",
	"people": [],
	"people_xy": [],
	
	"lastedit": "",	
}

#######################
# Read In Markdown
#######################

text_markdown = "\n \t"
with open('assets'+os.sep+'LoadInfo.md') as this_file:
    for a in this_file.read():
        if "\n" in a:
            text_markdown += "\n \t"
        else:
            text_markdown += a
            
           

################################################################################################################
# Bootstrap Style sheet and run.
################################################################################################################

external_stylesheets = [
    {
        "href": "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css",
        "rel": "stylesheet",
    },
]
external_scripts=[]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,external_scripts=external_scripts)
app.title = "Title"

################################################################################################################
# Banner & Defualts
################################################################################################################

def Banner():
	return html.Div(
            children=[
                html.P(children="👪🌳", className="header-emoji"),
                html.H1(
                    children="Photo Organiser", className="header-title"
                ),
                html.P(
                    children="Family tree photo catalogue tool",
                    className="header-description",
                ),
            ],
            className="header",
        )
        
def VariableContainers(Dat=metaTemplateDefault):
	return html.Div( 
		style={'display': 'none'},
		children = [
			html.H1(
				id='var_path',
				children=Dat['path'],
			),
			html.H1(
				id='var_filename',
				children=Dat['filename'],
			),
			html.H1(
				id='var_code',
				children=Dat['code'],
			),
			html.H1(
				id='var_title',
				children=Dat['title'],
			),
			html.H1(
				id='var_date',
				children=Dat['date'],
			),
			html.H1(
				id='var_caption',
				children=Dat['caption'],
			),
			html.H1(
				id='var_people',
				children=Dat['people'],
			),
			html.H1(
				id='var_people_xy',
				children=Dat['people_xy'],
			),
			html.H1(
				id='var_lastedit',
				children=Dat['lastedit'],
			),
			html.H1(
				id='null_clickdata',
				children="",
			),
		]
	)
		
################################################################################################################
# Menu Selection
################################################################################################################

def PathSelect():
	return html.Div(
		children=[
		    html.Div(
		        children=[
		            html.Div(children="Pick photo path", className="menu-title"),
		            dbc.Button(children="Select", id="PathButton", n_clicks=0, className="")
		        ]
		    ),
		    html.Div(
		        children=[
		            html.Div(children="Photo", className="menu-title"),
		            dcc.Dropdown(
		                id="PhotoSelectDropdown",
		                options=[],
		                value="organic",
		                clearable=False,
		                searchable=False,
		                className="dropdown",
		                placeholder=None,
		            ),
		        ],
		    ),
		],
		className="menu",
	)
	
@app.callback(
	[Output('var_path', 'children')],
	[Input("PathButton", "n_clicks")],
	[State("var_path", "children")],
	)
def update_path(n_clicks, FolderDir):
	if n_clicks == 0:
		return [FolderDir]
	path = easygui.diropenbox(default=FolderDir)
	if path is None:
		return [FolderDir]
	else:	
		return [path+os.sep]

@app.callback(
	[Output('PhotoSelectDropdown','options'),Output('PhotoSelectDropdown','value')],
	[Input('var_path', "children")],
	)
def update_dropdowns(Dir):
	globed = glob.glob(Dir+"*")
	options = []
	for f in globed:
		filename = f.split(Dir)[1]
		options.append({'label': filename.split(".")[0], 'value': filename})
	options = sorted(options, key=lambda d: d['value']) 
	return options, None
	
################################################################################################################
# Photo 
################################################################################################################

	
def CreatePictureFig(Path):
	if Path is None:
		img = data.chelsea()
	else:
		img = Image.open(Path) 
	xshape = img.shape[1]
	yshape = img.shape[0]
	Fig = go.Figure(
	layout = {
		"autosize":True,
		"margin" : {"l":10,"r":10,"t":10,"b":10},
		"xaxis_range": [0, xshape],
		"yaxis_range": [yshape, 0],
		}
	)
	Fig.add_trace(
		go.Image(
			name="",
			z=np.array(img),
			colormodel='rgb',
			hoverinfo="x+y+z",
			hovertemplate= "x: %{x}<br>"+"y: %{y}<br>"+"z: %{z}",
		)
	)
	
	Fig.add_scatter(
		x=[0], y=[0],
		mode="markers",
        marker=dict(size=0, color="LightSeaGreen"),
        name="person", 
    )
             
	return Fig

def Picture():
	config = {
		#"modeBarButtonsToAdd": [
		#    "drawrect",
		#    "eraseshape",
		#],
		"displayModeBar": False,
		"doubleClick":"reset"
	}
	return html.Div(children=[
           	dbc.Row([
		       	dbc.Col([
					dcc.Graph(
						figure = CreatePictureFig(None),
						id="picture", config=config,
					),
				]),
			]),
           	dbc.Row([
		       	dbc.Col([
					html.Div(
						children=[
						    html.Div(children="Name", className="menu-title"),
						    dbc.Input(children="Select", id="picture-nameperson"),
						]
					), 
				], width=12-3),
		       	dbc.Col([
					html.Div(
						children=[
						    html.Div(children="Add", className="menu-title"),
						    dbc.Button(children="Select", id="picture-addperson", n_clicks=0, className="")
						]
					),
				], width=3),
		    ]),   
		],
		#className = "menu",
	)
	
@app.callback(
	[Output('picture-nameperson', 'disabled'), Output('picture-addperson', 'disabled')],
	[Input('picture-addperson','n_clicks')])
def update(nclicks):
	return [True, True]
	
	
@app.callback(
	[Output('picture','figure')],
	[Input('PhotoSelectDropdown', "value"), Input('var_path', "children")],
	)
def update_dropdowns(filename, directory):
	if filename is None or directory is None:
		return [CreatePictureFig(None)]
	else:
		Path =  directory + filename
		return [CreatePictureFig(Path)]
		
@app.callback(
	[Output('null_clickdata', 'children'), Output("picture","figure")],
	[Input('picture', 'clickData')],
	[State('picture','figure')],
	prevent_initial_call = True
	)
def update_click(clickData, fig):
	x = clickData["points"][0]["x"]
	y = clickData["points"][0]["y"]
	xy = "(%s,%s)" % (x,y)
	
	fig["data"][1]["x"] = [x]
	fig["data"][1]["y"] = [y]
	fig["data"][1]["marker"]["size"] = 20
	

	return [xy, fig]
	
	

################################################################################################################
# Meta Data
################################################################################################################

def PeopleList(ps=metaTemplateDefault["people"], xys=metaTemplateDefault["people_xy"]):
	people = []
	for pi, xysi in zip(ps, xys):
		print(pi, xysi)
		#TODO
	return html.Div(
		children = people,
		id="metadata_people"
	)

def Data():
	return html.Div(
		children=[
		    html.Div(
            children=[
            	#Title
            	dbc.Row([
		            html.Div(
		                children="Title",
		                className="menu-title",
                    ),
                ]),
                dbc.Row([
					dcc.Input(
						placeholder='Enter a title...',
						id="metadata_title",
						type='text',
						value='',					
					),	    
            	#Datepicker
            	]),
                dbc.Row([
		            html.Div(
		                children="Date",
		                className="menu-title",
                    ),
                ]),
                dbc.Row([
		            dcc.DatePickerSingle(
						id="metadata_date",
						date=date.today(),
		                min_date_allowed=date.fromisoformat('1800-01-01'),
		                max_date_allowed=date.today(),
		            ),
                ]),
                #Person select unselect
                dbc.Row([
		            html.Div(
		                children="People",
		                className="menu-title",
		            ),
                ]),
                dbc.Row([
               		PeopleList(),
                ]),
                #Caption
            	dbc.Row([
		            html.Div(
		                children="Caption",
		                className="menu-title",
                    ),
                ]),
                dbc.Row([
					dcc.Textarea(
						placeholder='Enter a caption',
						value='',	
						id="metadata_caption",				
					),
				]),
				
				#Submit
            	dbc.Row([
		            html.Div(
		                children="Submit",
		                className="menu-title",
		            ),    
                ]),
                dbc.Row([
					html.Button(
						children='Submit', 
						id="metadata_submitbutton",
					),
				]),
            ],
        ),

		],
		className="metaform",
	)
	
@app.callback(
	[Output('var_title','children')],
	[Input('metadata_title', "value")],
	prevent_initial_call = True
	)
def update(text):
	return [text]
	
@app.callback(
	[Output('var_date','children')],
	[Input('metadata_date', "date")],
	prevent_initial_call = True
	)
def update(date):
	return [date]
	
@app.callback(
	[Output('var_caption','children')],
	[Input('metadata_caption', "value")],
	prevent_initial_call = True
	)
def update(text):
	return [text]

################################################################################################################
# Main page
################################################################################################################
	
def Main():
	return html.Div(
		children=[
			dbc.Row([
			dbc.Col(
				Data(),
			),
			dbc.Col(
				Picture(),
			),
			]),
		],
		className="wrapper"
	)

################################################################################################################
# Layout
################################################################################################################


app.layout = html.Div(
    children=[
        Banner(),
        VariableContainers(),
        PathSelect(),
        dbc.Row(
        	html.Div(),
        ),
        
        dbc.Row(
        	Main()
        )
    ]
)
			
if __name__ == "__main__":
	print("Run app dashboard")
	app.config.suppress_callback_exceptions = True	
	
	#Run as debug mode
	#app.run(debug=True, port=8050, threaded= True)
	#Run normally
	app.run(debug=True, port=8050, threaded= True, host= '0.0.0.0')
