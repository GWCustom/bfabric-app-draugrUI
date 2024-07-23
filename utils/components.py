import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_daq as daq

DEVELOPER_EMAIL = "gwhite@fgcz.ethz.ch"

# default_sidebar = [
#     html.P(id="sidebar_text", children="Select a Value"),
#     dcc.Slider(0, 20, 5, value=10, id='example-slider'),
#     html.Br(),
#     dcc.Dropdown(['Genomics', 'Proteomics', 'Metabolomics'], 'Genomics', id='example-dropdown'),
#     html.Br(),
#     dbc.Input(value='Enter Some Text', id='example-input'),
#     html.Br(),
#     dbc.Button('Submit', id='example-button'),
# ]

def lane_card(lane_position, container_ids):

    card_content = [
        dbc.CardHeader(f"Lane {lane_position}"),
        dbc.CardBody(
            [
                html.P(f"Container IDs:"),
            ] + [
                html.H5(name) for name in container_ids
            ]
        ),
    ]
    return dbc.Card(card_content, style={"max-width": "25vw", "margin": "10px"})

sushi_sidebar = []
raw_data_sidebar = []

default_sidebar = [
    html.P(id="sidebar_text", children="Select Orders to DMX"),
    dcc.Dropdown([], id='draugr-dropdown', multi=True),
    html.Br(),
    html.P(id="draugr-text-1", children="Skip Gstore Copy"),
    daq.BooleanSwitch(id='gstore', on=False),
    html.P(id="draugr-text-2", children="Disable Wizard"),
    daq.BooleanSwitch(id='wizard', on=False),
    html.P(id="draugr-text-3", children="Test Mode"),
    daq.BooleanSwitch(id='test', on=False),
    html.P(id="draugr-text-4", children="Is Multiome"),
    daq.BooleanSwitch(id='multiome', on=False),
    html.Br(),
    dbc.Input(value='Custom Bcl2fastq flags', id='bcl-input'),
    html.Br(),
    dbc.Input(value='Custom Cellranger flags', id='cellranger-input'),
    html.Br(),
    dbc.Input(value='Custom Bases2fastq flags', id='bases2fastq-input'),
    html.Br(),
    dbc.Button('Submit', id='draugr-button'),
]

no_auth = [
    html.P("You are not currently logged into an active session. Please log into bfabric to continue:"),
    html.A('Login to Bfabric', href='https://fgcz-bfabric.uzh.ch/bfabric/')
]

expired = [
    html.P("Your session has expired. Please log into bfabric to continue:"),
    html.A('Login to Bfabric', href='https://fgcz-bfabric.uzh.ch/bfabric/')
]

no_entity = [
    html.P("There was an error fetching the data for your entity. Please try accessing the applicaiton again from bfabric:"),
    html.A('Login to Bfabric', href='https://fgcz-bfabric.uzh.ch/bfabric/')
]

dev = [html.P("This page is under development. Please check back later."),html.Br(),html.A("email the developer for more details",href="mailto:"+DEVELOPER_EMAIL)]

auth = [html.Div(id="auth-div")]
auth2 = [html.Div(id="auth-div2", children=[html.P("This functionality is currently disabled while we implement this feature in Draugr. Please check back later!")])]
auth3 = [html.Div(id="auth-div3", children=[html.P("This functionality is currently disabled while we implement this feature in Draugr. Please check back later!")])]

tab1_content = dbc.Row(
    id="page-content-main",
    children=[
        dbc.Col(
            html.Div(
                id="sidebar",
                children=default_sidebar,
                style={"border-right": "2px solid #d4d7d9", "height": "100%", "padding": "20px", "font-size": "20px"}
            ),
            width=3,
        ),
        dbc.Col(
            dcc.Loading(
                html.Div(
                    id="page-content",
                    children=no_auth + [html.Div(id="auth-div")],style={"margin-top":"2vh", "margin-left":"2vw", "font-size":"20px"},
                ),
            ),
            width=9,
        ),
    ],
    style={"margin-top": "0px", "min-height": "40vh"}
)

tab2_content = dbc.Row(
    id="page-content-raw",
    children=[
        dbc.Col(
            html.Div(
                id="sidebar2",
                children=raw_data_sidebar,
                style={"border-right": "2px solid #d4d7d9", "height": "100%", "padding": "20px", "font-size": "20px"}
            ),
            width=3,
        ),
        dbc.Col(
            html.Div(
                id="page-content2",
                children=no_auth + [html.Div(id="auth-div2")],style={"margin-top":"20vh", "margin-left":"2vw", "font-size":"20px"},
            ),
            width=9,
        ),
    ],
    style={"margin-top": "0px", "min-height": "40vh"}
)

tab3_content = dbc.Row(
    id="page-content-sushi",
    children=[
        dbc.Col(
            html.Div(
                id="sidebar3",
                children=sushi_sidebar,
                style={"border-right": "2px solid #d4d7d9", "height": "100%", "padding": "20px", "font-size": "20px"}
            ),
            width=3,
        ),
        dbc.Col(
            html.Div(
                id="page-content3",
                children=no_auth + [html.Div(id="auth-div3")],style={"margin-top":"20vh", "margin-left":"2vw", "font-size":"20px"},
            ),
            width=9,
        ),
    ],
    style={"margin-top": "0px", "min-height": "40vh"}
)

tabs = dbc.Tabs(
    [
        dbc.Tab(tab1_content, label="Draugr / DMX"),
        dbc.Tab(tab2_content, label="Prepare Raw Data"),
        dbc.Tab(tab3_content, label="Sushify"),
    ]
)

modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Ready to DMX? 🚀")),
                dbc.ModalBody("Are you sure you're ready do demux?"),
                dbc.ModalFooter(
                    dbc.Button(
                        "Yes!", id="close", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="modal",
            is_open=False,
        ),
    ]
)