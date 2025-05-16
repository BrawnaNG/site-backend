#!/bin/bash
#

export DBUSER="brawna"
export DBPASS="brawna"
export DBHOST="localhost"
export DBNAME="wordpress"

# check python
if ! python -m django --version >/dev/null
then
    echo "Activate venv first"
    exit
fi

rm ../db.sqlite3
python ../manage.py migrate
python wpimport_users.py
python wpimport_tags.py
python wpimport_category.py
python wpimport_story.py
python wpimport_connect_story_category.py
python wpimport_connect_story_tag.py