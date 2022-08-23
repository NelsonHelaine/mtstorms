pip install import dash
from dash.dependencies import Input, Output, State
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.html.Div import Div
from dash.exceptions import PreventUpdate
import numpy as np
from numpy import nan
from pandas.io.formats import style
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pandas import DataFrame
import numpy as np
from dash import dash_table
import functions.parseFilesWeb as parseFiles
import functions.fitCumulant2ndOrderDash as fitCumulant2ndOrder
import functions.fitNNLS as fit_NNLS
import functions.internalSettingsWeb as internalSettings
#import orjson

#external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]#loading of the external stylesheet for webpage (CSS)
#external_stylesheets=[dbc.themes.BOOTSTRAP],
meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}]


internalSettings.init()#initialization of various variables
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}])

server = app.server
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)#app definition with the external stylesheet
#variable initialization:
#columns_data = ["File name", "Record", "Sample", "T (°C)", "Viscos.", "Angle (°)", "RI", "Time", "Gamma"]#names of the dataTable columns
#columns_Fit=["Sample", "Record", "Method", "Rh", "q", "D", "Time", "Fit", "Residues"]
columns_data = internalSettings.columns_data
#columns_Fit = internalSettings.columns_Fit
global dicData
dicData = [[nan, nan, nan, nan, nan, nan, nan, nan, nan]]#pre allocation of the dicData table which will store all loaded data
dicData = DataFrame(dicData,columns=internalSettings.columns_data)#generating a dataframe from the data
dicData = dicData.to_dict("records")#data transformation to dictionary
global dicFit
dicFit = [[nan, nan, nan, nan, nan, nan, nan, nan, nan]]#pre allocation of the dicData table which will store all loaded data
dicFit = DataFrame(dicFit,columns=internalSettings.columns_Fit)#generating a dataframe from the data
dicFit = dicFit.to_dict("records")#data transformation to dictionary
print("This how dicFit looks at start")
print(dicFit)

"""
Navbar (top bar) definition
"""
navbar = dbc.NavbarSimple(
    children=[
        #dbc.Button("Tools & parameters", outline=True, color="secondary", className="mr-1", id="btn_sidebar")
    ],
    #brand="Brand",
    #brand_href="#",
    color="white",
    dark=True,
    fluid=True,
    links_left=True
)

"""
Sidebar styling
"""
# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "height": "100%",
    "z-index": 1,
    "overflow-x": "hidden",
    "transition": "all 0.5s",
    "padding": "0rem 0.5rem",
    "background-color": "#ffffff",
}

SIDEBAR_HIDEN = {
    "position": "fixed",
    "top": 0,
    "left": "-16rem",
    "bottom": 0,
    "width": "16rem",
    "height": "100%",
    "z-index": 1,
    "overflow-x": "hidden",
    "transition": "all 0.5s",
    "padding": "0rem 0.5rem",
    "background-color": "#ffffff",
}


"""
Content styling
"""
# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "transition": "margin-left .5s",
    "margin-left": "16rem",
    "margin-right": "0rem",
    "padding": "0rem 0rem",
    "background-color": "#ffffff",
}

CONTENT_STYLE1 = {
    "transition": "margin-left .5s",
    "margin-left": "0.5rem",
    "margin-right": "0.5rem",
    "padding": "0rem 0rem",
    "background-color": "#ffffff",
}

"""
Tabs styling
"""

TABS_STYLES = {
    'height': '44px'
}
TAB_STYLE = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
    'fontSize':'70%'
}

TAB_SELECTED_STYLE = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px',
    'fontSize':'70%'
}

