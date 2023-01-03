"""============================================================================

Contents: 

Author: Joseph Walker j.j.walker@durham.ac.uk
============================================================================"""

#TODO Local or Remote modes
#TODO Documentation
"""
        Load config for simulator from world.yaml

        Parameters
        ----------
        leisure
        policies
        interaction
        world
        config_filename
            The path to the world yaml configuration
        comment
            A brief description of the purpose of the run(s)

        Returns
        -------
        A Simulator
        """
#TODO Markdown

#TODO Index codes?

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

#Image plotting
import plotly.graph_objects as go
import plotly.express as px
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

Title = "Family Photo Organiser"
Description = "Family tree photo catalogue tool"

#http://clipart-library.com/clip-art/2-25443_silhouette-child-drawing-family-computer-icons-silhouette-people.htm
DemoPath = "photos" 

#https://clipartix.com/family-tree-clipart-image-24755/
DemoPhoto = "assets"+os.sep+"DefaultPhoto.jpg" 

DefaultPath = "/home/joseph/Desktop/Photos"
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
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,external_scripts=external_scripts)
app.title = Title
app._favicon = ("assets/favicon.ico")


################################################################################################################
# Functions
################################################################################################################
            
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
			"complete": DefaultVar["complete"],
			"lastedit": DefaultVar["lastedit"],	
		}], index=[0])
			
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
		return options[index]["label"]["props"]["children"][0]
		

################################################################################################################
# Banner
################################################################################################################

def Banner():
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
				id='var_complete',
				children=Dat['complete'],
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
								value=0,
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
				])
			],
			className="menu",
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
		State("ExcelSheet","children")
	],
	prevent_initial_call = False
	)
def update_photoDropdowns(Dir, Excel):

	Excel = ConvertStoredJSON(Excel)
		
	globed = glob.glob(Dir+os.sep+"*")
	globed.sort()
	options = []
	N=0
	for f in globed:
		if f.endswith(".png")+f.endswith(".jpg")+f.endswith(".jpeg") != 1:
			continue
			
		filename = f.split(Dir)[1][1:]
		
		C = colourRed #Default Colour
		if filename in Excel["filename"].values: #Updating
			complete = Excel[Excel["filename"] == filename]["complete"].values
			if complete == "Y":
				C = colourGreen
			elif complete == "N":
				C = colourAmber
		
		
		options.append({
			'label': html.Span([filename], style={'color': C}),
			'value': N
		})
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
		Input('PhotoSelectDropdown','options'),
		Input('PhotoSelectDropdown','value'),
		Input('PhotoSelectPrev', "n_clicks"),
		Input('PhotoSelectNext', "n_clicks"),
	],
	[
		State('PhotoSelectDropdown','value')
	],
	prevent_initial_call = False
	)
def update_photoDropdowns(options, photo, prev_click, next_click, index):
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
# Photo 
################################################################################################################

	
def CreatePictureFig(Path):
	if Path is None:
		img = Image.open(DemoPhoto)
	else:
		img = Image.open(Path) 
		
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
	
	Fig.update_layout(layout)
	return Fig

def MainPicture():
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
			], className="metaform"
		),
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
							className=""
						)
					]
				),
			], width=3
			),
			], className="metaform"
		)
	])
	
	
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
			
			return [CreatePictureFig(None), "(0,0)", True, True, filename]
		else:
			Path =  directory + os.sep + dropdownfilename
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
		Output('picture-nameperson','value'),
		Output('var_people', 'children'), 
		Output('var_people_xy', 'children')
	],
	[
		Input('picture-addperson', "n_clicks"),
		Input( {'type': 'dynamic-deleteperson', 'index': ALL} , 'n_clicks'),
		Input('metadata_clearbutton', "n_clicks"),
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
		clearbutton,
		
		Name,
		Coords,
		ps,
		xys,
	):	
	
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
# Meta Data
################################################################################################################

