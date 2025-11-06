import logging
import azure.functions as func
from azure.data.tables import TableServiceClient, UpdateMode
from azure.core.exceptions import ResourceNotFoundError
import os
import json

# Environment variables
connection_string = os.environ["AzureWebJobsStorage"]
table_name = os.environ.get("COSMOS_TABLE_NAME", "visitorcounter")

# Initialize table client (deferred — not at import time to avoid errors during cold starts/CI)
def get_table_client():
    service = TableServiceClient.from_connection_string(conn_str=connection_string)
    return service.get_table_client(table_name=table_name)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("VisitorCounter function processed a request.")

    partition_key = "1"
    row_key = "1"
    table_client = get_table_client()

    try:
        # Try to get the entity
        entity = table_client.get_entity(partition_key=partition_key, row_key=row_key)

        # Increment the counter
        entity['counterId'] = int(entity.get('counterId', 0)) + 1
        table_client.update_entity(entity, mode=UpdateMode.MERGE)

    except ResourceNotFoundError:
        # Entity doesn't exist, create it
        entity = {
            'PartitionKey': partition_key,
            'RowKey': row_key,
            'counterId': 1
        }
        table_client.create_entity(entity)

    # Return JSON response
    return func.HttpResponse(
        json.dumps({"visitor_count": entity["counterId"]}),
        mimetype="application/json",
        status_code=200
    )
