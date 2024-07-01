from argparse import ArgumentParser, BooleanOptionalAction
from argparse import ArgumentDefaultsHelpFormatter


def parse_server_args():
    parser = ArgumentParser(
        description="Postfactum Analysis Dashboard server.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--ip",
        type=str,
        default="127.0.0.1",
        help="The IP address the server will listen on.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8050,
        help="The port the server will listen on",
    )
    parser.add_argument(
        "--solver",
        type=str,
        default="scip",
        choices=["scip", "gurobi"],
        help="The nonlinear programming solver used to calculate the upper perimeter of the WMSD space.",
    )
    parser.add_argument(
        "--debug",
        default=True,
        action=BooleanOptionalAction,
        help="Turns on debugging option in run_server() method.",
    )

    return parser.parse_args()
