#### Installation on Windows:
1. Ensure Java is installed on your machine (you can check & install it here: https://java.com/download/)
2. Ensure Python3 & pip installed on your machine (you can download and install it here: https://www.python.org/downloads/)
3. Download this repository
4. Download & extract browsermobproxy: 
https://github.com/lightbody/browsermob-proxy/releases/download/browsermob-proxy-2.1.4/browsermob-proxy-2.1.4-bin.zip
5. Download & extract chromedriver that matches your Chrome version: https://chromedriver.chromium.org/downloads
6. Copy chromedriver.exe to the script directory
7. In the script directory, open "config.txt", and replace it content with absolute path to browsermobproxy file (relative path from browsermobproxy archive, downloaded on step 4, is usually ".\browsermob-proxy-2.1.4\bin\browsermob-proxy")
8. Open command promt in the script directory and run this command:
```console
pip istall requirements.txt
```
9. After that you should be able to run the script. Check it by run this command in command promt:
```console
python3 -i list_of_links.txt -o test.json -l
```
After the script execution completes, you should see file "test.json" which contains requests logs.

#### Script arguments:
- -i - (mandatory) name of the input file, which contains list of pages to check (one page per line). Example: "-i input.txt"
- -o - (mandatory) name of output file, where script will save results. Example: "-o output.json"
- -p - (optional) the script will check the requests on page
- -l - (optional) the script will check the requests on each link within each page
- -h - show help & exit

Note: at least one (or both) flags -l -p should be provided.
