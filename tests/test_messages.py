import unittest
from backend.Messages import Post, Comment, Reaction
from backend.User import User, Admin
from backend.Forum import Forum


class TestPostBase(unittest.TestCase):
    # Base class for message-related tests with common setup
    def setUp(self):
        self.user = User("bryce", "bkelly@scu.edu", "CSEN", 2, None, None, None)
        self.other_user = User("kenny", "kkang@scu.edu", "CSEN", 3, None, None, None)
        self.post = Post(poster=self.user, message="Hello", title="Intro")
        self.forum = Forum("CSEN174")
        self.deleted_user = Forum.DELETED_USER


class TestPost(TestPostBase):
    # Test cases specifically for Post functionality

    def test_post_creation(self):
        # Test basic post creation
        self.assertIs(self.post.poster, self.user)
        self.assertEqual(self.post.message, "Hello")
        self.assertEqual(self.post.title, "Intro")
        self.assertTrue(isinstance(self.post.id, int))
        self.assertTrue(1000 <= self.post.id <= 9999)
        self.assertEqual(self.post.getcomments(), [])
        self.assertEqual(self.post.getreactions(), [])

    def test_empty_comments(self):
        # Test getting comments when there are none
        self.assertEqual(len(self.post.getcomments()), 0)
        self.assertEqual(self.post.getcomments(), [])

    def test_nested_comments(self):
        # Test nested comment structure
        # First level comment
        comment1 = Comment(poster=self.user, message="First", title="Re: Intro", parent=self.post)
        # Second level comment (reply to comment1)
        comment2 = Comment(poster=self.other_user, message="Second", title="Re: First", parent=comment1)
        # Third level comment (reply to comment2)
        comment3 = Comment(poster=self.user, message="Third", title="Re: Second", parent=comment2)

        # Verify comment hierarchy
        self.assertIn(comment1, self.post.getcomments())
        self.assertIn(comment2, comment1.getcomments())
        self.assertIn(comment3, comment2.getcomments())
        
        # Verify parent relationships
        self.assertEqual(comment1.getparent(), self.post)
        self.assertEqual(comment2.getparent(), comment1)
        self.assertEqual(comment3.getparent(), comment2)

    def test_deleted_user_post(self):
        # Test post behavior when user is deleted
        post = Post(poster=self.deleted_user, message="Deleted user post", title="Test")
        self.assertEqual(post.getposter().username, "[deleted]")
        self.assertEqual(post.getposter().email, "deleted@scu.edu")

    def test_invalid_post_creation(self):
        # Test creation of posts with invalid content
        # Test empty message
        with self.assertRaises(ValueError):
            Post(poster=self.user, message="", title="Empty")
        
        # Test empty title
        with self.assertRaises(ValueError):
            Post(poster=self.user, message="Content", title="")
        
        # Test explicit content (using a simple filter)
        explicit_words = ["explicit_word1", "explicit_word2"]  # Add actual words to filter
        for word in explicit_words:
            with self.assertRaises(ValueError):
                Post(poster=self.user, message=f"Contains {word}", title="Test")

        # Test None values
        with self.assertRaises(TypeError):
            Post(poster=None, message="Test", title="Test")
        with self.assertRaises(TypeError):
            Post(poster=self.user, message=None, title="Test")
        with self.assertRaises(TypeError):
            Post(poster=self.user, message="Test", title=None)

    def test_invalid_comment_creation(self):
        # Test creation of comments with invalid parameters
        # Test invalid parent type
        with self.assertRaises(TypeError):
            Comment(poster=self.user, message="Test", title="Test", parent="not a post")
        
        # Test None parent
        with self.assertRaises(TypeError):
            Comment(poster=self.user, message="Test", title="Test", parent=None)

        # Test commenting on a comment that's been removed from its parent
        comment = Comment(poster=self.user, message="Original", title="Test", parent=self.post)
        self.post.remove_comment(comment)
        with self.assertRaises(ValueError):
            Comment(poster=self.user, message="Reply", title="Re: Test", parent=comment)

    def test_comment_removal(self):
        # Test comment removal behavior preserving structure
        # Create a chain of comments
        comment1 = Comment(poster=self.user, message="First", title="Re: Intro", parent=self.post)
        comment2 = Comment(poster=self.other_user, message="Second", title="Re: First", parent=comment1)
        comment3 = Comment(poster=self.user, message="Third", title="Re: Second", parent=comment2)

        # Remove middle comment and verify it's marked as deleted but structure remains
        comment1.remove_comment(comment2)
        
        # Verify comment2 is still in the tree but marked as deleted
        self.assertIn(comment2, comment1.getcomments(), "Comment should remain in tree")
        self.assertEqual(comment2.getmessage(), "[deleted]", "Message should be marked as deleted")
        self.assertEqual(comment2.title, "[deleted]", "Title should be marked as deleted")
        
        # Verify comment3 is still attached and unchanged
        self.assertIn(comment3, comment2.getcomments(), "Child comment should remain in tree")
        self.assertEqual(comment3.getmessage(), "Third", "Child comment message should be unchanged")
        self.assertEqual(comment3.title, "Re: Second", "Child comment title should be unchanged")
        
        # Verify the full structure is maintained
        self.assertEqual(comment1.getparent(), self.post, "Parent relationship should be maintained")
        self.assertEqual(comment2.getparent(), comment1, "Parent relationship should be maintained")
        self.assertEqual(comment3.getparent(), comment2, "Parent relationship should be maintained")

    def test_post_deletion(self):
        # Create an admin and add users/forum
        admin = Admin("admin", "admin@scu.edu", "CSEN", 4)
        self.forum.addUser(admin)
        self.forum.addUser(self.user)
        self.user.addForum(self.forum)

        # Create a post with comments
        post = Post(poster=self.user, message="Test post", title="Test")
        self.user.addPost(self.forum, post)
        comment1 = Comment(poster=self.other_user, message="Reply 1", title="Re: Test", parent=post)
        comment2 = Comment(poster=self.user, message="Reply 2", title="Re: Reply 1", parent=comment1)
        
        # Delete the post through admin
        admin.removePost(self.forum, post)
        
        # Verify post is marked as deleted
        self.assertTrue(post.is_deleted)
        
        # Verify comments are still accessible through the forum
        forum_posts = self.forum.getPosts()
        self.assertIn(post, forum_posts)
        self.assertIn(comment1, post.getcomments())
        self.assertIn(comment2, comment1.getcomments())

    def test_deleted_post_interactions(self):
        # Set up admin and forum
        admin = Admin("admin", "admin@scu.edu", "CSEN", 4)
        self.forum.addUser(admin)
        self.forum.addUser(self.user)
        self.forum.addUser(self.other_user)
        self.user.addForum(self.forum)
        self.other_user.addForum(self.forum)

        # Create a post
        post = Post(poster=self.user, message="Test post", title="Test")
        self.user.addPost(self.forum, post)
        
        # Delete the post
        admin.removePost(self.forum, post)
        
        # Verify post is marked as deleted
        self.assertTrue(post.is_deleted)
        
        # Try to add comments to deleted post (should still work as per requirements)
        comment = Comment(poster=self.other_user, message="Reply to deleted", title="Re: Test", parent=post)
        
        # Verify comment was added successfully
        self.assertIn(comment, post.getcomments())
        
        # Verify the comment itself is not marked as deleted
        self.assertFalse(comment.is_deleted)

    def test_user_deleted_posts_visibility(self):
        # Set up admin and forum
        admin = Admin("admin", "admin@scu.edu", "CSEN", 4)
        self.forum.addUser(admin)
        self.forum.addUser(self.user)
        self.user.addForum(self.forum)

        # Create multiple posts
        post1 = Post(poster=self.user, message="Post 1", title="Test 1")
        post2 = Post(poster=self.user, message="Post 2", title="Test 2")
        self.user.addPost(self.forum, post1)
        self.user.addPost(self.forum, post2)
        
        # Delete the user through admin
        admin.deleteUser(self.user)
        
        # Verify all posts are marked as deleted
        self.assertTrue(post1.is_deleted)
        self.assertTrue(post2.is_deleted)


