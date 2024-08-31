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
empty_sidebar = []

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
    dbc.Input(value="", placeholder='Custom Bcl2fastq flags', id='bcl-input'),
    html.Br(),
    dbc.Input(value="", placeholder='Custom Cellranger flags', id='cellranger-input'),
    html.Br(),
    dbc.Input(value="", placeholder='Custom Bases2fastq flags', id='bases2fastq-input'),
    html.Br(),
    dbc.Button('Submit', id='draugr-button'),
]

sushi_sidebar = [
    html.P(id="sidebar_text2", children="Select Orders to Sushify"),
    dcc.Dropdown([], id='draugr-dropdown-2', multi=True),
    html.Br(),
    dbc.Button('Submit', id='draugr-button-2'),
]

no_auth = [
    html.P("You are not currently logged into an active session. Please log into B-Fabric to continue:"),
    html.A('Login to B-Fabric', href='https://fgcz-bfabric.uzh.ch/bfabric/')
]

expired = [
    html.P("Your session has expired. Please log into B-Fabric to continue:"),
    html.A('Login to B-Fabric', href='https://fgcz-bfabric.uzh.ch/bfabric/')
]

no_entity = [
    html.P("There was an error fetching the data for your entity. Please try accessing the applicaiton again from B-Fabric:"),
    html.A('Login to B-Fabric', href='https://fgcz-bfabric.uzh.ch/bfabric/')
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
                children=no_auth + [html.Div(id="auth-div2")],style={"margin-top":"2vh", "margin-left":"2vw", "font-size":"20px"},
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
                children=no_auth + [html.Div(id="auth-div3")],style={"margin-top":"2vh", "margin-left":"2vw", "font-size":"20px"},
            ),
            width=9,
        ),
    ],
    style={"margin-top": "0px", "min-height": "40vh"}
)

docs_tab = dbc.Row(
    id="page-content-docs",
    children=[
        dbc.Col(
            html.Div(
                id="sidebar_docs",
                children=empty_sidebar,
                style={"border-right": "2px solid #d4d7d9", "height": "100%", "padding": "20px", "font-size": "20px"}
            ),
            width=3,
        ),
        dbc.Col(
            html.Div(
                id="page-content-docs-children",
                children=[
                    html.H2("Welcome to Draugr UI"),
                    html.P([
                        "This app serves as the user-interface for ",
                        html.A("Draugr,", href="https://gitlab.bfabric.org/Genomics/draugr", target="_blank"),
                        " or Demultiplexing wRapper And Updated GRiffin."
                    ]),
                    html.Br(),
                    html.H4("Developer Info"),
                    html.P([
                        "This app was written by Griffin White, for the FGCZ. If you wish to report a bug, please use the \"bug reports\" tab. If you wish to contact the developer for other reasons, please use the email:",
                        html.A(" griffin@gwcustom.com", href="mailto:griffin@gwcustom.com"),
                    ]),
                    html.Br(),
                    html.H4("Draugr / DMX Tab"),
                    html.P([
                        html.B(
                            "Select Orders to DMX --"
                        ), " Select the order(s) for which you'd like to re-trigger demultiplexing.",
                        html.Br(),html.Br(),
                        html.B(
                            "Skip Gstore Copy --"
                        ), " Select this option if you don't want to copy to gstore. Mostly useful if you're not sure yet if the current settings will work.",
                        html.Br(),html.Br(),
                        html.B(
                            "Disable Wizard --"
                        ), " The wizard is Draugr's internal automatic-barcode detection and correction engine. If you're confident that the correct barcodes are assigned, or the wizard is creating barcode conflicts while checking new settings, you should turn the wizard off.",
                        html.Br(),html.Br(),
                        html.B(
                            "Test Mode --"
                        ), " test mode is currently disabled. It will be re-enabled in a future release.",
                        html.Br(),html.Br(),
                        html.B(
                            "Is Multiome --"
                        ), " If you're processing a multiome run, select this option.",
                        html.Br(),html.Br(),
                        html.B(
                            "Custom Bcl2fastq flags --"
                        ), """Custom bcl2fastq flags to use for the standard samples wrapped in a
                        string, with arguments separated by '|' characters, E.g. "--barcode-
                        mismatches 2|--minimum-trimmed-read-length ". For a full list of possible flags, see the """,
                        html.A(" bcl2fastq documentation.", href="https://support.illumina.com/content/dam/illumina-support/documents/documentation/software_documentation/bcl2fastq/bcl2fastq_letterbooklet_15038058brpmi.pdf", target="_blank"),
                        html.Br(),html.Br(),
                        html.B(
                            "Custom Cellranger flags --"
                        ), """ Custom cellranger mkfastq flags to use for the 10x samples wrapped in a
                        string, with arguments separated by '|' characters, E.g. "--barcode-
                        mismatches 2|--delete-undetermined". For a full list of possible flags, see the 
                        """,
                        html.A("cellranger documentation", href="https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq", target="_blank"),
                        html.Br(),html.Br(),
                        html.B(
                            "Custom Bases2fastq flags --"
                        ), """ Custom bases2fastq flags to use wrapped in a string, with arguments
                        separated by ';' characters, E.g. "--i1-cycles 8;--r2-cycles 40 ". For a full list of possible flags, see the 
                        """,
                        html.A("bases2fastq documentation", href="https://docs.elembio.io/docs/bases2fastq/", target="_blank"),
                        html.Br(),
                        html.Br(),
                        
                    ], style={"margin-left": "2vw"}),
                    html.H4("Prepare Raw Data Tab"),
                        html.P([
                            "This tab is currently disabled, and will be enabled in a future release, after raw-data processing is added to dragur."
                        ], style={"margin-left": "2vw"}
                    ),
                    html.Br(),
                    html.H4("Sushify Tab"),
                    html.P([
                        html.B(
                            "Select Orders to Sushify --"
                        ), " Select the order(s) for which you'd like to re-trigger sushification. After clicking \"submit\" and confirming your submission, DraugrUI will send a request to the sushi server to begin creating fastqc and fastqscreen reports. Order statuses will be updated at this stage as well. ",
                        html.Br(),html.Br(),
                    ], style={"margin-left": "2vw"}),
                    html.Br(), 
                    # html.H4("Bug Reports Tab"),

                ],
                style={"margin-top":"2vh", "margin-left":"2vw", "font-size":"20px", "padding-right":"40px", "overflow-y": "scroll", "max-height": "60vh"},
            ),
            width=9,
        ),
    ],
    style={"margin-top": "0px", "min-height": "40vh"}
)

