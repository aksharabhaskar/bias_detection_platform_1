# AI Fairness Audit Dashboard

An open-source project that explores how to detect bias and reason about fairness in AI recruitment systems. Built with React, FastAPI, and Flask, the dashboard currently offers 13 fairness metrics with visual explanations and shareable PDF exports to guide experimentation and learning.

## Features

- **13 Fairness Metrics**: Explore Demographic Parity, Disparate Impact, Equal Opportunity, and more as part of an evolving fairness toolkit
- **Interactive Visualizations**: Prototype charts and graphs powered by Recharts for quick insight
- **Detailed Explanations**: Living documentation with definitions, formulas, interpretations, and next-step ideas
- **PDF Report Generation**: Generate shareable ReportLab summaries for project notes or stakeholder feedback
- **Modern UI Experimentation**: Uses React, TypeScript, Tailwind CSS, and shadcn/ui components for a polished learning experience
- **Protected Attribute Analysis**: Current support for gender and age group comparisons
- **Auto Age Grouping**: Helper utility that derives age groups (20-30, 31-40, 41-50, 51-60) from raw age data

This project is still maturing. Expect active iteration, welcome rough edges, and feel free to experiment or contribute improvements.

## Prerequisites

- Docker Desktop (recommended for the fastest start)
- Optionally, Python 3.8+ and Node.js 16+ if you prefer running services without Docker

## Run with Docker (Recommended)

1. **Clone the repository**
  ```bash
  git clone https://github.com/aksharabhaskar/bias_detection_platform_1.git
  cd bias_detection_platform_1
  ```
2. **Start all services**
  ```bash
  docker compose up --build
  ```
  This single command builds the backend, frontend, and PDF service images, then launches them on a shared network for a local project demo.
