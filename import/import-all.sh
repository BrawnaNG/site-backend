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
echo "Importing users"
python wpimport_users.py
echo -e "\nImporting tags"
python wpimport_tags.py
echo -e "\nImporting categories"
python wpimport_category.py
echo -e "\nImporting stories"
python wpimport_story.py
echo -e "\nConnecting stories and categories"
python wpimport_connect_story_category.py
echo -e "\nConnecting stories and tag"
python wpimport_connect_story_tag.py