def PeopleList(ps="", xys=""):
	children = []
	N=0	
	
	pslist= ps.split("|")
	xyslist = xys.split("|")
	if "" in pslist:
		pslist.remove("")
	if "" in xyslist:
		xyslist.remove("")
		
	#TODO Order L to R?
	
	if len(pslist) > 0:
		for pi, xysi in zip(pslist, xyslist):
			if pi is None:
				continue
			row = dbc.Row([
				dbc.Col([
					html.Div(
						children="%s %s" % (pi, xysi),
						className="Locs",
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
					html.Div(
						children="Start tagging people!",
						className="Locs",
					)
				], width=12),
		])
		return html.Div(
			children = [row]
		) 

def MainForm():
	return html.Div(
		children=[
			html.Div(
				children=[
					dbc.Row([
						dbc.Col([
							html.P(children="TODO"),
						], width=6),

						dbc.Col([
							dbc.Button(
								children="Help",
								id="DashboardModal-Open",
							),
						], width=6) #TODO Formatting
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
								placeholder='Enter a title...',
								id="metadata_title",
								type='text',
								value='',	
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
									
							month_format='MMMM Y',
							display_format='Do MMM Y',
									
							clearable=True, 
							initial_visible_month=date.today(),
							min_date_allowed=date(MinYear, 1, 1),
							max_date_allowed=date.today(),
						),
						], width=6, style={"text-align": "center"}),
						dbc.Col([
						dbc.Input(
							placeholder='Enter a year...',
							id="metadata_pickyear",
							type='number',
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
								placeholder='Enter a location...',
								id="metadata_location",
								type='text',
								value='',		
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
								placeholder='Enter a caption...',
								value='',	
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
									{"label":html.Span(["Yes"], style={'padding-left': 3, 'padding-right': 10}), "value":"Y"},
									{"label":html.Span(["No"], style={'padding-left': 3, 'padding-right': 10}), "value":"N"},
								],
								value='N',	
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
								children='Clear', 
								id="metadata_clearbutton",
								n_clicks=0,
								style={"background-color": colourAmber,"border-color": colourAmber,"color": "black"},
							),
						], width=6, style={"text-align": "center"}),
						dbc.Col([
							dbc.Button(
								children='Submit', 
								id="metadata_submitbutton",
								n_clicks=0
							),
						], width=6, style={"text-align": "center"}),
						
					]),
				]
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
		Input('metadata_clearbutton', "n_clicks")
	],
	[
	
	],
	prevent_initial_call = True
	)
def update_metaTitle(text, Exceltext, clearbutton):
	if ctx.triggered_id == "metadata_title":
		return [text, text]
	elif ctx.triggered_id == "var_title":
		return [Exceltext, Exceltext]
	elif ctx.triggered_id == "metadata_clearbutton":
		return [DefaultVar["title"],DefaultVar["title"]]
	
@app.callback(
	[
		Output('var_date','children'),
		Output('metadata_date', "date"),
		Output("metadata_date", "initial_visible_month"),
		
		Output("metadata_pickyear", "value"),
	],
	[
		Input('metadata_date', "date"),
		Input('var_date','children'),
		Input("metadata_pickyear", "value"),
		Input('metadata_clearbutton', "n_clicks")
	],
	[
		
	],
	prevent_initial_call = True
	)
def update_metaData(metadate, Exceldate, year, clearbutton):
	if year is None:
		initialDate = None
	else:
		if isinstance(year, str):
			if len(year) == 4:
				year = int(year)
			else:
				year = int(datetime.strptime(year, '%Y-%m-%d').year)
		else:
			year = int(year)
		
		initialDate = str(date(year, 1, 1))
		
	
	if ctx.triggered_id == "metadata_pickyear":
		return [None, None, initialDate, year]
	
	elif ctx.triggered_id == "metadata_date":
		if metadate is None:
			pass
		else:	
			initialDate = str(datetime.strptime(metadate, '%Y-%m-%d').year)
		return [metadate, metadate, initialDate, initialDate]
		
	elif ctx.triggered_id == "var_date":
		if Exceldate == "":
			Exceldate = None 
			
		if Exceldate is None:
			pass
		else:	
			initialDate = str(datetime.strptime(Exceldate, '%Y-%m-%d').year)
		return [Exceldate, Exceldate, initialDate, initialDate]
		
	elif ctx.triggered_id == "metadata_clearbutton":
		return [ DefaultVar["date"],None, None, None]
			
