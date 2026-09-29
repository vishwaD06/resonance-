# Wavelength Backend API

AI-powered matchmaking platform backend built with FastAPI.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your actual values
```

3. Initialize the database:
```bash
python init_db.py
```

4. Run the development server:
```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Create new user
- `POST /api/v1/auth/login` - Login and get token
- `GET /api/v1/auth/me` - Get current user info

### Interview
- `POST /api/v1/interview/start` - Start interview session
- `POST /api/v1/interview/respond` - Submit interview response
- `GET /api/v1/interview/session/{session_id}` - Get session details

### Profile
- `POST /api/v1/profile/create` - Create user profile
- `GET /api/v1/profile/me` - Get user profile
- `PUT /api/v1/profile/me` - Update user profile
- `POST /api/v1/profile/complete` - Mark profile as complete

### Matching
- `POST /api/v1/matching/find` - Find best match
- `GET /api/v1/matching/pending` - Get pending match
- `GET /api/v1/matching/my-matches` - Get all user matches
- `POST /api/v1/matching/respond` - Respond to match

## Database Schema

- `users` - User accounts and authentication
- `profiles` - User personality profiles and embeddings
- `preferences` - User matching preferences
- `interview_sessions` - AI interview conversations
- `matches` - User matches and status
- `interactions` - Match interactions and feedback

## v0.1 Features

- Text-only AI interview for personality extraction
- Basic cosine similarity matching
- Waitlist landing page integration
- Simple profile management
- Basic authentication

## Development Notes

- Requires PostgreSQL with pgvector extension
- Requires OpenAI API key for AI features
- Uses JWT for authentication
- Async/await pattern throughout
