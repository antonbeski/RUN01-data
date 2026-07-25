# RUN01

Black-and-white terminal-styled stock data dashboard, powered by
`finvizfinance`.

## Structure
```
RUN01/
├─ api/index.py    # Flask app — serves the UI at "/" AND the JSON API at "/api/*"
├─ vercel.json      # routes every request to api/index.py
└─ requirements.txt
```

Everything (UI + API) is one Flask app in one function. `vercel.json`
rewrites all paths to it, so there's no static-file/function routing
ambiguity — Flask's own `@app.route("/")` and `@app.route("/api/...")`
handle every request.

## Deploy

1. Push this folder to a new GitHub repo.
2. In Vercel: **New Project → Import** the repo → Deploy. No config needed.

## Local run

```bash
pip install -r requirements.txt
python -c "from api.index import app; app.run(debug=True, port=5000)"
```
then open `http://127.0.0.1:5000/`.
