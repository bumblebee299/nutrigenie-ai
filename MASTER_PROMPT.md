# MASTER PROMPT

## Development Rules

- Work incrementally.
- Generate only the module requested in each prompt.
- Never modify unrelated files unless necessary.
- Keep commits logically separated.
- Ensure the project builds successfully after every task.
- Prefer maintainable, production-ready code over quick prototypes.
- Ask for confirmation before proceeding to the next module.

You are the lead software architect for this project.

Build a production-quality AI Nutrition Assistant.

Project Name:
NutriGenie AI

Goal:
Develop an intelligent nutrition assistant using IBM Granite and IBM Cloud Lite.

Technology Stack

Frontend
- Next.js
- React
- TypeScript
- Tailwind CSS

Backend
- Python FastAPI

Database
- IBM Cloudant

AI
- IBM Granite
- watsonx.ai

Storage
- IBM Cloud Object Storage

Deployment
- IBM Cloud Code Engine

Architecture Requirements

Use clean architecture.

backend/
    api/
    services/
    models/
    routes/
    database/
    prompts/

frontend/
    app/
    components/
    services/
    hooks/

Coding Standards

- TypeScript strict mode
- Python type hints
- Modular architecture
- Reusable components
- Environment variables
- Proper error handling
- Logging
- API documentation
- Responsive UI

Features

1. AI Chat

Users can ask nutrition questions.

Granite must generate answers.

2. Personalized Meal Planner

Input

Age
Height
Weight
Gender
Goal
Disease
Allergy
Cuisine
Budget
Lifestyle

Generate

Calories

Breakfast

Lunch

Dinner

Snacks

Water

Nutrition summary

3. Food Image Analysis

Upload image

Identify food

Estimate calories

Suggest healthier alternatives

4. Nutrition Label Reader

Upload label

Explain

Sugar

Fat

Protein

Sodium

Warnings

5. Healthy Food Swap

Example

Pizza
↓

Whole wheat vegetable pizza

6. Weekly Progress Dashboard

Calories

Protein

Water

Weight

Goal

Charts

7. Feedback Learning

Every recommendation asks

Helpful?

Store feedback in Cloudant.

Improve future recommendations.

8. Explainability

Every recommendation must include

Why this recommendation?

Nutritional explanation.

API Design

/auth
/chat
/meal-plan
/image-analysis
/food-swap
/label-analysis
/dashboard
/profile

Frontend

Modern dashboard

Dark mode

Responsive

Animated cards

Beautiful charts

Deployment

Docker support

README

.env.example

Testing

Unit tests

Integration tests

Generate production-quality code only.

Never leave TODO comments.

Never generate placeholder code unless explicitly requested.

Build one module at a time.

Wait after each module for confirmation before proceeding.