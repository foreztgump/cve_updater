import os
from time import sleep
from dotenv import load_dotenv  # remove if not using dotenv
from langchain_community.vectorstores import Meilisearch
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import JSONLoader


load_dotenv()


def metadata_editor(recode: dict, metadata: dict) -> dict:
    if "source" in metadata:
        source = metadata["source"].split("/")
        year = source[-2]
        filename = source[-1]
        new_url = f"https://raw.githubusercontent.com/foreztgump/cve_json/main/{year}/{filename}"
        metadata["source"] = new_url
    return metadata


def importer(json_file_path: str) -> None:
    # Load documents
    loader = JSONLoader(
        file_path=json_file_path,
        jq_schema="""
            {
                id: .id,
                product: .product,
                version: .version,
                vulnerability: .vulnerability | join(", "),
                description: .description,
                poc: (.poc.github + .poc.reference) | join(", ")
            }
            """,
        text_content=False,
        metadata_func=metadata_editor,
    )
    documents = loader.load()
    # print(documents)
    # print("Loaded {} documents".format(len(documents)))

    # parse json file name to get year and filename
    reference_name = json_file_path.split("/")[-1].split(".")[0]

    # Store documents in Meilisearch
    embeddings = OpenAIEmbeddings()
    vector_store = Meilisearch.from_documents(
        documents=documents,
        embedding=embeddings,
        index_name="cve",
        ids=[reference_name],
    )


def meili_update(file_list: list) -> None:
    error_list = []

    # print(len(json_file_list))
    print(f"Importing {len(file_list)} documents")
    for json_file in file_list:
        try:
            importer(json_file)
        except Exception as e:
            error_list.append(json_file)
            print(f"{json_file} failed to import for the first time with error: {e}")
        sleep(1)

    if error_list:
        for json_file in error_list:
            try:
                importer(json_file)
                error_list.remove(json_file)
            except Exception as e:
                print(
                    f"{json_file} failed to import for the second time with error: {e}"
                )
            sleep(1)
