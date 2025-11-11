import unittest
from backend.app import app
from backend.cleanup_db import cleanup_db
from backend.User import User
from backend.Forum import Forum


class TestPostCommentEndpoints(unittest.TestCase):
    def setUp(self):
        cleanup_db()
        self.client = app.test_client()
        
        # Create test user and forum
        self.user = User("test_poster", "poster@scu.edu", "CSEN", 2025, None, None, None)
        self.forum = Forum("TEST101")
        self.user.addForum(self.forum)
        self.forum.addUser(self.user)

    def test_create_post_endpoint(self):
        """Test POST /api/forums/<id>/posts creates a new post"""
        response = self.client.post(
            f"/api/forums/{self.forum.db_id}/posts",
            json={
                "title": "Test Post Title",
                "message": "This is a test post message",
                "user_email": self.user.email
            }
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("post", data)
        self.assertEqual(data["post"]["title"], "Test Post Title")
        self.assertEqual(data["post"]["message"], "This is a test post message")
        self.assertEqual(data["post"]["poster"], self.user.username)
        
        # Verify post was added to forum
        posts = self.forum.getPosts()
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].title, "Test Post Title")

    def test_create_post_requires_forum_membership(self):
        """Test that users must be forum members to post"""
        non_member = User("outsider", "outsider@scu.edu", "MATH", 2026, None, None, None)
        
        response = self.client.post(
            f"/api/forums/{self.forum.db_id}/posts",
            json={
                "title": "Unauthorized Post",
                "message": "This should fail",
                "user_email": non_member.email
            }
        )
        
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertIn("error", data)

    def test_create_comment_endpoint(self):
        """Test POST /api/posts/<id>/comments creates a new comment"""
        # First create a post
        from backend.Messages import Post
        post = Post(poster=self.user, message="Original post", title="Original Title")
        self.user.addPost(self.forum, post)
        
        # Now add a comment
        response = self.client.post(
            f"/api/posts/{post.db_id}/comments",
            json={
                "message": "This is a test comment",
                "user_email": self.user.email
            }
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("comment", data)
        self.assertEqual(data["comment"]["message"], "This is a test comment")
        self.assertEqual(data["comment"]["poster"], self.user.username)
        
        # Verify comment was added to post
        comments = post.getcomments()
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].message, "This is a test comment")

    def test_create_nested_comment(self):
        """Test creating a reply to a comment"""
        from backend.Messages import Post, Comment
        
        # Create post and first comment
        post = Post(poster=self.user, message="Original post", title="Original Title")
        self.user.addPost(self.forum, post)
        
        parent_comment = Comment(poster=self.user, message="Parent comment", title="Comment", parent=post)
        
        # Create reply to the comment
        response = self.client.post(
            f"/api/posts/{post.db_id}/comments",
            json={
                "message": "Reply to comment",
                "user_email": self.user.email,
                "parent_comment_id": parent_comment.db_id
            }
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["comment"]["message"], "Reply to comment")
        
        # Verify nested comment structure
        nested_comments = parent_comment.getcomments()
        self.assertEqual(len(nested_comments), 1)
        self.assertEqual(nested_comments[0].message, "Reply to comment")


if __name__ == "__main__":
    unittest.main()