report_bug_tab = dbc.Row(
    id="page-content-bug-report",
    children=[
        dbc.Col(
            html.Div(
                id="sidebar_bug_report",
                children=empty_sidebar,
                style={"border-right": "2px solid #d4d7d9", "height": "100%", "padding": "20px", "font-size": "20px"}
            ),
            width=3,
        ),
        dbc.Col(
            html.Div(
                id="page-content-bug-report-children",
                children=[
                    html.H2("Report a Bug"),
                    html.P([
                        "Please use the form below to report a bug in the Draugr UI. If you have any questions, please email the developer at ",
                        html.A(" griffin@gwcustom.com", href="mailto:griffin@gwcustom.com"),
                    ]),
                    html.Br(),
                    html.H4("Session Details: "),
                    html.Br(),
                    html.P(id="session-details", children="No Active Session"),
                    html.Br(),
                    html.H4("Bug Description"),
                    dbc.Textarea(id="bug-description", placeholder="Please describe the bug you encountered here.", style={"width": "100%"}),
                    html.Br(),
                    dbc.Button("Submit Bug Report", id="submit-bug-report", n_clicks=0, style={"margin-bottom": "60px"}),
                    html.Br(),
                ],
                style={"margin-top":"2vh", "margin-left":"2vw", "font-size":"20px", "padding-right":"40px"},
            ),
            width=9,
        ),
    ],
    style={"margin-top": "0px", "min-height": "40vh"}
)


tabs = dbc.Tabs(
    [
        dbc.Tab(docs_tab, label="Documentation"),
        dbc.Tab(tab1_content, label="Draugr / DMX"),
        dbc.Tab(tab2_content, label="Prepare Raw Data"),
        dbc.Tab(tab3_content, label="Sushify"),
        dbc.Tab(report_bug_tab, label="Report a Bug"),
    ]
)

modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Ready to DMX? 🚀")),
                dbc.ModalBody("Are you sure you're ready to demux?"),
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

modal2 = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Ready to Sushify? ⋅˚₊‧ ୨🍙🍣🍱🥢୧ ‧₊˚ ⋅")),
                dbc.ModalBody("Are you sure you're ready to sushify data?"),
                dbc.ModalFooter(
                    dbc.Button(
                        "Yes!", id="close2", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="modal2",
            is_open=False,
        ),
    ]
)