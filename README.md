# NutriGenie AI

**Intelligent Nutrition Assistant** powered by IBM Granite and watsonx.ai

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Project Architecture](#project-architecture)
4. [Technology Stack](#technology-stack)
5. [API Overview](#api-overview)
6. [Local Development Setup](#local-development-setup)
7. [Environment Variables](#environment-variables)
8. [Docker Deployment](#docker-deployment)
9. [IBM Cloud Code Engine Deployment](#ibm-cloud-code-engine-deployment)
10. [Code Quality](#code-quality)
11. [Testing](#testing)

---

## Overview

NutriGenie AI is a production-quality AI nutrition assistant that leverages **IBM Granite** (via watsonx.ai) to provide personalised meal plans, food image analysis, nutrition label interpretation, and intelligent food swap recommendations. All user data is stored in **IBM Cloudant** and food images are managed via **IBM Cloud Object Storage**.

---

## Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **AI Chat** | Natural language nutrition Q&A powered by IBM Granite |
| 2 | **Personalised Meal Planner** | Daily plan generation from user profile (age, weight, goals, allergies, cuisine, budget) |
| 3 | **Food Image Analysis** | Upload a photo — identify foods, estimate calories, suggest healthier alternatives |
| 4 | **Nutrition Label Reader** | Upload a label image — get a plain-English breakdown of sugar, fat, protein, sodium + health warnings |
| 5 | **Healthy Food Swap** | Swap unhealthy foods for nutritionally better alternatives with explanations |
| 6 | **Weekly Progress Dashboard** | Calories, protein, water, weight, and goal adherence charts |
| 7 | **Feedback Learning** | Every recommendation includes a "Helpful?" prompt; responses stored to continuously improve outputs |
| 8 | **Explainability** | All AI responses include a `why this recommendation?` explanation |

---

## Project Architecture

```
NutriGenie AI/
├── backend/                     # FastAPI application (clean architecture)
│   ├── api/
│   │   └── config.py            # Pydantic-settings — all env vars
│   ├── database/
│   │   ├── cloudant.py          # IBM Cloudant client singleton
│   │   └── cos.py               # IBM Cloud Object Storage client
│   ├── models/                  # Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── dashboard.py
│   │   ├── food_swap.py
│   │   ├── image_analysis.py
│   │   ├── label_analysis.py
│   │   ├── meal_plan.py
│   │   └── profile.py
│   ├── prompts/                 # Granite prompt templates
│   ├── routes/                  # FastAPI routers (one per domain)
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── dashboard.py
│   │   ├── food_swap.py
│   │   ├── image_analysis.py
│   │   ├── label_analysis.py
│   │   ├── meal_plan.py
│   │   └── profile.py
│   ├── services/                # Business logic & AI service layer
│   ├── tests/                   # pytest test suite
│   ├── main.py                  # FastAPI application factory
│   └── requirements.txt
│
├── frontend/                    # Next.js 14 App Router application
│   ├── app/
│   │   ├── layout.tsx           # Root layout (theme + providers)
│   │   ├── page.tsx             # Landing page
│   │   ├── providers.tsx        # React Query + Theme + Toast providers
│   │   └── globals.css          # Tailwind base + component classes
│   ├── components/              # Reusable React components
│   ├── hooks/                   # Custom React hooks
│   ├── services/
│   │   └── apiClient.ts         # Axios instance with auth interceptors
│   ├── public/
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── next.config.ts
│   ├── .eslintrc.json
│   └── package.json
│
├── Dockerfile                   # Multi-stage build (backend + frontend)
├── docker-compose.yml           # Local orchestration with Redis
├── pyproject.toml               # Ruff, Black, mypy, pytest config
├── .env.example                 # Environment variable template
└── README.md
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 · React 18 · TypeScript (strict) · Tailwind CSS |
| Backend | Python 3.11 · FastAPI · Pydantic v2 · Uvicorn |
| AI / LLM | IBM Granite via ibm-watsonx-ai SDK |
| Database | IBM Cloudant (NoSQL) |
| Storage | IBM Cloud Object Storage |
| Caching | Redis |
| Deployment | IBM Cloud Code Engine · Docker |

---

## API Overview

All backend routes are prefixed by default at `http://localhost:8000`.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Authenticate and receive JWT tokens |
| `POST` | `/auth/refresh` | Refresh access token |
| `POST` | `/auth/logout` | Invalidate session |
| `POST` | `/chat` | Send a nutrition question to Granite |
| `POST` | `/chat/feedback` | Submit thumbs-up/down feedback |
| `POST` | `/meal-plan` | Generate a personalised daily meal plan |
| `POST` | `/image-analysis` | Upload a food photo for analysis |
| `POST` | `/food-swap` | Request healthier alternatives for a food item |
| `POST` | `/label-analysis` | Upload a nutrition label for interpretation |
| `GET`  | `/dashboard/{user_id}` | Retrieve weekly progress data |
| `GET`  | `/profile/{user_id}` | Get user profile |
| `PATCH`| `/profile/{user_id}` | Update user profile |

Interactive documentation is available at **`/docs`** (Swagger UI) and **`/redoc`** when `ENVIRONMENT != production`.

---

## Local Development Setup

### Prerequisites

- **Node.js** ≥ 20
- **Python** ≥ 3.11
- **Docker** & **Docker Compose** (for containerised development)
- IBM Cloud account with:
  - watsonx.ai project
  - Cloudant instance
  - Cloud Object Storage bucket

### 1 — Clone & Configure Environment

```bash
git clone https://github.com/bumblebee299/nutrigenie-ai.git
cd nutrigenie-ai

cp .env.example .env
# Edit .env and fill in all IBM Cloud credentials
```

### 2 — Backend Setup

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run the development server (auto-reload)
uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000/docs`.

### 3 — Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the Next.js dev server
npm run dev
```

The frontend will be available at `http://localhost:3000`.

---

## Environment Variables

Copy `.env.example` to `.env` and populate all values. Key variables:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | JWT signing secret — use a 32+ character random string |
| `WATSONX_API_KEY` | IBM watsonx.ai API key |
| `WATSONX_PROJECT_ID` | watsonx.ai project ID |
| `GRANITE_MODEL_ID` | Granite model identifier (default: `ibm/granite-13b-instruct-v2`) |
| `CLOUDANT_URL` | IBM Cloudant service URL |
| `CLOUDANT_API_KEY` | IBM Cloudant IAM API key |
| `COS_API_KEY` | IBM COS IAM API key |
| `COS_INSTANCE_CRN` | IBM COS resource instance CRN |
| `NEXT_PUBLIC_API_BASE_URL` | Backend URL exposed to the browser |

---

## Docker Deployment

### Build & Run with Docker Compose

```bash
# Build and start all services (backend, frontend, redis)
docker-compose up --build

# Run in background
docker-compose up --build -d

# Tear down
docker-compose down
```

Services:

| Container | Port | Description |
|-----------|------|-------------|
| `nutrigenie_backend` | 8000 | FastAPI |
| `nutrigenie_frontend` | 3000 | Next.js |
| `nutrigenie_redis` | 6379 | Redis cache |

### Build Individual Images

```bash
# Backend only
docker build --target backend -t nutrigenie-backend .

# Frontend only
docker build --target frontend -t nutrigenie-frontend .
```

---

## IBM Cloud Code Engine Deployment

1. **Install IBM Cloud CLI** and the Code Engine plugin:

   ```bash
   ibmcloud plugin install code-engine
   ibmcloud ce project create --name nutrigenie-ai
   ibmcloud ce project select --name nutrigenie-ai
   ```

2. **Push images** to IBM Container Registry:

   ```bash
   ibmcloud cr namespace-add nutrigenie
   docker tag nutrigenie-backend us.icr.io/nutrigenie/backend:latest
   docker tag nutrigenie-frontend us.icr.io/nutrigenie/frontend:latest
   docker push us.icr.io/nutrigenie/backend:latest
   docker push us.icr.io/nutrigenie/frontend:latest
   ```

3. **Deploy applications**:

   ```bash
   # Backend
   ibmcloud ce app create \
     --name nutrigenie-backend \
     --image us.icr.io/nutrigenie/backend:latest \
     --port 8000 \
     --env-from-secret nutrigenie-secrets

   # Frontend
   ibmcloud ce app create \
     --name nutrigenie-frontend \
     --image us.icr.io/nutrigenie/frontend:latest \
     --port 3000 \
     --env NEXT_PUBLIC_API_BASE_URL=<backend-code-engine-url>
   ```

4. **Create secrets** for sensitive environment variables:

   ```bash
   ibmcloud ce secret create --name nutrigenie-secrets \
     --from-env-file .env
   ```

---

## Code Quality

### Backend

```bash
# Lint (Ruff)
ruff check backend/

# Auto-fix
ruff check --fix backend/

# Format (Black)
black backend/

# Type-check (mypy)
mypy backend/
```

### Frontend

```bash
cd frontend

# Lint (ESLint)
npm run lint

# Auto-fix
npm run lint:fix

# Format (Prettier)
npm run format

# Type-check (TypeScript)
npm run type-check
```

---

## Testing

### Backend

```bash
# Run all tests with coverage
pytest

# Watch mode
pytest --watch
```

### Frontend

```bash
cd frontend
npm test
```

---

## Development Roadmap

| Task | Module | Status |
|------|--------|--------|
| 1 | Project Foundation | ✅ Complete |
| 2 | Authentication + Profile | ⏳ Pending |
| 3 | AI Chat | ⏳ Pending |
| 4 | Meal Planner | ⏳ Pending |
| 5 | Food Image Analysis | ⏳ Pending |
| 6 | Food Swap | ⏳ Pending |
| 7 | Nutrition Label Reader | ⏳ Pending |
| 8 | Weekly Dashboard | ⏳ Pending |

---

*Built with IBM Granite · watsonx.ai · IBM Cloud*
