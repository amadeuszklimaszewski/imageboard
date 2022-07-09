db-name=postgres

build-dev:
	docker-compose build

up-dev:
	docker-compose run --rm backend bash -c "python manage.py migrate"
	docker-compose up

migrations:
	docker-compose exec backend bash -c "python manage.py makemigrations && python manage.py migrate"

superuser:
	docker-compose exec backend bash -c "python manage.py createsuperuser"

test:
	docker-compose exec backend bash -c "python manage.py test $(location)"

django-shell:
	docker-compose exec backend bash -c "python manage.py shell_plus --ipython --print-sql"

backend-bash:
	docker-compose exec backend bash

reset-db:
	docker-compose stop backend
	docker-compose exec db bash -c "runuser postgres -c 'dropdb $(db-name); createdb $(db-name)'"
	docker-compose start backend
	make migrations
