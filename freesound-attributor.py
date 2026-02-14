"""
Copyright © 2026 Eliot Lash

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import argparse
import os
import re
import sys
import urllib.request
from pathlib import Path

CC_LICENSE_URL_REGEX = re.compile(r'(?<=")https?://creativecommons\.org/(licenses|publicdomain)/.*?(?=")', re.IGNORECASE)

parser = argparse.ArgumentParser(
                    prog='freesound-attributor.py',
                    description='Examines a directory and subdirectories for audio files and attempts to collect and save attribution information for the ones that look like they came from Freesound.org',
)

parser.add_argument(
    '-r', '--rootdir',
    help='root directory to search for audio files, defaults to current directory',
    default=os.getcwd()
)

parser.add_argument(
    '-e', '--extensions',
    nargs='+',
    help='space-delimited, case-insensitive file extensions to include in search, ex: ogg wav flac. defaults to all valid file extensions on Freesound.',
    default=['ogg', 'wav', 'flac', 'fla', 'mp3', 'aiff', 'aif']
)

parser.add_argument(
    '-o', '--output',
    help='path to output file where attribution information will be saved, defaults to attribution.txt',
    default='attribution.txt'
)

parser.add_argument(
    '-p', '--projecttype',
    help='type of project this is, ex. film, game, etc. defaults to "project".',
    default='project'
)

parser.add_argument(
    '-c', '--collectlicenses',
    help='attempts to obtain the creative commons license link for each file. This is slower and requires an internet connection as we have to query Freesound for each file, but provides more complete attribution information to better comply with CC licenses.',
    action='store_true',
    default=False
)

args = parser.parse_args()
print(f"Got arguments: {args}")

def fetch_license_url(url: str) -> str:
    print(f"Fetching license URL for sample at {url}")
    with urllib.request.urlopen(url, data=None) as response:
        body = response.read().decode(response.headers.get_content_charset())
        cc_license_url_match = CC_LICENSE_URL_REGEX.search(body)
        assert cc_license_url_match is not None, f"Unable to obtain CC license URL for sound at URL:{url}"
        cc_license_url = cc_license_url_match.group(0)
        return cc_license_url

valid_files: list[str] = []
invalid_files: list[str] = []

def parse_filename(path: Path) -> None:
    # print(f"parse_filename({path})")
    basename = os.path.basename(path)
    components = basename.split("__")
    if len(components) < 3:
        invalid_files.append(str(path) + '\n')
        return

    sound_id = components[0]
    username = components[1]
    filename_short = components[2]
    url = f"https://freesound.org/people/{username}/sounds/{sound_id}/"
    if args.collectlicenses:
        license_url = fetch_license_url(url)
        valid_files.append(f"{filename_short} by {username} from {url} under license: {license_url}")
        return
    else:
        valid_files.append(f"{filename_short} by {username} from {url}")
        return

extensions = [f".{ext}" for ext in args.extensions]
wav_files_relative = (p.resolve() for p in Path(args.rootdir).glob("**/*") if p.is_file() and p.suffix.lower() in extensions)

for wav_file_relative in wav_files_relative:
    parse_filename(wav_file_relative)

output_lines: list[str] = []

if args.collectlicenses:
    output_lines.append(f"This {args.projecttype} uses the following sounds from freesound.org:")
else:
    output_lines.append(f"This {args.projecttype} uses the following sounds from freesound.org under Creative Commons licenses, see links for license details.")
for attribution_str in valid_files:
    output_lines.append(f" * {attribution_str}")

output_str = '\n'.join(output_lines)
with open(args.output, "w") as output_file:
    output_file.write(output_str)

print(f"\nWrote valid attribution data to {args.output}:\n\n{output_str}")

if len(invalid_files) > 0:
    sys.stderr.write("\nFound files with matching extensions which did not conform to the expected Freesound naming convention:\n")
    sys.stderr.writelines(invalid_files)
    exit(1)

