#!/bin/bash
#


source /var/www/stage.brawna.org/stage-venv/bin/activate
if ! python manage.py makemigrations --check ; then 
    python manage.py makemigrations
fi
if ! python manage.py migrate --check ; then
    python manage.py migrate
else
    echo "No migrations"
fi

