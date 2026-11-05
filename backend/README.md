# SHY BOUTIQUE API

## Local setup

```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Health endpoint: http://localhost:8000/health  
OpenAPI docs: http://localhost:8000/docs

This is an initial API scaffold. Product, inventory, customer, order, payment and delivery modules will be added in subsequent implementation phases.
