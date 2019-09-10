#/usr/bin/env bash -e

VENV=venv

rm -rf $VENV

if [ ! -d "$VENV" ]
then

    PYTHON=`which python3`

    if [ ! -f $PYTHON ]
    then
        echo "could not find python"
    fi
    virtualenv -p $PYTHON $VENV

fi

. $VENV/bin/activate

pip install -r requirements.txt

chmod +x action-schedule.py.tpl

mkdir -m 777 /var/lib/snips/snips-scheduler