class TestReaction(TestPostBase):
    # Test cases specifically for Reaction functionality
    def test_add_and_remove_reaction(self):
        # Test basic reaction functionality
        reaction = Reaction(reaction_type="like", user=self.user)
        self.post.addreaction(reaction)
        self.assertIn(reaction, self.post.getreactions())
        self.post.removereaction(reaction)
        self.assertNotIn(reaction, self.post.getreactions())

    def test_invalid_reactions(self):
        # Test invalid reaction scenarios
        # Test invalid reaction type
        with self.assertRaises(ValueError):
            Reaction(reaction_type="invalid_type", user=self.user)
        
        # Test None user
        with self.assertRaises(TypeError):
            Reaction(reaction_type="like", user=None)
        
        # Test duplicate reaction from same user
        reaction1 = Reaction(reaction_type="like", user=self.user)
        reaction2 = Reaction(reaction_type="like", user=self.user)
        self.post.addreaction(reaction1)
        with self.assertRaises(ValueError):
            self.post.addreaction(reaction2)

    def test_reaction_types(self):
        # Test all valid reaction types
        valid_types = ["like", "dislike", "heart", "flag"]
        for reaction_type in valid_types:
            reaction = Reaction(reaction_type=reaction_type, user=self.user)
            self.assertEqual(reaction.gettype(), reaction_type)
            self.assertEqual(reaction.getuser(), self.user)

    def test_reaction_equality(self):
        # Test reaction equality comparison
        reaction1 = Reaction(reaction_type="like", user=self.user)
        reaction2 = Reaction(reaction_type="like", user=self.user)
        reaction3 = Reaction(reaction_type="dislike", user=self.user)
        reaction4 = Reaction(reaction_type="like", user=self.other_user)

        # Same type and user should be equal
        self.assertEqual(reaction1, reaction2)
        # Different type or user should not be equal
        self.assertNotEqual(reaction1, reaction3)
        self.assertNotEqual(reaction1, reaction4)

    def test_reaction_getters(self):
        # Test all getter methods in Reaction class
        # Create a reaction with a parent post
        reaction = Reaction(reaction_type="heart", user=self.user, parent=self.post)
        
        # Test gettype()
        self.assertEqual(reaction.gettype(), "heart", "gettype() should return the reaction type")
        
        # Test getuser()
        self.assertIs(reaction.getuser(), self.user, "getuser() should return the user who made the reaction")
        
        # Test getparent()
        self.assertIs(reaction.getparent(), self.post, "getparent() should return the parent post")
        
        # Test parent is optional
        reaction_no_parent = Reaction(reaction_type="flag", user=self.user)
        self.assertIsNone(reaction_no_parent.getparent(), "getparent() should return None when no parent was set")





if __name__ == '__main__':
    unittest.main()
