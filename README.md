# Running locally

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=demo
export FLASK_ENV=development
flask init-db
flask run
```