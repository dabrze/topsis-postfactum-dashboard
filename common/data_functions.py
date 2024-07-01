import base64
import json
import io
import pandas as pd
import numpy as np
import csv


def get_delimiter(csv_file_contents):
    sniffer = csv.Sniffer()
    csv_file_contents = csv_file_contents.decode("utf-8")
    delimiter = sniffer.sniff(csv_file_contents).delimiter
    return delimiter


def parse_data_file(contents, filename):
    df = None
    message = ""

    try:
        if filename.endswith(".csv"):
            content_type, content_string = contents.split(",")
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
            message = "Please upload a CSV or Excel file."
    except Exception as e:
        message = f"File error: {e}"

    return df, message


def parse_params_file(contents, filename):
    params_dict = None
    message = ""

    try:
        if filename.endswith(".json"):
            content_type, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)
            params_dict = json.loads(decoded)
        else:
            message = "Please upload a .json file."
    except Exception as e:
        message = f"File error: {e}"

    return params_dict, message


def check_parameters_wizard_data_files(data, params, param_keys):

    criteria = list(data[0].keys())

    df_data = pd.DataFrame.from_dict(data).set_index(criteria[0])
    df_params = pd.DataFrame.from_dict(params)

    n_alternatives = df_data.shape[0]
    m_criteria = df_data.shape[1]

    if param_keys[1] in df_params:
        if len(df_params[param_keys[1]]) != m_criteria:
            if args.debug:
                print("Invalid value 'weights'.")
            return -1
        if not all(
            type(item) in [int, float, np.float64] for item in df_params[param_keys[1]]
        ):
            if args.debug:
                print(
                    "Invalid value 'weights'. Expected numerical value (int or float)."
                )
            return -1
        if not all(item >= 0 for item in df_params[param_keys[1]]):
            if args.debug:
                print("Invalid value 'weights'. Expected value must be non-negative.")
            return -1
        if not any(item > 0 for item in df_params[param_keys[1]]):
            if args.debug:
                print("Invalid value 'weights'. At least one weight must be positive.")
            return -1
    else:
        return -1

    if param_keys[4] in df_params:
        if len(df_params[param_keys[4]]) != m_criteria:
            if args.debug:
                print("Invalid value 'objectives'.")
            return -1
        if not all(item in ["min", "max"] for item in df_params[param_keys[4]]):
            if args.debug:
                print(
                    "Invalid value at 'objectives'. Use 'min', 'max', 'gain', 'cost', 'g' or 'c'."
                )
            return -1
    else:
        return -1

    if param_keys[2] in df_params and param_keys[3] in df_params:
        if len(df_params[param_keys[2]]) != m_criteria:
            if args.debug:
                print(
                    "Invalid value at 'expert_range'. Length of should be equal to number of criteria."
                )
            return -1
        if len(df_params[param_keys[3]]) != m_criteria:
            if args.debug:
                print(
                    "Invalid value at 'expert_range'. Length of should be equal to number of criteria."
                )
            return -1
        if not all(
            type(item) in [int, float, np.float64] for item in df_params[param_keys[2]]
        ):
            if args.debug:
                print(
                    "Invalid value at 'expert_range'. Expected numerical value (int or float)."
                )
            return -1
        if not all(
            type(item) in [int, float, np.float64] for item in df_params[param_keys[3]]
        ):
            if args.debug:
                print(
                    "Invalid value at 'expert_range'. Expected numerical value (int or float)."
                )
            return -1

        lower_bound = df_data.min()
        upper_bound = df_data.max()

        for lower, upper, mini, maxi in zip(
            lower_bound, upper_bound, df_params[param_keys[2]], df_params[param_keys[3]]
        ):
            if mini > maxi:
                if args.debug:
                    print(
                        "Invalid value at 'expert_range'. Minimal value  is bigger then maximal value."
                    )
                return -1
            if lower < mini:
                if args.debug:
                    print(
                        "Invalid value at 'expert_range'. All values from original data must be in a range of expert_range."
                    )
                return -1
            if upper > maxi:
                if args.debug:
                    print(
                        "Invalid value at 'expert_range'. All values from original data must be in a range of expert_range."
                    )
                return -1
    else:
        return -1

    return 1


def return_columns_wizard_parameters_params_table(param_keys):
    columns = [
        {"id": "criterion", "name": "Criterion", "type": "text", "editable": False},
        {"id": param_keys[1], "name": "Weight", "type": "numeric"},
        {"id": param_keys[2], "name": "Expert Min", "type": "numeric"},
        {"id": param_keys[3], "name": "Expert Max", "type": "numeric"},
        {"id": param_keys[4], "name": "Objective", "presentation": "dropdown"},
    ]

    return columns


def fill_parameters_wizard_parameters_params(params, df, param_keys):

    if params is None:
        m_criteria = df.shape[1]
        return np.ones(m_criteria), df.min(), df.max(), np.repeat("max", m_criteria)
    else:
        weights = list(params[param_keys[1]].values())
        mins = list(params[param_keys[2]].values())
        maxs = list(params[param_keys[3]].values())
        objectives = list(params[param_keys[4]].values())

        return weights, mins, maxs, objectives
