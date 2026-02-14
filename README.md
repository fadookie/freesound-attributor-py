# freesound-attributor.py
This project represents my third attempt to make a small tool to automate the process of generating an attribution list for samples downloaded from [Freesound.org](https://freesound.org). For why this is necessary, [please read the FAQ](https://freesound.org/help/faq/#what-do-i-need-to-do-to-legally-use-the-files-on-freesound). The first two attempts I made were GUI programs designed for general ease-of-use. This is a command-line only utility written in Python. It's based on a script I made for myself to use but I decided to clean it up enough to make it suitable for general-purpose use, for users comfortable with the command line.

I tried to make it easy enough to use that it can be called without any arguments and have reasonable default behavior. So if you don't already know how to use the command line, think it would be possible to spend a little bit of time on a tutorial - all you need are the basics of changing directories and running programs. Explaining how to use the command line is outside the scope of this README, but you can find plenty of help online.

# Installation
This is a Python 3 script with no external dependencies, designed to be easy to install. [Download a Python 3 runtime](https://www.python.org/downloads/) if you don't already have one. Then clone or download this repo or just the [freesound-attributor.py](./freesound-attributor.py) script. It was developed with Python 3.14 but should work with any version of Python 3 (I think!)

# Workflow
The intended workflow for this tool is to download whatever samples you need from Freesound.org and integrate them into your project. It's important not to modify the names of the files, because this tool works by parsing the names of the files to figure out the name, author, and Freesound URL. If you change the name of the file after the second double underscore, the tool will list the updated name but will still find the correct URL if the author and sound ID number have not been modified.

Errors will be logged to the terminal if files are found that match the included file extensions but don't conform to the Freesound file naming scheme. This will not prevent the remaining valid ones from being written to the attribution file.

# Usage
This document will use `python3` as the alias for your python interpreter but it may also just be called `python` on your system.

For help on usage, run `python3 freesound-attributor.py -h` which should print something like this:

```
usage: freesound-attributor.py [-h] [-r ROOTDIR] [-e EXTENSIONS [EXTENSIONS ...]]
                               [-o OUTPUT] [-p PROJECTTYPE] [-c]

Examines a directory and subdirectories for audio files and attempts to collect and save
attribution information for the ones that look like they came from Freesound.org

options:
  -h, --help            show this help message and exit
  -r, --rootdir ROOTDIR
                        root directory to search for audio files, defaults to current
                        directory
  -e, --extensions EXTENSIONS [EXTENSIONS ...]
                        space-delimited, case-insensitive file extensions to include in
                        search, ex: ogg wav flac. defaults to all valid file extensions on
                        Freesound.
  -o, --output OUTPUT   path to output file where attribution information will be saved,
                        defaults to attribution.txt
  -p, --projecttype PROJECTTYPE
                        type of project this is, ex. film, game, etc. defaults to "project".
  -c, --collectlicenses
                        attempts to obtain the creative commons license link for each file.
                        This is slower and requires an internet connection as we have to
                        query Freesound for each file, but provides more complete
                        attribution information to better comply with CC licenses.
```

As mentioned previously, all arguments are optional and should have reasonable defaults. By default, `--collectlicenses` is disabled as this causes the tool to run more slowly and requires an internet connection. But feel free to turn it on, doing so will provide output that conforms a bit better to the attribution requirements for applicable CC licenses.

To run the attributor on your audio files, either change to the root directory containing the files for your project and run the tool like so:
```shell
cd /PATH/TO/AUDIO/FILES
python3 /PATH/TO/freesound-attributor.py
```

or you can pass the `--rootdir` argument instead:
```shell
cd /PATH/TO/FREESOUND-ATTRIBUTOR
python3 freesound-attributor.py --rootdir /PATH/TO/AUDIO/FILES
```

By default, the attribution file will be saved to the current directory as `attribution.txt` but this can be changed using the `--output` argument.

# Implementation Trade-offs
I wanted to provide a bit of rationale behind some of the technical decisions I made in this project. While my previous attempts to make a tool like this were more user-friendly for non-technical people, I don't really have time to do cross-platform GUI development on a project like this. But I did want to spend an evening cleaning up this script for a general audience.

In addition, the performance of the `--collectlicenses` mode could be greatly improved by using [asyncio with the aiohttp library](https://pawelmhm.github.io/asyncio/python/aiohttp/2016/04/22/asyncio-aiohttp.html) to perform network requests in parallel. However, this would increase the complexity for users to install the package as it would require them to understand how to install PIP packages and (ideally) manage virtual environments. So I opted for the more naive, synchronous approach which didn't require any external dependencies, especially as I only expect people to need to run this tool once or twice at the end of a project.

Lastly, Freesound does provide an API which could be used to fetch data needed by the `--collectlicenses` mode. I looked into this, but unfortunately there was no way to query the API without an auth token. And to obtain an auth token requires manual approval from Freesound. I think without a way for certain endpoints to be queried without an auth token, this makes it unsuitable for use in a tool such as this because each user would need to manually request a token and wait for it to get approved in order to be able to use it. So I opted for a simple web scraping solution. This could break in the future if the formats of CC license links change, or Freesound adds additional links to [creativecommons.org](https://creativecommons.org/) on the sound detail page.