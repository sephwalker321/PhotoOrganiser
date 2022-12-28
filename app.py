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
from dash import dcc, ctx, MATCH, ALL
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
	"path" : "/home/joseph/Desktop/Photos",
	"filename" : "",
	"code" : "",
	
	"title": "",
	"date": "",
	"location": "",
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
				id='var_location',
				children=Dat['location'],
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
		        	dbc.Col([
		        	dbc.Row([
		        		dbc.Col([
		            	html.Div(children="Pick photo path", className="menu-title"),
		            	], width=6),
		            	
		            	dbc.Col([
		            	html.Div(children="Photo", className="menu-title"),
		            	], width=6)
		            ]),
		            dbc.Row([
		            	dbc.Col([
		            		dbc.Input(
								id="path_textInput",
								type='text',
								value=metaTemplateDefault['path'],
								debounce=True,		
							),	
		            	], width=6-2),
						dbc.Col([
							dbc.Button(children="Select", id="path_buttonInput", n_clicks=0)
		            	], width=2),
		            	
		            	dbc.Col([
		            	dcc.Dropdown(
				            id="PhotoSelectDropdown",
				            options=[],
				            value="organic",
				            clearable=False,
				            searchable=False,
				            placeholder="Select a photo...",
				            style={"display":"fill", "width":"100%"}
		            	),
		            	], width=6)
		        	])
			])], className="menu",
	)
	
@app.callback(
	[
		Output('var_path', 'children'),
		Output('path_textInput', 'value')
	],
	[
		Input("path_buttonInput", "n_clicks"),
		Input("path_textInput", "value")
	],
	[
		State("var_path", "children")
	],
	prevent_initial_call = True
	)
def update_photoPath(n_clicks, text, FolderDir):
	if ctx.triggered_id == "path_buttonInput":
		path = easygui.diropenbox(default=FolderDir)
		if path is None:
			return [FolderDir, FolderDir]

	elif ctx.triggered_id == "path_textInput":
		path = text

	return [path, path]

@app.callback(
	[
		Output('PhotoSelectDropdown','options'),
		Output('PhotoSelectDropdown','value')
	],
	[
		Input('var_path', "children")
	],
	[
	
	],
	prevent_initial_call = False
	)
def update_photoDropdowns(Dir):
	globed = glob.glob(Dir+os.sep+"*")
	options = []
	for f in globed:
		if f.endswith(".png")+f.endswith(".jpg")+f.endswith(".jpeg") != 1:
			continue
			
		filename = f.split(Dir)[1][1:]
		options.append({'label': filename.split(".")[0], 'value': filename})
	options = sorted(options, key=lambda d: d['value']) 
	return options, None
	
################################################################################################################
# Photo 
################################################################################################################

	
def CreatePictureFig(Path):
	if Path is None:
		img = data.chelsea()
		xshape = img.shape[1]
		yshape = img.shape[0]
	else:
		img = Image.open(Path) 
		xshape = img.size[0]
		yshape = img.size[1]
		
	
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
        name="", 
        hoverinfo="x+y",
		hovertemplate= "x: %{x}<br>"+"y: %{y}",
    )
             
	return Fig

def Picture():
	config = {
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
			], className="metaform"),
           	dbc.Row([
		       	dbc.Col([
					html.Div(
						children=[
						    html.Div(children="Name", className="menu-title"),
						    dbc.Input(
						    	placeholder='Enter a Name...',
						    	type="text",
						    	id="picture-nameperson",
						    	debounce=True
						    ),
						]
					), 
				], width=12-3),
		       	dbc.Col([
					html.Div(
						children=[
						    html.Div(
						    	children="Add", 
						    	className="menu-title"
						    ),
						    dbc.Button(
						    	children="Select", 
						    	id="picture-addperson",
						    	n_clicks=0,
						    	className=""
						    )
						]
					),
				], width=3),
		    ], className="metaform"),   
		],
	)
	
	
@app.callback(
	[
		Output('picture','figure'),
		Output('null_clickdata', 'children'),
		Output('picture-nameperson', 'disabled'),
		Output('picture-addperson', 'disabled')
	],
	[
		Input('PhotoSelectDropdown', "value"),
		Input('picture', 'clickData')
	],
	[
		State('var_path', "children"),
		State('picture','figure')
	],
	prevent_initial_call = True
	)
def update_figure(filename, clickData, directory, fig):
	if ctx.triggered_id == "PhotoSelectDropdown":
		if filename is None or directory is None:
			return [CreatePictureFig(None), "(0,0)", True, True]
		else:
			Path =  directory + os.sep + filename
			return [CreatePictureFig(Path), "(0,0)", True, True]
			
	elif ctx.triggered_id == "picture":
	
			x = clickData["points"][0]["x"]
			y = clickData["points"][0]["y"]
			xy = "(%s,%s)" % (x,y)
			
			fig["data"][1]["x"] = [x]
			fig["data"][1]["y"] = [y]
			fig["data"][1]["marker"]["size"] = 20
			
			return [fig, xy, False, False]
		
