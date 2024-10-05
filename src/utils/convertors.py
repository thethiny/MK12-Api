import json
import os

from src.x_ag import ag_to_json

def parse_other_mode(data):
    try:
        data = data.decode() # text
        try:
            data = json.loads(data)
            return data, "json"
        except Exception:
            # Text
            return data, "txt"
    except Exception:
        # raw
        return None, None

def parse_request_output(request_object, bin_data):
    mode = request_object.headers.get("content-type", "").lower()
    if mode == "application/x-ag-binary":
        json_data = ag_to_json(bin_data)
        return json_data, "json"
    elif mode == "application/json":
        json_data = json.loads(bin_data)
        return json_data, "json"
    elif mode == "":  # figure out mode
        return parse_other_mode(bin_data)
    else:
        print(f"Couldn't handle mode: {mode}. Parsing skipped!")
        return None, None

def save_data_as(path: str, name: str, extension, data):
    path = os.path.join(path, f"{name}.{extension.lower()}")
    with open(path, "w") as f:
        if extension == "json":
            json.dump(data, f, ensure_ascii=False, indent=4)
        elif extension == "txt":
            f.write(data)
        else:
            # Bin already written
            pass