@app.callback(
	[
		Output('var_location','children'),
		Output('metadata_location', "value"),
	],
	[
		Input('metadata_location', "value"),
		Input('var_location','children'),
		Input('metadata_clearbutton', "n_clicks")
	],
	[
	
	],
	prevent_initial_call = True
	)
def update_metaLoc(loc, locExcel, clearbutton):
	if ctx.triggered_id == "metadata_location":
		return [loc, loc]
	elif ctx.triggered_id == "var_location":
		return [locExcel, locExcel]
	elif ctx.triggered_id == "metadata_clearbutton":
		return [DefaultVar["location"],DefaultVar["location"]]
	
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
		Input('metadata_clearbutton', "n_clicks")
	],
	[
	
	],
	prevent_initial_call = True
	)
def update_metaCaption(text, textExcel, clearbutton):
	if ctx.triggered_id == "metadata_caption":
		return [text, text]
	elif ctx.triggered_id == "var_caption":
		return [textExcel, textExcel]
	elif ctx.triggered_id == "metadata_clearbutton":
		return [DefaultVar["caption"],DefaultVar["caption"]]
		
@app.callback(
	[
		Output('var_complete','children'),
		Output('metadata_complete', "value"),
	],
	[
		Input('metadata_complete', "value"),
		Input('var_complete','children'),
		Input('metadata_clearbutton', "n_clicks")
	],
	[
	
	],
	prevent_initial_call = True
	)
def update_metaComplete(Radio, RadioExcel, clearbutton):
	if ctx.triggered_id == "metadata_complete":
		return [Radio, Radio]
	elif ctx.triggered_id == "var_complete":
		return [RadioExcel, RadioExcel]
	elif ctx.triggered_id == "metadata_clearbutton":
		return [DefaultVar["complete"],DefaultVar["complete"]]
	
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
		State('var_complete', 'children'),
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
		complete,	
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
	if complete is None:
		complete = DefaultVar["complete"]
				
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
		"complete": complete,
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
			"complete":  Excel["complete"].values[0],
			
			"lastedit":  Excel["lastedit"].values[0],	
		}
		return [VariableContainers(Dat=Dat)]
	else: #Adding new one
		return [VariableContainers()]


	
################################################################################################################
# Callbacks
################################################################################################################

#######################
# Infopage
#######################

#Dashboard info screen 
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
	'''
	Toggle info modal displays

		Parameters:
			n1 (bool): Is open clicked
			 n2 (bool): Is close clicked
			is_open (bool): T/F is open or closed

		Returns:
			is_open (bool): T/F is open or closed
	'''
	if n1 or n2:
		return [not is_open]
	return [is_open]
	
def InfoPage():
	#Initial info splash screen
	text_markdown = "\n \t"
	with open('assets'+os.sep+'LoadInfo.md') as this_file:
		for a in this_file.read():
			if "\n" in a:
				text_markdown += "\n \t"
			else:
				text_markdown += a
	return dbc.Modal(
		children = [
			dbc.ModalBody(dcc.Markdown(text_markdown)),
			dbc.ModalFooter(
				dbc.Button("Close", id="DashboardModal-Close", className="ModalButton")
			),
		],
		is_open = True,
		scrollable=True,
		id="DashboardModal",
		size="xl",
		className="Modal",
	)


################################################################################################################
# Layout
################################################################################################################


app.layout = html.Div(
	children=[
		#Markdown info page
		InfoPage(), 
		#Header
		Banner(), 
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
	print("Run app dashboard")
	app.config.suppress_callback_exceptions = True	
	
	#Run as debug mode
	#app.run(debug=True, port=8050, threaded= True)
	#Run normally
	app.run(debug=True, port=8050, threaded= True, host= '0.0.0.0')
