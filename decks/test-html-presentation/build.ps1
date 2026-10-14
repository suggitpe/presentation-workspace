# PowerShell build script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$scriptDir\build.py"
