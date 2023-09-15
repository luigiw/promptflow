# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import os

from promptflow._cli._configuration import Configuration
from promptflow._telemetry.logging_handler import get_appinsights_log_handler

TELEMETRY_ENABLED = "TELEMETRY_ENABLED"
# TODO: increase the timeout
TELEMETRY_PROMPT_TIMEOUT_SECONDS = 10
PROMPTFLOW_LOGGER_NAMESPACE = "promptflow._telemetry"


def is_telemetry_enabled():
    """Check if telemetry is enabled. User can enable telemetry by
    1. setting environment variable TELEMETRY_ENABLED to true.
    2. running `promptflow telemetry enable` command.
    If None of the above is set, will prompt an input to ask user to enable telemetry.
    """
    telemetry_enabled = os.getenv(TELEMETRY_ENABLED)
    if telemetry_enabled is not None:
        return str(telemetry_enabled).lower() == "true"
    config = Configuration.get_instance()
    telemetry_consent = config.get_telemetry_consent()
    if telemetry_consent is not None:
        return telemetry_consent
    result = input(
        # TODO: refine the wording
        "Do you consent to telemetry data collection? (Y/N) ",
    )
    if result and result.lower() == "y":
        config.set_telemetry_consent(True)
        return True
    else:
        config.set_telemetry_consent(False)
        return False


def get_telemetry_logger():
    current_logger = logging.getLogger(PROMPTFLOW_LOGGER_NAMESPACE)
    current_logger.propagate = False
    current_logger.setLevel(logging.INFO)
    handler = get_appinsights_log_handler()
    current_logger.addHandler(handler)
    return current_logger
