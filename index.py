from dash import Input, Output, State, html, dcc
import dash_bootstrap_components as dbc
import dash
import json
import os
from datetime import datetime as dt
# import bfabric
from utils import auth_utils, components, draugr_utils as du
import time
from utils.objects import Logger
from dash import callback_context as ctx


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
                                children=[html.P(id="page-title",children=[str(" ")], style={"font-size":"40px", "margin-left":"20px", "margin-top":"10px"})],
                                style={"margin-top":"0px", "min-height":"80px","height":"6vh","border-bottom":"2px solid #d4d7d9"}
                            ),
                            dbc.Alert(
                                "Demultiplexing has begun! Please close this window now, and see B-Fabric for further status updates and logs.",
                                id="alert-fade",
                                dismissable=True,
                                is_open=False,
                                color="success",
                                style={"max-width":"50vw", "margin":"10px"}
                            ),
                            dbc.Alert(
                                "Sushification has begun! Please close this window now, and see Sushi for further status updates and logs.",
                                id="alert-fade-2",
                                dismissable=True,
                                is_open=False,
                                color="success",
                                style={"max-width":"50vw", "margin":"10px"}
                            ),
                            dbc.Alert(
                                "Sushification has FAILED! Please try DMX again, and then try Sushi again.",
                                id="alert-fade-2-fail",
                                dismissable=True,
                                is_open=False,
                                color="danger",
                                style={"max-width":"50vw", "margin":"10px"}
                            ),
                            dbc.Alert(
                                "You're bug report has been submitted. Thanks for helping us improve!",
                                id="alert-fade-3",
                                dismissable=True,
                                is_open=False,
                                color="info",
                                style={"max-width":"50vw", "margin":"10px"}
                            ),
                            dbc.Alert(
                                "Failed to submit bug report! Please email the developers directly at the email below!",
                                id="alert-fade-3-fail", 
                                dismissable=True,
                                is_open=False, 
                                color="danger",
                                style={"max-width":"50vw", "margin":"10px"}
                            ),
                            dbc.Alert(
                                "Your submission didn't go through, because you haven't selected any orders from the dropdown! Please select which orders you'd like to process and try again.",
                                id="alert-fade-4",
                                dismissable=True,
                                is_open=False,
                                color="danger",
                                style={"max-width":"50vw", "margin":"10px"}
                            )
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
                        barcode issues andthe information from B-Fabric is taken as-is.
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
                        Overrides B-Fabric-derived information.
             """,
            target="multiome"
        ),
        html.Div(id="empty-div-1"),
        components.modal,
        components.modal2,
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
        Output('bases2fastq-input', 'disabled'),
        Output('draugr-dropdown-2', 'disabled'),
        Output('draugr-button-2', 'disabled')
    ],
    [
        Input('url', 'search'),
    ]
)
def display_page(url_params):
    
    base_title = " "

    if not url_params:
        return None, None, None, components.no_auth, components.no_auth, components.no_auth, base_title, True, True, True, True, True, True, True, True, True, True, True
    
    token = "".join(url_params.split('token=')[1:])
    tdata_raw = auth_utils.token_to_data(token)
    
    if tdata_raw:
        if tdata_raw == "EXPIRED":
            return None, None, None, components.expired, components.expired, components.expired, base_title, True, True, True, True, True, True, True, True, True, True, True

        else: 
            tdata = json.loads(tdata_raw)
    else:
        return None, None, None, components.no_auth, components.no_auth, components.no_auth, base_title, True, True, True, True, True, True, True, True, True, True, True
    
    if tdata:
        entity_data = json.loads(auth_utils.entity_data(tdata))
        page_title = f"{tdata['entityClass_data']} - {entity_data['name']}" if tdata else "B-Fabric App Interface"

        if not tdata:
            return token, None, None, components.no_auth, components.no_auth, components.no_auth, page_title, True, True, True, True, True, True, True, True, True, True, True
        
        elif not entity_data:
            return token, None, None, components.no_entity, components.no_entity, components.no_entity, page_title, True, True, True, True, True, True, True, True, True, True, True
        
        else:
            if not DEV:
                return token, tdata, entity_data, components.auth, components.auth2, components.auth3, page_title, False, False, False, False, False, False, False, False, False, False, False
            else: 
                return token, tdata, entity_data, components.dev, components.dev, components.dev, page_title, True, True, True, True, True, True, True, True, True, True, True
    else: 
        return None, None, None, components.no_auth, components.no_auth, components.no_auth, base_title, True, True, True, True, True, True, True, True, True, True, True
    
@app.callback(
    Output('draugr-dropdown', 'options'),
    [Input('entity', 'data')],
    prevent_initial_call=True
)
def update_dropdown(entity_data):
    orders = entity_data.get('containers')
    options = [{"label": elt, "value": elt} for elt in orders]
    return options

@app.callback(
    Output('draugr-dropdown-2', 'options'),
    [Input('entity', 'data')],
    prevent_initial_call=True
)
def update_dropdown(entity_data):
    orders = entity_data['containers']
    options = [{"label": elt, "value": elt} for elt in orders]
    return options

@app.callback(
    [    Output('auth-div', 'children'),
         Output('auth-div2', 'children'),
         Output('auth-div3', 'children'),
         Output('session-details', 'children'),
    ],
    [
        Input("entity", "data"),
    ],
    [
        State("token", "data"),
    ]
)
def update_auth_div(entity_data, token):

    token_data = json.loads(auth_utils.token_to_data(token))

    if not entity_data: 
        session_details = [html.P("No session details available.")]
    else:
        session_details = [
            html.P([
                html.B("Entity Name: "), entity_data['name'],
                html.Br(),
                html.B("Entity Class: "), token_data['entityClass_data'],
                html.Br(),
                html.B("Environment: "), token_data['environment'],
                html.Br(),
                html.B("Entity ID: "), token_data['entity_id_data'],
                html.Br(),
                html.B("User Name: "), token_data['user_data'],
                html.Br(),
                html.B("Session Expires: "), token_data['token_expires'],
                html.Br(),
                html.B("Current Time: "), str(dt.now().strftime("%Y-%m-%d %H:%M:%S"))

            ])
        ]

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
    
    return container, functionality_disabled, container, session_details

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
    Output("modal2", "is_open"),
    [Input("draugr-button-2", "n_clicks"), Input("close2", "n_clicks")],
    [State("modal2", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    [
        Output("alert-fade-3", "is_open"),
        Output("alert-fade-3-fail", "is_open")
    ],
    [
        Input("submit-bug-report", "n_clicks")
    ],
    [
        State("token", "data"),
        State("entity", "data"),
        State("bug-description", "value")
    ],
    prevent_initial_call=True
)

def submit_bug_report(n_clicks, token, entity_data, bug_description):

    if token: 
        token_data = json.loads(auth_utils.token_to_data(token))
    else:
        token_data = ""

    L = Logger(
        jobid = token_data.get('jobId', None),
        username= token_data.get("user_data", "None"),
        environment= token_data.get("environment", "None"))

    if n_clicks:
        L.log_operation("bug report", "Initiating bug report submission process.", params=None, flush_logs=False)
        try:
            sending_result = auth_utils.send_bug_report(
                token_data=token_data,
                entity_data=entity_data,
                description=bug_description
            )

            if sending_result:
                L.log_operation("bug report", f"Bug report successfully submitted. | DESCRIPTION: {bug_description}", params=None, flush_logs=True)
                return True, False
            else:
                L.log_operation("bug report", "Failed to submit bug report!", params=None, flush_logs=True)
                return False, True
        except:
            L.log_operation("bug report", "Failed to submit bug report!", params=None, flush_logs=True)
            return False, True

    return False, False


@app.callback(
    [
        Output("empty-div-1", "children"), 
        Output("alert-fade", "is_open"),
        Output("alert-fade-2", "is_open"),
        Output("alert-fade-2-fail", "is_open"),
        Output("alert-fade-4", "is_open")
    ],
    [
        Input("close", "n_clicks"),
        Input("close2", "n_clicks")
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
        State("draugr-dropdown-2", "value")
    ],
    prevent_initial_call=True
)
def execute_draugr_command(n_clicks, n_clicks2, orders, gstore, wizard, test, multiome, bcl_flags, cellranger_flags, bases2fastq_flags, token, token_data, entity_data, orders2):

    L = Logger(
        jobid = token_data.get('jobId', None),
        username= token_data.get("user_data", "None"),
        environment= token_data.get("environment", "None"))

    button_clicked = ctx.triggered_id

    if button_clicked == "close":
        if not orders:
            return None, False, False, False, True
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
        
        L.log_operation(
            operation="execute",
            message="DMX execution",
            params={
                "system_call": draugr_command
            },
            flush_logs=True
        )

        return None, True, False, False, False
    
    elif button_clicked == "close2":
        if not orders2:
            return None, False, False, False, True
        print("ORDERS2:")
        print(orders2)

        try:
            draugr_command1, draugr_command2 = du.generate_sushi_command(
                order_list=orders2,
                run_name=entity_data['name']
            )
        except: 
            draugr_command1, draugr_command2 = None, None

        if not draugr_command1:
            L.log_operation("EXECUTE", "Sushification has FAILED! Please try DMX again, and then try Sushi again.", params=None, flush_logs=True)
            return None, False, False, True, False

        print("GENERATE SUSHI SCRIPT COMMAND:")
        print(draugr_command1)

        print("EXECUTE SUSHI SCRIPT COMMAND:")
        print(draugr_command2)

        os.system(draugr_command1)
        time.sleep(1) 
        os.system(draugr_command2)

        L.log_operation(
            operation="execute",
            message="FASTQ execution",
            params={
                "generate_bash_script": draugr_command1,
                "execute_bash_script": draugr_command2,
            },
            flush_logs=True
        )

        return None, False, True, False, False

    return None, False, False, False, False

if __name__ == '__main__':
    app.run_server(debug=False, port=PORT, host=HOST)