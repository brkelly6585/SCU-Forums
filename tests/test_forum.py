import unittest
from backend.Forum import Forum
from backend.User import User, Admin
from backend.Messages import Post, Comment


class TestForum(unittest.TestCase):
    def setUp(self):
        self.forum = Forum("CSEN174")
        self.user = User("james", "jhunter@scu.edu", "CSEN", 2, None, None, None)
        self.admin = Admin("admin", "admin@scu.edu", "CSEN", 4)
        
        # Add users to forum
        self.forum.addUser(self.user)
        self.forum.addUser(self.admin)

    def test_empty_forum_posts(self):
        # Test that a new forum has no posts
        # Create a new forum without adding any posts
        empty_forum = Forum("EmptyForum")
        self.assertEqual(len(empty_forum.getPosts()), 0, "New forum should have no posts")
        self.assertEqual(empty_forum.getPosts(), [], "getPosts should return empty list")

    def test_post_with_comments(self):
        # Test adding and retrieving a post with comments
        # Create initial post
        post = Post(poster=self.user, message="Main post", title="Test")
        self.forum.addPost(post)
        
        # Create comment on the post
        comment = Comment(poster=self.admin, message="Reply", title="Re: Test", parent=post)
        
        # Check that comment is in post's comments
        self.assertIn(comment, post.getcomments(), "Comment should be in post's comments")
        
        # Check that post with comment is in forum's posts
        forum_posts = self.forum.getPosts()
        self.assertEqual(len(forum_posts), 1, "Forum should have one post")
        retrieved_post = forum_posts[0]
        self.assertEqual(len(retrieved_post.getcomments()), 1, "Post should have one comment")
        self.assertEqual(retrieved_post.getcomments()[0].getmessage(), "Reply", "Comment message should match")
        self.assertEqual(retrieved_post.getcomments()[0].getparent(), post, "Comment should reference correct parent post")

    def test_authorized_users(self):
        # Test getting users with admin permissions
        # Initially no authorized users
        self.assertEqual(len(self.forum.authorized), 0, "New forum should have no authorized users")
        
        # Authorize user
        self.forum.authorizeUser(self.user)
        self.assertIn(self.user, self.forum.authorized, "User should be in authorized list")
        
        # Authorize admin
        self.forum.authorizeUser(self.admin)
        self.assertIn(self.admin, self.forum.authorized, "Admin should be in authorized list")
        
        # Check both users are authorized
        self.assertEqual(len(self.forum.authorized), 2, "Forum should have two authorized users")
        self.assertTrue(self.forum.isauthorized(self.user), "User should be authorized")
        self.assertTrue(self.forum.isauthorized(self.admin), "Admin should be authorized")
        
        # Remove authorization
        self.forum.deauthorizeUser(self.user)
        self.assertNotIn(self.user, self.forum.authorized, "User should not be in authorized list after removal")
        self.assertFalse(self.forum.isauthorized(self.user), "User should not be authorized after removal")

    def test_forum_user_post(self):
        # Test basic forum operations with posts
        self.assertEqual(self.forum.getCourseName(), "CSEN174")
        self.assertIn(self.user, self.forum.getUsers())
        self.forum.authorizeUser(self.user)
        self.assertTrue(self.forum.isauthorized(self.user))
        post = Post(poster=self.user, message="Q", title="Question")
        self.forum.addPost(post)
        self.assertIn(post, self.forum.getPosts())
        self.forum.removePost(post)
        self.assertNotIn(post, self.forum.getPosts())

    def test_restrict_unrestrict_user(self):
        # Test restricting and unrestricting users
        self.forum.restrictUser(self.user)
        self.assertIn(self.user, self.forum.restricted, "User should be in restricted list")
        self.forum.unrestrictUser(self.user)
        self.assertNotIn(self.user, self.forum.restricted, "User should not be in restricted list")

    def test_duplicate_operations(self):
        # Test handling of duplicate operations
        # Test duplicate user addition
        self.forum.addUser(self.user)  # user already added in setUp
        self.assertEqual(len([u for u in self.forum.getUsers() if u == self.user]), 1,
                        "User should appear only once in users list")

        # Test duplicate post addition
        post = Post(poster=self.user, message="Test", title="Test")
        self.forum.addPost(post)
        self.forum.addPost(post)  # Try to add same post again
        self.assertEqual(len([p for p in self.forum.getPosts() if p == post]), 1,
                        "Post should appear only once in posts list")

        # Test duplicate authorization
        self.forum.authorizeUser(self.user)
        self.forum.authorizeUser(self.user)  # Try to authorize again
        self.assertEqual(len([u for u in self.forum.authorized if u == self.user]), 1,
                        "User should appear only once in authorized list")

    def test_invalid_operations(self):
        # Test operations with invalid inputs
        # Test invalid user type
        with self.assertRaises(TypeError):
            self.forum.addUser("not a user")
        
        # Test invalid post type
        with self.assertRaises(TypeError):
            self.forum.addPost("not a post")
        
        # Test None values
        with self.assertRaises(TypeError):
            self.forum.addUser(None)
        with self.assertRaises(TypeError):
            self.forum.addPost(None)

    def test_unauthorized_operations(self):
        # Test operations by unauthorized/restricted users
        # Create another user not in the forum
        outside_user = User("other", "other@scu.edu", "CSEN", 3, None, None, None)
        
        # Try to add post from user not in forum
        outside_post = Post(poster=outside_user, message="Test", title="Test")
        with self.assertRaises(ValueError):
            self.forum.addPost(outside_post)

        # Try operations with restricted user
        self.forum.restrictUser(self.user)
        restricted_post = Post(poster=self.user, message="Test", title="Test")
        with self.assertRaises(ValueError):
            self.forum.addPost(restricted_post)

        # Verify that user stays restricted after failed post attempt
        self.assertIn(self.user, self.forum.restricted,
                     "User should remain restricted after failed post attempt")

        # Test post persistence after user removal
        self.forum.unrestrictUser(self.user)
        post = Post(poster=self.user, message="Test", title="Test")
        self.forum.addPost(post)  # Add post while user is in forum and not restricted
        self.forum.removeUser(self.user)
        
        # Verify post still exists but now has deleted user as poster
        self.assertIn(post, self.forum.getPosts(),
                     "Post should remain in forum after user removal")
        retrieved_post = next(p for p in self.forum.getPosts() if p == post)
        self.assertEqual(retrieved_post.poster.username, "[deleted]",
                        "Post should show [deleted] as username")
        self.assertNotIn(self.user, self.forum.getUsers(),
                        "User should be removed from forum")

    def test_status_conflicts(self):
        # Test conflicting user status operations
        # Test restricting an authorized user
        self.forum.authorizeUser(self.user)
        self.forum.restrictUser(self.user)
        
        # User should be removed from authorized when restricted
        self.assertNotIn(self.user, self.forum.authorized,
                        "Restricted user should not be in authorized list")
        self.assertFalse(self.forum.isauthorized(self.user),
                        "Restricted user should not be authorized")

        # Test authorizing a restricted user
        self.forum.authorizeUser(self.user)
        
        # User should be removed from restricted when authorized
        self.assertNotIn(self.user, self.forum.restricted,
                        "Authorized user should not be in restricted list")
        self.assertTrue(self.forum.isauthorized(self.user),
                        "User should be authorized after restriction is removed")


if __name__ == '__main__':
    unittest.main()
