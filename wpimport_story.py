import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from story.models import Story
import mysql.connector


cnx = mysql.connector.connect(user='wpuser', password='wpuser123',
                              host='devdb.brawna.org',
                              database='wordpress')
cursor = cnx.cursor()



query = ('select ID, post_name, post_date, post_author, post_content, post_title, post_parent from wp_posts where post_status = "publish"')

cursor.execute(query)
for (ID, post_name, post_date, post_author, post_content, post_title,
     post_parent) in cursor:
        print(post_name)
        try:
            story = Story.objects.create(
                user_id = 2,
                title = post_title,
                body = post_content,
                slug = post_name,
                created_at = post_date,
                old_brawna_id = ID
                )
            # NEED USER_ID
        except django.core.exceptions.ValidationError:
            next

cnx.close()
    #Category.objects.create(name=name, description=description)
    #user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #created_at = models.DateTimeField(auto_now_add=True)
    #modified_at = models.DateTimeField(auto_now=True)
    #tags = models.ManyToManyField(Tag, blank=True)
    #categories = models.ManyToManyField(Category)
    #chapters = models.ManyToManyField("self", blank=True, null=True, symmetrical=False)


#
# Story with category and tags
#
# SELECT post.ID, post.post_title, terms.term_id, terms.name FROM wp_posts AS post JOIN wp_term_relationships AS relationship on post.ID = relationship.object_id JOIN wp_term_taxonomy AS taxonomy on relationship.term_taxonomy_id = taxonomy.term_taxonomy_id JOIN wp_terms as terms on taxonomy.term_id = terms.term_id where post.post_author not in (0, 1) LIMIT 1000;
