import datetime
import json
import re
import os
import requests

from flask import Flask, Response, request
from dotenv import load_dotenv

from src.x_ag import json_to_ag, ag_to_json

env = os.environ if load_dotenv("env/MK12.env") else {}
app = Flask(env.get("SERVER", "MITM_Server"))
APP_PORT = int(env.get("PORT", 12181))

MK12_DOMAIN = env.get("ENDPOINT")
if not MK12_DOMAIN:
    raise ValueError(f"Missing value for `ENDPOINT`")
MK12_DOMAIN_PATTERN = re.compile(r"(?i)(?:^" + re.escape(MK12_DOMAIN) + r")(?:/)(.*)")

os.makedirs("requests", exist_ok=True)

def mk_redirect(url, data = None):
    print("Redirect Request", url)
    url = f"{MK12_DOMAIN}/{url}"
    # request.headers.pop("Host", None)
    resp = requests.request(
        method=request.method,
        url=url,
        headers={k:v for k, v in request.headers.items() if k != "Host"},
        data=data or request.get_data(),
        params=request.args, # type: ignore
        cookies=request.cookies,
        allow_redirects=False,
    )

    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [
        (name, value)
        for (name, value) in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]

    print("Request Redirected")
    response = Response(resp.content, resp.status_code, headers)
    return response

CURRENT_REQUEST = None

@app.route(
    "/mitm/<path:url>",
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
def redirect_route(url: str):
    global CURRENT_REQUEST
    CURRENT_REQUEST = datetime.datetime.utcnow().timestamp()
    print(request, url)
    cur_request_root = os.path.join("requests", f"{CURRENT_REQUEST}_{request.method}_{url.replace('/', '+')}")
    os.makedirs(cur_request_root, exist_ok=True)
    with open(os.path.join(cur_request_root, "request_headers.json"), "w") as f:
        json.dump(dict(request.headers), f, ensure_ascii=False, indent=4)
    with open(os.path.join(cur_request_root, "request.bin"), "wb") as f:
        f.write(request.get_data())
    with open(os.path.join(cur_request_root, "request.json"), "w") as f:
        try:
            json_data = request.get_json()
        except Exception:
            json_data = ag_to_json(request.get_data())
        json.dump(json_data, f, ensure_ascii=False, indent=4)
    # Edit the contents of json_data, example
    # json_data["contextual_droplists"]["shrine_loot_payload"]["data"]["MK12InventoryLootItem"][0]["amount"] = 9999999
    # converted_data = convert json_data to ag
    # response = mk_redirect(url, data=converted_data)
    response = mk_redirect(url)
    with open(os.path.join(cur_request_root, "response.bin"), "wb") as f:
        f.write(response.data)
    with open(os.path.join(cur_request_root, "response.json"), "w") as f:
        try:
            json_data = response.get_json()
            print("Data was JSON")
        except Exception:
            json_data = ag_to_json(response.data)
            print("Data was x-ag-binary")
        json.dump(json_data, f, ensure_ascii=False, indent=4)
    print("Redirected")
    return response

if __name__ == "__main__":
    app.run(port=APP_PORT)
