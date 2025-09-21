# 🚀 AI Startup Analyst Platform

AI-powered analyst platform that evaluates startups by synthesizing founder materials and public data to generate concise, actionable investment insights.

## 🎯 Overview

Early-stage investors often drown in unstructured startup data — pitch decks, founder calls, emails, and scattered news reports. This AI analyst cuts through the noise, evaluates startups like a trained associate, and generates investor-ready insights at scale.

## ✅ Key Features

- **Multi-Document Analysis**: PDF, DOCX, DOC files (pitch decks, transcripts, emails)
- **Structured Deal Notes**: Executive summaries, investment scores, recommendations
- **Sector Benchmarking**: Compare against industry peers with financial multiples
- **Risk Detection**: Identify inconsistent metrics and red flags
- **Growth Analysis**: Comprehensive growth potential assessment
- **Interactive Dashboards**: Chart.js visualizations with scoring breakdowns
- **Professional Reports**: Generate investor-ready PDF exports

## 🛠️ Tech Stack

### Google AI Services
- **Gemini 2.5 Flash**: Core AI analysis engine
- **Vertex AI**: ML capabilities for predictive analytics
- **Cloud Vision**: Document and image analysis
- **BigQuery**: Data analytics and benchmarking
- **Firestore**: Real-time data storage
- **Agent Builder**: Intelligent workflow orchestration

### Framework
- **Backend**: FastAPI with Python
- **Frontend**: Next.js 14 with TypeScript
- **Visualization**: Chart.js dashboards

## 📊 Analysis Framework

### Scoring Categories (0-100)
1. **Market Opportunity**: Market size, growth potential, competitive landscape
2. **Team Quality**: Founder experience, expertise, track record
3. **Product Innovation**: Uniqueness, technical feasibility, differentiation
4. **Financial Potential**: Revenue model, scalability, unit economics
5. **Execution Capability**: Go-to-market strategy, milestone achievement

### Risk Assessment
- **Risk Level**: High/Medium/Low classification
- **Red Flags**: Inconsistent metrics, inflated projections, team gaps
- **Mitigation**: Actionable recommendations for risk reduction

## 🚀 Quick Start

### Live Application
- **Frontend**: https://my-project-genai-464305.web.app/
- **Backend API**: https://startup-ai-analyst-backend-281259205924.us-central1.run.app
- **API Documentation**: https://startup-ai-analyst-backend-281259205924.us-central1.run.app/docs

### Local Development

#### Prerequisites
- Python 3.8+ with pip
- Node.js 18+ with npm
- Google Cloud credentials

#### Setup
```bash
# Clone repository
git clone https://github.com/thechetan9/startup-ai-analyst.git
cd startup-ai-analyst

# Backend setup
cd backend
pip install -r requirements.txt
# Configure .env file with your credentials

# Frontend setup
cd ../frontend
npm install
```

#### Run Locally
```bash
# Terminal 1: Backend
cd backend && python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

Access at:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## 📝 Usage

1. **Upload Documents**: Drag & drop PDF/DOCX files (pitch decks, business plans)
2. **AI Analysis**: Gemini processes documents and generates insights
3. **Review Results**: View scoring, benchmarks, and risk assessment
4. **Export Reports**: Generate PDF reports for investment decisions

## 🚀 Deployment

Deploy to Google Cloud:
```bash
# Backend to Cloud Run
cd backend
gcloud run deploy --source .

# Frontend to Firebase
cd ../frontend
npm run build
firebase deploy
```

## 📁 Project Structure

```
startup-ai-analyst/
├── backend/          # FastAPI backend with Google AI integration
├── frontend/         # Next.js frontend with TypeScript
├── diagrams/         # Architecture diagrams
└── README.md         # This documentation
```

## 📄 License

MIT License - see LICENSE file for details.
