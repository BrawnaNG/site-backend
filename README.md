# tag
list of all tags by pagination : http://127.0.0.1:8000/api/v1/tag/?page=1 <br />
search in tags : http://127.0.0.1:8000/api/v1/tag/?q <br />
add a tag : http://127.0.0.1:8000/api/v1/tag/add <br />
delete a tag : http://127.0.0.1:8000/api/v1/tag/change/'name' (by admin) <br />
update a tag : http://127.0.0.1:8000/api/v1/tag/change/'name' (by admin) <br />

# story
list of all story by pagination : http://127.0.0.1:8000/api/v1/story/list/?page=1 <br />
list of user story : 127.0.0.1:8000/api/v1/story/list/?username='username' <br />
add a story : http://127.0.0.1:8000/api/v1/story/add/ <br />
update a story : http://127.0.0.1:8000/api/v1/story/change/'slug' <br />
delete a story : http://127.0.0.1:8000/api/v1/story/change/'slug' <br />

# saved story
list of saved story by pagination : http://127.0.0.1:8000/api/v1/story/save-story-list/ <br />
saved story : http://127.0.0.1:8000/api/v1/story/save-story/'slug' <br />
delete saved story : http://127.0.0.1:8000/api/v1/story/delete-saved-story/'slug' <br />

# comment
list all comment by pagination: http://127.0.0.1:8000/api/v1/comment/list/ (for admin) <br />
list of all story comment : http://127.0.0.1:8000/api/v1/comment/list/?storyslug='slug' <br />
add a comment : http://127.0.0.1:8000/api/v1/comment/add/'story-slug'<br />
update a comment : http://127.0.0.1:8000/api/v1/comment/change/'comment-id' <br />
delete a comment : http://127.0.0.1:8000/api/v1/comment/change/'comment-id' <br />
list of user comments : http://127.0.0.1:8000/api/v1/comment/user-comment/ <br />
list of story comments : http://127.0.0.1:8000/api/v1/comment/story-comment/'story-slug' <br />

# category
list of all category : http://127.0.0.1:8000/api/v1/category/list/ <br />
add a category : http://127.0.0.1:8000/api/v1/category/add/ <br />
update a category : http://127.0.0.1:8000/api/v1/category/change/'name' <br />
delete a category : http://127.0.0.1:8000/api/v1/category/change/'name' <br />

# search for get stories
search with body, brief, alias name : http://127.0.0.1:8000/api/v1/story/search/?q='a' <br />
search by category : http://127.0.0.1:8000/api/v1/story/search/?category='a' <br />
search by user : http://127.0.0.1:8000/api/v1/story/search/?user='a' <br />
search by tag : http://127.0.0.1:8000/api/v1/story/search/?tag='tag' <br />


# account
registere user : http://127.0.0.1:8000/api/v1/accounts/registration/ <br />
activate user : http://127.0.0.1:8000/api/v1/accounts/activation/'token'  <br />
show last 10 users : http://127.0.0.1:8000/api/v1/accounts/last-user <br />
list of all users : http://127.0.0.1:8000/api/v1/accounts/list/ (for admin) <br />
change password by admin : http://127.0.0.1:8000/api/v1/accounts/change-password-admin/'email' <br />
disable user by admin : http://127.0.0.1:8000/api/v1/accounts/disable-user-admin/'email' <br />
search in user accounts by admin : http://127.0.0.1:8000/api/v1/accounts/list/?q='str' <br />

# jwt
get token : http://127.0.0.1:8000/api/token/ <br />
refresh token : http://127.0.0.1:8000/api/token/refresh/ <br />
admin username : Admin <br />
admin password : admin <br />
