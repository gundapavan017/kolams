# Kolam Mini Project

This folder contains a Python kolam generator and a full-stack web app in `kolam-project/`.

## Quick Start: Web App

```bash
cd kolam-project/backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal:

```bash
cd kolam-project/frontend
npm install
npm run dev
```

Then open `http://localhost:3000/`.

## Standalone Python Scripts

```bash
python kolam_generator.py
python kolam_interactive.py
```
