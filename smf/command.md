conda activate myenv
const list -n myenv

----- <AWS SSH> -----
# Tips
- Use Putty when connecting with SSH
# How to run a python server to keep alive even after a terminal closed.
    sudo nohup python3 -u manage.py runserver 0:80
# How to kill the server executed by nohup
    ps -ef
    kill PID

----- <Git> -----
revert local file before committing
git reset <pathspec>


----- <System>  -----
python manage.py runserver

python manage.py shell

python manage.py createsuperuser

python manage.py 


----- <DB>      -----
python manage.py migrate
# Apply all migrations: admin, auth, contenttypes, polls, sessions - create db fields based on the apps installed by default

python manage.py makemigrations myapp #important to add app name
# By running makemigrations, you’re telling Django that you’ve made some changes to your models 
# namely, it generates DB schema


python manage.py sqlmigrate [app] [dbfile]
ex) python manage.py sqlmigrate polls 0001
# it shows db data sql-based and readable format

## Therefore, the following commands needs to execute after model is changed
1.  python manage.py makemigrations (optional) myapp
2.  python manage.py migrate

# More DB queries
https://docs.djangoproject.com/en/4.1/intro/tutorial02/
