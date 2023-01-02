"""============================================================================
Python Dashboard produced to monitor timeseries data with high periodicity and search for anomlous regions in the data. 

Dashboard largely developed based on tutorial located at https://realpython.com/python-dash/ and inspired by https://dash-gallery.plotly.host/dash-manufacture-spc-dashboard/.

Contents: 

Author: Joseph Walker j.j.walker@durham.ac.uk
============================================================================"""

#TODO Date format is wrong
#Delete and updating the People is wrong on read in...


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

import glob
from datetime import date, datetime


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

DefaultPath = "photos"+os.sep+"input"+os.sep
DefaultPath = "/home/joseph/Desktop/Photos"

ExcelName = "PhotoDF.xlsx"

DefaultVar = {
	"filename" : "",
	"code" : "",
	
	"title": "",
	"date": "",
	"location": "",
	"caption": "",
	"people": "",
	"people_xy": "",
	
	"lastedit": "",	
}

converters={
	"path" : str,
	"filename" : str,
	"code" : str,
	"title": str,
	"date": str,
	"location": str,
	"caption": str,
	"people": str,
	"people_xy": str,
	"lastedit": str,
}

#######################
# Read In Markdown
#######################
            
def GetExcel(path=DefaultPath):
	ExcelPath = path + os.sep + ExcelName
	isExist = os.path.exists(ExcelPath)
	if isExist:
		Excel = pd.read_excel(
			ExcelPath, 
			index_col=0,
			converters=converters,
			keep_default_na=False)
						
	else:
		Excel = pd.DataFrame(data=[{
			"path" : path,
			"filename" : DefaultVar["filename"],
			"code" : DefaultVar["code"],
			"title": DefaultVar["title"],
			"date": DefaultVar["date"],
			"location": DefaultVar["location"],
			"caption": DefaultVar["caption"],
			"people": DefaultVar["people"],
			"people_xy": DefaultVar["people_xy"],
			"lastedit": DefaultVar["lastedit"],	
		}], index=[0])
		
	print("Input from Excel")
	print(Excel["path"].values[0], type(Excel["path"].values[0]))
	print(Excel["filename"].values[0], type(Excel["filename"].values[0]))
	print(Excel["code"].values[0], type(Excel["code"].values[0]))
	print(Excel["title"].values[0], type(Excel["title"].values[0]))
	print(Excel["date"].values[0], type(Excel["date"].values[0]))
	print(Excel["location"].values[0], type(Excel["location"].values[0]))
	print(Excel["caption"].values[0], type(Excel["caption"].values[0]))
	print(Excel["people"].values[0], type(Excel["people"].values[0]))
	print(Excel["people_xy"].values[0], type(Excel["people_xy"].values[0]))
	
	Excel = json.dumps(Excel.to_json())
	return Excel
           
           
def ConvertStoredJSON(JSON):
	Excel = pd.read_json(
		json.loads(JSON),
		orient='columns',
		dtype=converters,
	)

	Excel.replace({"NaT": ""}, inplace=True)
	return Excel
	
def GetFilename(options, index):
	if index is None:
		return None
	else:
		return options[index]["label"]
		


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
        
def AlbumVarContainers(path=DefaultPath, Excel=GetExcel()):
	return html.Div( 
		style={'display': 'none'},
		children = [
			html.H1(
				id='var_path',
				children=path,
			),
			html.H1(
				id='var_photoindex',
				children="",
			),
			html.H1(
				id='ExcelSheet',
				children=Excel,
			),
		]
	)
     
def VariableContainers(
		Dat = DefaultVar
	):		
	#print(Dat)
	return html.Div( 
		style={'display': 'none'},
		children = [
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
				id='null_submitPhoto',
				children="",
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
								value=DefaultPath,
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
				            value=None,
				            clearable=False,
				            searchable=False,
				            placeholder="Select a photo...",
				            style={"display":"fill", "width":"100%"}
		            	),
		            	], width=4),
		            	dbc.Col([
		            		dbc.Button(children="Prev", id="PhotoSelectPrev", n_clicks=0)
		            	], width=1),
		            	dbc.Col([
		            		dbc.Button(children="Next", id="PhotoSelectNext", n_clicks=0)
		            	], width=1),
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
		Output('PhotoSelectDropdown','options')
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
	globed.sort()
	options = []
	N=0
	for f in globed:
		if f.endswith(".png")+f.endswith(".jpg")+f.endswith(".jpeg") != 1:
			continue
			
		filename = f.split(Dir)[1][1:]
		options.append({'label': filename, 'value': N})
		N+=1
	options = sorted(options, key=lambda d: d['value']) 
	return [options]
	
