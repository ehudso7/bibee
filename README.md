# bibee

AI-powered vocal replacement platform. Upload a song, separate stems, and replace vocals with your own voice or an AI persona.

## Features

- **Stem Separation**: Automatically separate vocals, drums, bass, and instrumentals using Demucs AI
- **Voice Conversion**: Replace original vocals with your voice or create AI voice personas
- **Pro Mixing**: Mix and master your track with professional audio processing tools

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy 2.x, Celery, PostgreSQL, Redis
- **Frontend**: Next.js 14, Tailwind CSS, TypeScript
- **AI/Audio**: Demucs, librosa, PyTorch

## Quick Start

```bash
# Clone the repository
git clone https://github.com/ehudso7/bibee.git
cd bibee

# Copy environment file
cp .env.example .env

# Start with Docker Compose
docker-compose up --build
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

## Project Structure

```
bibee/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   ├── pipelines/    # Audio processing
│   │   └── workers/      # Celery tasks
│   └── tests/
├── frontend/
│   ├── app/              # Next.js pages
│   ├── components/       # React components
│   └── lib/              # Utilities
└── docker-compose.yml
```

## License

MIT