sidebar = html.Div(
    [
        html.Div(children=[
        dcc.Tabs(id="tabs-fitting", value='tabs_fitting', children=[
        dcc.Tab(label='Main parameters', value='tab-mainparams',style=TAB_STYLE,selected_style=TAB_SELECTED_STYLE,
            children=[
            html.Div(children=[
                html.Div([dcc.Dropdown(
                    id='fit-method-select',
                    options=[
                        {'label':'Cumulants 2nd order','value':'cu2nd'},
                        {'label':'Cumulants 3rd order','value':'cu3rd'},
                        {'label':'NNLS','value':'nnls'},
                        {'label':'SBL','value':'sbl'},
                        {'label':'REPES','value':'repes'}
                        ],
                    placeholder="Select a fitting method",
                    style={'display':'inline-block',
                        'width':'100%'}
                )],style={'display':'inline-block',
                                'width':'100%'}),
                html.Div([dcc.Dropdown(
                    id='weighting-select',
                    options=[
                        {'label':'1','value':'1'},
                        {'label':'1\sqrt(g)','value':'1/rac(g)'},
                        {'label':'g','value':'g'},
                        ],
                    placeholder="Select a weighting",
                    style={'display':'inline-block',
                        'width':'100%'}
                )],style={'display':'inline-block',
                                'width':'100%'}),
                html.Div([dcc.Dropdown(
                    id='geometry-select',
                    options=[
                        {'label':'Sphere','value':'sphere'},
                        {'label':'Ellispoid','value':'ellipsoid'},
                        {'label':'Nanorod (geometry)','value':'nanorod_geometry'},
                        {'label':'Nanorod (Stick)','value':'nanorod_stick'},
                        {'label':'Nanorod (Tirado)','value':'nanorod_tirado'},
                        {'label':'Nanorod (Broersma)','value':'nanorod_broersma'},
                        {'label':'Wormlike','value':'wormlike'},
                        ],
                    placeholder="Select a geometry",
                    style={'display':'inline-block',
                        'width':'100%'}
                )],style={'display':'inline-block',
                                'width':'100%'}),
                html.Div([dcc.Dropdown(
                    id='model-select',
                    options=[
                        {'label':'Small sphere (Rayleigh)','value':'small_sphere_rayleigh'},
                        {'label':'Vesicle (RGD model)','value':'vesicle_rgd'},
                        {'label':'Sphere (Mie)','value':'sphere_mie'},
                        {'label':'Coated sphere (Mie)','value':'coated_sphere_mie'},
                        {'label':'Micelle + Vesicle (Mie)','value':'micelle_vesicle_mie'}
                        ],
                    placeholder="Select a model",
                    style={'display':'inline-block',
                        'width':'100%'}
                )],style={'display':'inline-block',
                                'width':'100%'}),
                html.Br(),
                html.Br(),
                html.Div([
                    html.Div([
                        html.I('Alpha parameter :',style={'fontSize':'80%'}),
                        dcc.Input(id="input-alpha-param", type="number", placeholder="", style={
                            'marginLeft':'4%',
                            'fontSize':'80%',
                            'marginRight':'2%',
                            'width':'20%',
                            'height':'80%'}),
                        html.Br(),
                        html.I('Range :',style={'fontSize':'80%','marginLeft':'0%','marginTop':'2%'}),
                        dcc.Input(id="input-range", type="number", placeholder="", style={
                            'marginLeft':'4%',
                            'marginTop':'2%',
                            'fontSize':'80%',
                            'marginRight':'1%',
                            'width':'20%',
                            'height':'80%'})],style={'marginBottom':'2%'}),
                    html.Div([
                        html.I('Classes :',style={'fontSize':'80%'}),
                        dcc.Input(id="input-classes", type="number", placeholder="", style={
                            'marginLeft':'4%',
                            'fontSize':'80%',
                            'marginRight':'5%',
                            'width':'20%',
                            'height':'80%'}),
                        html.Br(),
                        html.I('Expansion :',style={'fontSize':'80%','marginLeft':'0%','marginTop':'2%'}),
                        dcc.Input(id="input-expansion", type="number", placeholder="", style={
                            'marginLeft':'4%',
                            'fontSize':'80%',
                            'marginRight':'1%',
                            'marginTop':'2%',
                            'width':'20%',
                            'height':'80%'})
                            ],style={'width':'100%','marginTop':'2%'})
                        ])
            ],style={'display':'inline-block','width':'100%','marginTop':'10%'})
            ]),
        dcc.Tab(label='Anisotropic particles', value='tab-anisotropic',style=TAB_STYLE,selected_style=TAB_SELECTED_STYLE,
        children=[
        html.Div([dcc.Dropdown(
            id='fixed-param-select',
            options=[
                {'label':'L/d constant','value':'L/d_constant'},
                {'label':'d constant (nm)','value':'d_constant'},
                {'label':'L = a+b*d','value':'L_a+b*d'},
                ],
            placeholder="Fixed parameter",
            style={'display':'inline-block',
                'width':'100%',
                'fontSize':'80%'}
        )],style={'display':'inline-block',
                        'width':'100%'}),
        html.Br(),
        html.Br(),
        html.Div([html.I('L/d = ',style={'fontSize':'80%','marginLeft':'5%'}),
        dcc.Input(id="input-L/d", type="number", placeholder="", style={
            'marginLeft':'4%',
            'fontSize':'80%',
            'marginRight':'0%',
            'width':'50%',
            'height':'80%',
            'horizontalAlign':'middle'})
            ],style={'width':'80%','horizontalAlign':'middle'})
        ]),
        dcc.Tab(label='Balistic correction', value='tab-balistic',style=TAB_STYLE,selected_style=TAB_SELECTED_STYLE,
            children=[
            daq.ToggleSwitch(
                id='balistic_on_off',
                size=30,
                label=('Off/On'),
                value=False,
                labelPosition='top',
                style={'fontSize':'80%',
                        'marginTop':'2vh'}
                ),
            html.Br(),
            html.Div([
                html.I('Speed (cm/s)',style={'fontSize':'80%'}),
                dcc.Input(id="input-speed", type="number", placeholder="", style={
                    'marginLeft':'4%',
                    'fontSize':'80%',
                    'marginRight':'2%',
                    'width':'30%',
                    'height':'80%'}),
                html.Br(),
                html.Br(),
                html.I('Geometry',style={'fontSize':'80%','marginLeft':'0%'}),
                dcc.Input(id="input-geometry", type="number", placeholder="", style={
                    'marginLeft':'4%',
                    'fontSize':'80%',
                    'marginRight':'1%',
                    'width':'45%',
                    'height':'80%'})],style={'marginBottom':'2%'})
            ])
            ],style=TABS_STYLES),
        html.Div(id='tabs-fitting-params')
        ]),
                                html.Div([
                                    html.Div([dcc.Dropdown(
                                        id='correlbkg-select',
                                        options=[{'label':'>=0','value':'val>=0'},
                                            {'label':'>=-0.2','value':'val>=-0.2'},
                                            {'label':'=0','value':'val=0'}],
                                        placeholder="Correlogram background",
                                        style={'width':'100%','fontSize':'90%'}
                                    )],style={'width':'100%'}),
                                    html.Br(),
                                    html.Div([
                                        dbc.Button("Fit", outline=False, color="danger", className="mr-1", id="fit_button",
                                        style={'marginTop':'1vh',
                                            'marginBottom':'1vh',
                                            'padding':'0.2vh',
                                            'horizontal-alignment':'middle',
                                            'height':'2vw',
                                            'width':'4vw',
                                            'fontSize':'0.8rem'})
                                        ],style={'display':'flex','justify-content':'center'})],style={'marginLeft':'1%','marginRight':'1%','marginTop':'10%'})
    ],
    id="sidebar",
    style=SIDEBAR_STYLE,
)



