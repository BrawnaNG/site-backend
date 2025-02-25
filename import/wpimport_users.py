import os
import sys
import django

sys.path.append(os.path.abspath(os.path.join(__file__, *[os.pardir] * 2)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import datetime
import mysql.connector
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

debug = False

def show_spinner(iteration):
    spinner = ['|', '/', '-', '\\']
    print(f'\r{spinner[iteration % 4]} Processing...', end='', flush=True)

DBUSER = os.environ.get("DBUSER")
DBPASS = os.environ.get("DBPASS")
DBHOST = os.environ.get("DBHOST")
DBNAME = os.environ.get("DBNAME")

cnx = mysql.connector.connect(user=DBUSER, password=DBPASS,
                              host=DBHOST,
                              database=DBNAME)
cursor = cnx.cursor()

query = ("SELECT ID, user_login, user_email FROM wp_users")

cursor.execute(query)
spinner_count = 0
for (ID, user_login, user_email) in cursor:
    if debug == True:
        print("login: '{}' email: '{}'").format(wp_user_login, wp_email)
    else:
        show_spinner(spinner_count)
        spinner_count += 1
    clean_user_login=user_login.replace(" ", "_")
    try:
        user = User.objects.create_user(username=clean_user_login,
                                        email=user_email,
                                        alias=clean_user_login,
                                        old_brawna_id = ID)
        user.save()
    except django.db.utils.IntegrityError:
        next

cnx.close()
