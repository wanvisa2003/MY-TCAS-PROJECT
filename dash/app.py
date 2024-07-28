
import pandas as pd
import plotly.express as px
import json
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

app = Dash(__name__)

# Load data
df = pd.read_csv("./data/engineer_data.csv")

# Rename columns to match the expected names
df = df.rename(columns={
    'uni': 'มหาวิทยาลัย',
    'major': 'ชื่อคณะ',
    'depart': 'สาขาวิชา',
    'course': 'ชื่อหลักสูตร',
    'eng_name': 'ชื่อหลักสูตรภาษาอังกฤษ',
    'fee': 'ค่าธรรมเนียมต่อหลักสูตร',
    'round1': 'รอบ 1 Portfolio',
    'round2': 'รอบ 2 Quota',
    'round3': 'รอบ 3 Admission',
    'round4': 'รอบ 4 Direct Admission'
})

# Debugging: Print column names
print("Column names in DataFrame after renaming:", df.columns)

with open('data/location_uni.json', 'r', encoding='utf-8') as f:
    unijson = json.load(f)

uni_coords = {}
for uni_name, coords in unijson.items():
    latitude = coords['latitude']
    longitude = coords['longitude']
    uni_coords[uni_name] = [latitude, longitude]

df['latitude'] = df['มหาวิทยาลัย'].map(lambda x: uni_coords.get(x, [None, None])[0])
df['longitude'] = df['มหาวิทยาลัย'].map(lambda x: uni_coords.get(x, [None, None])[1])

def create_map(university=None):
    dff = df[df['มหาวิทยาลัย'] == university]
  
    fig = px.scatter_mapbox(
            dff,
            lat='latitude',
            lon='longitude',
            hover_name='มหาวิทยาลัย',
            color_discrete_sequence=['#a62b4c'],
            zoom=6,
            height=500,
            mapbox_style="open-street-map"
        )
    fig.update_traces(marker=dict(size=10, symbol='circle'))

    return fig

# App layout
app.layout = html.Div(style={'display': 'flex', 'flex-direction': 'row', 'font-family': 'Arial, sans-serif'}, children=[
    html.Div(style={'flex': '1', 'padding': '20px', 'background-color': '#f0f2f5', 'border-radius': '10px', 'box-shadow': '0 2px 10px rgba(0,0,0,0.1)'}, children=[
        html.H1("มหาวิทยาลัยที่เปิดรับคณะวิศวกรรมศาสตร์", style={'text-align': 'center', 'color': '#333'}),
        dcc.Dropdown(df['มหาวิทยาลัย'].unique(), 'มหาวิทยาลัยสงขลานครินทร์', id='dropdown-selection', style={'margin-bottom': '20px'}),
        dcc.Dropdown(id='department-dropdown', placeholder="เลือกสาขา", style={'margin-bottom': '20px'}),
        dcc.Dropdown(id='course-dropdown', placeholder="เลือกหลักสูตร", style={'margin-bottom': '20px'}),
        html.Div(id='output_container', children=[]),
        html.Br(),
        dcc.Graph(id='map', style={'width': '100%'})
    ]),
    html.Div(style={'flex': '1', 'padding': '20px', 'background-color': '#ffffff', 'border-radius': '10px', 'box-shadow': '0 2px 10px rgba(0,0,0,0.1)'}, children=[
        html.H2('รายละเอียด', style={'text-align': 'center', 'color': '#333'}),
        html.Div(id='text-box', style={'whiteSpace': 'pre-line', 'padding': '10px', 'color': '#555', 'font-size': '16px'})
    ])
])

# Update department dropdown options based on the selected university
@app.callback(
    Output('department-dropdown', 'options'),
    Input('dropdown-selection', 'value')
)
def set_department_options(selected_university):
    filtered_df = df[df['มหาวิทยาลัย'] == selected_university]
    departments = filtered_df['สาขาวิชา'].unique()
    return [{'label': dept, 'value': dept} for dept in departments]

# Update course dropdown options based on the selected department
@app.callback(
    Output('course-dropdown', 'options'),
    Input('dropdown-selection', 'value'),
    Input('department-dropdown', 'value')
)
def set_course_options(selected_university, selected_department):
    filtered_df = df[(df['มหาวิทยาลัย'] == selected_university) & (df['สาขาวิชา'] == selected_department)]
    courses = filtered_df['ชื่อหลักสูตร'].unique()
    return [{'label': course, 'value': course} for course in courses]

# Update graphs and details box based on selections
@app.callback(
    [Output('output_container', 'children'),
     Output('map', 'figure'),
     Output('text-box', 'children')],
    [Input('dropdown-selection', 'value'),
     Input('department-dropdown', 'value'),
     Input('course-dropdown', 'value')]
)
def update_graphs(selected_university, selected_department, selected_course):
    container = f"{selected_university}"

    dff = df[df["มหาวิทยาลัย"] == selected_university]

    # Map
    map_fig = create_map(selected_university)
    
    map_fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color="PaleTurquoise"
    )

    # Extract detailed information
    filtered_df = df[(df['มหาวิทยาลัย'] == selected_university) & 
                     (df['สาขาวิชา'] == selected_department) & 
                     (df['ชื่อหลักสูตร'] == selected_course)]
    if not filtered_df.empty:
        detail_info = filtered_df.iloc[0].to_dict()
        # Construct text box content without 'มหาวิทยาลัย', 'latitude', and 'longitude'
        excluded_keys = ['มหาวิทยาลัย', 'latitude', 'longitude']
        text_box_content = "\n".join([f"{key}: {value}" for key, value in detail_info.items() if key not in excluded_keys])
        text_box_content = f"{selected_university}\n" + text_box_content
    else:
        text_box_content = "No data available for the selected options."

    return container, map_fig, text_box_content

if __name__ == '__main__':
    app.run_server(debug=True)
