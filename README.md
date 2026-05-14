# AI-Driven Predictive Maintenance Dashboard

This project implements a Predictive Maintenance (PdM) system using the AI4I 2020 PdM dataset. It includes a machine learning model for failure classification and RUL (Remaining Useful Life) estimation, a FastAPI backend, and a Streamlit frontend with a live 2D machine health schematic.

## Features
- **XGBoost Models**: Classification for failure detection and Regression for RUL estimation.
- **FastAPI Backend**: Serves real-time predictions.
- **Streamlit Dashboard**:
  - Live sensor graphs (Plotly).
  - 2D Machine Health Schematic that changes color based on health status.
  - Discord Webhook integration for high-risk alerts.

## Project Structure
```
.
├── data/               # Dataset directory
├── models/             # Trained models and encoders
├── src/
│   ├── api/            # FastAPI backend
│   ├── dashboard/      # Streamlit frontend
│   └── utils/          # Utility scripts (alerts, etc.)
├── requirements.txt    # Python dependencies
├── train.py            # Model training script
└── README.md           # Documentation
```

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Train Models**:
   ```bash
   python train.py
   ```

3. **Start the Backend**:
   ```bash
   uvicorn src.api.main:app --host 0.0.0.0 --port 8000
   ```

4. **Start the Dashboard**:
   In a new terminal:
   ```bash
   PYTHONPATH=. streamlit run src.dashboard.app.py
   ```

## Usage
- Open the Streamlit dashboard in your browser.
- Click **Start Simulation** to begin cycling through the dataset.
- Observe the live sensor trends and the machine schematic.
- (Optional) Add a Discord Webhook URL in the sidebar to receive alerts for high failure probabilities (>80%).