#LAYOUT

content = html.Div(
                id = 'page-content',
                style=CONTENT_STYLE,
                children=[
                #Title image


            #second row
                #datatable
            html.Div(style={'display':'flex','flex-direction':'row'},children=[
                html.Div(children=[
                    html.Div(style={},children=[
                    html.Div([
                    dcc.Upload(
                        id="upload-data",#upload button id
                        children=html.Button(children=[html.Img(src=app.get_asset_url('Data_add.svg'),style={'width':'100%'})],
                                            style={'verticalAlign':'middle','borderStyle':'solid','borderWidth':'1px'}),#drag and drop part
                        style={#button styling
                            #"width": "100%",
                            "height": "2vh",
                            "lineHeight": "100%",
                            "borderWidth": "1px",
                            "borderStyle": "none",
                            "borderRadius": "0px",
                            "textAlign": "center",
                            "margin-left": "1%",
                            'margin-right':'1%',
                            'margin-bottom':'0%',
                            'padding':'0%',
                            'horizontalAlign':'center',
                            'verticalAlign':'center',
                            'hoverInfo':'Data files import',
                            'display':'inline-block'

                            },
                        multiple=True
                        )],style={'display':'inline-block','width':'3.52vw','marginRight':'1%'}),
                    html.Button(id='data_seldes_all',children=[html.Img(src=app.get_asset_url('Data_seldes.svg'),style={'width':'100%'})],
                                        style={'verticalAlign':'middle',
                                                'borderStyle':'solid',
                                                'borderWidth':'1px',
                                                'width':'3.3vw',
                                                'marginRight':'1%',
                                                'display':'inline-block'}),
                    html.Button(children=[html.Img(src=app.get_asset_url('Seldes_fit.svg'),style={'width':'100%'})],
                                        style={'verticalAlign':'middle',
                                                'borderStyle':'solid',
                                                'borderWidth':'1px',
                                                'width':'3.3vw',
                                                'marginRight':'1%',
                                                'display':'inline-block'}),
                    html.Button(id='data_suppr',children=[html.Img(src=app.get_asset_url('Data_suppr.svg'),style={'width':'100%'})],
                                        style={'verticalAlign':'middle',
                                                'borderStyle':'solid',
                                                'borderWidth':'1px',
                                                'width':'3.28vw',
                                                'marginRight':'1%',
                                                'display':'inline-block'}),
                    html.Button(children=[html.Img(src=app.get_asset_url('Del_all_fits.svg'),style={'width':'100%'})],
                                        style={'verticalAlign':'middle',
                                                'borderStyle':'solid',
                                                'borderWidth':'1px',
                                                'width':'3.4vw',
                                                'marginRight':'1%',
                                                'display':'inline-block'}),
                    html.Button(children=[html.Img(src=app.get_asset_url('Save_storms.svg'),style={'width':'100%'})],
                                        style={'verticalAlign':'middle',
                                                'borderStyle':'solid',
                                                'borderWidth':'1px',
                                                'width':'2.32vw',
                                                'marginRight':'1%',
                                                'display':'inline-block'}),
                    html.Button(children=[html.Img(src=app.get_asset_url('Export_xls.svg'),style={'width':'100%'})],
                                        style={'verticalAlign':'middle',
                                                'borderStyle':'solid',
                                                'borderWidth':'1px',
                                                'width':'2.32vw',
                                                'marginRight':'1%',
                                                'display':'inline-block'}),
                    html.Button(children=[html.Img(src=app.get_asset_url('Load_storms.svg'),style={'width':'100%'})],
                                        style={'verticalAlign':'middle',
                                                'borderStyle':'solid',
                                                'borderWidth':'1px',
                                                'width':'2.32vw',
                                                'marginRight':'1%',
                                                'display':'inline-block'}),
                    dbc.Button("Fit options", outline=False, color="warning", className="mr-1", id="btn_sidebar",
                    style={'marginTop':'1vh',
                        'marginBottom':'1vh',
                        'marginRight':'0.5vh',
                        'padding':'0.2vh',
                        'horizontal-alignment':'middle',
                        'height':'2vw',
                        'fontSize':'0.8rem'}),
                    dbc.Button("Fit", outline=False, color='danger', className="mr-1", id="btn_fit_navbar",
                    style={'marginTop':'1vh',
                    'marginBottom':'1vh',
                    'padding':'0.4vh',
                    'horizontal-alignment':'middle',
                    'height':'2vw',
                    'width':'4vw',
                    'fontSize':'0.8rem'}),
                    dash_table.DataTable(
                        id="datatable-interactivity",#id datatable

                        columns=[{"name": i, "id": i} for i in internalSettings.columns_data],#columns creation

                        #data=[],
                        style_table={'height':'40vh','width': '100%', 'overflowY':'auto', 'overflowX':'auto','display': 'inline-block','vertical-alignment':'top'},#styling of the table
                        #fixed_rows={'headers': True},
                        style_cell_conditional=[
                            {'if': {'column_id': 'File name'},
                                'width': '15%'},
                            {'if': {'column_id': 'Record'},
                                'width': '8%'},
                            {'if': {'column_id': 'Sample'},
                                'width': '15%'},
                            {'if': {'column_id': 'T (°C)'},
                                'width': '8%'},
                            {'if': {'column_id': 'Viscos.'},
                                'width': '10%'},
                            {'if': {'column_id': 'Angle (°)'},
                                'width': '12%'},
                            {'if': {'column_id': 'RI'},
                                'width': '6%'},
                            {'if': {'column_id': 'Time'},
                                'width': '8%'},
                            {'if': {'column_id': 'g(tau)'},
                                'width': '8%'}],
                        editable=True,
                        style_cell={
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'maxWidth': 0,
                            'fontSize':'70%'
                        },

                        style_header={'fontSize':'70%'},
                        filter_action="native",

                        sort_action="native",
                        sort_mode="multi",
                        column_selectable="single",
                        row_selectable="multi",
                        row_deletable=True,
                        selected_columns=[],
                        selected_rows=[],
                        page_action="none",

                    )]),
                    html.Div(style={},children=[
                    dash_table.DataTable(
                        id="fit-table-interactivity",#id datatable
                        columns=[{"name": i, "id": i} for i in internalSettings.columns_Fit],#columns creation
                        #data=[],
                        style_table={'height':'50vh','width': '100%', 'overflowY':'auto','overflowX':'auto','display':'inline-block','vertical-alignment':'top'},#styling of the table
                        #fixed_rows={'headers': True},
                        style_cell_conditional=[
                            {'if': {'column_id': 'Sample'},
                                'width': '15%'},
                            {'if': {'column_id': 'Record'},
                                'width': '8%'},
                            {'if': {'column_id': 'Method'},
                                'width': '15%'},
                            {'if': {'column_id': 'Rh'},
                                'width': '8%'},
                            {'if': {'column_id': 'q'},
                                'width': '10%'},
                            {'if': {'column_id': 'D'},
                                'width': '12%'},
                            {'if': {'column_id': 'Time'},
                                'width': '6%'},
                            {'if': {'column_id': 'Fit'},
                                'width': '8%'},
                            {'if': {'column_id': 'Residues'},
                                'width': '8%'}],
                        editable=True,
                        style_cell={
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'maxWidth': 0,
                            'fontSize':'70%'
                        },
                        style_header={'overflow':'hidden','fontSize':'70%'},
                        filter_action="native",
                        sort_action="native",
                        sort_mode="multi",
                        column_selectable="single",
                        row_selectable="multi",
                        row_deletable=True,
                        selected_columns=[],
                        selected_rows=[],
                        page_action="none",

                    )]),
                    #dcc.Graph(id='2Dplot',style={'width':'45%','display':'flex'})
                    ],style={'height':'100%','width':'50%','verticalAlign':'top'}),
                    #graph
                    html.Div(children=[
                        html.Div([
                                dcc.Graph(id='2Dplot',style={'height':'39vh','marginTop':'1vh','marginBottom':'1vh'})
                            ]),
                        html.Div(children=[
                            dcc.Tabs(id="tabs-analysis", value='tab_analysis', children=[
                            dcc.Tab(label='Distribution', value='tab-distribution',style=TAB_STYLE,selected_style=TAB_SELECTED_STYLE),
                            dcc.Tab(label='\u0393=f(q\u00B2)', value='tab-gamma_fq2',style=TAB_STYLE,selected_style=TAB_SELECTED_STYLE),
                            dcc.Tab(label='Unselected data', value='tab-unselected-data',style=TAB_STYLE,selected_style=TAB_SELECTED_STYLE),
                            dcc.Tab(label='D = f(t)', value='tab-D_ft',style=TAB_STYLE,selected_style=TAB_SELECTED_STYLE),
                            dcc.Tab(label='D =f(T\u00B0)', value='tab-D_fT',style=TAB_STYLE,selected_style=TAB_SELECTED_STYLE),
                            ]),
                            html.Div(id='tabs-content-analysis')
                            ],style={'height':'50%'})
                    ],style={'height':'100%','width':'48%','verticalAlign':'top'})
                ]),
])


