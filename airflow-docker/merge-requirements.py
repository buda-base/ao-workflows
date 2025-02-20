#!/usr/bin/env python3
"""merge requirements files
Merges two pip requirements, finding the later version if versions are specified
"""

import re
import sys


def parse_requirements(file_path):
    requirements = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                match = re.match(r'([a-zA-Z0-9\-_]+)([>=<~!]*)([0-9a-zA-Z.\-]*)', line)
                if match:
                    from packaging.specifiers import SpecifierSet
                    package, operator, version = match.groups()
                    # parse into specifier sets
                    specifier = f"{operator}{version}" if version else ""
                    if package in requirements:
                        requirements[package] &= SpecifierSet(specifier)
                    else:
                        requirements[package] = SpecifierSet(specifier)
                    # This take defaults version to 0.0.0 if not found
                    # if not version:
                    #     version = '0.0.0'
                    # if package not in requirements or parse_version(version) > parse_version(requirements[package]):
                    #     requirements[package] = [ operator, version ]
    return requirements


def merge_requirements(file1, file2, output_file):
    reqs1 = parse_requirements(file1)
    reqs2 = parse_requirements(file2)

    merged_reqs = reqs1.copy()
    # for package, version_data in reqs2.items():
    #     if package not in merged_reqs or parse_version(version_data) > parse_version(merged_reqs[package]):
    #         merged_reqs[package] = version_data
    for package, specifier in reqs2.items():
        if package in merged_reqs:
            merged_reqs[package] &= specifier
        else:
            merged_reqs[package] = specifier

    for package, specifier in sorted(merged_reqs.items()):
        output_file.write(f"{package}{str(specifier)}\n")


# Example usage
if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Merge two requirements files")
    ap.add_argument('file1', help="First requirements file")
    ap.add_argument('file2', help="Second requirements file")
    ap.add_argument('-o', '--output', type=argparse.FileType('w'), help="Output merged requirements file",
                    required=False, default=sys.stdout)
    args = ap.parse_args()
    merge_requirements(args.file1, args.file2, args.output)
