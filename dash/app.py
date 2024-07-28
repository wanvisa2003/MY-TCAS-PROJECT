import pandas as pd
import plotly.express as px
import json
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

app = Dash(__name__)

# Load data
df = pd.read_csv("./data/engineer_data.csv")

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

def create_pie_chart(admission_info):
    # Pie chart for admission rounds
    pie_data = {
        'รอบ 1 Portfolio': admission_info.get('รอบ 1 Portfolio', 0),
        'รอบ 2 Quota': admission_info.get('รอบ 2 Quota', 0),
        'รอบ 3 Admission': admission_info.get('รอบ 3 Admission', 0),
        'รอบ 4 Direct Admission': admission_info.get('รอบ 4 Direct Admission', 0)
    }
    
    
    pastel_colors = ['#EADFF2', '#DCCBED', '#FEE5EB', '#FCB7D0']
    
    fig = px.pie(
        names=list(pie_data.keys()),
        values=list(pie_data.values()),
        color_discrete_sequence=pastel_colors,
        title='Distribution of Admission Rounds'
    )
    fig.update_layout(
        title_font_size=18,
        margin={"r":0,"t":40,"l":0,"b":0},
        height=300  # Set the height of the pie chart
    )
    return fig


# App layout
app.layout = html.Div(style={'display': 'flex', 'flex-direction': 'row', 'font-family': 'Arial, sans-serif'}, children=[
    html.Div(style={'flex': '1', 'padding': '20px', 'background-color': '#f0f2f5', 'border-radius': '10px', 'box-shadow': '0 2px 10px rgba(0,0,0,0.1)', 'margin-right': '20px'}, children=[
        html.H1("มหาวิทยาลัยที่เปิดรับคณะวิศวกรรมศาสตร์", style={'text-align': 'center', 'color': '#333'}),
        dcc.Dropdown(df['มหาวิทยาลัย'].unique(), 'มหาวิทยาลัยสงขลานครินทร์', id='dropdown-selection', style={'margin-bottom': '20px'}),
        dcc.Dropdown(id='department-dropdown', placeholder="เลือกสาขา", style={'margin-bottom': '20px'}),
        dcc.Dropdown(id='course-dropdown', placeholder="เลือกหลักสูตร", style={'margin-bottom': '20px'}),
        html.Div(id='output_container', children=[]),
        html.Br(),
        dcc.Graph(id='map', style={'width': '100%'})
    ]),
    html.Div(style={'flex': '2', 'padding': '20px', 'background-color': '#ffffff', 'border-radius': '10px', 'box-shadow': '0 2px 10px rgba(0,0,0,0.1)'}, children=[
        html.H2('รายละเอียด', style={'text-align': 'center', 'color': '#333'}),
        html.Div(id='text-box-general', style={'whiteSpace': 'pre-line', 'padding': '10px', 'color': '#555', 'font-size': '16px', 'background-color': '#e0f7fa', 'border-radius': '5px', 'box-shadow': '0 2px 10px rgba(0,0,0,0.1)', 'margin-bottom': '20px'}),
        html.Div(id='text-box-admission', style={'whiteSpace': 'pre-line', 'padding': '10px', 'color': '#555', 'font-size': '16px', 'background-color': '#ffe0b2', 'border-radius': '5px', 'box-shadow': '0 2px 10px rgba(0,0,0,0.1)', 'margin-bottom': '20px'}),
        dcc.Graph(id='pie-chart', style={'width': '100%', 'height': '300px'})  # Set the height of the pie chart container
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
     Output('text-box-general', 'children'),
     Output('text-box-admission', 'children'),
     Output('pie-chart', 'figure')],
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
        excluded_keys = ['มหาวิทยาลัย', 'latitude', 'longitude', 'รอบ 1 Portfolio', 'รอบ 2 Quota', 'รอบ 3 Admission', 'รอบ 4 Direct Admission']
        
        # General Information
        general_info = "\n".join([f"{key}: {value}" for key, value in detail_info.items() if key not in excluded_keys])
        general_info = f"{selected_university}\n" + general_info
        
        # Admission Rounds Information
        admission_info = []
        for round_key in ['รอบ 1 Portfolio', 'รอบ 2 Quota', 'รอบ 3 Admission', 'รอบ 4 Direct Admission']:
            value = detail_info.get(round_key, 0)
            if value == 0:
                admission_info.append(f"{round_key}: ไม่เปิดรับสมัครในรอบนี้")
            else:
                admission_info.append(f"{round_key}: {value}")
        admission_info_text = "\n".join(admission_info)
        
        # Pie chart data
        pie_chart_figure = create_pie_chart(detail_info)
        
    else:
        general_info = "No data available for the selected options."
        admission_info_text = "No data available for the selected options."
        pie_chart_figure = create_pie_chart({
            'รอบ 1 Portfolio': 0,
            'รอบ 2 Quota': 0,
            'รอบ 3 Admission': 0,
            'รอบ 4 Direct Admission': 0
        })

    return container, map_fig, general_info, admission_info_text, pie_chart_figure

if __name__ == '__main__':
    app.run_server(debug=True)
