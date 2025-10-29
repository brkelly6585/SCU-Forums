import unittest
from backend.User import User, Admin
from backend.Forum import Forum
from backend.Messages import Post


class TestUser(unittest.TestCase):
    def setUp(self):
        self.user = User("bryce", "bkelly@scu.edu", "CSEN", 2, None, None, None)
        self.forum = Forum("CSEN174")

    def test_user_getters_and_forums(self):
        self.assertTrue(self.user.getAccountInfo().startswith("User ID:"))
        self.assertEqual(self.user.getposts(), [])
        self.assertEqual(self.user.getforums(), [])
        self.user.addForum(self.forum)
        self.assertIn(self.forum, self.user.getforums())
        self.user.removeForum(self.forum)
        self.assertNotIn(self.forum, self.user.getforums())

    def test_invalid_email_creation(self):
        # Test that creating users with non-SCU emails raises ValueError
        invalid_emails = [
            "user@gmail.com",
            "student@berkeley.edu",
            "test@example.com",
            "@scu.edu",  # Missing username
            "user@scu",  # Missing .edu
            "user@fake.scu.edu"  # Wrong domain
        ]
        for email in invalid_emails:
            with self.assertRaises(ValueError, msg=f"Should reject invalid email: {email}"):
                User("test", email, "CSEN", 1, None, None, None)

    def test_invalid_parameters(self):
        # Test handling of invalid parameter types
        # Test invalid year type
        with self.assertRaises(TypeError):
            User("test", "test@scu.edu", "CSEN", "not_a_number", None, None, None)
        
        # Test negative year
        with self.assertRaises(ValueError):
            User("test", "test@scu.edu", "CSEN", -1, None, None, None)

        # Test empty username
        with self.assertRaises(ValueError):
            User("", "test@scu.edu", "CSEN", 1, None, None, None)

        # Test empty major
        with self.assertRaises(ValueError):
            User("test", "test@scu.edu", "", 1, None, None, None)

    def test_unauthorized_post_operations(self):
        # Test operations on posts that user doesn't own
        other_user = User("other", "other@scu.edu", "CSEN", 3, None, None, None)
        other_post = Post(poster=other_user, message="Not mine", title="Other's Post")
        
        # Try to edit someone else's post
        with self.assertRaises(ValueError):
            self.user.editPost(other_post, "New message")
        
        # Try to add reaction to someone else's post
        with self.assertRaises(ValueError):
            self.user.addReaction(other_post, "like")

    def test_invalid_forum_operations(self):
        # Test invalid forum operations
        # Try to add post to forum user isn't part of
        post = Post(poster=self.user, message="Test", title="Test")
        with self.assertRaises(ValueError):
            self.user.addPost(self.forum, post)  # Haven't joined forum yet
        
        # Try to add invalid forum
        with self.assertRaises(TypeError):
            self.user.addForum("not a forum")
        
        # Try to add None as forum
        with self.assertRaises(TypeError):
            self.user.addForum(None)

    def test_add_post_to_forum(self):
        # Test that a post can be added to both user's posts and forum's posts
        self.user.addForum(self.forum)
        post = Post(poster=self.user, message="Test Post", title="Test")
        self.user.addPost(self.forum, post)
        self.assertIn(post, self.user.getposts(), "Post should be in user's posts")
        self.assertIn(post, self.forum.getPosts(), "Post should be in forum's posts")

    def test_edit_post(self):
        # Test that a user can edit their own post
        self.user.addForum(self.forum)
        post = Post(poster=self.user, message="Original", title="Test")
        self.user.addPost(self.forum, post)
        
        new_message = "Edited Message"
        self.user.editPost(post, new_message)
        self.assertEqual(post.getmessage(), new_message, "Post message should be updated")

    def test_add_reaction_to_post(self):
        # Test that reactions are properly added to both the post and user
        self.user.addForum(self.forum)
        post = Post(poster=self.user, message="Post", title="Test")
        self.user.addPost(self.forum, post)
        
        # Initially no reactions
        self.assertEqual(len(post.getreactions()), 0, "Post should start with no reactions")
        self.assertEqual(len(self.user.getreactions()), 0, "User should start with no reactions")
        
        # Add reaction
        self.user.addReaction(post, "like")
        
        # Verify reaction was added to both post and user
        self.assertEqual(len(post.getreactions()), 1, "Post should have one reaction")
        self.assertEqual(len(self.user.getreactions()), 1, "User should have one reaction")
        self.assertEqual(post.getreactions()[0].gettype(), "like", "Reaction should be of type 'like'")
        self.assertIs(post.getreactions()[0].getuser(), self.user, "Reaction should be from the correct user")


