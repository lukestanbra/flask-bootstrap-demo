# Installing locally

```
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

# Running locally

```
source venv/bin/activate
export FLASK_APP=demo
export FLASK_ENV=development
flask init-db
flask run
```

# Build distrbution

```
python3 -m build
```