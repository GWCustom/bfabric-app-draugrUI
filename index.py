from dash import Input, Output, State, html, dcc
import dash_bootstrap_components as dbc
import dash
import json
import os
# import bfabric
from utils import auth_utils, components, draugr_utils as du


if os.path.exists("./PARAMS.py"):
    try:
        from PARAMS import PORT, HOST, DEV
    except:
        PORT = 8050
        HOST = 'localhost'
        DEV = True
else:
    PORT = 8050
    HOST = 'localhost'
    DEV = True
    

####### Main components of a Dash App: ########
# 1) app (dash.Dash())
# 2) app.layout (html.Div())
# 3) app.callback()

#################### (1) app ####################
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

#################### (2) app.layout ####################

app.layout = html.Div(
    children=[
        dcc.Location(
            id='url',
            refresh=False
        ),
        dbc.Container(
            children=[    
                dbc.Row(
                    dbc.Col(
                        html.Div(
                            className="banner",
                            children=[
                                html.Div(
                                    children=[
                                        html.P(
                                            'Run Processing UI',
                                            style={'color':'#ffffff','margin-top':'15px','height':'80px','width':'100%',"font-size":"40px","margin-left":"20px"}
                                        )
                                    ],
                                    style={"background-color":"#000000", "border-radius":"10px"}
                                ),
                            ],
                        ),
                    ),
                ),
                dbc.Row(
                    dbc.Col(
                        [
                            html.Div(
                                children=[html.P(id="page-title",children=[str("Genomics Runs")], style={"font-size":"40px", "margin-left":"20px", "margin-top":"10px"})],
                                style={"margin-top":"0px", "min-height":"80px","height":"6vh","border-bottom":"2px solid #d4d7d9"}
                            ),
                            dbc.Alert(
                                "Demultiplexing has begun! Please close this window now, and see bfabric for further status updates and logs.",
                                id="alert-fade",
                                dismissable=True,
                                is_open=False,
                                style={"max-width":"50vw", "margin":"10px"}
                            ),
                        ]
                    )
                ),
                components.tabs,
            ], style={"width":"100vw"},  
            fluid=True
        ),
        dcc.Store(id='token', storage_type='session'), # Where we store the actual token
        dcc.Store(id='entity', storage_type='session'), # Where we store the entity data retrieved from bfabric
        dcc.Store(id='token_data', storage_type='session'), # Where we store the token auth response
        dbc.Tooltip(
            """Custom bcl2fastq flags to use for the standard samples wrapped in a
                string, with arguments separated by '|' characters, E.g. "--barcode-
                mismatches 2|--minimum-trimmed-read-length" """,
                target="bcl-input",
        ),
        dbc.Tooltip(
            """Custom cellranger mkfastq flags to use for the 10x samples wrapped in a
                        string, with arguments separated by '|' characters, E.g. "--barcode-
                        mismatches 2|--delete-undetermined"
                 """,
                target="cellranger-input",
        ),
        dbc.Tooltip(
            """Custom bases2fastq flags to use wrapped in a string, with arguments
                        separated by ';' characters, E.g. "--i1-cycles 8;--r2-cycles 40 "
             """,
            target="bases2fastq-input"
        ),
        dbc.Tooltip(
            """Disable the demultiplexing Wizard. None of the samples are tested for
                        barcode issues andthe information from BFabric is taken as-is.
             """,
            target="wizard"
        ),
        dbc.Tooltip(
            "Will skip copying files to gstore.",
            target="gstore"
        ),
        dbc.Tooltip(
            """For single-index 10X samples, determines if we should run in multiome-
                        mode (with CellRangerARC) or with the default program (CellRanger).
                        Overrides BFabric-derived information.
             """,
            target="multiome"
        ),
        html.Div(id="empty-div-1"),
        components.modal,
    ],style={"width":"100vw", "overflow-x":"hidden", "overflow-y":"scroll"}
)