app.layout = html.Div(
    [
        dcc.Store(id='side_click'),
        dcc.Location(id="url"),
        #navbar,
        sidebar,
        content,
    ],
)


"""
CALLBACKS SECTION - manage program interactivity
"""
"""
Sidebar callback - opens sidebar when fit options button is clicked
"""
@app.callback(
    [
        Output("sidebar", "style"),
        Output("page-content", "style"),
        Output("side_click", "data"),
    ],

    [Input("btn_sidebar", "n_clicks")],
    [
        State("side_click", "data"),
    ]
)
def toggle_sidebar(n, nclick):
    if n:
        if nclick == "SHOW":
            sidebar_style = SIDEBAR_HIDEN
            content_style = CONTENT_STYLE1
            cur_nclick = "HIDDEN"

        else:
            sidebar_style = SIDEBAR_STYLE
            content_style = CONTENT_STYLE
            cur_nclick = "SHOW"
    else:
        sidebar_style = SIDEBAR_STYLE
        content_style = CONTENT_STYLE
        cur_nclick = 'SHOW'

    return sidebar_style, content_style, cur_nclick

"""
Analysis graphs callback - update analysis graphs when data/fits are selected in the datatables
"""
@app.callback(Output('tabs-content-analysis', 'children'),
              Input('tabs-analysis', 'value'),
              Input('fit-table-interactivity', 'derived_virtual_selected_rows'),
              Input('fit-table-interactivity', 'derived_virtual_data'))
