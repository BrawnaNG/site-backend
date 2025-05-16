import os, sys
import django

sys.path.append(os.path.abspath(os.path.join(__file__, *[os.pardir] * 2)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
from story.models import Story
from story.models import Chapter
from category.models import Category

import mysql.connector

debug = False


DBUSER="brawna"
DBPASS="brawna"
DBHOST="localhost"
DBNAME="wordpress"

def show_spinner(iteration):
    spinner = ['|', '/', '-', '\\']
    print(f'\r{spinner[iteration % 4]} Processing...', end='', flush=True)

cnx = mysql.connector.connect(user=DBUSER, password=DBPASS,
                              host=DBHOST,
                              database=DBNAME)
cursor = cnx.cursor()

#
# Order by ID so we deal with Stories before Chapters
#
# With post_parent = 0 the WP post is either a stand-alone story without
# chapters(and thus a Story and Chapter for us), or it is a multi-chapter story
# (and thus a Story with Chapters to be added later for us)
#
query = ('SELECT ID, post_name, post_date, post_author, post_title, \
         post_parent, post_content \
         FROM wp_posts WHERE post_status = "publish" AND post_author > 1 AND \
         post_parent=0 ORDER by ID')
cursor.execute(query)
posts = cursor.fetchall()

spinner_count = 0
for (ID, post_name, post_date, post_author, post_title,
     post_parent, post_content) in posts:
        show_spinner(spinner_count)
        spinner_count += 1
        if debug:
            print("")
            print(f"Importing {ID} {post_name}")

        user = User.objects.get(old_brawna_id=post_author)

        # print("TODO Check it's not already loaded")
        if debug:
            print(f"Search for wp_posts with '{post_name}-chapter-%' AND post_author is the same")
        query = (f"SELECT ID, post_name, post_date, post_author, post_title, \
                 post_content \
                 FROM wp_posts WHERE post_name LIKE '{post_name}-chapter-%' \
                 AND post_author='{post_author}' order by post_author;")
        cnx.reconnect()
        cursor.execute(query)
        children = cursor.fetchall()
        if not children:
            #
            # No children, this is a complete work. Make a Story with the
            # metadata, make a connect chapter with the content.
            #
            if debug:
                print("No chapters found, adding a Story")
            story = Story.objects.create(
                user = user,
                title = post_title,
                slug = post_name,
                created_at = post_date,
                # brief = post_content,
                has_chapters = False,
                old_brawna_id = ID,
                old_brawna_parent_id = 0,
                is_published = True
            )
            if debug:
                print("Put the content in a Chapter, connect that to the Story just created")

            if not Chapter.objects.filter(old_brawna_id=ID).exists():
                chapter = Chapter.objects.create(
                    user = user,
                    title = post_title,
                    created_at = post_date,
                    body = post_content,
                    old_brawna_id = ID,
                    old_brawna_parent_id = 0,
                    story = story
                )
        else:
            if debug:
                print ("Found children, make wp_post a Story, fetch all the retrieved 'chapter' posts into attached Chapters")
            #
            # Make the post into a Story, then find all it's children, and make
            # those connected Chapters
            #
            story = Story.objects.create(
                user = user,
                title = post_title,
                slug = post_name,
                created_at = post_date,
                # brief = post_content,
                has_chapters = True,
                old_brawna_id = ID,
                old_brawna_parent_id = 0,
                is_published = True
            )
            parent_brawna_id = ID
            for (ID, post_name, post_date, post_author, post_title, post_content) in children:
                if not Chapter.objects.filter(old_brawna_id=ID).exists():
                    chapter = Chapter.objects.create(
                        user = user,
                        title = post_title,
                        created_at = post_date,
                        body = post_content,
                        old_brawna_id = ID,
                        old_brawna_parent_id = parent_brawna_id,
                        story = story,
                    )

if debug:
    print("All posts with post_parent==0 processed.")

#
# Now find all the WP posts that have parents, making them Chapters for us,
# linked back to Storys created above.
# We may need to climb the tree through parents
#
query = ('SELECT ID, post_name, post_date, post_author, post_title, post_parent \
         FROM wp_posts WHERE post_status = "publish" AND post_author > 1 AND \
         post_parent!=0 ORDER by ID')

debug = False
cnx.reconnect()
cursor.execute(query)

parent_tree = {}

for (ID, post_name, post_date, post_author,post_title, post_parent) in cursor:

    parent_tree[ID] = post_parent

    while not Story.objects.filter(old_brawna_id=post_parent).exists():
        if post_parent in parent_tree:
            post_parent = parent_tree[post_parent]
        else:
            post_parent = -1
            break

    if post_parent == -1:
        print(f"Did not connect {ID} to a parent, might be a sub-chapter")
        continue

    if debug:
        print(f"Importing {ID} {post_name}, connecting to {post_parent}")
    try:
        parent = Story.objects.get(old_brawna_id=post_parent)
    except:
        print(f"Did not connect {ID} to a parent might be a sub-chapter")

    if not Chapter.objects.filter(old_brawna_id=ID).exists():
        chapter = Chapter.objects.create(
            user = user,
            title = post_title,
            created_at = post_date,
            body = post_content,
            old_brawna_id = ID,
            old_brawna_parent_id = parent.old_brawna_id,
            story = parent,
    )

cnx.close()
