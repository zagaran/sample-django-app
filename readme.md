# Local Project Setup

```
pip install -r requirements.txt
cp config/.env.example config/.env
nano config/.env  # Fill in missing env vars
python manage.py migrate
```


To run the project, use `python manage.py runserver_plus`

To access the database, use `python manage.py shell_plus`