def render_content(tab,derived_virtual_selected_rows,rowsFit):
    #dff = dicData #if rows is None else pd.DataFrame(rows)
    dffFit = dicFit if rowsFit is None else pd.DataFrame(rowsFit)
    print("this is dffFit")
    print(dffFit)
    #data=[]
    if tab == 'tab-distribution':
        print("this is dffFit 2")
        print(dffFit)
        layoutDistSize=go.Layout(xaxis={'title': 'Size (nm)','type':'log'},
                        yaxis={'title': "Prob. (a.u.)"},
                        hovermode='closest',
                        showlegend=False,
                        margin=dict(l=0, r=0, t=0, b=0))
        figureDistSize = go.Figure(layout=layoutDistSize)
        for i in derived_virtual_selected_rows:
            print('this is dffFit 3')
            print(dffFit.iloc[i,7])
            figureDistSize.add_trace(go.Scattergl(x=dffFit.iloc[i,6],
                            y=dffFit.iloc[i,7],
                            mode='markers',
                            marker=dict(color='red',opacity=0.6)))
        layoutDistResidues=go.Layout(xaxis={'title': 'Time (\u03bc)','type':'log'},
                        yaxis={'title': 'res'},
                        hovermode='closest',
                        showlegend=False,
                        margin=dict(l=0, r=0, t=0, b=0))

        figureDistResidues = go.Figure(layout=layoutDistResidues)
        #if len(derived_virtual_selected_rows) == 1:
        for i in derived_virtual_selected_rows:
            #print(dffFit.iloc[i,4])
            yRes=np.asarray(dffFit.iloc[i,8])
            yRes=yRes.tolist()
            #print(yRes)
            figureDistResidues.add_trace(go.Scattergl(x=dffFit.iloc[i,7],
                        y=yRes,
                        mode='markers',
                        marker=dict(color='red',opacity=0.6)))
        return html.Div([
            dcc.Graph(
                id='dist-1',
                figure=figureDistSize,
                style={'width':'100%',
                    'height':'20vh'}
            ),

            dcc.Graph(
                id='dist-2',
                figure=figureDistResidues,
                style={'width':'100%',
                    'height':'20vh'}
            ),
            dcc.Graph(
                id='dist-3',
                figure={
                    'data': [{
                        'x': [1, 2, 3],
                        'y': [3, 1, 2],
                        'type': 'scatter'
                    }],
                    "layout": {
                        "xaxis": {
                            'type': 'linear',
                            "automargin": True,
                            'title':"Time (\u03bcs)"
                        },
                        "yaxis": {
                            "automargin": True,
                            "title": {"text": "\u0393 (a.u.)"}
                        },
                        "height": '10vh',
                        "margin": {"t": 0, "l": 10, "r": 10},
                    }
                },style={'width':'100%',
                    'height':'20vh',
                    'marginTop':'0vh',
                    'marginBottom':'0vh',}
            )
            ])
    elif tab == 'tab-gamma_fq2':
        return html.Div([
            dcc.Graph(
                id='graph-2-tabs',
                figure={
                    'data': [{
                        'x': [1, 2, 3],
                        'y': [5, 10, 6],
                        'type': 'bar'
                    }]
                }
            )
        ])

