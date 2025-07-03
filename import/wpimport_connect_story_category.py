import os, sys
import django

sys.path.append(os.path.abspath(os.path.join(__file__, *[os.pardir] * 2)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
from story.models import Story
from category.models import Category

import mysql.connector

DBUSER = os.environ.get("DBUSER","brawna")
DBPASS = os.environ.get("DBPASS","brawna")
DBHOST = os.environ.get("DBHOST","localhost")
DBNAME = os.environ.get("DBNAME","wordpress")

debug = False

def show_spinner(iteration):
    spinner = ['|', '/', '-', '\\']
    print(f'\r{spinner[iteration % 4]} Processing...', end='', flush=True)

cnx = mysql.connector.connect(user=DBUSER, password=DBPASS,
                              host=DBHOST,
                              database=DBNAME)
cursor = cnx.cursor()


# Get stories and associated catagories
query = ('SELECT wp_terms.term_id as id, wp_terms.name as term_name, wp_posts.ID as story_id FROM  wp_terms \
         JOIN wp_term_taxonomy ON wp_terms.term_id = wp_term_taxonomy.term_id \
         JOIN wp_term_relationships ON  wp_term_relationships.term_taxonomy_id = \
                                        wp_term_taxonomy.term_taxonomy_id \
         JOIN wp_posts ON wp_term_relationships.object_id = wp_posts.ID \
         WHERE  wp_term_taxonomy.parent IN (1570, 1584, 1592, 1696, 1717, 1723);')

cursor.execute(query)

spinner_count = 0
for (term_id, term_name, story_id) in cursor:
    if not debug:
        show_spinner(spinner_count)
        spinner_count += 1

    if debug:
        print (f"Add category #{term_id} ({term_name}) Story ID: {story_id}")
    category = Category.objects.get(old_brawna_term_id=term_id)
    try:
        story = Story.objects.get(old_brawna_id = story_id)
    except Story.DoesNotExist:
        # Assume this is a chapter
        continue
    story.categories.add(category)
cnx.close()
