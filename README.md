# Wavelength - AI-Powered Matchmaking

An AI-driven matchmaking app that replaces swipe-based discovery with conversational AI onboarding and compatibility-based matching.

## Architecture

This project follows the architecture outlined in `AI_Matchmaker_Architecture_Plan.md` and implements v0.1 features:

- **Frontend**: React + Vite with kastle.ai-inspired design
- **Backend**: FastAPI with PostgreSQL + pgvector
- **AI**: OpenAI GPT-4 for interview and embeddings
- **Matching**: Cosine similarity on personality embeddings

## Project Structure

```
resonance/
├── frontend/              # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx       # Main landing page
│   │   ├── services/
│   │   │   └── api.js    # API service layer
│   │   └── index.css     # Tailwind CSS + custom styles
│   └── package.json
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── auth/         # Authentication service
│   │   ├── interview/    # AI interview service
│   │   ├── profile/      # Profile management
│   │   ├── matching/     # Matching algorithm
│   │   └── database/     # Database schema & connection
│   ├── main.py           # FastAPI application
│   ├── requirements.txt  # Python dependencies
│   └── .env.example      # Environment variables template
└── README.md
```

## v0.1 Features

### Frontend
- Waitlist landing page with email signup
- kastle.ai-inspired design (fintech dark UI aesthetic)
- Responsive design with scroll animations
- Connected to backend API

### Backend
- User authentication (signup/login with JWT)
- Text-only AI interview for personality extraction
- Profile creation with trait storage
- Simple cosine similarity matching
- Match rationale generation using GPT-4

## Setup

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

### Backend Setup

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your actual values
```

Required environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key
- `SECRET_KEY` - JWT secret key

3. Initialize database:
```bash
python init_db.py
```

4. Run the backend server:
```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs on `http://localhost:8000`

### Database Setup

The project requires PostgreSQL with the following extensions:
- Standard PostgreSQL features
- For v0.1, we're using text storage for embeddings (pgvector can be added for v0.5+)

Create database:
```sql
CREATE DATABASE wavelength;
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

## Development Roadmap

### v0.1 (Current)
- ✅ Text-only onboarding interview
- ✅ Simple cosine-similarity matching
- ✅ Waitlist landing page
- ✅ Basic authentication
- ✅ Profile management

### v0.5 (Next)
- FastAPI backend completion
- LLM-based match rationale generation
- Push + email handoff
- Basic admin dashboard
- PostgreSQL + pgvector integration

### v1.0
- Voice-based interview (STT)
- Age/identity verification
- Automated moderation pipeline
- Analytics pipeline

### v2.0
- Learned ranking model
- Managed vector DB (Qdrant/Pinecone)
- Automated date-concierge integrations

## Tech Stack

### Frontend
- React 19
- Vite
- Tailwind CSS v4
- Custom CSS variables for theming

### Backend
- FastAPI
- SQLAlchemy ORM
- PostgreSQL
- OpenAI GPT-4
- JWT authentication
- NumPy & scikit-learn for similarity calculations

## Design System

The frontend follows the kastle.ai design specification:
- Light theme with #ffffff background
- #171717 body text
- #0000ee accent color (CTAs only)
- Fraunces font for headings
- JetBrains Mono for body text
- Sharp edges, generous whitespace
- Subtle scroll animations

## License

ISC