"""
callback importing data
"""
@app.callback(
    Output("datatable-interactivity", "data"),
    Input("data_suppr", "n_clicks"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
)
def update_output(n_clicks,list_of_contents, list_of_names, list_of_dates):
    print(list_of_names)
    columns_data = internalSettings.columns_data
    dicData=[]
    trigger=[]
    j=1
    ctx = dash.callback_context
    if ctx.triggered:
        trigger = (ctx.triggered[0]['prop_id'].split('.')[0])
        if trigger == "data_suppr":
            print('suppr')
            data = pd.DataFrame().to_dict('records')
            return data
        elif trigger== "upload-data":
            print("upload")
            if list_of_contents is not None:
                #print('upload')
                for i in range(0,np.shape(list_of_names)[0]):
                    c, n, d = list(zip(list_of_contents, list_of_names, list_of_dates))[i]
                    dataTemp=parseFiles.openDataFile(c, n, d).iloc[:, :]
                    dataTemp.columns=columns_data
                    dataTemp=dataTemp.to_dict("records")
                    dicData=dicData+dataTemp
                try:
                    print("upload")
                    return dicData
                except:
                    pass
            else:
                dicData = [[nan, nan, nan, nan, nan, nan, nan, nan, nan]]
                dicData = DataFrame (dicData,columns=columns_data)
                dicData = dicData.to_dict("records")
                try:
                    return dicData
                except:
                    pass
        else:
            pass
    else:
        pass

"""
Select/Deselect all rows in data table
"""
@app.callback(
    [Output('datatable-interactivity', 'selected_rows')],
    [Input('data_seldes_all', 'n_clicks'),],
    [Input('datatable-interactivity','derived_virtual_selected_rows'),],
    [Input('datatable-interactivity','derived_virtual_row_ids'),],
    [State('datatable-interactivity','derived_virtual_data'),],
)
def select_deselect(data_seldes_all, selected_rows, derived_virtual_selected_rows, derived_virtual_row_ids):
    ctx = dash.callback_context
    trigger = (ctx.triggered[0]['prop_id'].split('.')[0])

    if trigger == 'data_seldes_all':
        print('Nb de lignes selectionnées')
        print(len(selected_rows))
        print('Nb de lignes')
        print(len(derived_virtual_row_ids))
        tuple([i for i in range(len(derived_virtual_row_ids))])
        if selected_rows is None:
            selected_rows=[[]]#return [[i for i in range(len(derived_virtual_row_ids))]]
        else:
            if (len(selected_rows)==len(derived_virtual_row_ids)):
                selected_rows=[[]]
            else:
                selected_rows=[[i for i in range(len(derived_virtual_row_ids))]]
    else:
        if derived_virtual_row_ids is None :
            selected_rows=[[]]
        else :
            #selected_rows=[[i for i in range(len(selected_rows))]]
            selected_rows=[[i for i in selected_rows]]

    return(selected_rows)

"""
callback main graph  interactive plotting
"""
@app.callback(
    Output('2Dplot', 'figure'),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows"),
    Input('fit-table-interactivity', 'derived_virtual_data'),
    Input('fit-table-interactivity', 'derived_virtual_selected_rows'))
def update_graphs(rows, derived_virtual_selected_rows,rowsFit, derived_virtual_selected_rowsFit):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncrasy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []
    if derived_virtual_selected_rowsFit is None:
        derived_virtual_selected_rowsFit = []

    dff = dicData if rows is None else pd.DataFrame(rows)
    dffFit = dicFit if rowsFit is None else pd.DataFrame(rowsFit)
    #print(dff)
    data=[]
    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]

    layout =  go.Layout(xaxis={'title': 'Time (\u03bcs)','type':'log'},
                    yaxis={'title': "g (a.u.)"},
                    hovermode='closest',
                    showlegend=False,
                    margin=dict(l=0, r=0, t=0, b =0))
    figure = go.Figure(layout=layout)
    for i in derived_virtual_selected_rows:
        figure.add_trace(go.Scattergl(x=dff.iloc[i,7],
                        y=dff.iloc[i,2],
                        mode='markers',
                        marker=dict(color='red',opacity=0.6)))

    for i in derived_virtual_selected_rowsFit:
        print(dffFit.iloc[i,7])
        figure.add_trace(go.Scattergl(x=dffFit.iloc[i,7],
                        y=dffFit.iloc[i,1],
                        mode='lines',
                        marker=dict(color='black',opacity=0.6)))

    return figure

