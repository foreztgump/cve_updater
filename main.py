from trickest_module import check_repos, check_updated_files
from cve_json import parse_and_update_json, cve_json_push
from meili_module import meili_update


def main():
    trickest_repo_folder, json_repo_folder = check_repos()
    if updated_files := check_updated_files(trickest_repo_folder):
        json_updated_list = parse_and_update_json(updated_files, json_repo_folder)
        print(f"Updated {len(updated_files)} files.")
        cve_json_push(json_repo_folder)
        meili_update(json_updated_list)


if __name__ == "__main__":
    main()
