import hashlib
import json
import os

from git_module import GitModule

# get the current working directory
cwd = os.getcwd()


def check_repos():
    print("Checking repos...")
    # create a trickest folder if it doesn't exist
    trickest_repo_folder = os.path.join(cwd, "trickest")
    if not os.path.exists(trickest_repo_folder):
        os.mkdir(trickest_repo_folder)
        git_module = GitModule(trickest_repo_folder)
        git_module.clone_from_trickest()

    # create a json folder if it doesn't exist
    json_repo_folder = os.path.join(cwd, "json")
    if not os.path.exists(json_repo_folder):
        os.mkdir(json_repo_folder)
        git_module = GitModule(json_repo_folder)
        git_module.clone_from_json()

    return trickest_repo_folder, json_repo_folder


def check_updated_files(trickest_repo_folder):
    print("Checking updated files...")
    # create hash file if it doesn't exist
    trickest_hash_file = os.path.join(cwd, "trickest_hash.json")
    if not os.path.exists(trickest_hash_file):
        f = open(trickest_hash_file, "w")
        f.close()

    # update the trickest repo
    git_module = GitModule(trickest_repo_folder)
    git_module.pull()

    # create hash of all files in trickest repo to a dictionary
    trickest_hash = {}
    retry_list = []
    for root, dirs, files in os.walk(trickest_repo_folder):
        # Only walk the subdirectories, excluding the root folder and folders without a digit as the name
        if root != trickest_repo_folder and any(
            dir.isdigit() for dir in os.path.basename(root)
        ):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.sha1(f.read()).hexdigest()
                    trickest_hash[file_path] = file_hash
                except Exception as e:
                    print(f"Error: {e} on {file_path}. - adding to retry list.")
                    retry_list.append(file_path)

    # retry the files that failed
    for file_path in retry_list:
        try:
            with open(file_path, "rb") as f:
                file_hash = hashlib.sha1(f.read()).hexdigest()
            trickest_hash[file_path] = file_hash
        except Exception as e:
            print(f"Error: {e} on {file_path} after retry - skipping.")

    # read the hash file
    with open(trickest_hash_file, "r") as f:
        if file_contents := f.read():
            old_trickest_hash = json.loads(file_contents)
        else:
            old_trickest_hash = {}

    updated_files = [
        file_path
        for file_path, file_hash in trickest_hash.items()
        if file_path not in old_trickest_hash
        or file_hash != old_trickest_hash[file_path]
    ]
    # update the hash file
    with open(trickest_hash_file, "w") as f:
        json.dump(trickest_hash, f)

    return updated_files
