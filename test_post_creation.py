"""
Quick test to simulate frontend post creation
"""
import sys
import os
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

from backend.cleanup_db import cleanup_db
from backend.User import User
from backend.Forum import Forum
from backend.Messages import Post

# Reset database
cleanup_db()

# Create a user and forum (like demo)
user1 = User("bkelly", "bkelly@scu.edu", "CSEN", 2026, None, None, None)
forum_csen174 = Forum("CSEN174")

# Add user to forum
user1.addForum(forum_csen174)
forum_csen174.addUser(user1)

print(f"User created: {user1.username} (db_id={user1.db_id})")
print(f"Forum created: {forum_csen174.course_name} (db_id={forum_csen174.db_id})")
print(f"User forums: {[f.course_name for f in user1.getforums()]}")
print(f"Forum users: {[u.username for u in forum_csen174.getUsers()]}")

# Simulate what the API does when creating a post
print("\n--- Simulating API post creation ---")
user_email = "bkelly@scu.edu"
title = "Test Post"
message = "This is a test message"

# Load user by email (like the API does)
user = User.load_by_email(user_email)
print(f"Loaded user: {user.username} (db_id={user.db_id})")

# Load forum by id (like the API does)
forum = Forum.load_by_id(forum_csen174.db_id)
print(f"Loaded forum: {forum.course_name} (db_id={forum.db_id})")

# Check membership
user_forums = user.getforums()
print(f"User's forums: {[f.course_name + f' (db_id={f.db_id})' for f in user_forums]}")

user_forum_ids = [f.db_id for f in user_forums]
print(f"User forum IDs: {user_forum_ids}")
print(f"Forum db_id: {forum.db_id}")
print(f"Is member (by ID)? {forum.db_id in user_forum_ids}")

# Try to create the post
try:
    new_post = Post(poster=user, message=message, title=title)
    print(f"\nPost created: {new_post.title} (db_id={new_post.db_id})")
    user.addPost(forum, new_post)
    print("Post added to forum successfully!")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

# Verify the post is in the forum
forum_posts = forum.getPosts()
print(f"\nForum posts: {[p.title for p in forum_posts]}")
