.PHONY: up down reset logs web makemigrations migrate createsuperuser clean

up:
	docker compose up -d --build

down:
	docker compose down

reset:
	docker compose down -v
	docker compose up -d --build

logs:
	docker compose logs -f

web:
	docker compose exec web bash

makemigrations:
	docker compose exec web python manage.py makemigrations

migrate:
	docker compose exec web python manage.py migrate

createsuperuser:
	docker compose exec web python manage.py createsuperuser

clean:
	docker system prune -f