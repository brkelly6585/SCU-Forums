"""
Test API call for creating a post
"""
import requests
import json

# First, reset the DB and create test data
import sys
import os
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

from backend.cleanup_db import cleanup_db
from backend.User import User
from backend.Forum import Forum

# Reset database
cleanup_db()

# Create a user and forum
user1 = User("bkelly", "bkelly@scu.edu", "CSEN", 2026, None, None, None)
forum_csen174 = Forum("CSEN174")

# Add user to forum
user1.addForum(forum_csen174)
forum_csen174.addUser(user1)

print(f"Setup complete:")
print(f"  User: {user1.username} ({user1.email}) - db_id={user1.db_id}")
print(f"  Forum: {forum_csen174.course_name} - db_id={forum_csen174.db_id}")
print(f"  User is member: {forum_csen174 in user1.getforums()}")
print()

# Now test the API call
url = f"http://127.0.0.1:5000/api/forums/{forum_csen174.db_id}/posts"
payload = {
    "title": "Test Post from API",
    "message": "This is a test message from the API test script",
    "user_email": "bkelly@scu.edu"
}

print(f"Making POST request to: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print()

try:
    response = requests.post(url, json=payload)
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response body: {response.text}")
    
    if response.ok:
        data = response.json()
        print("\nSUCCESS! Post created:")
        print(f"  Title: {data['post']['title']}")
        print(f"  Message: {data['post']['message']}")
    else:
        print(f"\nERROR: {response.status_code}")
        try:
            error_data = response.json()
            print(f"  Error message: {error_data.get('error', 'Unknown error')}")
        except:
            print(f"  Raw response: {response.text}")
except Exception as e:
    print(f"Exception occurred: {e}")
    import traceback
    traceback.print_exc()
