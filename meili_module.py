import os
from meilisearch_python_sdk import AsyncClient
from dotenv import load_dotenv
import json
import asyncio

load_dotenv()


async def main(json_file_list: list):
    url = os.getenv("MEILI_HTTP_ADDR")
    master_key = os.getenv("MEILI_MASTER_KEY")
    error_list = []
    async with AsyncClient(url=url, api_key=master_key) as client:
        index = client.index("cve")
        # prepare documents for import
        print(f"Importing {len(json_file_list)} documents")
        batch = []
        for json_file in json_file_list:
            try:
                with open(json_file, "r") as f:
                    document = json.load(f)
                    batch.append(document)
            except Exception as e:
                error_list.append(str(e))

        max_retries = 2
        for i in range(max_retries):
            try:
                tasks = await index.add_documents_in_batches(batch, batch_size=2000)
                print(f"Waiting for {len(tasks)} tasks to complete")
                await asyncio.gather(
                    *[
                        client.wait_for_task(task.task_uid, timeout_in_ms=None)
                        for task in tasks
                    ]
                )
                print("All tasks completed")
                break
            except Exception as e:
                print(f"Error occurred: {str(e)}, retrying ({i+1}/{max_retries})")
                if i == max_retries - 1:
                    error_list.append(str(e))
                else:
                    await asyncio.sleep(2**i)

        print("All tasks completed")
        # Print any errors
        if error_list:
            with open("errors.txt", "w") as f:
                f.write("Errors:\n")
                for error in error_list:
                    f.write(f"{error}\n")


def meili_update(json_updated_list: list):
    asyncio.run(main(json_updated_list))
