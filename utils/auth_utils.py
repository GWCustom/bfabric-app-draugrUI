
import requests
import json
import datetime
from dash import html
import dash_bootstrap_components as dbc
import os
import bfabric
from bfabric import BfabricAuth
from bfabric import BfabricClientConfig
from .objects import Logger


VALIDATION_URL = "https://fgcz-bfabric.uzh.ch/bfabric/rest/token/validate?token="
HOST = "fgcz-bfabric.uzh.ch"

def token_to_data(token: str) -> str: 

    if not token:
        return None

    validation_url = VALIDATION_URL + token
    res = requests.get(validation_url, headers={"Host": HOST})
    
    if res.status_code != 200:
        res = requests.get(validation_url)
    
        if res.status_code != 200:
            return None
    try:
        master_data = json.loads(res.text)
    except:
        return None
    
    if True: 

        userinfo = json.loads(res.text)
        expiry_time = userinfo['expiryDateTime']
        current_time = datetime.datetime.now()
        five_minutes_later = current_time + datetime.timedelta(minutes=5)

        # Comparing the parsed expiry time with the five minutes later time

        if not five_minutes_later <= datetime.datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%S"):
            return "EXPIRED"
        
        environment_dict = {"Production":"https://fgcz-bfabric.uzh.ch/bfabric","Test":"https://fgcz-bfabric-test.uzh.ch/bfabric"}

        token_data = dict(
            environment = userinfo['environment'],
            user_data = userinfo['user'],
            token_expires = expiry_time,
            entity_id_data = userinfo['entityId'],
            entityClass_data = userinfo['entityClassName'],
            webbase_data = environment_dict.get(userinfo['environment'], None),
            application_params_data = {},
            application_data = str(userinfo['applicationId']),
            userWsPassword = userinfo['userWsPassword'],
            jobId = userinfo['jobId']
        )


        return json.dumps(token_data)
    

def token_response_to_bfabric(token_response: dict) -> str:

    bfabric_auth = BfabricAuth(login=token_response.get('user_data'), password=token_response.get('userWsPassword'))
    bfabric_client_config = BfabricClientConfig(base_url=token_response.get('webbase_data')) 

    bfabric_wrapper = bfabric.Bfabric(config=bfabric_client_config, auth=bfabric_auth)

    return bfabric_wrapper


def entity_data(token_data: dict) -> str:
    """
    This function takes in a token from B-Fabric and returns the entity data for the token.
    Edit this function to change which data is stored in the browser for this entity
    """

    entity_class_map = {
        "Run": "run",
        "Sample": "sample",
        "Project": "container",
        "Order": "container",
        "Container": "container",
        "Plate": "plate"
    }

    if not token_data:
        return None

    wrapper = token_response_to_bfabric(token_data)
    entity_class = token_data.get('entityClass_data')
    endpoint = entity_class_map.get(entity_class)
    entity_id = token_data.get('entity_id_data')
    jobId = token_data.get('jobId', None)
    username = token_data.get("user_data", "None")

    sample_lanes = {}

    if wrapper and entity_class and endpoint and entity_id:

        L = Logger(jobid=jobId, username=username)

        entity_data_list = L.logthis(
            api_call=wrapper.read,
            endpoint=endpoint,
            obj={"id": entity_id},
            max_results=None,
            flush_logs = False
        )

        if not entity_data_list:
            return json.dumps({})
        entity_data_dict = entity_data_list[0]

        rununit_id = entity_data_dict.get("rununit", {}).get("id")
        if not rununit_id:
            return json.dumps({})

        #lane_data_list = wrapper.read(endpoint="rununit", obj={"id": str(rununit_id)}, max_results=None)

        lane_data_list = L.logthis(
                    api_call=wrapper.read,
                    endpoint="rununit",
                    obj={"id": str(rununit_id)},
                    max_results=None,
                    flush_logs = False
        )

        if not lane_data_list:
            return json.dumps({})
        lane_data = lane_data_list[0]

        #lane_samples = wrapper.read(endpoint="rununitlane", obj={"id": [str(elt["id"]) for elt in lane_data.get("rununitlane", [])]}, max_results=None)

        lane_samples = L.logthis(
            api_call=wrapper.read,
            endpoint="rununitlane",
            obj={"id": [str(elt["id"]) for elt in lane_data.get("rununitlane", [])]},
            max_results=None,
            flush_logs=False
        )

        for lane in lane_samples:
            samples = []
            sample_ids = [str(elt["id"]) for elt in lane.get("sample", [])]
            if len(sample_ids) < 100:
                
                #samples = wrapper.read(endpoint="sample", obj={"id": sample_ids}, max_results=None)
                samples = L.logthis(
                    api_call=wrapper.read,
                    endpoint="sample",
                    obj={"id": sample_ids},
                    max_results=None,
                    flush_logs=False
                )

            else:
                for i in range(0, len(sample_ids), 100):
                    
                    #samples += wrapper.read(endpoint="sample", obj={"id": sample_ids[i:i+100]}, max_results=None)
                    samples += L.logthis(
                        api_call=wrapper.read,
                        endpoint="sample",
                        obj={"id": sample_ids[i:i+100]},
                        max_results=None,
                        flush_logs=False
                    )

            container_ids = list(set([sample.get("container", {}).get("id") for sample in samples if sample.get("container")]))
            sample_lanes[str(lane.get("position"))] = [f"{container_id} {L.logthis(api_call=wrapper.read,endpoint='container', obj={'id': str(container_id)}, max_results=None, flush_logs=True )[0].get('name', '')}"
                                                       for container_id in container_ids
        ]
    else:
        L.flush_logs()
        return json.dumps({})

    json_data = {
        "name": entity_data_dict.get("name", ""),
        "createdby": entity_data_dict.get("createdby", ""),
        "created": entity_data_dict.get("created", ""),
        "modified": entity_data_dict.get("modified", ""),
        "lanes": sample_lanes,
        "containers": [container["id"] for container in entity_data_dict.get("container", []) if container.get("classname") == "order"],
        "server": entity_data_dict.get("serverlocation", ""),
        "datafolder": entity_data_dict.get("datafolder", "")
    }


    print(json_data)
    L.flush_logs()
    return json.dumps(json_data)


def send_bug_report(token_data, entity_data, description):

    mail_string = f"""
    BUG REPORT FROM DRAUGR-UI
        \n\n
        token_data: {token_data} \n\n 
        entity_data: {entity_data} \n\n
        description: {description} \n\n
        sent_at: {datetime.datetime.now()} \n\n
    """

    # mail = f"""
    #     echo "{mail_string}" | mail -s "Bug Report" griffin@gwcustom.com
    # """

    mail = f"""
        echo "{mail_string}" | mail -s "Bug Report" gwtools@fgcz.system
    """

    print("MAIL STRING:")
    print(mail_string)

    print("MAIL:")
    print(mail)

    os.system(mail)

    return True