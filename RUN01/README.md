# RUN01

Black-and-white terminal-styled stock data dashboard, powered by
`finvizfinance`.

## Structure
```
RUN01/
├─ api/index.py     # Flask API (Vercel serverless function)
├─ index.html        # terminal UI (static)
├─ vercel.json        # routes /api/* to api/index.py
└─ requirements.txt
```

## Deploy

1. Push this folder to a new GitHub repo.
2. In Vercel: **New Project → Import** the repo → Deploy.
   (No build settings needed — Vercel auto-detects `api/index.py` as a
   Python function and serves `index.html` as a static file.)

## Local run

```bash
pip install -r requirements.txt flask-cors
python -c "from api.index import app; app.run(debug=True, port=5000)"
```
then open `index.html` directly, or serve it with any static server pointed
at `http://127.0.0.1:5000` as the API host.