#################### (3) app.callback ####################
@app.callback(
    [
        Output('token', 'data'),
        Output('token_data', 'data'),
        Output('entity', 'data'),
        Output('page-content', 'children'),
        Output('page-content2', 'children'),
        Output('page-content3', 'children'),
        Output('page-title', 'children'),
        Output('draugr-button', 'disabled'),
        Output('gstore', 'disabled'),
        Output('wizard', 'disabled'),
        Output('test', 'disabled'),
        Output('multiome', 'disabled'),
        Output('bcl-input', 'disabled'),
        Output('cellranger-input', 'disabled'),
        Output('draugr-dropdown', 'disabled'),
        Output('bases2fastq-input', 'disabled')
    ],
    [
        Input('url', 'search'),
    ]
)
def display_page(url_params):
    
    base_title = "Genomics Runs"

    if not url_params:
        return None, None, None, components.no_auth, components.no_auth, components.no_auth, base_title, True, True, True, True, True, True, True, True, True
    
    token = "".join(url_params.split('token=')[1:])
    tdata_raw = auth_utils.token_to_data(token)
    
    if tdata_raw:
        if tdata_raw == "EXPIRED":
            return None, None, None, components.expired, components.expired, components.expired, base_title, True, True, True, True, True, True, True, True, True

        else: 
            tdata = json.loads(tdata_raw)
    else:
        return None, None, None, components.no_auth, components.no_auth, components.no_auth, base_title, True, True, True, True, True, True, True, True, True
    
    if tdata:
        entity_data = json.loads(auth_utils.entity_data(tdata))
        page_title = f"{base_title} - {tdata['entityClass_data']} - {tdata['entity_id_data']} ({tdata['environment']} System)" if tdata else "Bfabric App Interface"

        if not tdata:
            return token, None, None, components.no_auth, components.no_auth, components.no_auth, page_title, True, True, True, True, True, True, True, True, True
        
        elif not entity_data:
            return token, None, None, components.no_entity, components.no_entity, components.no_entity, page_title, True, True, True, True, True, True, True, True, True
        
        else:
            if not DEV:
                return token, tdata, entity_data, components.auth, components.auth2, components.auth3, page_title, False, False, False, False, False, False, False, False, False
            else: 
                return token, tdata, entity_data, components.dev, components.dev, components.dev, page_title, True, True, True, True, True, True, True, True, True
    else: 
        return None, None, None, components.no_auth, components.no_auth, components.no_auth, base_title, True, True, True, True, True, True, True, True, True
    
@app.callback(
    Output('draugr-dropdown', 'options'),
    [Input('entity', 'data')],
)
def update_dropdown(entity_data):
    
    orders = entity_data['containers']
    options = [{"label": elt, "value": elt} for elt in orders]
    return options

@app.callback(
    [    Output('auth-div', 'children'),
         Output('auth-div2', 'children'),
         Output('auth-div3', 'children')
    ],
    [
        Input("entity", "data"),
    ]
)
def update_auth_div(entity_data):

    functionality_disabled = [html.P("This functionality is currently disabled while we implement this feature in Draugr. Please check back later!")]

    if len(list(entity_data['lanes'].values())) != 8:
        container = dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                components.lane_card(
                                    lane_position=lane_position,
                                    container_ids=container_ids
                                ) for lane_position, container_ids in entity_data['lanes'].items()
                            ]
                        )
                    ]
                )
            ]
        )

    else:
        container = dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                components.lane_card(
                                    lane_position=i,
                                    container_ids=entity_data['lanes'][str(i)]
                                ) for i in range(1,5)
                            ]
                        ),
                        dbc.Col(
                            [
                                components.lane_card(
                                    lane_position=i,
                                    container_ids=entity_data['lanes'][str(i)]
                                ) for i in range(5,9)
                            ]
                        )
                    ]
                )
            ]
        )
    
    return container, functionality_disabled, functionality_disabled

@app.callback(
    Output("modal", "is_open"),
    [Input("draugr-button", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    [
        Output("empty-div-1", "children"), 
        Output("alert-fade", "is_open")
    ],
    [
        Input("close", "n_clicks")
    ],
    [
        State("draugr-dropdown", "value"),
        State("gstore", "on"),
        State("wizard", "on"),
        State("test", "on"),
        State("multiome", "on"),
        State("bcl-input", "value"),
        State("cellranger-input", "value"),
        State("bases2fastq-input", "value"),
        State("token", "data"),
        State("token_data", "data"),
        State("entity", "data"),
    ]

)
def execute_draugr_command(n_clicks, orders, gstore, wizard, test, multiome, bcl_flags, cellranger_flags, bases2fastq_flags, token, token_data, entity_data):
    
    if n_clicks:
        print("ORDERS:")
        print(orders)
        draugr_command = du.generate_draugr_command(
            server=entity_data['server'],
            run_folder=entity_data['datafolder'],
            order_list=orders,
            skip_gstore=gstore,
            disable_wizard=wizard,
            test_mode=test,
            is_multiome=multiome,
            bcl_flags=bcl_flags,
            cellranger_flags=cellranger_flags,
            bases2fastq_flags=bases2fastq_flags
        )
        
        print("DRAUGR COMMAND:")
        print(draugr_command)
        os.system(draugr_command)

        return None, True
    return None, False

if __name__ == '__main__':
    app.run_server(debug=False, port=PORT, host=HOST)