function Write-Error($message) {
    [Console]::ForegroundColor = 'red'
    [Console]::Error.WriteLine($message)
    [Console]::ResetColor()
}

function Write-Host($message) {
    [Console]::ForegroundColor = 'cyan'
    [Console]::Error.WriteLine($message)
    [Console]::ResetColor()
}

$rootDir = (Resolve-Path "$PSScriptRoot/../../..").Path

Write-Host "Creating virtual env at $rootDir\.venv..."
try {
    python3.10 -m venv $rootDir/.venv
} catch{
    Write-Error "Error while creating virtual env."
    exit
}

Write-Host "Activating virtual env..."
try {
    . "$rootDir/.venv/Scripts/Activate.ps1"
} catch {
    Write-Error "Error while activating virtual env."
    exit
}

Write-Host "Installing requirements..."
try {
    python -m pip install -r $PSScriptRoot/../requirements.txt
} catch {
    Write-Error "Error while installing requirements, check if $((Resolve-Path $PSScriptRoot/../requirements.txt).Path) exists and is correctly configured."
    deactivate
    exit
}

try {
    python -m pip install $PSScriptRoot/fbx-2020.3.4-cp310-none-win_amd64.whl
} catch {
    Write-Error "Error while installing requirements, check if $((Resolve-Path $PSScriptRoot/fbx-2020.3.4-cp310-none-win_amd64.whl).Path) exists and is for python 3.10."
    deactivate
    exit
}

$packageDir = python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"

Write-Host "Adding $((Resolve-Path $PSScriptRoot/../FbxCommon.py).Path) to $packageDir..."
try {
    Copy-Item -Path $PSScriptRoot/../FbxCommon.py -Destination $packageDir
} catch {
    Write-Error "Error while moving FbxCommon.py, check if the file is present at $((Resolve-Path $PSScriptRoot/../).Path)"
    deactivate
    exit
}

Write-Host "Adding $rootDir to python path..."
try {
    Set-Content $packageDir/OGrEE-Tools.pth $rootDir
} catch {
    Write-Error "Error while writing $packageDir/OGrEE-Tools.pth"
    deactivate
    exit
}

Write-Host '

##############################################################################################################

Virtual environment configured. To exit, type "deactivate". To enter again, type ".\.venv\Scripts\activate".'