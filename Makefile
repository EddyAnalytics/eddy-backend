migrate:
	python3 manage.py makemigrations
	python3 manage.py migrate

dev:
	python3 manage.py createadminuser
	HOST=127.0.0.1 DEBUG=True python3 manage.py runserver
