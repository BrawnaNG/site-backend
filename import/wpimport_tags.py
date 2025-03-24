import os, sys
import django

sys.path.append(os.path.abspath(os.path.join(__file__, *[os.pardir] * 2)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

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

query = ('select A.term_id, name from wp_term_taxonomy as A join wp_terms as B on A.term_id=B.term_id where A.parent=1614')

cursor.execute(query)
spinner_count = 0

for (id, name) in cursor:
    if debug:
        print(name)
    else:
        show_spinner(spinner_count)
        spinner_count += 1
    Tag.objects.create(name=name, old_brawna_term_id=id)
