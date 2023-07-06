# OGREE-Tools: AR server
This tool is to be connected to the AR version of OGrEE-3D, to do character recognition on the label by doing several operations :
- Color Detection
- image Cropping
- Optical Character Recognition (OCR)
- Matching and correction between OCR and Regular Expressio

# How to use
## Clone this branch
First, clone the branch with the command below:

```
git clone https://github.com/ditrit/OGrEE-Tools.git
```
## Move into the directory
Go into the directory created.

```
cd OGrEE-Tools/
```

## Set up the virtual environment
We are using Python **${\color{red}3.10 \space{}only}$**.

```
python AR/setup/setup.py
```

## Activate the virtual environment

### Windows

```
.venv/Script/activate
```

### Linux

```
. .venv/bin/activate
```

## .conf.json file
You need to provide a file (named .conf.json) in the AR/ repository containing all the information about the site's labels. The range filed refers to the value range in the HSV field around the hexa color code provided.
A file named .conf.json.example is provided :

```json
{ 
    "tenants" : [
      
      {
      "customer" : "DEMO",
      "range" : 10,
      "regexps"  : [
          {  "regexp" : "FR[1-8]R[A-B]-[A-Z][0-9]{2}",      "type": "rack", "site": "FR1",  "room" : [ "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8" ], "background" : [ "orange" ]          }
        ]
      },
  
      {
      "customer" : "DEMO2",
      "range" : 10,
      "regexps"  : [
          {  "regexp" : "Site1[1-8]-[A-Z][0-9]{2}[b|BIS]?",  "type": "rack", "site": "Site1",  "room" : [ "R1", "R2" ], "background" : [ "orange" ]          },
          {  "regexp" : "[AB][1-4] ?QF[0-9]{2}",            "type": "mdi",  "site": "Site1",  "room" : [ "R1", "R2" ], "background" : [ "white" ]           },
          {  "regexp" : "Site3[A-B]-MD[A-Z][0-9]",             "type": "rack", "site": "Site1",  "room" : [ "R3", "R4" ],                                   "background" : [ "orange", "white" ] },
          {  "regexp" : "Site2[124]-[A-Z][0-9]{2}[b|BIS]?",   "type": "rack", "site": "Site2",  "room" : [ "R5", "R6", "R7" ],                            "background" : [ "orange" ]          },
          {  "regexp" : "{MDI}? ?[0-9]{2}[A-Z][0-9]{2}",    "type": "mdi",  "site": "Site2",  "room" : [ "R5", "R6", "R7" ],                            "background" : [ "red", "yellow" ]   }
        ]
      }
  
    ]
  }
```

## .env.json file
You need to provide a file (named .env.json) in the AR/ repository containing all of the needed parameters to connect to the database API (and odbc if you're connecting to dcTrack).
A file named .env.json.example is provided :

```json
{
	"api_url": "url",
	"database": "dctrack",
	"headers": {
		"Authorization": "token"
	},
	"domain": "DOMAIN",
	"site": "SITE",
	"odbc": {
		"driver": "{driver}",
		"server": "server",
		"port": "port",
		"database": "database",
		"uid": "uid",
		"pwd": "pwd"
	}
}
```

## ODBC (dcTrack)

If you are using this server to connect to a dcTrack API, you will need to download and install the latest psqlodbc release [here](https://www.postgresql.org/ftp/odbc/versions/msi/). If you are using this server to connect the AR client to OGrEE, you can skip this step.


## Start the server

```
python AR/source/Server.py [-h] [--verbose {INFO,WARNING,ERROR,DEBUG}] [--debug DEBUG]
```

The server has two optionnal parameters to specify the verbosity level and to toggle the debug mode :


   Arguments                            | Description
  --------------------------------------|---------------------------    
  `-h`, `--help`                        | show this help message and exit
  `--verbose {INFO,WARNING,ERROR,DEBUG}`| Specify the verbosity level
  `--debug DEBUG`                             | Specify a room and rack name with [ROOM].[RACK] format. If this argument is provided, the server won't try to read any picture for a label and will use this instead

## Troubleshooting

On Windows, when attempting to activate the virtual environment, if you get an error saying : `Activate.ps1 cannot be loaded because the execution of scripts is disabled on this system`, you can type

`Set-ExecutionPolicy Unrestricted -Scope Process`

into the terminal you are using. This will allow you tu load PowerShell scripts on this terminal only until it is closed.

# Contact
For any information about the project, please contact [Hervé Chibois](mailto:herve.chibois@orness.com) or [Timothé Rios](mailto:rios.timothe@gmail.com).
