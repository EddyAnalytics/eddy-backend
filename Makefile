migrate:
	python3 manage.py makemigrations
	python3 manage.py migrate

dev:
	python3 manage.py createadminuser
	python3 manage.py runserver
