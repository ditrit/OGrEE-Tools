# Contact
For any information about the project, please contact Hervé Chibois or Vincent TAUFFLIEB.

# OGREE-Tools: Label Reader API
Python API to be connected to a Unity Application, to do character recognition on the label by doing several operations
- Color Detection
- image Cropping
- Optical Character Recognition (OCR)
- Matching and correction between OCR and Regular Expression

# Link to the Unity Application Repository:
https://github.com/ditrit/OGrEE-3D/tree/master-ar

# Information before using
## .conf.json file
You need to provide a file (named .conf) containing all the information about the customer. The range filed refers to the value range in the HSV field around the hexa color code provided.
It should be as follows:

```
{ 
  "tenants" : [
    {
    "customer" : "MYCUST1",
    "range" : 10,
    "regexps"  : [
       {  "regexp" : "Ro[1-3]-Rack[A-B][0-9]",  "type": "rack", "site": "MYSITE", "room" : [ "Ro1", "Ro2", "Ro3" ], "background" : [ "orange", "white", "#4287f5" ] },
        ]
     },

     {
    "customer" : "MYCUST2",
    "range" : 10,
    "regexps"  : [
       {  "regexp" : "Ro[1-3]-Rack[A-B][0-9]",  "type": "rack", "site": "MYSITE", "room" : [ "Ro1", "Ro2", "Ro3" ], "background" : [ "orange", "white", "#4287f5" ] },
        ]
     },
   ]
}
```

## .env.json file
You need to provide a file (named .env) containing all of the API parameters as below:

```
{
    "api_url": "proto://ipaddress:port",
    "api_endpoint" : { "myEndpoint" : "route/to/object" },
    "api_token": "Bearer <Token>"
}
```

Example 
```
{
    "api_url": "http://172.16.24.31:3001" ,
    "api_url": "https://myapi.mydomain" ,
    "api_endpoint" : { "allracks" : "api/racks" },
    "api_endpoint" : { "allrooms" : "api/racksapi/rooms" },
    "api_token": "Bearer <token>"
}
```

## What does the script do?
The function takes all images in a folder and performs color detection, cropping, OCR, and correction on all of them. The label that was read is returned in the terminal as well as Debug info.

# How to use
## Clone this branch
First, clone the branch with the command below:

```
git clone -b dev-label --single-branch https://github.com/ditrit/OGrEE-Tools.git
```
## Move into the directory
Go into the directory created.

```
cd OGrEE-Tools
```

## Verify all the requirements
We are using Python 3.9.
To ensure you have all of the required packages installed, please install the following modules :

```
torch >= 1.11.0
torchvision >= 0.12.0
opencv-python == 4.5.4.60
Pillow >= 8.0.1
requests >= 2.25.0
easyocr >= 1.4.2
opencv-contrib-python == 4.5.4.60
Flask >= 2.0.3
gevent >= 21.12.0
```
To do so, run the commands for your OS:

LINUX

```
sudo apt install pip
sudo pip install -r requirements.txt
```

WINDOWS

```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
pip install -r requirements.txt
```

## Add the .env file and the .conf file to /Configuration_Files directory
Please ensure to have added your .env file and the .conf file into the directory /Configuration_Files.
If the API URL or the token is wrong, the script will throw an exception.

## FOR STANDALONE USE: Call ogLabelReader.py with the right arguments
The function to call is LabelReader.py. It should be used as follows:

```
ogLabelReader.py [-h] --mode {image,imagedir} --path PATH --site SITE [--verbose {INFO,WARNING,ERROR,DEBUG}]
```

It takes 3 required arguments as input: --mode (to process a single image or all of the images in a directory), --path (path to the image/directory to use) and --site (name of the customer and the site) which should be in the following format <MYCUS>.<MYSITE>

The function also takes an optional argument: --verbose (display different level of verbose), INFO is the lowest level (Default Level) and DEBUG is the highest level.
  
```
python ogLabelReader.py --mode imagedir --path /path/to/the/folder/with/all/the/images --site MYCUST.MYSITE --verbose DEBUG
python ogLabelReader.py --mode image --path /path/to/the/folder/with/all/the/images/image.jpg --site MYCUST.MYSITE --verbose INFO
```
## FOR USE AS A SERVER(backend for Unity Application): Call ogLabelServer.py
The function to call is LabelReader.py. It should be used as follows:

```
python ogLabelServer.py
```
## Troubleshooting
You may need to do some additional steps if you have the error below :
  
```
The function is not implemented. Rebuild the library with Windows, GTK+ 2.x or Cocoa support. If you are on Ubuntu or Debian, install libgtk2.0-dev and pkg-config, then re-run cmake or configure script in function 'cvNamedWindow'
```
  
In this case, please run the following commands:
  
LINUX
```
sudo pip uninstall opencv-python-headless
sudo pip uninstall opencv-python
sudo pip install opencv-python==4.5.4.60
```
  
WINDOWS
  
```
pip uninstall opencv-python-headless
pip uninstall opencv-python
pip install opencv-python==4.5.4.60
```

