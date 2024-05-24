init:
	pip install -r requirements.txt

clean:
	find . -name '*.pyc' -delete

generate_migrations:
	python3 manage.py makemigrations

migrate:
	python3 manage.py migrate

server:
	python3 manage.py runserver

db:
	docker-compose up -d db

start: db server
