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
    dcc.Dropdown(id='department-dropdown', placeholder="เลือกสาขา"),
    dcc.Dropdown(id='course-dropdown', placeholder="เลือกหลักสูตร"),
    html.Div(id='output_container', children=[]),
    html.Br(),
    dcc.Graph(id='map', style={'width': '30%'}),
    html.Div(id='text-box', style={'whiteSpace': 'pre-line'}) # Add this line for the text box
])

# Update department dropdown options based on the selected university
@app.callback(
    Output('department-dropdown', 'options'),
    Input('dropdown-selection', 'value')
)

def set_department_options(selected_university):
    filtered_df = df[df['uni'] == selected_university]
    departments = filtered_df['depart'].unique()
    return [{'label': dept, 'value': dept} for dept in departments]

# Update course dropdown options based on the selected depart
@app.callback(
    Output('course-dropdown', 'options'),
    Input('dropdown-selection', 'value'),
    Input('department-dropdown', 'value')
)

def set_course_options(selected_university, selected_department):
    filtered_df = df[(df['uni'] == selected_university) & (df['depart'] == selected_department)]
    course = filtered_df['course'].unique()
    return [{'label': cou, 'value': cou} for cou in course]

# Update graphs based on selections
@app.callback(
    [Output('output_container', 'children'),
     Output('map', 'figure'),
     Output('text-box', 'children')],
    [Input('dropdown-selection', 'value'),
     Input('department-dropdown', 'value'),
     Input('course-dropdown', 'value')]
)

def update_graphs(selected_university, selected_department, selected_course):
    container = f"The University chosen by user was: {selected_university}, Department: {selected_department}, Course: {selected_course}"

    dff = df[df["uni"] == selected_university]

    # Map
    map_fig = create_map(selected_university)
    
    map_fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color="PaleTurquoise"
    )

    # Extract fee and round data
    filtered_df = df[(df['uni'] == selected_university) & 
                     (df['depart'] == selected_department) & 
                     (df['course'] == selected_course)]
    if not filtered_df.empty:
        fee = filtered_df.iloc[0]['fee']
        round1 = filtered_df.iloc[0]['round1']
        round2 = filtered_df.iloc[0]['round2']
        round3 = filtered_df.iloc[0]['round3']
        round4 = filtered_df.iloc[0]['round4']
        text_box_content = (
            f"Fee: {fee}\n"
            f"Round 1: {round1}\n"
            f"Round 2: {round2}\n"
            f"Round 3: {round3}\n"
            f"Round 4: {round4}"
        )
    else:
        text_box_content = "No data available for the selected options."

    return container, map_fig, text_box_content

if __name__ == '__main__':
    app.run_server(debug=True)
