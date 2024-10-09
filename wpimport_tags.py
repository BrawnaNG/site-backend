import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from tag.models import Tag
import mysql.connector


cnx = mysql.connector.connect(user='wpuser', password='wpuser123',
                              host='devdb.brawna.org',
                              database='wordpress')
cursor = cnx.cursor()

query = ('select A.term_id, name from wp_term_taxonomy as A join wp_terms as B on A.term_id=B.term_id where A.parent=1614')

cursor.execute(query)
for (id, name) in cursor:
    print(name)
    Tag.objects.create(name=name, old_brawna_term_id=id)
