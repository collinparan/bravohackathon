#!/usr/bin/python

import plotly.express as px
from dash import html
from dash import dcc
from dash.dependencies import Output,Input,State
import dash_bootstrap_components as dbc
import dash
import dash_auth
import plotly.graph_objs as go
import plotly.express as px
import uvicorn
import json
import asyncio
from fastapi import FastAPI, Request, Response, Body, Form, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from starlette.middleware.wsgi import WSGIMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import aiofiles
import base64
import os
from pydantic import BaseModel

import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
# from fbprophet import Prophet

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.types import NVARCHAR, VARCHAR, String, CHAR
from sqlalchemy.inspection import inspect
import datetime as dt


parent_dir_path = os.path.dirname(os.path.realpath(__file__))

engine = create_engine('postgresql+psycopg2://postgres:123@postgres_db/postgres')

server = FastAPI(
    title='Firefly API',
    description='The goal of this API is to serve Data and ML predictions to others apps')

server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], )

##################################################
# Example of APIs
##################################################

@server.get('/hello/',
            tags=['Dummy API'],
            summary="Hello World",
            description="Returns a message")
async def hello():
    return "Is it me you're looking for?"


@server.get('/hello/database',
            tags=["Dummy API"],
            summary="From the database",
            description="DB")
async def from_db():
    df = pd.read_sql('''SELECT 'world' as "message";''', con=engine)
    return df.to_dict(orient='records')

@server.get('/hello/database/timestamp',
            tags=["Dummy API"],
            summary="Timestamp from the database",
            description="DB")
async def from_db():
    df = pd.read_sql('''SELECT CURRENT_TIMESTAMP as "realtime_data";''', con=engine)
    return df.to_dict(orient='records')

class load_filename(BaseModel):
    file_name: str 

#Load CSV Example
@server.post('/data/load/csv/', 
        tags=['Data Load'], 
        summary="Loads CSV Data",
        description="Receives CSV Filename and Uploads to PostgresDB")
async def load_csv_data(payload: load_filename):
    file_name = payload.file_name
    xls = pd.ExcelFile(f'./data/{file_name}')
    for table_name in xls.sheet_names:
        df = pd.read_excel(f'./data/{file_name}', sheet_name=table_name)
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    return f"Loaded {file_name}"

#Load Excel Example
@server.post('/data/load/excel/', 
        tags=['Data Load'], 
        summary="Loads Excel Data",
        description="Receives Excel Filename and Uploads to PostgresDB")
async def load_excel_data(payload: load_filename):
    file_name = payload.file_name
    xls = pd.ExcelFile(f'./data/{file_name}')
    for table_name in xls.sheet_names:
        df = pd.read_excel(f'./data/{file_name}', sheet_name=table_name)
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    return f"Loaded {file_name}"

server.mount("/src/", StaticFiles(directory="templates/ar_src"), name="static")
server.mount("/ar_models/", StaticFiles(directory="templates/ar_assets"), name="static")

templates = Jinja2Templates(directory="templates")

@server.get("/ar/", response_class = HTMLResponse, 
        tags=['Data Visualization'], 
        summary="AR HTML",
        description="Augmented Reality Test")
def ar(request:Request):
    return templates.TemplateResponse("ar.html", {"request": request})


##################################################
# Realtime Websockets
##################################################

@server.websocket("/timer")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await asyncio.sleep(0.1)
        payload = pd.read_sql('''SELECT CURRENT_TIMESTAMP as "realtime_data";''', con=engine).to_json(orient='records')
        await websocket.send_json(payload)

@server.websocket("/message")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

##################################################
# Beginning of Dash app
##################################################

# Keep this out of source code repository - save in a file or a database
VALID_USERNAME_PASSWORD_PAIRS = {
    'hello': 'world'
}

app = dash.Dash(__name__, routes_pathname_prefix="/", external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True
app.head = [
    html.Link(
        href=app.get_asset_url('favicon.ico'),
        rel='icon'
    ),
]
app.title = 'Dashboard'
navbar = dbc.Navbar(
    children=[
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=app.get_asset_url('bah_full_logo.png'), height="35px", style={'padding': '0px 20px'})),
                    dbc.Col(dbc.NavbarBrand("Firefly", className="ml-2")),
                ],
                align="center",
            ),
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
    ],
    color="#01807e",
    dark=True,
    sticky="top"
)

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

def generate_card(title, long_title, value, pct_change):
    if pct_change > 0:
        pct_direction="▲"
        pct_class="card-diff-up"
    elif pct_change < 0:
        pct_direction="▼"
        pct_class="card-diff-down"
    else:
        pct_direction=""
        pct_class="card-diff-no-change"

    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4(f"{title}", className="card-title"),
                    html.P(
                        f"{long_title}",
                        className="card-target",
                    ),
                    html.P(
                        f"{value}",
                        className="card-value",
                        id=f"{title.replace(' ', '-').lower()}-card-text"
                    ),
                    html.Span(
                        f"{pct_direction}",
                        className=f"{pct_class}",
                    ),
                    html.Span(
                        f" {pct_change}% change",
                        className=f"{pct_class}",
                    ),
                ]
            ),
        ],
        className="shadow p-3 mb-5 bg-white rounded",
    )
    return card

#Card row
kpirow = html.Div(dbc.Row(
    id="card-deck-id",
    children= [
            dbc.Col(generate_card("ROI","Return On Investment",'$ '+format(10000000, ',.2f'), 2.0)),
            dbc.Col(generate_card("Total","Total Investment",'$ '+format(10000000, ',.2f'), 1.0)),
            dbc.Col(generate_card("Number","Investment Volume",20, 1.0)),
    ],
    style={'padding': '25px'}
    )
    )

#Sankey Example
sankey_fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = ["A1", "A2", "B1", "B2", "C1", "C2"],
      color = "blue"
    ),
    link = dict(
      source = [0, 1, 0, 2, 3, 3], # indices correspond to labels, eg A1, A2, A1, B1, ...
      target = [2, 3, 3, 4, 4, 5],
      value = [8, 4, 2, 8, 4, 2]
  ))])

sankey_fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)

sankey_row = html.Div([
    dcc.Graph(figure=sankey_fig)
])

#Map Example
us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")
map_fig = px.scatter_mapbox(us_cities, lat="lat", lon="lon", hover_name="City", hover_data=["State", "Population"],
                        color_discrete_sequence=["fuchsia"], zoom=3, height=600)
map_fig.update_layout(mapbox_style="open-street-map")

map_row = html.Div([
    dcc.Graph(figure=map_fig)
])

#bar chart example
animals=['giraffes', 'orangutans', 'monkeys']

bar_fig = go.Figure(data=[
    go.Bar(name='SF Zoo', x=animals, y=[20, 14, 23]),
    go.Bar(name='LA Zoo', x=animals, y=[12, 18, 29])
])

bar_row = html.Div([
    dcc.Graph(figure=bar_fig)
])
#####

app.layout = html.Div(
children=[
    navbar,
    kpirow,
    sankey_row,
    map_row,
    bar_row
    ]
)
      
server.mount("/", WSGIMiddleware(app.server))

if __name__ == "__main__":
    uvicorn.run("app:server", host="0.0.0.0", port=80, log_level="info", reload=True)