3. **Open the dashboard** at [http://localhost](http://localhost).
4. **Stop the stack** when finished:
  ```bash
  docker compose down
  ```
  Add `-v` if you want to clear uploaded datasets.

Once running, uploads are stored in `backend/uploads` on the host so they persist between container restarts, making it easier to iterate on sample datasets.

## Manual Installation (Optional)

If you prefer to run everything without Docker, use the steps below to set up your local development environment and explore the codebase.

### 1. Clone the Repository

```bash
git clone https://github.com/aksharabhaskar/bias_detection_platform_1.git
cd bias_detection_platform_1
```

### 2. Backend Setup (FastAPI)

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. PDF Service Setup (Flask)

```bash
cd ../pdf_service
python -m venv venv

# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Frontend Setup (React + Vite)

```bash
cd ../frontend
npm install
```

### 5. Environment Configuration

Copy the example environment files and configure if needed:

```bash
# Root directory
cp .env.example .env

# Frontend directory
cd frontend
cp .env.example .env
```

## Running the Application

You need to run three services simultaneously:

### Terminal 1: FastAPI Backend

```bash
cd backend
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
python main.py
```

The FastAPI server will start at `http://localhost:8000`

### Terminal 2: Flask PDF Service

```bash
cd pdf_service
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
python app.py
```

The Flask PDF service will start at `http://localhost:8001`

### Terminal 3: React Frontend

```bash
cd frontend
npm run dev
```

The React app will start at `http://localhost:5173`

## Using the Dashboard

### 1. Upload Dataset

- Click or drag-and-drop a CSV file in the upload area
- Required column: `shortlisted` (binary: 0 or 1)
- Optional columns: `gender`, `age` (or `age_group`), `actual`, `predicted`, `score`
- Maximum file size: 10MB

### 2. Select Protected Attribute

- Choose between `gender` or `age_group`
- Age groups are automatically generated from the `age` column

### 3. Analyze Fairness

- Click "Analyze Fairness" to calculate all 13 metrics
- View results organized by status (All, Fair, Warnings, Violations)
- Each metric includes:
  - Visual assessment badge (Fair/Warning/Violation)
  - Interactive charts
  - Detailed explanations
  - Contextual recommendations

### 4. Export PDF Report

- Click "Export PDF Report" to generate a comprehensive audit document
- PDF includes all metrics, visualizations, and recommendations
- Draft format suitable for project reviews, retrospectives, or classroom walkthroughs

## Fairness Metrics

### 1. Demographic Parity
Ensures equal selection rates across groups

### 2. Disparate Impact (80% Rule)
Legal standard for detecting adverse impact

### 3. Equal Opportunity (TPR Equality)
Equal true positive rates for qualified candidates

### 4. Predictive Equality (FPR Equality)
Equal false positive rates across groups

### 5. Calibration by Group
Score reliability across demographic groups

### 6. False Negative Rate Parity
Equal rates of missing qualified candidates

### 7. False Discovery Rate Parity
Equal error rates among selected candidates

### 8. Accuracy Equality
Equal prediction accuracy across groups

### 9. Predictive Parity (PPV)
Equal precision among selections

### 10. Equalized Odds
Combines equal opportunity and predictive equality

### 11. Statistical Parity Difference
Absolute difference in selection rates

### 12. Average Odds Difference
Average of TPR and FPR differences

### 13. Theil Index
Distribution inequality measure

## Project Structure

```
bias_detection/
├── backend/                    # FastAPI backend
│   ├── main.py                # Main API endpoints
│   ├── models.py              # Pydantic data models
│   ├── fairness_metrics.py    # Metric calculations
│   ├── metric_definitions.py  # Metric explanations
│   ├── utils.py               # Utility functions
│   └── requirements.txt       # Python dependencies
├── pdf_service/               # Flask PDF generation
│   ├── app.py                # PDF generation service
│   └── requirements.txt      # Python dependencies
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── lib/             # API and store
│   │   ├── App.tsx          # Main app component
│   │   └── main.tsx         # Entry point
│   ├── package.json         # Node dependencies
│   └── vite.config.ts       # Vite configuration
└── README.md                # This file
```

## API Documentation

### FastAPI Endpoints

#### Upload Dataset
```http
POST /api/upload
Content-Type: multipart/form-data
```

#### Get Dataset
```http
GET /api/dataset/{dataset_id}?rows=100
```

#### Analyze Dataset
```http
POST /api/analyze
Content-Type: application/json

{
  "dataset_id": "uuid",
  "protected_attr": "gender",
  "metric_name": "demographic_parity"  // optional
}
```

#### Compare Datasets
```http
POST /api/compare
Content-Type: application/json

{
  "dataset_id_1": "uuid",
  "dataset_id_2": "uuid",
  "protected_attr": "gender"
}
```

#### Get Metrics
```http
GET /api/metrics
```

#### Delete Dataset
```http
DELETE /api/dataset/{dataset_id}
```

### Flask PDF Service

#### Generate PDF
```http
POST /pdf/generate-pdf
Content-Type: application/json

{
  "dataset_name": "recruitment_data.csv",
  "rows": 1000,
  "columns": 10,
  "upload_date": "2025-12-29",
  "protected_attr": "gender",
  "metrics": [...],
  "summary": {...}
}
```

## Development

### Building for Production Tests

Use these commands when you want to create production-like artifacts for demos or comparative benchmarking.

```bash
# Frontend
cd frontend
npm run build

# Backend - no build needed, use production ASGI server
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app
```

### Environment Variables

#### Backend (.env)
```
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

#### PDF Service (.env)
```
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
```

#### Frontend (.env)
```
VITE_API_URL=/api
VITE_PDF_SERVICE_URL=/pdf
```

## Dataset Requirements

Your CSV file should include:

**Required:**
- `shortlisted`: Binary column (0 or 1) indicating if candidate was shortlisted

**For Protected Attributes:**
- `gender`: Categorical (e.g., "Male", "Female", "Non-binary")
- `age`: Numeric (will auto-generate age groups) OR
- `age_group`: Categorical (e.g., "20-30", "31-40")

**Optional (for advanced metrics):**
- `actual`: True labels (0 or 1)
- `predicted`: Predicted labels (0 or 1)
- `score`: Confidence scores (0-100)

## Troubleshooting

### Port Already in Use
```bash
# Windows - find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

### CORS Issues
Ensure `CORS_ORIGINS` in backend `.env` includes your frontend URL

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt
npm install
```

### PDF Generation Fails
Ensure matplotlib backend is set correctly (non-interactive) - already configured in `pdf_service/app.py`

## Security Considerations

- Baseline file size limits enforced (10MB default)
- CSV validation before processing to protect the demo environment
- Basic safeguards against common injection attacks
- CORS configured for specific origins during development
- No sensitive data persisted beyond the session by design

Hardening for production scenarios is outside the current scope and contributions are encouraged.

## License

This project is created for educational and auditing exploration.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Project Contributors

- Adhya Hebbar
- Akshara Bhaskar
- Aastha Singh

## Support

For issues, questions, or suggestions:
- Check the troubleshooting section
- Review API documentation
- Open an issue on GitHub

## Acknowledgments

- Built with React, FastAPI, Flask, and modern web technologies
- UI components from shadcn/ui
- Visualizations with Recharts
- PDF generation with ReportLab

---

**Note**: This project introduces fairness auditing concepts and should complement, not replace, expert-led governance, ethics review, and legal assessment.