@app.callback(
	[
		Output('picture-nameperson','value'),
		Output('var_people', 'children'), 
		Output('var_people_xy', 'children')
	],
	[
		Input('picture-addperson', "n_clicks"),
		Input( {'type': 'dynamic-deleteperson', 'index': ALL} , 'n_clicks'),
	],
	[
		State('picture-nameperson', "value"), 
		State('null_clickdata', 'children'), 
		State('var_people', 'children'), 
		State('var_people_xy', 'children')
	],
	prevent_initial_call = True
	)
def update_peopleList(
		nclicks,
		nclicks_del,
		
		Name,
		Coords,
		ps,
		xys,
	):
	if ctx.triggered_id == "picture-addperson":
		if Name is None:
			pass
		elif Name in ps:
			index = ps.index(Name)
			xys[index] = Coords
		else:
			ps.append(Name)
			xys.append(Coords)
	elif ctx.triggered_id["type"] == "dynamic-deleteperson":
		index = int(ctx.triggered_id["index"])
		ps.pop(index)
		xys.pop(index)
		
	return [None, ps, xys]
	
	


	

################################################################################################################
# Meta Data
################################################################################################################

def PeopleList(ps=metaTemplateDefault["people"], xys=metaTemplateDefault["people_xy"]):
	children = []
	N=0
	
	if len(ps) > 0:
		for pi, xysi in zip(ps, xys):
			if pi is None:
				continue
			row = dbc.Row([
				dbc.Col([
					html.H5(
						children="%s %s" % (pi, xysi),
						className="",
					)
				], width=12-3),
				dbc.Col([
					dbc.Button(
						children="Delete",
						id={
								'type': 'dynamic-deleteperson',
								'index': N
						},
						n_clicks=0,
						className="button"
					)
				], width=3),
			])	
			children.append(row)
	  
			N+=1
			
		return html.Div(
			children = children
		)
	else:
		row = dbc.Row([
				dbc.Col([
					html.H5(
						children="Start tagging people!",
						className="",
					)
				], width=12),
		])
		return html.Div(
			children = [row]
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
					dbc.Input(
						placeholder='Enter a title...',
						id="metadata_title",
						type='text',
						value='',	
						debounce=True					
					),	    
            	]),
            	#Datepicker
                dbc.Row([
		            html.Div(
		                children="Date",
		                className="menu-title",
                    ),
                ]),
                dbc.Row([
		            dcc.DatePickerSingle(
						id="metadata_date",
						date=None,
						placeholder="Pick a date...",
						
						month_format='MMMM Y',
						display_format='Do MMM Y',
						
						clearable=True, 
						initial_visible_month=date(2017, 8, 5),
		                min_date_allowed=date(1800, 1, 1),
		                max_date_allowed=date.today(),
		                
		            ),
                ]),
                #Title
            	dbc.Row([
		            html.Div(
		                children="Location",
		                className="menu-title",
                    ),
                ]),
                dbc.Row([
					dbc.Input(
						placeholder='Enter a location...',
						id="metadata_location",
						type='text',
						value='',		
						debounce=True				
					),	    
            	]),
                #Person select unselect
                dbc.Row([
		            html.Div(
		                children="People",
		                className="menu-title",
		            ),
                ]),
                dbc.Row(
               		children=[PeopleList()],
               		id="metadata_people"
                ),
                #Caption
            	dbc.Row([
		            html.Div(
		                children="Caption",
		                className="menu-title",
                    ),
                ]),
                dbc.Row([
                	dbc.Textarea(
						placeholder='Enter a caption...',
						value='',	
						id="metadata_caption",		
						n_blur=0,		
					),
				]),
				
				#Submit
            	dbc.Row([
		            html.Div(
		                children="\n",
		                className="menu-title",
		            ),    
                ]),
                dbc.Row([
					dbc.Button(
						children='Submit', 
						id="metadata_submitbutton",
						n_clicks=0, className=""
					),
				]),
            ],
        ),

		],
		className="metaform",
	)
	
@app.callback(
	[
		Output('var_title','children')
	],
	[
		Input('metadata_title', "value")
	],
	[
	
	],
	prevent_initial_call = True
	)
def update_metaTitle(text):
	return [text]
	
@app.callback(
	[
		Output('var_date','children')
	],
	[
		Input('metadata_date', "date")
	],
	[
	
	],
	prevent_initial_call = True
	)
def update_metaData(date):
	return [date]
	
@app.callback(
	[
		Output('var_location','children')
	],
	[
		Input('metadata_location', "value")
	],
	[
	
	],
	prevent_initial_call = True
	)
def update_metaLoc(loc):
	return [loc]
	
@app.callback(
	[
		Output('metadata_people','children')
	],
	[
		Input('var_people', 'children'), 
	],
	[
		State('var_people_xy', 'children')
	],
	prevent_initial_call = True
	)
def update_metaPeople(ps, xys):
	return [PeopleList(ps=ps, xys=xys)]
	
@app.callback(
	[
		Output('var_caption','children')
	],
	[
		Input('metadata_caption', "value")
	],
	[
	
	],
	prevent_initial_call = True
	)
def _metaCaption(text):
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

        Main()
        
    ]
)
			
if __name__ == "__main__":
	print("Run app dashboard")
	app.config.suppress_callback_exceptions = True	
	
	#Run as debug mode
	#app.run(debug=True, port=8050, threaded= True)
	#Run normally
	app.run(debug=True, port=8050, threaded= True, host= '0.0.0.0')
