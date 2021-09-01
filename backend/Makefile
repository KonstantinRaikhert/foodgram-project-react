run:
	python manage.py runserver

del:
	sudo ss -lptn 'sport = :5432'

migration:
	python manage.py migrate
	python manage.py createadmin
	python manage.py filldb
	python manage.py runserver
