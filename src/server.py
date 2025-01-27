from datetime import datetime
import json
import re
import os
import requests

from flask import Flask, Response, request
from dotenv import load_dotenv

from src.utils.convertors import parse_request_output, save_data_as
# SSC = no auth
# /profiles/<id> and /accounts/<id> require ANY creds

excluded_headers = [
    "content-encoding",
    "content-length",
    "transfer-encoding",
    "connection",
]

env = os.environ if load_dotenv("env/MK12.env") else {}
app = Flask(env.get("SERVER", "MITM_Server"))
APP_PORT = int(env.get("PORT", 12181))

MK12_DOMAIN = env.get("ENDPOINT")
if not MK12_DOMAIN:
    raise ValueError(f"Missing value for `ENDPOINT`")
MK12_DOMAIN_PATTERN = re.compile(r"(?i)(?:^" + re.escape(MK12_DOMAIN) + r")(?:/)(.*)")

launch_date = datetime.now().strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
logging_folder = os.path.join("requests", f"{launch_date}_{datetime.now().timestamp()}")
os.makedirs(logging_folder, exist_ok=True)


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
    request_time = datetime.utcnow().timestamp()
    print(request, url)
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

    response = mk_redirect(url)

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
