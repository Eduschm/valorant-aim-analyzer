# 🎮 Valorant Aim Analyzer

**Real-time AI-powered analysis of Valorant gameplay for aim improvement.**

Automatically analyze your aim, positioning, crosshair placement, and game sense with frame-by-frame breakdowns, weapon statistics, and personalized coaching insights.

---

## 🎯 Features

- **📊 Aim Statistics**: Headshot percentage, accuracy, ADR (Aim Damage Rating), HS/TP ratio
- **🎯 Weapon Analysis**: Performance metrics per weapon type (Vandal, Phantom, Sheriff, etc.)
- **💡 Agent-Specific Insights**: Tailored advice based on character selection
- **🔄 Round-by-Round Breakdown**: Detailed analysis of each round's performance
- **📈 Trend Tracking**: Historical data to track improvement over time
- **🤖 AI Coaching**: Natural language insights on mechanical skill and game sense
- **🎬 Annotated Clip Analysis** (Phase 2): Frame-by-frame video review with annotations
- **📱 Responsive Design**: Full support for desktop and tablet

---

## 📋 Project Structure

```
valorant-aim-analyzer/
├── frontend/                    # Next.js 14 web application
│   ├── app/                    # App Router pages & routing
│   ├── components/             # React components
│   ├── lib/                    # Utilities, API client, stores
│   ├── public/                 # Static assets
│   ├── package.json
│   └── README_DETAILED.md      # Frontend-specific docs
│
├── services/                    # Microservices architecture
│   ├── api/                    # Main REST API (Flask/FastAPI)
│   │   ├── app.py             # API server entry
│   │   ├── requirements.txt    # Python dependencies
│   │   └── routes/            # API route handlers
│   │
│   ├── cv/                     # Computer Vision service
│   │   ├── main.py            # CV pipeline entry point
│   │   ├── config.py          # Configuration
│   │   ├── requirements.txt    # Python dependencies
│   │   ├── src/               # Processing modules
│   │   ├── models/            # YOLO weights & model files
│   │   └── output/            # Generated reports & videos
│   │
│   ├── llm/                    # Language Model service
│   │   └── app.py             # LLM inference wrapper
│   │
│   └── riot/                   # Riot API integration
│       └── client.py           # Riot API client
│
├── contracts/                   # Shared type definitions
│   └── schemas.py              # Data models & interfaces
│
├── data/                        # Dataset & training files
│   ├── data.yaml              # Dataset config
│   ├── train/                 # Training annotations
│   └── valid/                 # Validation annotations
│
├── scripts/                     # Utility scripts
│   ├── train.py               # Model training
│   ├── download_dataset.py    # Data fetching
│   └── label_tool.py          # Annotation tool
│
├── API_CONTRACT.md             # Frontend-backend API spec
├── FRONTEND_PLAN.md           # Frontend requirements
├── NEXT_STEPS.md              # Integration checklist
└── CLAUDE.md                  # Development philosophy
```

---

## 🛠️ Tech Stack

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| **Node.js** | 18+ | Runtime |
| **Next.js** | 14.2.3 | React framework (App Router) |
| **React** | 18.3.1 | UI library |
| **TypeScript** | 5.4.2 | Type safety |
| **Tailwind CSS** | 3.4.1 | Styling (Valorant theme) |
| **Zustand** | 4.5.0 | State management |
| **React Hook Form** | 7.51.0 | Form handling |
| **Zod** | 3.22.4 | Schema validation |
| **Recharts** | 2.12.0 | Data visualization |
| **NextAuth.js** | 5.0.0-beta | Authentication |
| **Lucide React** | 0.408.0 | Icons |

### Backend Services
| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.10+ | Runtime |
| **FastAPI** / **Flask** | Latest | Web framework |
| **YOLOv8** | - | Object detection model |
| **OpenCV** | Latest | Computer vision |
| **Anthropic Claude** | Latest | AI insights (local) |
| **SQLAlchemy** | - | ORM |
| **Pydantic** | - | Data validation |

### Infrastructure
- **Development**: Docker, Docker Compose
- **Deployment**: Vercel (frontend), AWS/GCP/VPS (backend)
- **Version Control**: Git + GitHub

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and **npm**
- **Python** 3.10+ and **pip**
- **Docker** and **Docker Compose** (optional)

### Option 1: Run Everything with Docker Compose
```bash
# Clone and setup
git clone <repo-url>
cd valorant-aim-analyzer

# Start all services
docker-compose up

# Frontend: http://localhost:3000
# API: http://localhost:3001
# CV: Running in background
```

