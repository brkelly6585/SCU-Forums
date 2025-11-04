import unittest

from backend.cleanup_db import cleanup_db
from backend.User import User
from backend.Forum import Forum
from backend.Messages import Post


class TestDemoFlow(unittest.TestCase):
    def setUp(self):
        # Ensure a clean DB for each test
        cleanup_db()

    def test_user_login_post_visibility(self):
        # User1 creates account, joins forum, and posts
        user1 = User("alice", "alice@scu.edu", "CSEN", 2, None, None, None)
        forum = Forum("CSEN174")
        user1.addForum(forum)
        post = Post(poster=user1, message="Hello from Alice", title="Intro")
        user1.addPost(forum, post)

        # Simulate new session: reload by email
        user1_reloaded = User.load_by_email("alice@scu.edu")
        self.assertIsNotNone(user1_reloaded)
        self.assertEqual(user1.db_id, user1_reloaded.db_id)

        # Reloaded user should see the forum and the post
        forums = user1_reloaded.getforums()
        self.assertTrue(any(f.course_name == "CSEN174" for f in forums))

        forum_reloaded = next((f for f in forums if f.course_name == "CSEN174"), None)
        self.assertIsNotNone(forum_reloaded)

        posts = forum_reloaded.getPosts()
        self.assertTrue(any(p.title == "Intro" and p.message == "Hello from Alice" for p in posts))

        # Another user logs in and joins the same forum and should see the post
        user2 = User("bob", "bob@scu.edu", "CSEN", 3, None, None, None)
        user2.addForum(forum_reloaded)
        posts_user2 = forum_reloaded.getPosts()
        self.assertTrue(any(p.title == "Intro" for p in posts_user2))


if __name__ == '__main__':
    unittest.main()
