from trickest_module import check_repos, check_updated_files
from cve_json import parse_and_update_json, cve_json_push


def main():
    trickest_repo_folder, json_repo_folder = check_repos()
    if updated_files := check_updated_files(trickest_repo_folder):
        parse_and_update_json(updated_files, json_repo_folder)
        cve_json_push(json_repo_folder)


if __name__ == "__main__":
    main()
