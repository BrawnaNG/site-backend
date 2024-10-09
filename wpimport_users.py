import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import datetime
import mysql.connector
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

# MAYBE: from django.contrib.auth import get_user_model
cnx = mysql.connector.connect(user='wpuser', password='wpuser123',
                              host='devdb.brawna.org',
                              database='wordpress')
cursor = cnx.cursor()

query = ("SELECT ID, user_login, user_email FROM wp_users")

cursor.execute(query)
for (ID, user_login, user_email) in cursor:
    #print("login: '{}' email: '{}'").format(wp_user_login, wp_email)
    clean_user_login=user_login.replace(" ", "_")
    try:
        print(clean_user_login)
        user = User.objects.create_user(username=clean_user_login,
                                        email=user_email,
                                        alias=clean_user_login
                                        old_brawna_id = ID)
        user.save()
    except django.db.utils.IntegrityError:
        next

cnx.close()


"""
for (first_name, last_name, hire_date) in cursor:
  print("{}, {} was hired on {:%d %b %Y}".format(
    last_name, first_name, hire_date))

cursor.close()
cnx.close()


import mysql.connector

cnx.close()

"""

