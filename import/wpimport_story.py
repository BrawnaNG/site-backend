import os, sys
import django
from django.db.models import Count

sys.path.append(os.path.abspath(os.path.join(__file__, *[os.pardir] * 2)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
from story.models import Story
from story.models import Chapter
from story.models import StoryChapters

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
                    old_brawna_parent_id = 0
                )
                storychapter = StoryChapters.objects.create(story = story, chapter = chapter, order = 1)

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
            order = 0
            for (ID, post_name, post_date, post_author, post_title, post_content) in children:
                if not Chapter.objects.filter(old_brawna_id=ID).exists():
                    chapter = Chapter.objects.create(
                        user = user,
                        title = post_title,
                        created_at = post_date,
                        body = post_content,
                        old_brawna_id = ID,
                        old_brawna_parent_id = parent_brawna_id
                    )
                    storychapter = StoryChapters.objects.create(story = story, chapter = chapter, order = order)
                    order += 1

if debug:
    print("All posts with post_parent==0 processed.")

#
# Now find all the WP posts that have parents, making them Chapters for us,
# linked back to Storys created above.
# We may need to climb the tree through parents
#

debug = True
parent_tree = {}
#go through once to create the parent_tree
query = ('SELECT ID, post_parent \
         FROM wp_posts WHERE post_status = "publish" AND post_author > 1 AND \
         post_parent !=0 ORDER by ID')
cnx.reconnect()
cursor.execute(query)
for (ID, post_parent) in cursor:
    parent_tree[ID] = post_parent
cnx.close()

#Now go through the posts to add them as chapters
query = ('SELECT ID, post_name, post_date, post_author, post_title, post_parent, post_content \
         FROM wp_posts WHERE post_status = "publish" AND post_author > 1 AND \
         post_parent!=0 ORDER by ID')

cnx.reconnect()
cursor.execute(query)
for (ID, post_name, post_date, post_author,post_title, post_parent, post_content) in cursor:
    while not Story.objects.filter(old_brawna_id=post_parent).exists():
        if post_parent in parent_tree:
            post_parent = parent_tree[post_parent]
        else:
            post_parent = -1
            break

    if post_parent == -1:
        if debug:
            print(f"Did not connect {ID} to a parent, no entry in parent treer")
        continue

    try:
        parent = Story.objects.get(old_brawna_id=post_parent)
    except:
        if debug:
            print(f"Did not connect {ID} to a parent, could not find parent")
        continue

    if not Chapter.objects.filter(old_brawna_id=ID).exists():
        chapter = Chapter.objects.create(
            user = user,
            title = post_title,
            created_at = post_date,
            body = post_content,
            old_brawna_id = ID,
            old_brawna_parent_id = parent.old_brawna_id
        )
        order = StoryChapters.objects.filter(story=parent).count() + 1
        storychapter = StoryChapters.objects.create(story = parent, chapter = chapter, order = order)    

cnx.close()

#set has chapters true for anything with more than one chapter
Story.objects.annotate(chapter_count=Count('chapters')).filter(chapter_count__gt=1).update(has_chapters=True);