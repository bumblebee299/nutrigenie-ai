# 🥗 NutriGenie AI

> **An AI-powered Nutrition Assistant built with IBM watsonx.ai, FastAPI, Next.js, IBM Cloudant, and IBM Cloud Object Storage.**

NutriGenie AI helps users make healthier dietary decisions through conversational AI, personalized meal planning, food image analysis, nutrition label interpretation, healthy food recommendations, and weekly nutrition tracking.

---

## 🚀 Live Demo

**Frontend:**  
https://nutrigenie-ai.vercel.app

**Backend API:**  
https://nutrigenie-ai.onrender.com

**Swagger Documentation:**  
https://nutrigenie-ai.onrender.com/docs

---

# ✨ Features

## 🤖 AI Nutrition Chat

- Ask nutrition and health-related questions.
- Personalized responses.
- Context-aware conversations.
- Powered by IBM watsonx.ai.

---

## 🍽 Personalized Meal Planner

Generate AI-powered meal plans using:

- Age
- Height
- Weight
- Fitness Goal
- Dietary Preference
- Allergies
- Cuisine Preference
- Budget

Includes:

- Breakfast
- Lunch
- Dinner
- Snacks
- Daily Nutrition Summary

---

## 📸 Food Image Analysis

Upload a food image to receive:

- Detected food items
- Estimated calories
- Portion estimation
- Nutritional notes
- Healthier alternatives
- AI explanation

Images are securely stored in **IBM Cloud Object Storage** before analysis.

---

## 🏷 Nutrition Label Reader

Upload a nutrition facts label and receive:

- Calories
- Protein
- Sugar
- Fat
- Sodium
- Health warnings
- Easy-to-understand explanation

---

## 🥗 Healthy Food Swap

Get healthier alternatives for unhealthy foods.

Examples:

- French Fries → Baked Sweet Potato
- Cola → Lemon Water
- Ice Cream → Greek Yogurt

Each recommendation includes an explanation.

---

## 📊 Weekly Dashboard

Track your nutrition progress through:

- Calories
- Protein
- Water Intake
- Weight
- Weekly Progress

---

## 🔐 Secure Authentication

- User Registration
- Login
- JWT Authentication
- Protected Routes

---

# 🏗 Project Architecture

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

# 🏛 System Architecture

```
                    User
                      │
                      ▼
              Next.js Frontend
                      │
                      ▼
              FastAPI Backend
         ┌──────────┼──────────┐
         ▼          ▼          ▼
 IBM watsonx.ai   Cloudant    IBM COS
      AI         Database     Image Storage
```

---

# 🛠 Technology Stack

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

# 📡 API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/auth/register` | Register User |
| POST | `/auth/login` | Login |
| GET | `/auth/me` | Current User |
| POST | `/chat` | AI Nutrition Chat |
| POST | `/meal-plan` | Generate Meal Plan |
| POST | `/image-analysis` | Food Image Analysis |
| POST | `/label-analysis` | Nutrition Label Analysis |
| POST | `/food-swap` | Healthy Food Alternatives |
| GET | `/dashboard/{user_id}` | Weekly Dashboard |
| GET | `/profile/{user_id}` | User Profile |
| PATCH | `/profile/{user_id}` | Update Profile |

Swagger:

```
https://nutrigenie-ai.onrender.com/docs
```

---

# ⚙ Local Development

## Clone Repository

```bash
git clone https://github.com/bumblebee299/nutrigenie-ai.git

cd nutrigenie-ai
```

---

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

# 🔑 Environment Variables

Create a `.env` file:

```env
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

# 🐳 Docker

Build and Run

```bash
docker-compose up --build
```

Stop

```bash
docker-compose down
```

---

# ☁ Deployment

| Component | Platform |
|------------|----------|
| Frontend | Vercel |
| Backend | Render |
| AI | IBM watsonx.ai |
| Database | IBM Cloudant |
| Storage | IBM Cloud Object Storage |

---

# ✅ Code Quality

## Backend

```bash
ruff check backend

black backend

mypy backend
```

## Frontend

```bash
cd frontend

npm run lint

npm run type-check

npm run build
```

---

# 🧪 Testing

Backend

```bash
pytest
```

Frontend

```bash
npm test
```

---

# 📂 IBM Cloud Services Used

- IBM watsonx.ai
- IBM Cloudant
- IBM Cloud Object Storage
- IBM IAM

---

# 🧠 AI Model

Current Model

```
meta-llama/llama-3-3-70b-instruct
```

Used for:

- AI Nutrition Chat
- Meal Planner
- Food Image Analysis
- Nutrition Label Reader
- Healthy Food Swap

---

# 📈 Project Status

| Module | Status |
|----------|--------|
| Project Setup | ✅ |
| Authentication | ✅ |
| User Profile | ✅ |
| AI Chat | ✅ |
| Meal Planner | ✅ |
| Food Image Analysis | ✅ |
| Nutrition Label Reader | ✅ |
| Healthy Food Swap | ✅ |
| Weekly Dashboard | ✅ |
| IBM Cloud Integration | ✅ |
| Deployment | ✅ |

---

# 🛣 Roadmap

- Responsive mobile dashboard improvements
- Barcode scanning support
- Meal history analytics
- Multi-language support
- Mobile application

---

# 🤝 Acknowledgements

This project was built using:

- IBM watsonx.ai
- IBM Cloudant
- IBM Cloud Object Storage
- FastAPI
- Next.js
- React
- Tailwind CSS
- TypeScript

---

# 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Shrvan Kumat**

GitHub: https://github.com/bumblebee299

---

⭐ If you found this project useful, consider giving it a star!
