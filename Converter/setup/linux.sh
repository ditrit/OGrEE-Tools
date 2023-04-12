#!/bin/bash

{
	SCRIPT="$(realpath "${BASH_SOURCE[-1]}")" &&
	SCRIPTPATH=$(dirname "$SCRIPT") &&
	sudo apt install python3-virtualenv &&
	virtualenv $SCRIPTPATH/../../.venv &&
	source $SCRIPTPATH/../../.venv/bin/activate &&
	pip install -r $SCRIPTPATH/requirements.txt &&
	packageDir=$(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") &&
	echo $SCRIPTPATH/../.. > $packageDir/OGrEE-Tools.pth &&
	cp $SCRIPTPATH/fbxModule/* $packageDir &&
	printf "\n########################################################################################################################\n\nVirtual environment configured. To exit, type \"deactivate\". To 	enter again, type \". .venv/bin/activate\".\n" 
}||{
	printf "\n########################################################################################################################\n\nSomething wrong occured. If something is broken, ask for help.\n"
	{
		deactivate 2>/dev/null
	}||{
	 	echo ""
	 }
}
	
