# Тестовое задание сервиса rest api с интерфейсом openapi/swagger ui
Версия Python 3.10.0, Fastapi 0.94.0

Для запуска программы в doker, необходимо скопировать код из репозитория, иметь установленный doker. Перейти в корневую папку, где находятся файлы docerfile и docer-compose, в терминале ввести команду: "docker-compose up -d --build".
Дождаться создания образа doker. 
Страница Swagger ui после запуска doker: "http://localhost:8000/docs".

В папке с программой находится файл: "sample_file". Этот файл служит примером входного файла пользователя для проведения расчетов.

Для запуска программы на локальной машине, необходимо изменить в файле database.py переменную "SQLALCHEMY_DATABASE_URL"(строка 8), в данной переменной необходимо заменить HOST: "db" на "localhost". А так же при необходимости развернуть виртуальную среду и выполнить установку с помощью файла requirements.txt
