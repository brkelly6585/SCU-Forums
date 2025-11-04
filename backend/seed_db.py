"""
Seed the database with demo data for testing the login flow.
Creates a user (bkell@scu.edu), a forum (CSEN174), and 2 posts.
"""
from backend.User import User
from backend.Forum import Forum
from backend.Messages import Post
from backend.cleanup_db import cleanup_db

def seed_database():
    # Clean the database first
    print("Cleaning database...")
    cleanup_db()
    
    # Create user
    print("Creating user bkelly@scu.edu...")
    user = User(
        username="Bryce Kelly",
        email="bkelly@scu.edu",
        major="CSEN",
        year=3,
        posts=None,
        forum=None,
        reactions=None
    )
    print(f"✓ Created user: {user.username} (ID: {user.db_id})")
    
    # Create forum
    print("\nCreating forum CSEN174...")
    forum = Forum("CSEN174")
    print(f"✓ Created forum: {forum.course_name} (ID: {forum.db_id})")
    
    # Add user to forum
    print("\nAdding user to forum...")
    user.addForum(forum)
    print(f"✓ User added to forum")
    
    # Create first post
    print("\nCreating first post...")
    post1 = Post(
        poster=user,
        message="This is my first post on the SCU Forums! I'm really excited to connect with other students in CSEN174. Has anyone started the first project yet?",
        title="Introduction - New to CSEN174"
    )
    user.addPost(forum, post1)
    print(f"✓ Created post: {post1.title} (ID: {post1.db_id})")
    
    # Create second post
    print("\nCreating second post...")
    post2 = Post(
        poster=user,
        message="I'm having trouble understanding the purpose of Singletons. Can someone explain it with a simple example? Thanks!",
        title="Question: Singleton Help"
    )
    user.addPost(forum, post2)
    print(f"✓ Created post: {post2.title} (ID: {post2.db_id})")
    
    print("\n" + "="*60)
    print("Database seeded successfully!")
    print("="*60)
    print(f"\nUser Details:")
    print(f"  Email: {user.email}")
    print(f"  Username: {user.username}")
    print(f"  Major: {user.major}, Year: {user.year}")
    print(f"  Forums: {len(user.getforums())}")
    print(f"  Posts: {len(user.getposts())}")
    print(f"\nYou can now log in with: bkell@scu.edu")
    print("="*60)

if __name__ == "__main__":
    seed_database()