@app.callback(
	[
		Output('PhotoSelectDropdown','value'),
		Output('PhotoSelectPrev','disabled'),
		Output('PhotoSelectNext','disabled')
	],
	[
		Input('PhotoSelectDropdown','value'),
		Input('PhotoSelectPrev', "n_clicks"),
		Input('PhotoSelectNext', "n_clicks"),
	],
	[
		State('PhotoSelectDropdown','value'),
		State('PhotoSelectDropdown','options'),	
	],
	prevent_initial_call = False
	)
def update_photoDropdowns(photo, prev_click, next_click, index, options):
	NOptions = len(options)
	if index is None:
		return [index, True, True]
		
	PrevDisable = False
	NextDisable = False
	

	if ctx.triggered_id == "PhotoSelectPrev":
		index -=  1
	if ctx.triggered_id == "PhotoSelectNext":
		index += 1
		
	if index == NOptions-1:
		NextDisable = True
	if index == 0:
		PrevDisable = True
		
	return [index, PrevDisable, NextDisable]
	
	
	


	
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
		Output('picture-addperson', 'disabled'),
		Output('var_filename', 'children'),
	],
	[
		Input('PhotoSelectDropdown', "value"),
		Input('picture', 'clickData')
	],
	[
		State('PhotoSelectDropdown', "options"),
		State('var_path', "children"),
		State('var_filename', 'children'),
		State('picture','figure')
	],
	prevent_initial_call = True
	)
def update_figure(dropdownindex, clickData, dropdownoptions, directory, filename, fig):
	dropdownfilename = GetFilename(dropdownoptions, dropdownindex) 
	if ctx.triggered_id == "PhotoSelectDropdown":
		if dropdownfilename is None or directory is None:
			
			return [CreatePictureFig(None), "(0-0)", True, True, filename]
		else:
			Path =  directory + os.sep + dropdownfilename
			return [CreatePictureFig(Path), "(0-0)", True, True, dropdownfilename]
			
	elif ctx.triggered_id == "picture":
	
			x = clickData["points"][0]["x"]
			y = clickData["points"][0]["y"]
			xy = "(%s-%s)" % (x,y)
			
			fig["data"][1]["x"] = [x]
			fig["data"][1]["y"] = [y]
			fig["data"][1]["marker"]["size"] = 20
			
			return [fig, xy, False, False, dropdownfilename]
		
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
	pslist= ps.split(",")
	xyslist = xys.split(",")
	if "" in pslist:
		pslist.remove("")
	if "" in xyslist:
		xyslist.remove("")
	
	if ctx.triggered_id == "picture-addperson":
		if Name is None:
			pass
		elif Name in ps:
			index = pslist.index(Name)
			xyslist[index] = Coords
			ps = ""
			xys = ""
			for i in range(len(pslist)):
				ps += pslist[i] + ","
				xys += xyslist[i] + ","
		else:
			ps += Name + ","
			xys += Coords + ","
			
	elif ctx.triggered_id  is None:
		return  [None, ps, xys]
		
	elif ctx.triggered_id["type"] == "dynamic-deleteperson":
		index = int(ctx.triggered_id["index"])
		if nclicks_del[index] > 0:	
			pslist.pop(index)
			xyslist.pop(index)
			
			ps = ""
			xys = ""
			for i in range(len(pslist)):
				ps += pslist[i] + ","
				xys += xyslist[i] + ","
	return [None, ps, xys]
	
################################################################################################################
# Meta Data
################################################################################################################

def PeopleList(ps="", xys=""):
	children = []
	N=0	
	
	pslist= ps.split(",")
	xyslist = xys.split(",")
	if "" in pslist:
		pslist.remove("")
	if "" in xyslist:
		xyslist.remove("")
	
	if len(pslist) > 0:
		for pi, xysi in zip(pslist, xyslist):
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
						initial_visible_month=date.today(),
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
						n_clicks=0
					),
				]),
            ],
        ),

		],
		className="metaform",
	)
	
@app.callback(
	[
		Output('var_title','children'),
		Output('metadata_title', "value"),
	],
	[
		Input('metadata_title', "value"),
		Input('var_title','children'),
	],
	[
	
	],
	prevent_initial_call = True
	)
def update_metaTitle(text, Exceltext):
	if ctx.triggered_id == "metadata_title":
		return [text, text]
	elif ctx.triggered_id == "var_title":
		return [Exceltext, Exceltext]
	
@app.callback(
	[
		Output('var_date','children'),
		Output('metadata_date', "date"),
	],
	[
		Input('metadata_date', "date"),
		Input('var_date','children'),
	],
	[
	
	],
	prevent_initial_call = True
	)
