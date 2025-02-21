from datetime import datetime
import json
import re
import os
import requests

from flask import Flask, Response, request
from dotenv import load_dotenv
import requests.structures

from src.utils.convertors import parse_request_output, save_data_as

attacked_urls = {
    # "ssc/invoke/get_mapmode_progression": open("requests/1728147825.096242_GET_ssc+invoke+get_mapmode_progression/response.bin", "rb").read()
}
# SSC = no auth
# /profiles/<id> and /accounts/<id> require ANY creds

excluded_headers = [
    "content-encoding",
    "content-length",
    "transfer-encoding",
    "connection",
]

env = os.environ if load_dotenv("env/.env") else {}
app = Flask(env.get("SERVER", "MITM_Server"))
APP_PORT = int(env.get("PORT", 12181))

servers_config = requests.structures.CaseInsensitiveDict()
for e in env.keys():
    if e.endswith("_ENDPOINT"):
        e_name = e.rsplit("_", 1)[0]
        servers_config[e_name.upper()] = {"name": e_name, "endpoint": env[e]}

if not servers_config:
    raise EnvironmentError(f"No Endpoints found in .env file!")

print("Attacking Endpoints", servers_config)


launch_date = datetime.now().strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
launch_date_folder_name = f"{launch_date}_{datetime.now().timestamp()}"

for server in servers_config:
    server_folder = os.path.join("requests", server, launch_date_folder_name)
    servers_config[server]["folder"] = server_folder
    servers_config[server]["first_run"] = True


def call_orig_endpoint(url, server, data):
    domain = servers_config[server]["endpoint"]
    url = f"{domain}/{url}"
    resp = requests.request(
            method=request.method,
            url=url,
            headers={k:v for k, v in request.headers.items() if k != "Host"},
            data=data,
            params=request.args, # type: ignore
            cookies=request.cookies,
            allow_redirects=False,
        )
    
    headers = [
        (name, value)
        for (name, value) in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]
    
    return resp, headers

def redirect_to_orig_endpoint(url, server, data = None):
    print("Redirect Request", url)
    
    resp, headers = call_orig_endpoint(url, server, data or request.get_data())

    print("Request Redirected")
    response = Response(resp.content, resp.status_code, headers)
    return response

def attack_url(url, injected_response, server, data = {}, skip_headers = False):
    if data:
        raise NotImplementedError(f"POST data is not implemented")
    
    if skip_headers:
        return Response(injected_response, 200, [("content-type", "application/x-ag-binary")])
    
    resp, headers = call_orig_endpoint(url, server, data or request.get_data())
    
    response = Response(injected_response, resp.status_code, headers)

    return response


@app.route(
    "/mitm/<string:server_name>/<path:url>",
    methods=[
        "GET",
        "HEAD",
        "POST",
        "PUT",
        "DELETE",
        "CONNECT",
        "OPTIONS",
        "TRACE",
        "PATCH",
    ],
)
def redirect_route(server_name: str, url: str):
    request_time = datetime.utcnow().timestamp()
    print(request, url)

    if server_name not in servers_config:
        raise KeyError(f"Server {server_name} doesn't have a proper ENDPOINT in environment: `{server_name.upper()}_ENDPOINT`")

    logging_folder = servers_config[server_name]["folder"]
    if servers_config[server_name]["first_run"]:
        os.makedirs(logging_folder, exist_ok=True)
        servers_config[server_name]["first_run"] = False
    cur_request_root = os.path.join(
        logging_folder, f"{request_time}_{request.method}_{url.replace('/', '+')}"
    )
    os.makedirs(cur_request_root, exist_ok=True)

    with open(os.path.join(cur_request_root, "request_params.json"), "w", encoding="utf-8") as f:
        query_dict = request.args.to_dict(False)
        query_string = request.query_string.decode("utf-8")
        json.dump({
            "params": query_dict,
            "query_string": query_string
        }, f, ensure_ascii=False, indent=4)

    with open(os.path.join(cur_request_root, "request_headers.json"), "w") as f:
        json.dump(dict(request.headers), f, ensure_ascii=False, indent=4)

    with open(os.path.join(cur_request_root, "request.bin"), "wb") as f:
        f.write(request.get_data())

    json_data, ext = parse_request_output(request, request.get_data())
    save_data_as(cur_request_root, "request", ext, json_data)

    # End of request

    if url in attacked_urls:
        print(f"Attacked URL :=: {url}")
        response = attacked_urls[url]
        return attack_url(url, response, server_name)

    response = redirect_to_orig_endpoint(url, server_name)

    # Start of response

    with open(os.path.join(cur_request_root, "response_headers.json"), "w") as f:
        json.dump(dict(response.headers), f, ensure_ascii=False, indent=4)

    with open(os.path.join(cur_request_root, "response.bin"), "wb") as f: 
        f.write(response.data)

    json_data, ext = parse_request_output(response, response.data)
    save_data_as(cur_request_root, "response", ext, json_data)

    return response

if __name__ == "__main__":
    app.run(port=APP_PORT)
