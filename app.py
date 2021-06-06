# Load packages used in dashboard
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input
#from jupyter_dash import JupyterDash # for Jupiter Notebook


# Load dataset and dataframes
#data = pd.read_excel("DV_Group8_Project2.xlsx") #for excel format
data = pd.read_csv("DV_Group8_Project2.csv", sep=";")
data.sort_values("Year", inplace=True)


# Add Transformed Variables
#data['Pop_scaled']=(data['Population']*1000).astype('int64') 


# Setup the style from the link
external_stylesheets = [{"href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet"}]


# Embed style to the dashabord

    #for Jupiter Notebook (development mode):
#app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

    #for Server deploy:
app =  dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.title = "Human (d)Evolution"

    # Setup Headers
Header1=html.H1(children="Country analytics", className="header-title")
Header2=html.P(children="Analyze historical behavior of",className="header-description")
Header3=html.P(children="Population, GDP per Capita and CO2 emissions across time",className="header-description")

    # Setup Filters
Filter1=html.Div(children=[html.Div(children="Country", className="menu-title"),
                        dcc.Dropdown(id="country-filter",
                            options=[
                                {"label": country, "value": country} 
                                for country in np.sort(data.Country.unique())],
                            value="United States",
                            clearable=False,
                            className="dropdown")])

Filter2=html.Div(children=[html.Div(children="Year (start)",className="menu-title"),
                         dcc.Dropdown(id="year-start",
                            options=[{"label": year, "value": year}
                                for year in np.sort(data.Year.unique())],
                            value=data.Year.min(),
                            clearable=False,
                            searchable=False,
                            className="dropdown")])

Filter3=html.Div(children=[html.Div(children="Year (end)",className="menu-title"),
                         dcc.Dropdown(id="year-end",
                            options=[{"label": year, "value": year}
                                for year in np.sort(data.Year.unique())],
                            value=data.Year.max(),
                            clearable=False,
                            searchable=False,
                            className="dropdown",)])

    # Setup Graphs layout
Graph1=html.Div(children=dcc.Graph(id="population-chart", config={"displayModeBar": False}), 
                style={'width': '33%', 'display': 'inline-block'}, className="card")

Graph2= html.Div(children=dcc.Graph(id="gdp-chart", config={"displayModeBar": False}),
                  style={'width': '33%', 'display': 'inline-block'}, className="card")

Graph3= html.Div(children=dcc.Graph(id="co2-chart", config={"displayModeBar": False}),
                  style={'width': '33%', 'display': 'inline-block'}, className="card")

Graph4= html.Div(children=dcc.Graph(id="summary-chart", config={"displayModeBar": False}), className="card")


    # Setup rows layout
row1 = html.Div(children=[Header1, Header2, Header3],className="header")
row2 = html.Div(children=[Filter1, Filter2, Filter3],className="menu")
row3 = html.Div(children=[Graph4], className="wrapper")
row4 = html.Div(children=[Graph1, Graph2, Graph3], className="wrapper")

    # Apply layout
app.layout = html.Div(children=[row1,row2,row3, row4])


# Setup App
@app.callback([Output("population-chart", "figure"), Output("gdp-chart", "figure"), Output("co2-chart", "figure"), 
               Output("summary-chart", "figure")],
              [Input("country-filter", "value"),Input("year-start", "value"), Input("year-end", "value")])

    # Aplly filters
def update_charts(country, year_start, year_end):
    mask = (
        (data.Country == country)
        & (data.Year >= year_start)
        & (data.Year <= year_end)
    )
    
    mask_summary = (
        (data.Year >= year_start)
        & (data.Year <= year_end)
    )
    
    filtered_data = data.loc[mask, :]
        
    filtered_data_summary= data.loc[mask_summary, :]
    
    data_summary = filtered_data_summary.groupby(['Country','Region']).agg(
        Population_max=('Population',max),GDP_per_Capita_tot=('GDP per Capita',sum), CO2_tot=('CO2',sum))
    data_summary = data_summary.reset_index()

    x=data_summary.loc[data_summary['Country']==country]['Population_max']
    y=data_summary.loc[data_summary['Country']==country]['GDP_per_Capita_tot']
    x_input=x.iloc[0] # selected country coordenates for highlight
    y_input=y.iloc[0] # selected country coordenates for hughlight
    
    # Setup Graphs
    population_chart_figure = {
        "data": [
            {
                "x": filtered_data["Year"],
                "y": filtered_data["Population"],
                "type": "lines",
                "hovertemplate": "%{y:,.0f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {"text": "Population","x": 0.05,"xanchor": "left"},
            "xaxis": {"title": "Year","fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#17B897"],
        },
    }

    gdp_chart_figure = {
        "data": [
            {
                "x": filtered_data["Year"],
                "y": filtered_data["GDP per Capita"],
                "type": "lines",
                "hovertemplate": "USD %{y:,.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {"text": "GDP per Capita", "x": 0.05, "xanchor": "left"},
            "xaxis": {"title": "Year","fixedrange": True},
            "yaxis": {"tickprefix": "USD ","fixedrange": True},
            "colorway": ["blue"],
        },
    }
    
    co2_chart_figure = {
        "data": [
            {
                "x": filtered_data["Year"],
                "y": filtered_data["CO2"],
                "type": "lines",
                "hovertemplate": "%{y:,.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {"text": "CO2 Emissions", "x": 0.05, "xanchor": "left"},
            "xaxis": {"title": "Year","fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }     
    
    summary_chart_figure = px.scatter(
        data_summary, x="Population_max", y="GDP_per_Capita_tot",size="CO2_tot",color="Region",
        hover_name="Country",log_x=True, size_max=60, 
        labels=dict(Population_max="Population (max.)", GDP_per_Capita_tot="GDP per Capita (acum.)",
                    CO2_tot="CO2 emissions (acum.)"))
    
    summary_chart_figure.update_layout(title='Accumulated CO2 emissions across time')
    
    
    summary_chart_figure.add_vline(x=x_input, line_color="green", line_width=3, line_dash="dot") # Highlight select country
    
    summary_chart_figure.add_hline(y=y_input, line_color="green", line_width=3, line_dash="dot") # Highlight select country
    
    
    return population_chart_figure, gdp_chart_figure, co2_chart_figure, summary_chart_figure


# Publish App
if __name__ == "__main__":
    app.run_server(debug=True)