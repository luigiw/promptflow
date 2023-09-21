# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import re
from typing import List

from promptflow._cli._user_agent import USER_AGENT as CLI_USER_AGENT
from promptflow._core.operation_context import OperationContext
from promptflow._sdk._constants import MAX_LIST_CLI_RESULTS, AZURE_WORKSPACE_REGEX_FORMAT, LOGGER_NAME
from promptflow._sdk._logger_factory import LoggerFactory
from promptflow._sdk.entities._connection import _Connection


logger = LoggerFactory.get_logger(name=LOGGER_NAME, verbosity=logging.WARNING)


class LocalAzureConnectionOperations:
    def __init__(self, connection_provider):
        from promptflow.azure._pf_client import PFClient as PFAzureClient
        from azure.identity import AzureCliCredential, DefaultAzureCredential
        self._connection_provider = connection_provider

        subscription_id, resource_group, workspace_name = self._extract_workspace()
        self._pfazure_client = PFAzureClient(
            credential=AzureCliCredential() if self._from_cli() else DefaultAzureCredential(),
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            workspace_name=workspace_name,
        )

    @classmethod
    def _from_cli(cls):
        return CLI_USER_AGENT in OperationContext.get_instance().get_user_agent()

    def _extract_workspace(self):
        match = re.match(AZURE_WORKSPACE_REGEX_FORMAT, self._connection_provider)
        if not match:
            raise ValueError(
                "Malformed connection provider string, expected azureml:/subscriptions/<subscription_id>/"
                "resourceGroups/<resource_group>/providers/Microsoft.MachineLearningServices/"
                "workspaces/<workspace_name>"
            )
        subscription_id = match.group(1)
        resource_group = match.group(2)
        workspace_name = match.group(3)
        return subscription_id, resource_group, workspace_name

    def list(
        self,
        max_results: int = MAX_LIST_CLI_RESULTS,
        all_results: bool = False,
    ) -> List[_Connection]:
        """List connections.

        :return: List of run objects.
        :rtype: List[~promptflow.sdk.entities._connection._Connection]
        """
        if max_results != MAX_LIST_CLI_RESULTS or all_results:
            logger.warning(
                "max_results and all_results are not supported for workspace connection and will be ignored."
            )
        return self._pfazure_client._connections.list()

    def get(self, name: str, **kwargs) -> _Connection:
        """Get a connection entity.

        :param name: Name of the connection.
        :type name: str
        :return: connection object retrieved from the database.
        :rtype: ~promptflow.sdk.entities._connection._Connection
        """
        with_secrets = kwargs.get("with_secrets", False)
        if with_secrets:
            return self._pfazure_client._arm_connections.get(name)
        return self._pfazure_client._connections.get(name)

    def delete(self, name: str) -> None:
        """Delete a connection entity.

        :param name: Name of the connection.
        :type name: str
        """
        raise NotImplementedError(
            "Delete connection is not supported for workspace connection, please go to Azure Portal to delete it.")

    def create_or_update(self, connection: _Connection, **kwargs):
        """Create or update a connection.

        :param connection: Run object to create or update.
        :type connection: ~promptflow.sdk.entities._connection._Connection
        """
        raise NotImplementedError(
            "Create or update connection is not supported for workspace connection, "
            "please go to Azure Portal to create or update it."
        )