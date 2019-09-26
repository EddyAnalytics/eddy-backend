migrate:
	python3 manage.py makemigrations --no-input
	python3 manage.py migrate --no-input

dev:
	python3 manage.py createadminuser
	HOST=127.0.0.1 DEBUG=True python3 manage.py runserver