class TestAdmin(unittest.TestCase):
    def setUp(self):
        # Create an admin user
        self.admin = Admin("admin", "admin@scu.edu", "CSEN", 4)
        # Create a regular user to manage
        self.user = User("student", "student@scu.edu", "CSEN", 2, None, None, None)
        # Create a forum
        self.forum = Forum("TestForum")
        # Add users to forum
        self.forum.addUser(self.admin)
        self.forum.addUser(self.user)

    def test_restrict_user(self):
        # Test that an admin can restrict a user
        # Initially user should not be restricted
        self.assertNotIn(self.user, self.forum.restricted)
        
        # Admin restricts user
        self.admin.restrictUser(self.forum, self.user)
        self.assertIn(self.user, self.forum.restricted)

    def test_unrestrict_user(self):
        # Test that an admin can unrestrict a previously restricted user
        # First restrict the user
        self.admin.restrictUser(self.forum, self.user)
        self.assertIn(self.user, self.forum.restricted)
        
        # Then unrestrict
        self.admin.unrestrictUser(self.forum, self.user)
        self.assertNotIn(self.user, self.forum.restricted)

    def test_authorize_user(self):
        # Test that an admin can grant authorization to a user
        # Initially user should not be authorized
        self.assertFalse(self.forum.isauthorized(self.user))
        
        # Admin authorizes user
        self.admin.authorizeUser(self.forum, self.user)
        self.assertTrue(self.forum.isauthorized(self.user))
        
        # Admin can deauthorize user
        self.admin.deauthorizeUser(self.forum, self.user)
        self.assertFalse(self.forum.isauthorized(self.user))

    def test_restrict_already_restricted_user(self):
        # Test that restricting an already restricted user has no effect
        # First restriction
        self.admin.restrictUser(self.forum, self.user)
        self.assertIn(self.user, self.forum.restricted)
        
        # Get the initial restricted users count
        initial_restricted_count = len(self.forum.restricted)
        
        # Try to restrict again
        self.admin.restrictUser(self.forum, self.user)
        
        # Should still be in restricted list, but only once
        self.assertIn(self.user, self.forum.restricted)
        self.assertEqual(len(self.forum.restricted), initial_restricted_count)

    def test_admin_invalid_operations(self):
        # Test invalid admin operations
        # Try to restrict a non-existent user
        non_existent_user = User("fake", "fake@scu.edu", "CSEN", 1, None, None, None)
        with self.assertRaises(ValueError):
            self.admin.restrictUser(self.forum, non_existent_user)
        
        # Try to authorize with invalid forum
        with self.assertRaises(TypeError):
            self.admin.authorizeUser("not a forum", self.user)
        
        # Try to restrict with invalid user
        with self.assertRaises(TypeError):
            self.admin.restrictUser(self.forum, "not a user")

    def test_user_deletion(self):
        # Create a post before deletion
        self.user.addForum(self.forum)
        post = Post(poster=self.user, message="Original post", title="Test")
        self.user.addPost(self.forum, post)
        
        # Delete the user
        self.admin.deleteUser(self.user)
        
        # Verify user is marked as deleted
        self.assertTrue(self.user.is_deleted)
        
        # Try to perform operations with deleted user
        with self.assertRaises(ValueError):
            self.user.addPost(self.forum, Post(poster=self.user, message="New post", title="Test"))
            
        # Check account info shows [DELETED]
        self.assertIn("[DELETED]", self.user.getAccountInfo())

    def test_user_deletion_permissions(self):
        # Delete a user
        self.admin.deleteUser(self.user)
        
        # Verify admin operations on deleted user fail
        with self.assertRaises(ValueError):
            self.admin.restrictUser(self.forum, self.user)
        
        with self.assertRaises(ValueError):
            self.admin.authorizeUser(self.forum, self.user)
            
        with self.assertRaises(ValueError):
            self.admin.unrestrictUser(self.forum, self.user)
            
        with self.assertRaises(ValueError):
            self.admin.deauthorizeUser(self.forum, self.user)

    def test_user_undelete(self):
        # Delete then undelete a user
        self.user.addForum(self.forum)
        
        self.admin.deleteUser(self.user)
        
        # Create posts that should remain deleted
        post = Post(poster=self.user, message="Test post", title="Test")
        self.assertTrue(post.is_deleted)
        
        # Undelete the user
        self.admin.undeleteUser(self.user)
        
        # Verify user is no longer marked as deleted
        self.assertFalse(self.user.is_deleted)
        
        # Verify posts remain deleted
        self.assertTrue(post.is_deleted)
        
        # Verify user can create new posts
        new_post = Post(poster=self.user, message="New post", title="Test")
        self.user.addPost(self.forum, new_post)
        self.assertFalse(new_post.is_deleted)

    def test_double_deletion(self):
        # Delete a user
        self.admin.deleteUser(self.user)
        
        # Try to delete again
        with self.assertRaises(ValueError):
            self.admin.deleteUser(self.user)
            
        # Undelete the user
        self.admin.undeleteUser(self.user)
        
        # Try to undelete again
        with self.assertRaises(ValueError):
            self.admin.undeleteUser(self.user)


if __name__ == '__main__':
    unittest.main()