def update_metaData(date, Exceldate):
	if ctx.triggered_id == "metadata_date":
		return [date, date]
		
	elif ctx.triggered_id == "var_date":
		if Exceldate == "":
			Exceldate = None 
		return [Exceldate, Exceldate]
	
@app.callback(
	[
		Output('var_location','children'),
		Output('metadata_location', "value"),
	],
	[
		Input('metadata_location', "value"),
		Input('var_location','children'),
	],
	[
	
	],
	prevent_initial_call = True
	)
def update_metaLoc(loc, locExcel):
	if ctx.triggered_id == "metadata_location":
		return [loc, loc]
	elif ctx.triggered_id == "var_location":
		return [locExcel, locExcel]
	
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
		Output('var_caption','children'),
		Output('metadata_caption', "value"),
	],
	[
		Input('metadata_caption', "value"),
		Input('var_caption','children'),
	],
	[
	
	],
	prevent_initial_call = True
	)
def update_metaCaption(text, textExcel):
	if ctx.triggered_id == "metadata_caption":
		return [text, text]
	elif ctx.triggered_id == "var_caption":
		return [textExcel, textExcel]
	
@app.callback(
	[
		Output('null_submitPhoto','children'),
		Output('ExcelSheet','children')
	],
	[
		Input('metadata_submitbutton', "n_clicks")
	],
	[
		State("ExcelSheet","children"),
		State('var_path', 'children'),
		State('var_filename', 'children'),
		State('var_code', 'children'),
		State('var_title', 'children'),
		State('var_date', 'children'),
		State('var_location', 'children'),
		State('var_caption', 'children'),
		State('var_people', 'children'),
		State('var_people_xy', 'children'),
	],
	prevent_initial_call = True
	)
def submit_phototoexcel(
		n_clicks,
		
		Excel, 
		
		path,
		filename,
		code,
		title,
		meta_date,
		location,
		caption,
		people,
		people_xy,	
	):
	if filename == "":
		return ["", Excel]
				
	if filename is None:
		filename = DefaultVar["filename"]
	if code is None:
		code = DefaultVar["code"]
	if title is None:
		title = DefaultVar["title"]
	if meta_date is None:
		meta_date = DefaultVar["date"]
	if caption is None:
		caption = DefaultVar["caption"]
	if people is None:
		people = DefaultVar["people"]
	if people_xy is None:
		people_xy = DefaultVar["people_xy"]
		
	print("Output to Excel")
	print(path, type(path))
	print(filename, type(filename))
	print(code, type(code))
	print(title, type(title))
	print(meta_date, type(meta_date))
	print(location, type(location))
	print(caption, type(caption))
	print(people, type(people))
	print(people_xy, type(people_xy))
		
	df_i = pd.DataFrame(data=[{
		"path" : path,
		"filename" : filename,
		"code" : code,
		"title": title,
		"date": meta_date,
		"location": location,
		"caption": caption,
		"people": people,
		"people_xy": people_xy,
		"lastedit": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),	
	}], index=[0])
	
	Excel = ConvertStoredJSON(Excel)
	if filename in Excel["filename"].values: #Updating
		Excel[Excel["filename"] == filename] = df_i.values
		
	else: #Adding new one
		Excel = pd.concat([Excel, df_i], ignore_index=True)

		
	ExcelPath = path + os.sep + ExcelName
	
	Excel = Excel[Excel.filename != ""]
	with pd.ExcelWriter(ExcelPath) as writer:
		Excel.to_excel(writer)  
	return ["", json.dumps(Excel.to_json())]
	

@app.callback(
	[
		Output('variables','children')
	],
	[
		Input('PhotoSelectDropdown', "value")
	],
	[
		Input('PhotoSelectDropdown', "options"),
		State("ExcelSheet","children"),
	],
	prevent_initial_call = True
	)
def update_metadata(dropdownindex, dropdownoptions, Excel):
	filenamedropdown = GetFilename(dropdownoptions, dropdownindex) 
	Excel = ConvertStoredJSON(Excel)
	if filenamedropdown in Excel["filename"].values: #Updating
		Excel = Excel[Excel["filename"] == filenamedropdown]
		Dat = {
			"filename" : Excel["filename"].values[0],
			"code" :  Excel["code"].values[0],
			
			"title":  Excel["title"].values[0],
			"date":  Excel["date"].values[0],
			"location":  Excel["location"].values[0],
			"caption":  Excel["caption"].values[0],
			"people":  Excel["people"].values[0],
			"people_xy":  Excel["people_xy"].values[0],
			
			"lastedit":  Excel["lastedit"].values[0],	
		}
		return [VariableContainers(Dat=Dat)]
	else: #Adding new one
		return [VariableContainers()]


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
        AlbumVarContainers(),
        html.Div(
		    id = "variables",
		    children=VariableContainers(),
        ),
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
