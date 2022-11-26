# OpenHexagonLevelConverter
A tool to automatically port Open Hexagon 1.92 Levels to the new Open Hexagon
# Known Issues
- This branch uses my fork of the game to do some things that would be impossible otherwise
- timings may feel different, due to 1.92 being framerate dependant
# Usage
You may need to set `LD_LIBRARY_PATH` to `/usr/local/lib` for it to find SSVUtilsJson
```
usage: main.py [-h] {convert-pack,convert-runtime} ...

Convert packs for Open Hexagon 1.92 to be compatible with the steam version.

positional arguments:
  {convert-pack,convert-runtime}
    convert-pack        converts a pack
    convert-runtime     converts the 192_runtime to use the correct prefix

options:
  -h, --help            show this help message and exit
```
To get the 192 runtime (dependency of every pack)
```
usage: main.py convert-runtime [-h] destination_folder

positional arguments:
  destination_folder  the path the converted pack will be created at

options:
  -h, --help          show this help message and exit
```
To convert any 1.92 pack
```
usage: main.py convert-pack [-h] [--timing-options level performance_level fps_limit_lower fps_limit_upper] [--default-timing-options performance_level fps_limit_lower fps_limit_upper]
                            [--quiet]
                            source_pack destination_folder

positional arguments:
  source_pack           the 1.92 pack to be converted
  destination_folder    the path the converted pack will be created at

options:
  -h, --help            show this help message and exit
  --timing-options level performance_level fps_limit_lower fps_limit_upper
                        set timing options for a level that may depend on it (default: None)
  --default-timing-options performance_level fps_limit_lower fps_limit_upper
                        set the default timing options (default: [0.03, 240, 960])
  --quiet               with this option converted packs will not print out error messages from the original lua (default: False)
```
# Installation
## From source
### Building the JSON fixer
#### 1. Dependencies
The following dependencies need to be installed to build SSVUtilsJson
- git
- make
- cmake
- gcc
- pybind11

on debian based dstributions this can be done with this command:
```sh
sudo apt install git make cmake gcc g++ python3-pybind11
```
#### 2. Building SSVUtilsJson
This part can be skipped if you already built 1.92 from source on your system
```sh
git clone https://github.com/vittorioromeo/SSVUtilsJson.git
cd SSVUtilsJson
git checkout 57c7c45eb4e2cf8b114a153d690fb111ea520ceb
git submodule update --init --recursive
cd extlibs/SSVJsonCpp
cmake .
make
sudo make install
cd -
cd extlibs/SSVUtils
cmake .
make
sudo make install
cd -
cmake .
make
sudo make install
```
#### 3. Building the python lib
In a bash shell execute this command in the source directory
```bash
g++ -O3 -Wall -shared -std=c++11 -fPIC $(python3 -m pybind11 --includes) json_fixer.cpp -o json_fixer$(python3-config --extension-suffix) -ISSVUtilsJson/extlibs/SSVJsonCpp/include -lSSVJsonCpp -lSSVUtilsJson
```
### Installing the python dependencies
```sh
pip install -r requirements.txt
```
Everything should be ready after that, so you can look at the [Usage](#usage) section for information on how to use the tool.
