import re
import os
import json
import urllib.parse
from git_module import GitModule


def parse_and_update_json(file_list, json_repo_folder):
    print("Parsing and updating json files...")
    for file in file_list:
        # read the file
        with open(os.path.abspath(file), "r", encoding="utf-8") as f:
            data = f.read()

        # get the cve id
        cve_id = re.search(r"(CVE-\d{4}-\d{1,7})", data)
        if cve_id:
            cve_id = cve_id[1]
        else:
            print(f"Error: cve id not found in file: {file}")
            continue

        # get the product
        product = re.search(r"label=Product&message=(.*?)&", data)
        product = urllib.parse.unquote(product[1].strip()) if product else "n/a"
        # get the version
        version = re.search(r"label=Version&message=(.*?)&", data)
        version = urllib.parse.unquote(version[1].strip()) if version else "n/a"
        # get the vulnerability
        vulnerability = re.findall(r"label=Vulnerability&message=(.*?)&", data)
        if vulnerability:
            vulnerability = [urllib.parse.unquote(v.strip()) for v in vulnerability]
        else:
            vulnerability = "n/a"
        # get the description
        description = re.search(r"Description(.*?)### POC", data, re.DOTALL)
        if description:
            description = description[1].strip().replace("\n\n", " ")
        else:
            print(f"Error: description not found in file: {file}")
            description = "Unknown"

        if poc_text := re.search(r"POC(.*?)$", data, re.DOTALL):
            poc_text = poc_text[1].strip()

            # get the reference
            reference = re.search(
                r"#### Reference(.*?)#### Github", poc_text, re.DOTALL
            )
            if reference:
                reference = reference[1].strip()
                reference = [
                    line.lstrip("- ").strip() for line in reference.split("\n") if line
                ]
            else:
                reference = "Unknown"

            # get the github
            github = re.search(r"#### Github(.*?)$", poc_text, re.DOTALL)
            if github:
                github = github[1].strip()
                github = [
                    line.lstrip("- ").strip() for line in github.split("\n") if line
                ]
            else:
                github = "Unknown"

            poc = {"reference": reference, "github": github}
        else:
            print(f"Error: poc not found in file: {file}")
            poc = {"reference": "Unknown", "github": "Unknown"}

        # create a dictionary with the data
        data_dict = {
            "id": cve_id,
            "product": product,
            "version": version,
            "vulnerability": vulnerability,
            "description": description,
            "poc": poc,
        }

        # parse file name and dir name
        file_name = os.path.basename(file)
        dir_name = os.path.basename(os.path.dirname(file))

        # create a json file name
        json_file_name = f"{cve_id}.json"
        json_file_path = os.path.join(json_repo_folder, dir_name, json_file_name)

        # check if the json file exists, if not create one, if yes, update it
        if not os.path.exists(json_file_path):
            with open(json_file_path, "w") as f:
                json.dump(data_dict, f, indent=4)
        else:
            with open(json_file_path, "r") as f:
                json_data = json.load(f)
            json_data.update(data_dict)
            with open(json_file_path, "w") as f:
                json.dump(json_data, f, indent=4)


def cve_json_push(json_repo_folder):
    print("Pushing json files to git...")
    git_module = GitModule(json_repo_folder)
    git_module.add()
    git_module.commit("Update cve json files")
    git_module.push()
