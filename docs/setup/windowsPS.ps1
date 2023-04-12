try {
pip install virtualenv;
virtualenv $PSScriptRoot/../../.venv;
. "$PSScriptRoot/../../.venv/Scripts/Activate.ps1";
pip install -r $PSScriptRoot/requirements.txt;
Write-Output '

##############################################################################################################

Virtual environment configured. To exit, type "deactivate". To enter again, type ".\.venv\Scripts\activate".';
}
catch {
Write-Output '

########################################

Something wrong occured. If something is broken, ask for help.';
}