import unittest
from backend.app import app
from backend.User import User
from backend.Forum import Forum
from backend.Messages import Post


class TestLoginEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.email = "login_test@scu.edu"
        self.username = "login_tester"
        self.major = "CSEN"
        self.year = 2

    def test_login_returns_forums_and_posts_by_email(self):
        # 1) Create a new user via login endpoint
        resp_create = self.client.post(
            "/api/login",
            json={
                "email": self.email,
                "username": self.username,
                "major": self.major,
                "year": self.year,
            },
        )
        self.assertIn(resp_create.status_code, (200, 201))
        data_create = resp_create.get_json()
        self.assertEqual(data_create["email"], self.email)

        # 2) Add a forum and a post for the user using backend classes
        user = User.load_by_email(self.email)
        forum = Forum("CSEN174")
        user.addForum(forum)
        post = Post(poster=user, message="Hello from login test", title="Login Test Post")
        user.addPost(forum, post)

        # 3) Login again using only email and verify forums and posts are returned
        resp_login = self.client.post("/api/login", json={"email": self.email})
        self.assertEqual(resp_login.status_code, 200)
        data_login = resp_login.get_json()

        self.assertEqual(data_login["email"], self.email)
        # Forums should include CSEN174 with one post
        self.assertTrue(isinstance(data_login.get("forums"), list))
        self.assertEqual(len(data_login["forums"]), 1)
        self.assertEqual(data_login["forums"][0]["course_name"], "CSEN174")
        self.assertEqual(len(data_login["forums"][0]["posts"]), 1)
        self.assertEqual(data_login["forums"][0]["posts"][0]["title"], "Login Test Post")

        # User-level posts should include the same post
        self.assertTrue(isinstance(data_login.get("posts"), list))
        titles = [p["title"] for p in data_login["posts"]]
        self.assertIn("Login Test Post", titles)


if __name__ == "__main__":
    unittest.main()
