import os
from meilisearch_python_sdk import AsyncClient
from time import sleep
from dotenv import load_dotenv
import json
import asyncio

load_dotenv()


async def wait_for_task_forever(client, task_uid):
    while True:
        task = await client.get_task(task_uid)
        if task.status != "enqueued":
            return task
        await asyncio.sleep(5)  # wait for 1 second before checking again


async def main(json_file_list: list):
    url = os.getenv("MEILI_HTTP_ADDR")
    master_key = os.getenv("MEILI_MASTER_KEY")
    error_list = []
    async with AsyncClient(url=url, api_key=master_key) as client:
        index = client.index("cve")
        # prepare documents for import
        batch = []
        for json_file in json_file_list:
            with open(json_file, "r") as f:
                document = json.load(f)
                batch.append(document)

            # Limit to 20000 documents per import
            if len(batch) >= 2000:
                from_id = batch[0]["id"]
                to_id = batch[-1]["id"]
                print(f"Importing {len(batch)} documents from {from_id} to {to_id}")
                task = await index.add_documents(list(batch))
                await wait_for_task_forever(client, task.task_uid)
                batch.clear()

        # Add any remaining documents
        if batch:
            from_id = batch[0]["id"]
            to_id = batch[-1]["id"]
            print(f"Importing {len(batch)} documents from {from_id} to {to_id}")
            task = await index.add_documents(list(batch))
            await wait_for_task_forever(client, task.task_uid)
            batch.clear()

        # Print any errors
        if error_list:
            with open("errors.txt", "w") as f:
                f.write("Errors:\n")
                for error in error_list:
                    f.write(f"{error}\n")


def meili_update(json_updated_list):
    asyncio.run(main(json_updated_list))
