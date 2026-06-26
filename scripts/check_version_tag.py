import argparse
import re
from pathlib import Path


def read_project_version(pyproject_path):
    pyproject = Path(pyproject_path).read_text(encoding="utf-8")
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', pyproject)
    if not match:
        raise RuntimeError("Could not find project version in {0}".format(pyproject_path))
    return match.group(1)


def main():
    parser = argparse.ArgumentParser(description="Check that a release tag matches pyproject.toml version.")
    parser.add_argument("tag_name")
    parser.add_argument("--pyproject", default="pyproject.toml")
    args = parser.parse_args()

    tag_version = args.tag_name[1:] if args.tag_name.startswith("v") else args.tag_name
    project_version = read_project_version(args.pyproject)
    if project_version != tag_version:
        raise SystemExit(
            "Tag {0} does not match pyproject.toml version {1}".format(args.tag_name, project_version)
        )
    print("version_tag_match={0}".format(project_version))


if __name__ == "__main__":
    main()
