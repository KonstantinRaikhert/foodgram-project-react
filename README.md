[![codestyle PEP8](https://github.com/raikhert13/foodgram-project-react/actions/workflows/codestyle.yaml/badge.svg)](https://github.com/raikhert13/foodgram-project-react/actions/workflows/codestyle.yaml)
[![deploy](https://github.com/raikhert13/foodgram-project-react/actions/workflows/production_deploy.yaml/badge.svg)](https://github.com/raikhert13/foodgram-project-react/actions/workflows/production_deploy.yaml)
# Продуктовый помощник. Дипломный проект курса python-разработчика - Яндекс.Практикум
Онлайн-сервис, где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд

# Проект доступен по [этому](http://foodgram.fun/) адресу
Если ссылка уже не работает - значит VPS, на котором развёрнут проект, закончил свою работу.

## [ Документация ](http://84.252.134.12/foodgram/docs/)
Автоматическая документация API проекта

## Технологии и требования
```
Python 3.9+
Django
Django REST Framework
Docker
Nginx
Poetry
Black
Factory-Boy
xhtml2pdf
```


## Запуск проекта в Docker окружении и заполнить тестовыми данными
- Запустить проект в папке infra:
    ```shell
    docker-compose -f develop.yaml up --build -d
     ```
 Автоматически создаются миграции, пользователь с супер правами и заполняется тестовыми данными при помощи библиотеки **Factory Boy**


- Остановить проект сохранив данные в БД:
    ```shell
    docker-compose -f develop.yaml down
    ```
- Остановить проект удалив данные в БД:
    ```shell
    docker-compose -f develop.yaml down --volumes
    ```

## Заполнение БД тестовыми данными
В проекте есть 2 кастомные команды:
1. Создаёт суперпользователя с данными из переменных окружения
```
python manage.py createadmin
```
2. Команда, использующая библиотеку **Factory boy**, заполняет пользователями, профессиями, телефонами, фирмами
```
python manage.py filldb
```
используйте аргумент **-help** для дополнительной информации

## Работа с зависимостями и пакетами
По желанию можно использовать Poetry(менеджер зависимостей).
Детальное описание в [документации poetry](https://python-poetry.org/docs/cli/)
```shell
poetry shell
poetry install
```

и pre-commit hooks:
```
pre-commit install --all
```

собрать файл requirments.txt без хешей:
```shell
poetry export --without-hashes --dev --output backend/requirements/develop.txt
```

# Импорт в Postman:
По пути backend/data доступна конфигурация для Postman: **Diplom.postman_collection.json**
