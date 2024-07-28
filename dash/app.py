import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import json
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

app = Dash(__name__)

# Load data
df = pd.read_csv("./data/engineer_data.csv")

with open('data/location_uni.json', 'r', encoding='utf-8') as f:
    unijson = json.load(f)

uni_coords = {}
for uni_name, coords in unijson.items():
    latitude = coords['latitude']
    longitude = coords['longitude']
    uni_coords[uni_name] = [latitude, longitude]

df['latitude'] = df['uni'].map(lambda x: uni_coords.get(x, [None, None])[0])
df['longitude'] = df['uni'].map(lambda x: uni_coords.get(x, [None, None])[1])

def create_map(university=None):

    dff = df[df['uni'] == university]
  
    fig = px.scatter_mapbox(
            dff,
            lat='latitude',
            lon='longitude',
            hover_name='uni',
            color_discrete_sequence=['red'],
            zoom=6,
            height=500,
            mapbox_style="carto-positron"
        )
    

    return fig

# App
app.layout = html.Div([
    html.H1("มหาวิทยาลัยที่เปิดรับคณะวิศวกรรมศาสตร์", style={'text-align': 'center'}),
    dcc.Dropdown(df.uni.unique(), 'มหาวิทยาลัยสงขลานครินทร์', id='dropdown-selection'),
    html.Div(id='output_container', children=[]),
    html.Br(),
    dcc.Graph(id='map', style={'width': '30%'}),
])

@app.callback(
    [Output('output_container', 'children'),
     Output('map', 'figure')],
    [Input('dropdown-selection', 'value')]
)
def update_graphs(selected_university):
    container = f"The University chosen by user was: {selected_university}"

    dff = df[df["uni"] == selected_university]

    # Map
    map_fig = create_map(selected_university)
    
    map_fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color="PaleTurquoise"
    )

    return container, map_fig

if __name__ == '__main__':
    app.run_server(debug=True)