### Option 2: Run Services Separately

#### 1. Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

#### 2. Backend API
```bash
cd services/api
pip install -r requirements.txt
python app.py
# → http://localhost:3001
```

#### 3. CV Service (Optional - for analysis)
```bash
cd services/cv
pip install -r requirements.txt
python main.py
# → Runs analysis jobs
```

---

## 📝 Development Workflow

### 1. Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run production build
npm start

# Type check
npm run type-check

# Format code
npm run format
```

### 2. Backend Development
```bash
cd services/api

# Install dependencies
pip install -r requirements.txt

# Run with hot reload (development)
python -m flask --app app run --reload

# Run with Uvicorn (FastAPI)
uvicorn app:app --reload --port 3001
```

### 3. CV Service Development
```bash
cd services/cv

# Install dependencies
pip install -r requirements.txt

# Run analysis on a single video
python main.py --input video.mp4 --output ./output

# Run with config file
python main.py --config config.py
```

---

## 🔌 API Integration

### Frontend → Backend Communication

The frontend communicates with the backend via typed API client. All endpoints defined in:
- **Specification**: [API_CONTRACT.md](API_CONTRACT.md)
- **Client Code**: [frontend/lib/api.ts](frontend/lib/api.ts)

### Key Endpoints

**Authentication**
- `POST /api/auth/signin` - Send magic link
- `POST /api/auth/callback` - Verify magic link
- `GET /api/auth/session` - Current session

**Analysis**
- `POST /api/analysis/tracker` - Create new analysis
- `GET /api/analysis/:id` - Get analysis details
- `GET /api/analysis/history` - List user's analyses

**User**
- `GET /api/user/profile` - Get profile
- `PUT /api/user/profile` - Update profile

### Backend → CV Service Communication

The API routes requests to the CV service:
1. User uploads gameplay video → API receives
2. API queues job in CV service
3. CV service processes video (YOLO detection, metrics calculation)
4. CV service writes JSON + CSV reports to `services/cv/output/`
5. API returns results to frontend

---

## 📊 Project Phases

### ✅ Phase 1: Tracker-Only MVP (COMPLETE)
- Single game analysis upload
- Basic aim statistics
- Weapon performance
- Agent recommendations
- Magic link authentication

### 🔄 Phase 2: Clip Analysis (In Progress)
- Video clip upload with drag & drop
- Frame-by-frame breakdowns
- Annotated playback
- Engagement timeline
- Mistake highlights

### 🎯 Phase 3: Monetization
- Stripe payment integration
- Subscription pricing
- Usage metering
- Trial system (7-day free)
- Premium features

---

## 🧪 Testing

### Frontend Testing
```bash
cd frontend

# Unit & integration tests
npm run test

# E2E tests
npm run e2e

# Coverage report
npm run test:coverage
```

### Backend Testing
```bash
cd services/api

# Run tests
pytest

# With coverage
pytest --cov=.

# Specific test
pytest tests/test_auth.py -v
```

### CV Service Testing
```bash
cd services/cv

# Test detection model
python -m pytest src/tests/ -v

# Benchmark processing speed
python scripts/benchmark.py
```

---

## 🚢 Deployment

### Frontend Deployment

**Option 1: Vercel (Recommended)**
```bash
# Push to GitHub
git push origin main

# Connect repository in Vercel dashboard
# Auto-deploys on push to main branch
```

**Option 2: Docker**
```bash
# Build image
docker build -t valorant-frontend:latest ./frontend

# Run container
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://api.example.com valorant-frontend:latest
```

**Option 3: Traditional Hosting (VPS/AWS)
```bash
# Build production bundle
cd frontend && npm run build

# Use process manager (pm2)
pm2 start "npm start" --name "valorant-frontend"
```

### Backend Deployment

**Option 1: Docker (Recommended)**
```bash
# Build API service
docker build -t valorant-api:latest ./services/api

# Run with environment variables
docker run -p 3001:3001 \
  -e DATABASE_URL=postgresql://... \
  -e MAGIC_LINK_SECRET=... \
  valorant-api:latest
```

**Option 2: AWS Lambda**
```bash
# Package for Lambda
serverless package

# Deploy
serverless deploy
```

**Option 3: Traditional VPS**
```bash
# Using Gunicorn + Nginx
gunicorn -w 4 -b 0.0.0.0:3001 app:app

