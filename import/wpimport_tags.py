import os, sys
import django

sys.path.append(os.path.abspath(os.path.join(__file__, *[os.pardir] * 2)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from tag.models import Tag
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

query = ('SELECT DISTINCT t.term_id as id, t.name as name \
         FROM wp_term_taxonomy tt \
         JOIN wp_terms t ON t.term_id = tt.term_id \
         JOIN wp_term_relationships tr ON tr.term_taxonomy_id = tt.term_taxonomy_id \
         JOIN wp_posts p ON p.ID = tr.object_id \
         WHERE tt.parent IN (1614) AND LENGTH(t.name) <= 50 and p.post_status = "publish" AND p.post_author > 1;')

cursor.execute(query)
spinner_count = 0

for (id, name) in cursor:
    name = name.replace('\'','')
    if debug:
        print(name)
    else:
        show_spinner(spinner_count)
        spinner_count += 1
    Tag.objects.create(name=name, old_brawna_term_id=id)



