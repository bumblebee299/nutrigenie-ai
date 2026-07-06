# NutriGenie AI

> Intelligent AI-powered Nutrition Assistant built with **Next.js**, **FastAPI**, **IBM watsonx.ai**, **IBM Cloudant**, and **IBM Cloud Object Storage**.

---

# Overview

NutriGenie AI is a full-stack AI nutrition assistant that helps users make healthier food choices through conversational AI, personalized meal planning, food image analysis, nutrition label interpretation, healthy food swaps, and progress tracking.

The application is powered by **IBM watsonx.ai** using **Meta Llama 3.3 70B Instruct**, while leveraging IBM Cloud services for secure storage and scalable deployment.

---

# Features

## AI Nutrition Chat
- Ask nutrition and health-related questions.
- Personalized responses based on user profile.
- Context-aware conversations.

---

## Personalized Meal Planner
Generate meal plans based on:

- Age
- Height
- Weight
- Fitness goal
- Dietary preference
- Allergies
- Cuisine preference
- Budget

Includes:

- Breakfast
- Lunch
- Dinner
- Snacks
- Daily nutrition summary

---

## Food Image Analysis

Upload a food image to receive:

- Detected food items
- Estimated calories
- Portion estimation
- Nutritional notes
- Healthier alternatives
- AI explanation

Images are securely stored in **IBM Cloud Object Storage**.

---

## Nutrition Label Reader

Upload a nutrition facts label and receive:

- Calories
- Protein
- Fat
- Sugar
- Sodium
- Health warnings
- Easy-to-understand explanation

---

## Healthy Food Swap

Replace unhealthy foods with healthier alternatives.

Example:

- French Fries → Baked Sweet Potato
- Cola → Lemon Water
- Ice Cream → Greek Yogurt

Includes explanation for every recommendation.

---

## Weekly Dashboard

Track:

- Calories
- Protein
- Water Intake
- Weight
- Weekly progress

---

## User Authentication

- Register
- Login
- JWT Authentication
- Protected Routes

---

# Project Architecture

```
NutriGenie AI
│
├── backend
│   ├── api
│   ├── database
│   ├── models
│   ├── prompts
│   ├── routes
│   ├── services
│   ├── tests
│   └── main.py
│
├── frontend
│   ├── app
│   ├── components
│   ├── hooks
│   ├── services
│   ├── public
│   └── package.json
│
├── Dockerfile
├── docker-compose.yml
├── README.md
└── pyproject.toml
```

---

# Technology Stack

## Frontend

- Next.js 14
- React
- TypeScript
- Tailwind CSS
- Axios

---

## Backend

- FastAPI
- Python 3.11
- Pydantic v2
- Uvicorn

---

## AI

- IBM watsonx.ai
- Meta Llama 3.3 70B Instruct
- IBM watsonx-ai SDK

---

## IBM Cloud Services

- IBM watsonx.ai
- IBM Cloudant
- IBM Cloud Object Storage
- IBM IAM

---

# API Endpoints

| Method | Endpoint | Description |
|----------|------------------------|----------------|
| POST | /auth/register | Register user |
| POST | /auth/login | Login |
| GET | /auth/me | Current user |
| POST | /chat | AI Chat |
| POST | /meal-plan | Generate meal plan |
| POST | /image-analysis | Analyze food image |
| POST | /label-analysis | Analyze nutrition label |
| POST | /food-swap | Healthy food alternatives |
| GET | /dashboard/{user_id} | Weekly dashboard |
| GET | /profile/{user_id} | User profile |
| PATCH | /profile/{user_id} | Update profile |

Swagger:

```
http://localhost:8000/docs
```

---

# Local Development

## Backend

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r backend/requirements.txt

uvicorn backend.main:app --reload --port 8000
```

Backend:

```
http://localhost:8000
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend:

```
http://localhost:3000
```

---

# Environment Variables

Create a `.env` file and configure:

```
SECRET_KEY=

WATSONX_API_KEY=

WATSONX_PROJECT_ID=

WATSONX_URL=

GRANITE_MODEL_ID=meta-llama/llama-3-3-70b-instruct

CLOUDANT_URL=

CLOUDANT_API_KEY=

COS_API_KEY=

COS_INSTANCE_CRN=

COS_BUCKET_IMAGES=

COS_ENDPOINT=

NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

# Docker

Build:

```bash
docker-compose up --build
```

Stop:

```bash
docker-compose down
```

---

# Code Quality

Backend

```bash
ruff check backend

black backend

mypy backend
```

Frontend

```bash
cd frontend

npm run lint

npm run type-check

npm run build
```

---

# Testing

Backend

```bash
pytest
```

Frontend

```bash
npm test
```

---

# IBM Cloud Services Used

- IBM watsonx.ai
- IBM Cloudant
- IBM Cloud Object Storage
- IBM IAM
- IBM Cloud Code Engine (deployment ready)

---

# AI Model

Current model:

```
meta-llama/llama-3-3-70b-instruct
```

The application uses IBM watsonx.ai for all AI-powered features including:

- AI Chat
- Meal Planning
- Food Image Analysis
- Nutrition Label Reader
- Healthy Food Swap

---

# Project Status

| Module | Status |
|----------|---------|
| Project Setup | ✅ Complete |
| Authentication | ✅ Complete |
| User Profile | ✅ Complete |
| AI Chat | ✅ Complete |
| Meal Planner | ✅ Complete |
| Food Image Analysis | ✅ Complete |
| Nutrition Label Reader | ✅ Complete |
| Healthy Food Swap | ✅ Complete |
| Weekly Dashboard | ✅ Complete |
| IBM Cloud Integration | ✅ Complete |

---

# Future Improvements

- Multimodal IBM Granite Vision model support (when available)
- Meal history tracking
- Feedback learning
- Push notifications
- Mobile application

---

# License

MIT License

---

Built with ❤️ using IBM watsonx.ai and IBM Cloud.