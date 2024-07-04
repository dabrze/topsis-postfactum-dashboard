import base64
import json
import io
import pandas as pd
import csv


def get_delimiter(csv_file_contents):
    sniffer = csv.Sniffer()
    csv_file_contents = csv_file_contents.decode("utf-8")
    delimiter = sniffer.sniff(csv_file_contents).delimiter
    return delimiter


def parse_data_file(contents, filename):
    df = None

    try:
        if filename.endswith(".csv"):
            content_string = contents.split(",")[1]
            decoded = base64.b64decode(content_string)
            sep = get_delimiter(decoded)
            if sep == ";":
                decimal = ","
            else:
                decimal = "."

            df = pd.read_csv(
                io.StringIO(decoded.decode("utf-8")), sep=sep, decimal=decimal
            )
        elif filename.endswith(".xls") or filename.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            raise Exception("Please upload a CSV or Excel file.")
    except Exception as e:
        raise Exception(f"File error: {e}")

    return df


def parse_params_file(contents, filename):
    params_dict = None

    try:
        if filename.endswith(".json"):
            content_string = contents.split(",")[1]
            decoded = base64.b64decode(content_string)
            params_dict = json.loads(decoded)
        else:
            raise Exception("Please upload a .json file.")
    except Exception as e:
        raise Exception(f"File error: {e}")

    return params_dict


def create_default_params_dict(df):
    params_dict = dict()

    for criterion in df.columns:
        if df[criterion].dtype == "object":
            params_dict[criterion] = {
                "id_column": "true",
                "weight": 0,
                "expert_min": 0,
                "expert_max": 1,
                "objective": "max",
            }
        else:
            params_dict[criterion] = {
                "id_column": "false",
                "weight": 1,
                "expert_min": df[criterion].min(),
                "expert_max": df[criterion].max(),
                "objective": "max",
            }

    return params_dict


def extract_settings_from_dict(params_dict, data_df):
    criteria = []
    settings = []

    for k, v in params_dict.items():
        criteria.append(k)
        settings.append(pd.DataFrame.from_dict({c: [s] for c, s in v.items()}))

    params_df = pd.concat(settings)
    params_df.index = pd.Index(criteria)
    params_df.index.name = "criterion"

    # make sure the order of criteria is the same as in the data
    params_df = params_df.loc[data_df.columns, :]

    return params_df


def prepare_wmsd_data(df, params_dict):
    params_df = extract_settings_from_dict(params_dict, df)

    # setting id columns as indices
    ids = params_df[params_df["id_column"] == "true"].index.tolist()
    params_df = params_df[params_df["id_column"] == "false"]
    df = df.set_index(ids)

    # preparing settings i a WMSD-suitable format
    expert_ranges = [
        [min, max] for min, max in zip(params_df.expert_min, params_df.expert_max)
    ]
    weights = params_df.weight.tolist()
    objectives = params_df.objective.tolist()

    return df, expert_ranges, weights, objectives
