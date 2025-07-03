import os
import django
import sys

sys.path.append(os.path.abspath(os.path.join(__file__, *[os.pardir] * 2)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from category.models import Category
import mysql.connector

DBUSER = os.environ.get("DBUSER","brawna")
DBPASS = os.environ.get("DBPASS","brawna")
DBHOST = os.environ.get("DBHOST","localhost")
DBNAME = os.environ.get("DBNAME","wordpress")


debug = False

def LoadCursor(cursor):
    for (wp_term_id, name, description, parent_id) in cursor:
        if debug:
            print(f"Loading category '{name}', with parent of '{parent_id}'")
        try:
            parent = Category.objects.get(old_brawna_term_id=parent_id)
            Category.objects.create(old_brawna_term_id=wp_term_id,
                                    name=name,
                                    description=description,
                                    parent=parent,
                                   )
        except django.db.utils.IntegrityError:
            print(f"Category {name} already exists")


# ( wp_term_id, "name", "description" )

TopLevelCategories = [
                     (1570, "transformation", ""),
                     (1584, "strength level",
                      "What level of strength does the female character or characters possess?"
                     ),
                     (1592, "muscularity",
                      "The level of muscularity of the powerful female in this story."),
                     (1696, "Height",
                      "The height of the strong female in this story."),
                     (1717, "sexual content",
                      "The degree of sexual content or situations depicted in a story."
                     ),
                     (1723, "activities", "Things that occur in this story."),
                     ]
for wp_term_id, name, desc in TopLevelCategories:
    try:
        Category.objects.create(old_brawna_term_id=wp_term_id,
                                name=name, description=desc)
    except django.db.utils.IntegrityError:
        print(f"Category {name} already exists")

cnx = mysql.connector.connect(user=DBUSER, password=DBPASS,
                              host=DBHOST,
                              database=DBNAME)
cursor = cnx.cursor()

#
# Load up all the children of TopLevelCatagories
#
query = ('select wp_terms.term_id, wp_terms.name, wp_term_taxonomy.description, wp_term_taxonomy.parent from wp_terms join wp_term_taxonomy on wp_terms.term_id = wp_term_taxonomy.term_id where wp_term_taxonomy.parent in (1570, 1584, 1592, 1696, 1717, 1723);')

cursor.execute(query)
LoadCursor(cursor)

#
# Load up all the grand-children of TopLevelCatagories
# Old brawna site had only children and grand-children
#
query = ('select wp_terms.term_id, wp_terms.name, wp_term_taxonomy.description, wp_term_taxonomy.parent from wp_terms join wp_term_taxonomy on wp_terms.term_id = wp_term_taxonomy.term_id where wp_term_taxonomy.parent in (select term_id from wp_term_taxonomy where parent in (1570, 1584, 1592, 1696, 1717, 1723));')
cursor.execute(query)
LoadCursor(cursor)
