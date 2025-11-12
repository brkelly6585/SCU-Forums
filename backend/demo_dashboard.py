'''
Multi-user dashboard demo via console.
Seeds a few users with different forum memberships and posts,
then simulates each user logging in and viewing their dashboard.
'''
import sys
import os

# Add parent directory to path to enable backend imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from backend.cleanup_db import cleanup_db
from backend.User import User
from backend.Forum import Forum
from backend.Messages import Post

def print_section(title):
    # Print a formatted section header
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_user_dashboard(email):
    # Simulate a login and display the user's dashboard data
    print(f"\nLogging in as: {email}")
    user = User.load_by_email(email)
    
    if not user:
        print(f"   ERROR: User not found: {email}")
        return
    
    print(f"   Welcome, {user.username}!")
    print(f"   Email: {user.email}")
    print(f"   Major: {user.major}, Year: {user.year}")
    
    forums = user.getforums()
    print(f"\n   Enrolled Forums ({len(forums)}):")
    if not forums:
        print("\t(none)")
    else:
        for forum in forums:
            posts_in_forum = forum.getPosts()
            print(f"\t- {forum.course_name} - {len(posts_in_forum)} posts")
    
    user_posts = user.getposts()
    print(f"\n   My Posts ({len(user_posts)}):")
    if not user_posts:
        print("\t(none)")
    else:
        for post in user_posts:
            # Find which forum this post belongs to
            forum_name = "Unknown"
            for forum in forums:
                if post in forum.getPosts():
                    forum_name = forum.course_name
                    break
            print(f"\t- \"{post.title}\" in {forum_name}")
            print(f"\t > {post.message[:60]}{'...' if len(post.message) > 60 else ''}")
    
    # Show all posts across all forums (simulating "Recent Posts" on dashboard)
    print(f"\n   Recent Posts Across All Forums:")
    all_posts = []
    for forum in forums:
        for post in forum.getPosts():
            all_posts.append((forum.course_name, post))
    
    if not all_posts:
        print("\t(none)")
    else:
        for forum_name, post in all_posts[:5]:  # Limit to 5 most recent
            poster_name = post.poster.username if post.poster else "Unknown"
            print(f"\t- [{forum_name}] \"{post.title}\" by {poster_name}")
            print(f"\t > {post.message[:60]}{'...' if len(post.message) > 60 else ''}")

def main():
    print_section("Setting up fresh database")
    cleanup_db()
    print("   > Database reset complete")
    
    print_section("Creating users and forums")
    
    # User 1: Bryce Kelly
    user1 = User("bkelly", "bkelly@scu.edu", "CSEN", 2026, None, None, None)
    print(f"   > Created user: {user1.username} ({user1.email})")
    
    # User 2: Kenny Kang
    user2 = User("kkang", "kkang@scu.edu", "CSEN", 2025, None, None, None)
    print(f"   > Created user: {user2.username} ({user2.email})")
    
    # User 3: James Hunter
    user3 = User("jhunter", "jhunter@scu.edu", "CSEN", 2027, None, None, None)
    print(f"   > Created user: {user3.username} ({user3.email})")
    
    print_section("Creating forums")
    
    # Forums
    forum_csen174 = Forum("CSEN174")
    print(f"   > Created forum: {forum_csen174.course_name}")
    
    forum_csen161 = Forum("CSEN161")
    print(f"   > Created forum: {forum_csen161.course_name}")
    
    forum_math51 = Forum("MATH51")
    print(f"   > Created forum: {forum_math51.course_name}")
    
    print_section("Setting up forum memberships")
    
    # User 1 joins CSEN174 and MATH51
    user1.addForum(forum_csen174)
    forum_csen174.addUser(user1)
    print(f"   > {user1.username} joined {forum_csen174.course_name}")
    
    user1.addForum(forum_math51)
    forum_math51.addUser(user1)
    print(f"   > {user1.username} joined {forum_math51.course_name}")
    
    # User 2 joins CSEN174 and CSEN161
    user2.addForum(forum_csen174)
    forum_csen174.addUser(user2)
    print(f"   > {user2.username} joined {forum_csen174.course_name}")
    
    user2.addForum(forum_csen161)
    forum_csen161.addUser(user2)
    print(f"   > {user2.username} joined {forum_csen161.course_name}")
    
    # User 3 joins all three
    user3.addForum(forum_csen174)
    forum_csen174.addUser(user3)
    print(f"   > {user3.username} joined {forum_csen174.course_name}")
    
    user3.addForum(forum_csen161)
    forum_csen161.addUser(user3)
    print(f"   > {user3.username} joined {forum_csen161.course_name}")
    
    user3.addForum(forum_math51)
    forum_math51.addUser(user3)
    print(f"   > {user3.username} joined {forum_math51.course_name}")
    
    print_section("Creating posts")
    
    # Posts in CSEN174
    post1 = Post(user1, "I'm having trouble understanding how to set up nested routes in Flask. Any tips?", "Help with Flask routes")
    user1.addPost(forum_csen174, post1)
    print(f"   > {user1.username} posted in {forum_csen174.course_name}: \"{post1.title}\"")
    
    post2 = Post(user2, "How do I set up a many-to-many relationship with an association table?", "SQLAlchemy relationship question")
    user2.addPost(forum_csen174, post2)
    print(f"   > {user2.username} posted in {forum_csen174.course_name}: \"{post2.title}\"" )
    
    post3 = Post(user3, "Looking for interesting project ideas for our final. What has everyone done in the past?", "Team project ideas")
    user3.addPost(forum_csen174, post3)
    print(f"   > {user3.username} posted in {forum_csen174.course_name}: \"{post3.title}\"" )
    
    # Posts in CSEN161
    post4 = Post(user2, "When should I use Grid vs Flexbox for layouts? I'm confused about best practices.", "CSS Grid vs Flexbox")
    user2.addPost(forum_csen161, post4)
    print(f"   > {user2.username} posted in {forum_csen161.course_name}: \"{post4.title}\"" )
    
    post5 = Post(user3, "What's the best way to manage global state? Context API or Redux?", "React state management")
    user3.addPost(forum_csen161, post5)
    print(f"   > {user3.username} posted in {forum_csen161.course_name}: \"{post5.title}\"" )
    
    # Posts in MATH51
    post6 = Post(user1, "Can someone explain everything to me?", "Help")
    user1.addPost(forum_math51, post6)
    print(f"   > {user1.username} posted in {forum_math51.course_name}: \"{post6.title}\"" )
    
    post7 = Post(user3, "Anyone want to form a study group for the midterm next week?", "Study group for midterm")
    user3.addPost(forum_math51, post7)
    print(f"   > {user3.username} posted in {forum_math51.course_name}: \"{post7.title}\"" )

    print_section("Simulating User Logins")
    
    # Simulate each user logging in and viewing their dashboard
    print_user_dashboard("bkelly@scu.edu")
    print("\n" + "-"*70)
    
    print_user_dashboard("kkang@scu.edu")
    print("\n" + "-"*70)
    
    print_user_dashboard("jhunter@scu.edu")
    
    print_section("Demo Complete")
    print("   All users successfully logged in and viewed their dashboards")
    print("   Each user sees only the forums they're enrolled in and relevant posts")
    print("\n   React setup for these emails:")
    print("      - bkelly@scu.edu")
    print("      - kkang@scu.edu")
    print("      - jhunter@scu.edu")
    print()

if __name__ == "__main__":
    main()