# Proxy through Nginx to port 80/443
```

### Environment Variables

Create `.env` files in each service:

**Frontend: `frontend/.env.local`**
```env
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_AUTH_URL=http://localhost:3000
```

**API: `services/api/.env`**
```env
DATABASE_URL=postgresql://user:pass@localhost/valorant_db
MAGIC_LINK_SECRET=your-secret-key
LLM_SERVICE_URL=http://localhost:3002
CV_SERVICE_URL=http://localhost:3003
RIOT_API_KEY=your-riot-key
```

**CV: `services/cv/.env`**
```env
YOLO_MODEL_PATH=./models/yolov8n.pt
OUTPUT_DIR=./output
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[README.md](README.md)** | You are here - Project overview |
| **[frontend/README_DETAILED.md](frontend/README_DETAILED.md)** | Complete frontend guide |
| **[API_CONTRACT.md](API_CONTRACT.md)** | Frontend-backend API specification |
| **[FRONTEND_PLAN.md](FRONTEND_PLAN.md)** | Frontend requirements & design |
| **[NEXT_STEPS.md](NEXT_STEPS.md)** | Integration checklist |
| **[DEPLOYMENT.md](frontend/DEPLOYMENT.md)** | Deployment guides for all platforms |
| **[CLAUDE.md](CLAUDE.md)** | Development philosophy & standards |

---

## 🤝 Contributing

### Development Standards
- All code must have passing tests
- TypeScript for frontend (strict mode)
- Python 3.10+ type hints for backend
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
- Open a PR for review before merging

### Code Style
```bash
# Frontend
npm run format        # Format with Prettier
npm run lint          # Check with ESLint

# Backend
black services/       # Format with Black
flake8 services/      # Lint with Flake8
```

### Adding a New Feature

1. **Create feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Implement changes** in relevant service(s)

3. **Add tests** and documentation

4. **Run tests locally**
   ```bash
   npm run test          # Frontend
   pytest               # Backend
   ```

5. **Commit & push**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin feature/my-feature
   ```

6. **Open PR** on GitHub

### Directory Conventions
- One concern = one service
- Each service has own tests, config, requirements
- Shared types in `contracts/`
- No circular dependencies between services
- All file operations use UTF-8 encoding

---

## 🐛 Troubleshooting

### Frontend Issues

**Port 3000 already in use**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
PORT=3001 npm run dev
```

**Module not found errors**
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**TypeScript errors**
```bash
# Type check entire project
npm run type-check
```

### Backend Issues

**Port 3001 already in use**
```bash
python -m flask run --port 3002
```

**Database connection failed**
```bash
# Check DATABASE_URL in .env
# Verify PostgreSQL is running
```

**YOLO model not found**
```bash
# Download model
python scripts/download_models.py
```

### CV Service Issues

**Out of memory on video processing**
```python
# Reduce batch size in config.py
BATCH_SIZE = 8  # Default 32
```

**GPU not detected**
```bash
# Verify CUDA installation
python -c "import torch; print(torch.cuda.is_available())"
```

---

## 📞 Support & Resources

### Getting Help
- **Issues**: GitHub Issues for bugs
- **Discussions**: GitHub Discussions for questions
- **Documentation**: See docs/ folder
- **Email**: support@valorantaimanalyzer.com

### Learning Resources
- [Next.js 14 Docs](https://nextjs.org/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [YOLOv8 Guide](https://docs.ultralytics.com/models/yolov8/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Zustand](https://github.com/pmndrs/zustand)

### Community
- Discord: [Join Community](https://discord.gg/valorant-analyzer)
- Twitter: [@ValorantAnalyzer](https://twitter.com/valorantanalyzer)
- Reddit: [r/ValorantAnalyzer](https://reddit.com/r/valorantanalyzer)

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

## 🙌 Acknowledgments

- **YOLOv8**: Ultralytics for object detection
- **Next.js Team**: For the amazing React framework
- **Valorant**: Riot Games for the game & API access
- **Community**: Contributors and beta testers

---

## 🔄 Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Frontend** | ✅ Complete | Production-ready, Next.js 14 |
| **API Service** | 🔄 In Progress | Skeleton created, endpoints needed |
| **CV Service** | 🔄 In Progress | YOLO detection working, needs refinement |
| **LLM Service** | ⏱️ Queued | Coaching insights generation |
| **Riot Integration** | ⏱️ Queued | API client for player stats |
| **Database** | ⏱️ Queued | PostgreSQL schema needed |

---

**Last Updated**: June 2026 | **Maintained By**: Eduardo & Team
