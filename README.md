# Library Service API

The API performs basic library actions, where you can borrow some books.

### Technologies
1. Python, Django, ORM, SQLite and Git
2. All endpoints documented via Swagger

### How to run with GitHub
1. Clone repo from GitHub `git clone https://github.com/DanSheremeta/airport-api.git`
2. Create virtual environment and install dependencies
```shell
cd library-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Set environment variables and make migrations to db
```shell
set SECRET_KEY=<your secret key>
python manage.py makemigrations
python manage.py migrate
```
4. Run server `python manage.py runserver`

### Getting access
- Create default user via `/api/user/register/`
- For admin access, you can create user via `python manage.py createsuperuser`
- Get access and refresh tokens via `/api/user/token/`
- When accessing endpoints, pass the token to the headers with name `Authorize` and value `Bearer <access-token>`

### Documentation
- All endpoints available via `/api/doc/swagger/`
