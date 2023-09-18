import os
import json
import argparse

from promptflow._cli._pf._connection import create_connection
from promptflow._cli._pf._flow import serve_flow

def create_connections(directory_path) -> None:
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            create_connection(file_path)


def set_environment_variable(file_path) -> None:
    with open(file_path, "r") as file:
        json_data = json.load(file)
    environment_variables = list(json_data.keys())
    for environment_variable in environment_variables:
        # Check if the required environment variable is set
        if not os.environ.get(environment_variable):
            print(f"{environment_variable} is not set.")
            user_input = input(f"Please enter the value for {environment_variable}: ")
            # Set the environment variable
            os.environ[environment_variable] = user_input


if __name__ == "__main__":
    create_connections("./connections")
    set_environment_variable("./settings.json")
    # Execute 'pf flow serve' command
    # setup argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        default="flow",
    )
    parser.add_argument(
        "--port",
        default="8080",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
    )
    parser.add_argument(  # noqa: E731
        "--static_folder", type=str, help=argparse.SUPPRESS
    )

    parser.add_argument(
        "--environment-variables",
        help="Environment variables to set by specifying a property path and value. Example: --environment-variable "
        "key1='${my_connection.api_key}' key2='value2'. The value reference to connection keys will be resolved "
        "to the actual value, and all environment variables specified will be set into os.environ.",
        nargs="+",
    )

    args = parser.parse_args()
    serve_flow(args)