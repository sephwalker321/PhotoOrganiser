"""============================================================================
https://github.com/sephwalker321/PhotoOrganiser

Author: Joseph Walker j.j.walker@durham.ac.uk

Wishlist
	#TODO Add people highlighting?
	
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

#Pandas for data import and management
import pandas as pd
import numpy as np
from datetime import date, datetime

#Image plotting
import plotly.graph_objects as go
import plotly.express as px
#from skimage import data
from PIL import Image

#For moving data around as child
import json

#Command lines
import argparse
import os
import glob

#Folder selector
import easygui

#IP Address for non-local running
import socket

#######################
# Local Parameters
#######################

Title = "Family Photo Organiser"
Description = "Family tree photo catalogue tool"
HelpText = "Fill out the form below and submit"

DemoPath = "photos" 

DemoPhoto = "assets"+os.sep+"DefaultPhoto.jpg" 

DefaultPath = DemoPath

ExcelName = "AlbumInfo.xlsx"

DefaultVar = {
	"filename" : "",
	"code" : "",
	
	"title": "",
	"date": "",
	"location": "",
	"caption": "",
	"people": "",
	"people_xy": "",
	"complete": "N",
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
	"complete": str,
	"lastedit": str,
}

#Dropdown colors
colourRed = "red"
colourAmber = "orange"
colourGreen = "green"
colourMarker = "black"

MinYear = 1800
MaxYear = date.today().year

################################################################################################################
# Define the app
################################################################################################################

external_stylesheets = [
	{
	"href": "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css",
	"rel": "stylesheet",
	},
]
external_scripts=[]
app = dash.Dash(Title, external_stylesheets=external_stylesheets,external_scripts=external_scripts)
app.title = Title
app._favicon = ("assets/favicon.ico")

################################################################################################################
# Functions
################################################################################################################

def LoadExcel(path=DefaultPath):
	"""
	Load in the album excel catalogue and convert to json

	Parameters
	----------
	path: dtype=str
		Directory of album

	Returns
	-------
	JSON: dtype=dict
		json dict of album
	
	"""
	ExcelPath = path + os.sep + ExcelName
	pathExist = False
	fileExist = False
	pathExist = os.path.exists(path)
	if pathExist:
		fileExist = os.path.exists(ExcelPath)

	if fileExist:
		Excel = pd.read_excel(
			ExcelPath, 
			index_col = 0,
			converters = converters,
			keep_default_na = False
		)
						
	else:
		Excel = pd.DataFrame(
			data=[{
				"path" : path,
				"filename" : DefaultVar["filename"],
				"code" : DefaultVar["code"],
				"title": DefaultVar["title"],
				"date": DefaultVar["date"],
				"location": DefaultVar["location"],
				"caption": DefaultVar["caption"],
				"people": DefaultVar["people"],
				"people_xy": DefaultVar["people_xy"],
				"complete": DefaultVar["complete"],
				"lastedit": DefaultVar["lastedit"],	
			}],
			index=[0]
		)	
	return Jsonify(Excel)
	
def Jsonify(EXCEL):
	"""
	Convert DataFrame to Json

	Parameters
	----------
	EXCEL: dtype=pd.DataFrame
		Album info

	Returns
	-------
	JSON: dtype=dict
		Album info
	
	"""
	return json.dumps(EXCEL.to_json())

def DataFrameify(JSON):
	"""
	Convert Json to DataFrame

	Parameters
	----------
	JSON: dtype=dict
		Album info

	Returns
	-------
	EXCEL: dtype=pd.DataFrame
		Album info
	
	"""
	Excel = pd.read_json(
		json.loads(JSON),
		orient="columns",
		dtype=converters,
	)
	Excel.replace({"NaT": ""}, inplace=True)
	return Excel
	
def DropdownGetFilename(options, index):
	"""
	Get photo filename from dropdown selection

	Parameters
	----------
	options: dtype=dict
		Dropdown options
		
	index: dtype=int
		value of index of dropdown selection

	Returns
	-------
	filename: dtype=str
		photo filename
	
	"""
	if index is None:
		return None
	else:
		return options[index]["label"]["props"]["children"][0]
		
	
################################################################################################################
# Variable containters
################################################################################################################

def AlbumVarContainers(path=DefaultPath, Excel=LoadExcel()):
	"""
	Generate album variables in a Div container

	Parameters
	----------
	path: dtype=str
		Directory of album
	
	Excel: dtype=dict
		json dict of album infomation
	

	Returns
	-------
	Element: dtype=html.Div
		Hidden div containing album variables
	
	"""
	return html.Div( 
		style={"display": "none"},
		children = [
			html.H1(
				id="var_path",
				children=path,
			),
			html.H1(
				id="var_photoindex",
				children="",
			),
			html.H1(
				id="ExcelSheet",
				children=Excel,
			),
		]
	)

def VariableContainers(
		Dat = DefaultVar
	):
	"""
	Generate variables for photo metadata in a Div container

	Parameters
	----------
	Dat: dtype=dict
		Directory of photo meta data
	
	Returns
	-------
	Element: dtype=html.Div
		Hidden div containing photo metadata variables
	
	"""		
	return html.Div( 
		style={"display": "none"},
		children = [
			html.H1(
				id="var_filename",
				children=Dat["filename"],
			),
			html.H1(
				id="var_code",
				children=Dat["code"],
			),
			html.H1(
				id="var_title",
				children=Dat["title"],
			),
			html.H1(
				id="var_date",
				children=Dat["date"],
			),
			html.H1(
				id="var_location",
				children=Dat["location"],
			),
			html.H1(
				id="var_caption",
				children=Dat["caption"],
			),
			html.H1(
				id="var_people",
				children=Dat["people"],
			),
			html.H1(
				id="var_people_xy",
				children=Dat["people_xy"],
			),
			html.H1(
				id="var_complete",
				children=Dat["complete"],
			),
			html.H1(
				id="var_lastedit",
				children=Dat["lastedit"],
			),
			html.H1(
				id="null_submitPhoto",
				children="",
			),
			html.H1(
				id="null_clickdata",
				children="",
			),
		]
	)
	
################################################################################################################
# Banner
################################################################################################################

def Header():
	"""
	Generate dashboard header 

	Parameters
	----------
	
	Returns
	-------
	Element: dtype=html.Div
		Title and description in a banner
	"""	
	return html.Div(
		children=[
			html.P(children="👪🌳", className="header-emoji"),
				html.H1(
				children=Title, className="header-title"
			),
			html.P(
				children=Description,
				className="header-description",
			)
		],
		className="header",
	)
	
		

################################################################################################################
# InfoPage
################################################################################################################

def InfoPage():
	"""
	Generate info page / help screen from markdown LoadInfo.md

	Parameters
	----------
	
	Returns
	-------
	Element: dtype=dbc.Modal
		info / help screen
	"""	
	#Load in markdown
	text_markdown = "\n \t"
	with open("assets"+os.sep+"LoadInfo.md") as this_file:
		for a in this_file.read():
			if "\n" in a:
				text_markdown += "\n \t"
			else:
				text_markdown += a
	return dbc.Modal(
		children = [
			dbc.ModalBody(dcc.Markdown(text_markdown)),
			dbc.ModalFooter(
				dbc.Button("Close", id="DashboardModal-Close", className="button")
			),
		],
		is_open = False,
		scrollable=True,
		id="DashboardModal",
		size="xl",
		className="Modal",
	)
	
#######################
# Callbacks
#######################

@app.callback(
	[
		Output("DashboardModal", "is_open"),
	],
	[
		Input("DashboardModal-Open", "n_clicks"), Input("DashboardModal-Close", "n_clicks")
	],
	[
		State("DashboardModal", "is_open")
	]
)
def toggle_modal(n1, n2, is_open):
	"""
	Toggle info modal displays
	"""
	if n1 or n2:
		return [not is_open]
	return [is_open]
		
################################################################################################################
# Photo path and photo selector
################################################################################################################
			
def PathSelect():
	"""
	Generate album path and photo selection menu

	Parameters
	----------
	
	Returns
	-------
	Element: dtype=html.Div
		album and photo selector
	"""	
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
							type="text",
							value=DefaultPath,
							debounce=True,		
						),	
					], width=6-2),
					dbc.Col([
						dbc.Button(children="Select", id="path_buttonInput", n_clicks=0, className="button")
					], width=2),
					dbc.Col([
						dcc.Dropdown(
							id="PhotoSelectDropdown",
							options=[],
							value=0,
							clearable=False,
							searchable=False,
							placeholder="Select a photo...",
							style={"display":"fill", "width":"100%"}
						),
					], width=4),
					dbc.Col([
						dbc.Button(children="Prev", id="PhotoSelectPrev", n_clicks=0, className="button")
					], width=1),
					dbc.Col([
						dbc.Button(children="Next", id="PhotoSelectNext", n_clicks=0, className="button")
					], width=1),
					
					
				])
			])
		],
		className="menu",
	)
	
#######################
# Callbacks
#######################
	
@app.callback(
	[
		Output("var_path", "children"),
		Output("path_textInput", "value")
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
def update_photoPath(path_buttonInput, path_textInput, var_path):
	"""
	Callback to update album selection path
	"""	
	if ctx.triggered_id == "path_buttonInput":
		path = easygui.diropenbox(default=var_path)
		if path is None:
			return [var_path, var_path]
	elif ctx.triggered_id == "path_textInput":
		path = path_textInput
	return [path, path]

@app.callback(
	[
		Output("PhotoSelectDropdown","options")
	],
	[
		Input("var_path", "children")
	],
	[
		State("ExcelSheet","children")
	],
	prevent_initial_call = False
	)
def update_photoDropdowns(var_path, ExcelSheet):
	"""
	Callback to update photo dropdown selection
	"""
	Excel = DataFrameify(ExcelSheet)
		
	globed = glob.glob(var_path+os.sep+"*")
	globed.sort()
	options = []
	N=0
	for f in globed:
		if f.endswith(".png")+f.endswith(".jpg")+f.endswith(".jpeg") != 1:
			continue
			
		filename = f.split(var_path)[1][1:]
		
		C = colourRed #Default Colour
		if filename in Excel["filename"].values: #Updating
			complete = Excel[Excel["filename"] == filename]["complete"].values
			if complete == "Y":
				C = colourGreen
			elif complete == "N":
				C = colourAmber
		
		
		options.append({
			"label": html.Span([filename], style={"color": C}),
			"value": N
		})
		N+=1
	options = sorted(options, key=lambda d: d["value"]) 
	return [options]
	
@app.callback(
	[
		Output("PhotoSelectDropdown","value"),
		Output("PhotoSelectPrev","disabled"),
		Output("PhotoSelectNext","disabled")
	],
	[
		Input("PhotoSelectDropdown","options"),
		Input("PhotoSelectDropdown","value"),
		Input("PhotoSelectPrev", "n_clicks"),
		Input("PhotoSelectNext", "n_clicks"),
	],
	[
		State("PhotoSelectDropdown","value")
	],
	prevent_initial_call = False
	)
def update_photoDropdowns(options, photo, prev_click, next_click, index):
	"""
	Callback to update photo selection by button or default
	"""
	NOptions = len(options)
	if ctx.triggered_id == "PhotoSelectDropdown": 
		if NOptions > 0:
			PrevDisable = True
			NextDisable = False
			if NOptions == 1:
				NextDisable = True
			return [0, PrevDisable, NextDisable]
		else:
			return [None, True, True]

	if index is None:
		return [None, True, True]
		
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
# Meta Data
################################################################################################################

def PeopleList(ps="", xys=""):
	"""
	Generate div element containing the list of people in the photo with delete button.

	Parameters
	----------
	ps: dtype=str
		string of | separated names of people
		
	xys: dtype=str
		string of | separated coordinates of people in photo
	
	Returns
	-------
	Element: dtype=html.Div
		list of people div element
	"""
	children = []
	N=0	
	
	pslist= ps.split("|")
	xyslist = xys.split("|")
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
					html.Div(
						children="%s %s" % (pi, xysi),
						className="peopleList",
					)
				], width=12-3),
				dbc.Col([
					dbc.Button(
						children="Delete",
						id={
							"type": "dynamic-deleteperson",
							"index": N
						},
						n_clicks=0,
						className="button-del"
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
					html.Div(
						children="Start tagging people!",
						className="peopleList",
					)
				], width=12),
		])
		return html.Div(
			children = [row]
		) 

def MainForm():
	"""
	Generate div element of the metadata form for the photo

	Parameters
	----------
	
	Returns
	-------
	Element: dtype=html.Div
		element of form
	"""
	return html.Div(
		children=[
			html.Div(
				children=[
					dbc.Row([
						dbc.Col([
							html.P(children=HelpText, className="text"),
						], width=12-3),

						dbc.Col([
							dbc.Button(
								children="Help",
								id="DashboardModal-Open",
								className="button"
							),
						], width=3)
					]),
					
					#Title
					dbc.Row([
						dbc.Col([
							html.Div(
								children="Title",
								className="menu-title",
							),
						]),
					]),
					dbc.Row([
						dbc.Col([
							dbc.Input(
								placeholder="Enter a title...",
								id="metadata_title",
								type="text",
								value="",	
								debounce=True					
							),
						]),
					]),
					#Datepicker
					dbc.Row([
						dbc.Col([
							html.Div(
								children="Date",
								className="menu-title",
							),
						]),
					]),
					dbc.Row([
						dbc.Col([
						dcc.DatePickerSingle(
							id="metadata_date",
							date=None,
							placeholder="Pick a date...",
									
							month_format="MMMM Y",
							display_format="Do MMM Y",
									
							clearable=True, 
							initial_visible_month=date.today(),
							min_date_allowed=date(MinYear, 1, 1),
							max_date_allowed=date.today(),
						),
						], width=6, style={"text-align": "center"}),
						dbc.Col([
						dbc.Input(
							placeholder="Enter a year...",
							id="metadata_pickyear",
							type="number",
							value=None,		
							debounce=True,		
							
							min=MinYear, max=MaxYear, step=1
						),
						], width=6, style={"text-align": "center"}),
						dbc.Col([
							html.Div(),
						], width=0)
					]),
					#Title
					dbc.Row([
						dbc.Col([
							html.Div(
								children="Location",
								className="menu-title",
							),
						]),
					]),
					dbc.Row([
						dbc.Col([
							dbc.Input(
								placeholder="Enter a location...",
								id="metadata_location",
								type="text",
								value="",		
								debounce=True				
							),
						]),	
					]),
					#Person select unselect
					dbc.Row([
						dbc.Col([
							html.Div(
								children="People",
								className="menu-title",
							),
						]),
					]),
					dbc.Row(
						dbc.Col([
							html.Div([PeopleList()], id="metadata_people"
							)
						]),
					),
					#Caption
					dbc.Row([
						dbc.Col([
							html.Div(
								children="Caption",
								className="menu-title",
							),
						]),
					]),
					dbc.Row([
						dbc.Col([
							dbc.Textarea(
								placeholder="Enter a caption...",
								value="",	
								id="metadata_caption",		
								n_blur=0,		
							),
						]),
					]),
					#Is Photo documentation complete?
					dbc.Row([
						dbc.Col([
							html.Div(
								children="Complete",
								className="menu-title",
							),
						]),
					]),
					dbc.Row([
						dbc.Col([
							dcc.RadioItems(
								options=[
									{"label":html.Span(["Yes"], style={"padding-left": 3, "padding-right": 10}), "value":"Y"},
									{"label":html.Span(["No"], style={"padding-left": 3, "padding-right": 10}), "value":"N"},
								],
								value="N",	
								id="metadata_complete",
							),
						]),
					]),
				
					#Submit
					dbc.Row([
						dbc.Col([
							html.Div(
								children="\n",
								className="menu-title",
							),
						]),
					]),
					dbc.Row([
						dbc.Col([
							dbc.Button(
								children="Clear", 
								id="metadata_clearbutton",
								n_clicks=0,
								style={"background-color": colourAmber,"border-color": colourAmber,"color": "black"},
								className="button"
							),
						], width=6, style={"text-align": "center"}),
						dbc.Col([
							dbc.Button(
								children="Submit", 
								id="metadata_submitbutton",
								n_clicks=0,
								className="button"
							),
						], width=6, style={"text-align": "center"}),
						
					]),
				]
			),
		],
		className="metaform",
	)
	
#######################
# Callbacks
#######################
	
@app.callback(
	[
		Output("var_title","children"),
		Output("metadata_title", "value"),
	],
	[
		Input("metadata_title", "value"),
		Input("var_title","children"),
		Input("metadata_clearbutton", "n_clicks")
	],
	[
	
	],
	prevent_initial_call = True
	)
def update_metaTitle(metadata_title, var_title, metadata_clearbutton):
	"""
	Callback to update meta title
	"""
	if ctx.triggered_id == "metadata_title":
		return [metadata_title, metadata_title]
	elif ctx.triggered_id == "var_title":
		return [var_title, var_title]
	elif ctx.triggered_id == "metadata_clearbutton":
		return [DefaultVar["title"],DefaultVar["title"]]
	
@app.callback(
	[
		Output("var_date","children"),
		Output("metadata_date", "date"),
		Output("metadata_date", "initial_visible_month"),
		
		Output("metadata_pickyear", "value"),
	],
	[
		Input("metadata_date", "date"),
		Input("var_date","children"),
		Input("metadata_pickyear", "value"),
		Input("metadata_clearbutton", "n_clicks")
	],
	[
		
	],
	prevent_initial_call = True
	)
def update_metaDate(metadata_date, var_date, metadata_pickyear, metadata_clearbutton):
	"""
	Callback to update meta date
	"""
	if metadata_pickyear is None:
		initialDate = None
	else:
		if isinstance(metadata_pickyear, str):
			if len(metadata_pickyear) == 4:
				metadata_pickyear = int(metadata_pickyear)
			else:
				metadata_pickyear = int(datetime.strptime(metadata_pickyear, "%Y-%m-%d").year)
		else:
			metadata_pickyear = int(metadata_pickyear)
		
		initialDate = str(date(metadata_pickyear, 1, 1))
		
	if ctx.triggered_id == "metadata_pickyear":
		return [None, None, initialDate, metadata_pickyear]
	
	elif ctx.triggered_id == "metadata_date":
		if metadata_date is None:
			pass
		else:	
			initialDate = str(datetime.strptime(metadata_date, "%Y-%m-%d").year)
		return [metadata_date, metadata_date, initialDate, initialDate]
		
	elif ctx.triggered_id == "var_date":
		if var_date == "":
			var_date = None 
			
		if var_date is None:
			pass
		else:	
			initialDate = str(datetime.strptime(var_date, "%Y-%m-%d").year)
		return [var_date, var_date, initialDate, initialDate]
		
	elif ctx.triggered_id == "metadata_clearbutton":
		return [ DefaultVar["date"],None, None, None]
			
@app.callback(
	[
		Output("var_location","children"),
		Output("metadata_location", "value"),
	],
	[
		Input("metadata_location", "value"),
		Input("var_location","children"),
		Input("metadata_clearbutton", "n_clicks")
	],
	[
	
	],
	prevent_initial_call = True
	)
def update_metaLoc(metadata_location, var_location, metadata_clearbutton):
	"""
	Callback to update meta location
	"""
	if ctx.triggered_id == "metadata_location":
		return [metadata_location, metadata_location]
	elif ctx.triggered_id == "var_location":
		return [var_location, var_location]
	elif ctx.triggered_id == "metadata_clearbutton":
		return [DefaultVar["location"],DefaultVar["location"]]
	
@app.callback(
	[
		Output("metadata_people","children")
	],
	[
		Input("var_people", "children"), 
	],
	[
		State("var_people_xy", "children")
	],
	prevent_initial_call = True
	)
def update_metaPeople(var_people, var_people_xy):
	"""
	Callback to update list of people div
	"""
	return [PeopleList(ps=var_people, xys=var_people_xy)]

		
@app.callback(
	[
		Output("var_caption","children"),
		Output("metadata_caption", "value"),
	],
	[
		Input("metadata_caption", "value"),
		Input("var_caption","children"),
		Input("metadata_clearbutton", "n_clicks")
	],
	[
	
	],
	prevent_initial_call = True
	)
def update_metaCaption(metadata_caption, var_caption, metadata_clearbutton):
	"""
	Callback to update meta caption
	"""
	if ctx.triggered_id == "metadata_caption":
		return [metadata_caption, metadata_caption]
	elif ctx.triggered_id == "var_caption":
		return [var_caption, var_caption]
	elif ctx.triggered_id == "metadata_clearbutton":
		return [DefaultVar["caption"],DefaultVar["caption"]]
		
@app.callback(
	[
		Output("var_complete","children"),
		Output("metadata_complete", "value"),
	],
	[
		Input("metadata_complete", "value"),
		Input("var_complete","children"),
		Input("metadata_clearbutton", "n_clicks")
	],
	[
	
	],
	prevent_initial_call = True
	)
def update_metaComplete(metadata_complete, var_complete, metadata_clearbutton):
	"""
	Callback to update meta complete tick box
	"""
	if ctx.triggered_id == "metadata_complete":
		return [metadata_complete, metadata_complete]
	elif ctx.triggered_id == "var_complete":
		return [var_complete, var_complete]
	elif ctx.triggered_id == "metadata_clearbutton":
		return [DefaultVar["complete"],DefaultVar["complete"]]
	
@app.callback(
	[
		Output("null_submitPhoto","children"),
		Output("ExcelSheet","children")
	],
	[
		Input("metadata_submitbutton", "n_clicks"),
		Input("var_path", "children")
	],
	[
		State("ExcelSheet","children"),
		State("var_filename", "children"),
		State("var_code", "children"),
		State("var_title", "children"),
		State("var_date", "children"),
		State("var_location", "children"),
		State("var_caption", "children"),
		State("var_people", "children"),
		State("var_people_xy", "children"),
		State("var_complete", "children"),
	],
	prevent_initial_call = True
	)
def submit_phototoexcel(
		metadata_submitbutton,
		var_path,
		
		ExcelSheet, 
		var_filename,
		var_code,
		var_title,
		var_date,
		var_location,
		var_caption,
		var_people,
		var_people_xy,
		var_complete,	
	):
	"""
	Callback to update excel album infomation
	"""
	
	if ctx.triggered_id == "metadata_submitbutton":
		if var_filename == "":
			return ["", ExcelSheet]
					
		if var_filename is None:
			var_filename = DefaultVar["filename"]
		if var_code is None:
			var_code = DefaultVar["code"]
		if var_title is None:
			var_title = DefaultVar["title"]
		if var_date is None:
			var_date = DefaultVar["date"]
		if var_caption is None:
			var_caption = DefaultVar["caption"]
		if var_people is None:
			var_people = DefaultVar["people"]
		if var_people_xy is None:
			var_people_xy = DefaultVar["people_xy"]
		if var_complete is None:
			var_complete = DefaultVar["complete"]
					
		df_i = pd.DataFrame(data=[{
			"path" : var_path,
			"filename" : var_filename,
			"code" : var_code,
			"title": var_title,
			"date": var_date,
			"location": var_location,
			"caption": var_caption,
			"people": var_people,
			"people_xy": var_people_xy,
			"complete": var_complete,
			"lastedit": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),	
		}], index=[0])
		
		Excel = DataFrameify(ExcelSheet)
		if var_filename in Excel["filename"].values: #Updating
			Excel[Excel["filename"] == filename] = df_i.values
			
		else: #Adding new one
			Excel = pd.concat([Excel, df_i], ignore_index=True)

			
		ExcelPath = var_path + os.sep + ExcelName
		
		Excel = Excel[Excel["filename"] != ""]
		with pd.ExcelWriter(ExcelPath) as writer:
			Excel.to_excel(writer)  
		return ["", Jsonify(Excel)]
	elif ctx.triggered_id == "var_path":
		if var_path is None:
			return ["", LoadExcel()]
		else:
			return ["", LoadExcel(var_path)]
	
@app.callback(
	[
		Output("variables","children")
	],
	[
		Input("PhotoSelectDropdown", "value")
	],
	[
		Input("PhotoSelectDropdown", "options"),
		State("ExcelSheet","children"),
	],
	prevent_initial_call = True
	)
def update_metadata(value, options, ExcelSheet):
	"""
	Callback to update metadata
	"""
	filenamedropdown = DropdownGetFilename(options, value) 
	Excel = DataFrameify(ExcelSheet)
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
			"complete":  Excel["complete"].values[0],
			
			"lastedit":  Excel["lastedit"].values[0],	
		}
		return [VariableContainers(Dat=Dat)]
	else: #Adding new one
		return [VariableContainers()]
		
@app.callback(
	[
		Output("metadata_submitbutton","disabled"),
	],
	[
		Input("PhotoSelectDropdown", "value"),
	],
	[
		State("PhotoSelectDropdown", "options"),
	],
	prevent_initial_call = True
	)
def submitbutton_enabledisable(value, options):
	"""
	Callback to disable submit button if no image selected
	"""
	dropdownfilename = DropdownGetFilename(options, value) 
	
	if dropdownfilename is None:
		return [True]
	else:
		return [False]
	
################################################################################################################
# Photo
################################################################################################################

def CreatePictureFig(path=DemoPhoto):
	"""
	Generate figure containing the photo

	Parameters
	----------
	path: dtype=str
		path of photo
	
	Returns
	-------
	Fig: dtype=px.fig
		figure containing image and selection cross
	"""
	if path is None:
		path = DemoPhoto
	
	img = Image.open(path) 
		
	xshape = img.size[0]
	yshape = img.size[1]
		
	layout = {
		"autosize":True,
		"margin" : {"l":10,"r":10,"t":10,"b":10},
		"xaxis_range": [0, xshape],
		"yaxis_range": [yshape, 0],
	}
	
	# Add image
	Fig = px.imshow(img)
	Fig.add_scatter(
		x=[-100], y=[-100],
		opacity=.8,
		mode="markers",
		marker=dict(size=20, symbol="x-thin", color=colourMarker, line=dict(width=5, color=colourMarker)),
		name="", 
		hoverinfo="x+y",
		hovertemplate= "x: %{x}<br>"+"y: %{y}",
	)
	
	#TODO Add people highlighting?
	
	Fig.update_layout(layout)
	return Fig

def MainPicture():
	"""
	Generate div element containing photo and add person

	Parameters
	----------
	
	Returns
	-------
	Element: dtype=html.Div
		element of div
	"""
	config = {
		"displayModeBar": False,
		"doubleClick":"reset"
	}
	return html.Div(children=[
		dbc.Row([
			dbc.Col([
				dcc.Graph(
					figure = CreatePictureFig(),
					id="picture", config=config,
				),
			]),
			], className="metaform"
		),
		dbc.Row([
			dbc.Col([
				html.Div(
					children=[
						html.Div(children="Name", className="menu-title"),
						dbc.Input(
							placeholder="Enter a Name...",
							type="text",
							id="picture-nameperson",
							debounce=True
						),
					]
				),
				], width=12-3	
			),
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
							className="button"
						)
					]
				),
			], width=3
			),
			], className="metaform"
		)
	])
	
#######################
# Callbacks
#######################
		
@app.callback(
	[
		Output("picture","figure"),
		Output("null_clickdata", "children"),
		Output("picture-nameperson", "disabled"),
		Output("picture-addperson", "disabled"),
		Output("var_filename", "children"),
	],
	[
		Input("PhotoSelectDropdown", "value"),
		Input("picture", "clickData")
	],
	[
		State("PhotoSelectDropdown", "options"),
		State("var_path", "children"),
		State("var_filename", "children"),
		State("picture","figure")
	],
	prevent_initial_call = True
	)
def update_figure(value, clickData, options, var_path, var_filename, fig):
	"""
	Callback to update figure
	"""
	dropdownfilename = DropdownGetFilename(options, value) 
	if ctx.triggered_id == "PhotoSelectDropdown":
		if dropdownfilename is None or var_path is None:
			
			return [CreatePictureFig(None), "(0,0)", True, True, var_filename]
		else:
			Path =  var_path + os.sep + dropdownfilename
			return [CreatePictureFig(Path), "(0,0)", True, True, dropdownfilename]
			
	elif ctx.triggered_id == "picture":
	
			x = clickData["points"][0]["x"]
			y = clickData["points"][0]["y"]
			xy = "(%s,%s)" % (x,y)
			
			fig["data"][1]["x"] = [x]
			fig["data"][1]["y"] = [y]
			fig["data"][1]["marker"]["size"] = 20
			
			return [fig, xy, False, False, dropdownfilename]
		
@app.callback(
	[
		Output("picture-nameperson","value"),
		Output("var_people", "children"), 
		Output("var_people_xy", "children")
	],
	[
		Input("picture-addperson", "n_clicks"),
		Input( {"type": "dynamic-deleteperson", "index": ALL} , "n_clicks"),
		Input("metadata_clearbutton", "n_clicks"),
	],
	[
		State("picture-nameperson", "value"), 
		State("null_clickdata", "children"), 
		State("var_people", "children"), 
		State("var_people_xy", "children")		
	],
	prevent_initial_call = True
	)
def update_peopleList(
		nclicks_add,
		nclicks_del,
		metadata_clearbutton,
		
		Name,
		Coords,
		ps,
		xys,
	):
	"""
	Callback to update people list
	"""	
	if ctx.triggered_id == "metadata_clearbutton":
		return [None,  DefaultVar["people"],  DefaultVar["people_xy"]]
				
	pslist= ps.split("|")
	xyslist = xys.split("|")
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
				ps += pslist[i] + "|"
				xys += xyslist[i] + "|"
		else:
			ps += Name + "|"
			xys += Coords + "|"
			
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
				ps += pslist[i] + "|"
				xys += xyslist[i] + "|"
	
	#Sort in order			
	pslist= ps.split("|")
	xyslist = xys.split("|")
	if "" in pslist:
		pslist.remove("")
	if "" in xyslist:
		xyslist.remove("")
	xslist = [int(xy.split(",")[0][1:]) for xy in xyslist]
	xslist, pslist, xyslist = zip(*sorted(zip(xslist, pslist, xyslist)))
	ps = ""
	xys = ""
	for i in range(len(pslist)):
		ps += pslist[i] + "|"
		xys += xyslist[i] + "|"	
	
	return [None, ps, xys]
	
################################################################################################################
# Layout
################################################################################################################

app.layout = html.Div(
	children=[
		#Markdown info page
		InfoPage(), 
		#Header
		Header(), 
		#Excel info storage
		AlbumVarContainers(),
		#Photo info storage
		html.Div(
			id = "variables",
			children=VariableContainers(),
		),
		#Album path selector
		PathSelect(),
		#Form and photo
		html.Div(
			children=[
				dbc.Row([
					dbc.Col(
						MainForm(),
					),
					dbc.Col(
						MainPicture(),
					),
				]),
			],
			className="wrapper"
		)
	]
)

if __name__ == "__main__":
	#Feed in command line arguments	
	parser = argparse.ArgumentParser()
	parser.add_argument("-l", "--local", type=bool, help="Run server on local machine default=False", default=True)
	parser.add_argument("-p", "--port", type=int, help="Port used to serve the application default=8050", default=8050)
	parser.add_argument("-d", "--debug", type=bool, help="Set Flask debug mode and enable dev tools default=False", default=False)
	
	args = parser.parse_args()
	#Interpret the arguments
	if args.local:
		host = "127.0.0.1"
		IPAddr = host
	else:
		host = "0.0.0.0"
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		IPAddr = s.getsockname()[0]
		s.close()
		
		print("Dash is running remotely on "+"http:"+os.sep+os.sep+IPAddr+":"+str(args.port)+os.sep)
	
	if args.debug:
		use_reloader=True
	else:
		use_reloader=False

	app.config.suppress_callback_exceptions = True	
	threaded = True
	app.run(debug=args.debug, port=args.port, threaded=threaded, host=host, use_reloader=use_reloader)
