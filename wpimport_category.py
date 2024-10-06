import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from category.models import Category
import mysql.connector


cnx = mysql.connector.connect(user='wpuser', password='wpuser123',
                              host='devdb.brawna.org',
                              database='wordpress')
cursor = cnx.cursor()

query = ('select A.term_id, name, description from wp_term_taxonomy as A join wp_terms as B on A.term_id=B.term_id where taxonomy="category" and description <> ""')

cursor.execute(query)
for (id, name, description) in cursor:
    print(name)
    Category.objects.create(name=name, description=description)