"""
callback fit button (launch fit calculation)
"""
@app.callback(
    Output('fit-table-interactivity', 'data'),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows"),
    Input('fit_button','n_clicks'),
    Input('fit-method-select','value'),
    Input('weighting-select','value'),
    Input('geometry-select','value'),
    Input('model-select','value'),
    Input('input-alpha-param','value'),
    Input('input-range','value'),
    Input('input-classes','value'),
    Input('input-expansion','value'),
    Input('correlbkg-select','value'),
    Input('fixed-param-select','value'),
    Input('input-L/d','value'),
    Input('balistic_on_off','value'),
    Input('input-speed','value'),
    Input('input-geometry','value')
    )
def fit_table_interact(dataToFit,dataSelected,fitButtonClicked,
                        fitMethodValue,weightingValue,geometryValue,
                        modelValue,alphaParamValue,rangeValue,
                        classesValue,expansionValue,correlbkgValue,
                        fixedParamValue,inputLDValue,balisticOnOffValue,
                        speedValue,balGeometryValue):
    #columns_Fit=["Sample", "Record", "Method", "Rh", "q", "D", "Time", "Fit", "Residues"]


    ctx = dash.callback_context
    trigger = (ctx.triggered[0]['prop_id'].split('.')[0])
    print('above trigger')
    if trigger == 'fit_button':
        #print(fitMethodValue,weightingValue,geometryValue,
        #modelValue,alphaParamValue,rangeValue,
        #classesValue,expansionValue,correlbkgValue,
        #fixedParamValue,inputLDValue,balisticOnOffValue,
        #speedValue,balGeometryValue)
        print('trigger fit button')

        if fitMethodValue=='cu2nd':
            dicFit=pd.DataFrame(internalSettings.fitMainContainer).T
            print("dicFit 1")
            print(dicFit)

            print("dicFit 2")
            print(dicFit)
            dicFit=dicFit.to_dict("records")
            print('cumulants')
            fitTemp = fitCumulant2ndOrder.fit(dataToFit,dataSelected)
            fitTemp.columns=internalSettings.columns_Fit
            fitTemp=fitTemp.to_dict("records")
            dicFit=dicFit+fitTemp
        if fitMethodValue=='nnls':
            dicFit=pd.DataFrame(internalSettings.fitMainContainer).T
            print("dicFit NNLS")

            dicFit=dicFit.to_dict("records")
            fitTemp = fit_NNLS.fit_NNLS(dataToFit,dataSelected)
            #fitTemp.columns=internalSettings.columns_Fit
            #fitTemp=fitTemp.to_dict("records")
            #dicFit=dicFit+fitTemp

        try:
            print("Fit 1st")
            #print(dicFit)
            return dicFit

        except:
            pass

        else:
            try:
                return dicFit
            except:
                pass
    else:
        print("Fit check")
        #print(dicFit)
        try:
            return dicFit
        except:
            pass

if __name__ == "__main__":
    app.title="Multi STORMS web version 0.1"
    app.run_server(debug=False)
