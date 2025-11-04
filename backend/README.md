# SCU-Forums Backend

Backend API for the SCU Forums application, built with Flask and SQLAlchemy.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

## Setup

1. **Clone the repository** (if you haven't already):
   ```powershell
   git clone https://github.com/brkelly6585/SCU-Forums.git
   cd SCU-Forums
   ```

2. **Create a virtual environment**:
   ```powershell
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. **Install dependencies**:
   ```powershell
   python -m pip install -r requirements.txt
   ```

## Running the Backend

Start the Flask development server:
```powershell
.\.venv\Scripts\Activate.ps1
python .\backend\app.py
```

The server will start on `http://localhost:5000`

## Running Tests

Run the full test suite:
```powershell
.\.venv\Scripts\Activate.ps1
python -m unittest discover -v
```

Run a specific test file:
```powershell
python -m unittest tests/test_login_endpoint.py -v
```

## API Endpoints

### POST /api/login

Email-based login endpoint that returns or creates a user.

**Request (existing user)**:
```json
{
  "email": "user@scu.edu"
}
```

**Request (new user)**:
```json
{
  "email": "newuser@scu.edu",
  "username": "New User",
  "major": "CSEN",
  "year": 2
}
```

**Response** (200 or 201):
```json
{
  "id": 1,
  "username": "New User",
  "email": "newuser@scu.edu",
  "major": "CSEN",
  "year": 2,
  "is_deleted": false,
  "forums": [
    {
      "id": 1,
      "course_name": "CSEN174",
      "posts": [
        {
          "id": 1,
          "title": "Post Title",
          "message": "Post content",
          "poster": "username",
          "is_deleted": false
        }
      ]
    }
  ],
  "posts": [
    {
      "id": 1,
      "title": "Post Title",
      "message": "Post content",
      "forum_id": 1,
      "is_deleted": false
    }
  ]
}
```

**Error Response** (400):
```json
{
  "error": "A valid scu.edu email is required"
}
```

## Database

The backend uses SQLite for data persistence. The database file (`scu_forums.db`) is automatically created when the application first runs.

To reset the database:
```powershell
python .\backend\cleanup_db.py
```

## Project Structure

```
backend/
├── app.py              # Flask application and API endpoints
├── User.py             # User and Admin classes
├── Forum.py            # Forum class
├── Messages.py         # Post, Comment, and Reaction classes
├── models.py           # SQLAlchemy ORM models
├── db.py               # Database configuration
├── object_registry.py  # Identity registry for wrappers
└── cleanup_db.py       # Database cleanup utility

tests/
├── test_user.py
├── test_forum.py
├── test_messages.py
├── test_demo_flow.py
└── test_login_endpoint.py
```

## Notes for Frontend Developers

- The API uses simple CORS headers allowing all origins (`*`) for local development
- All endpoints return JSON
- Email validation requires `@scu.edu` domain
- The login endpoint automatically creates new users if they don't exist (with required fields)
- Use `http://localhost:5000/api/login` as your backend URL

## Troubleshooting

**ModuleNotFoundError: No module named 'flask'**
- Make sure your virtual environment is activated
- Run `python -m pip install -r requirements.txt`

**Database errors**
- Try resetting the database: `python .\backend\cleanup_db.py`

**Port already in use**
- Stop any other Flask processes
- Or modify `app.py` to use a different port: `app.run(debug=True, port=5001)`
