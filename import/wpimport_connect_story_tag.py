import os, sys
import django

sys.path.append(os.path.abspath(os.path.join(__file__, *[os.pardir] * 2)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
from story.models import (
    Story,
    Chapter
)
from tag.models import Tag

import mysql.connector

DBUSER="brawna"
DBPASS="brawna"
DBHOST="localhost"
DBNAME="wordpress"

debug = False

def show_spinner(iteration):
    spinner = ['|', '/', '-', '\\']
    print(f'\r{spinner[iteration % 4]} Processing...', end='', flush=True)

cnx = mysql.connector.connect(user=DBUSER, password=DBPASS,
                              host=DBHOST,
                              database=DBNAME)
cursor = cnx.cursor()


# Get stories and associated tags
query = ('SELECT t.term_id, t.name, p.ID \
	FROM wp_term_taxonomy tt \
	JOIN wp_terms t ON t.term_id = tt.term_id \
	JOIN wp_term_relationships tr ON tr.term_taxonomy_id = tt.term_taxonomy_id \
	JOIN wp_posts p ON p.ID = tr.object_id \
	WHERE tt.parent IN (1614) AND LENGTH(t.name) <= 50 AND p.post_status = "publish" AND p.post_author > 1;')

cursor.execute(query)

spinner_count = 0
for (term_id, term_name, story_id) in cursor:
    if not debug:
        show_spinner(spinner_count)
        spinner_count += 1

    if debug:
        print (f"Add tag #{term_id} ({term_name}) Story ID: {story_id}")
    tag = Tag.objects.get(old_brawna_term_id=term_id)
    
    if Story.objects.filter(old_brawna_id=story_id).exists():
        story = Story.objects.get(old_brawna_id = story_id)
    elif Chapter.objects.filter(old_brawna_id=story_id).exists():
        chapter = Chapter.objects.get(old_brawna_id = story_id)
        if Story.objects.filter(old_brawna_id=chapter.old_brawna_parent_id).exists():
            story = Story.objects.get(old_brawna_id = chapter.old_brawna_parent_id)
        else:
            if debug:
                print (f"Unable to connect #{term_id} and Chapter ID: {story_id} and Parent: {chapter.old_brawna_parent_id}")
            continue
    else:
        if debug:
            print (f"Unable to connect #{term_id} and Story ID: {story_id}")
        continue

    # don't try to add tags more than once
    if story.tags.contains(tag):
        continue
    story.tags.add(tag)
cnx.close()
