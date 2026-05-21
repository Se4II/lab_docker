# Отчет по лабораторной работе: Работа с контейнерами Docker

**Студент:** петров Владисла ИУ8-22
**Операционная система:** Linux (Fedora/Debian)  
**Инструменты:** Docker 24+, Docker Compose v2, Python 3.9, MySQL 8.0  

---

## 1. Цель работы
Изучить основы технологии контейнеризации приложений с помощью Docker, освоить создание образов через `Dockerfile`, управление контейнерами в интерактивном режиме, а также настройку многоконтейнерных сред с использованием `docker-compose`.

---

## 2. Часть I. Работа с Docker

### 2.1. Подготовка структуры проекта
Создана директория проекта со следующей структурой:
lab_docker/
├── app/
│   ├── main.py          # Web-приложение на Flask
│   └── requirements.txt # Зависимости Python
├── db/
│   ── init.sql         # Скрипт инициализации БД
├── Dockerfile           # Инструкция сборки образа
├── docker-compose.yml   # Конфигурация оркестрации
└── README.md            # Описание проекта

### 2.2. Создание Dockerfile
Файл `Dockerfile` описывает процесс сборки образа приложения:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

EXPOSE 5000
CMD ["python", "main.py"]
```

Образ базируется на официальном python:3.9-slim. Установлены системные заголовки для компиляции mysql-connector-python, скопированы зависимости и исходный код, открыт порт 5000.
## 2.3. Сборка и запуск контейнера
Сборка образа выполнена командой:
```bash
$ docker build -t lab-docker .
```

Запуск контейнера в интерактивном режиме с удалением после остановки:

```bash
$ docker run --rm -it --name lab_app lab-docker bash
```
Контейнер успешно запущен, терминал переключён в оболочку Alpine/Debian внутри контейнера.

## 2.4. Копирование файла и проверка

В отдельном терминале выполнен копирование файла из хост-системы в работающий контейнер:


## 2.4. Копирование файла и проверка
В отдельном терминале выполнен копирование файла из хост-системы в работающий контейнер

Внутри контейнера проверено наличие файла  -> Файл успешно скопирован, права доступа сохранены.

## 2.5. Завершение работы контейнера
Выход из интерактивного режима и остановка

3. Часть II. Оркестрация с Docker Compose
3.1. Настройка docker-compose.yml
Создан файл docker-compose.yml, описывающий связку приложения и СУБД:

```yaml
version: '3.8'

services:
  app:
    build: 
      context: .
      dockerfile: Dockerfile
    container_name: lab_app
    ports:
      - "5000:5000"
    environment:
      - DB_HOST=db
      - DB_USER=taskuser
      - DB_PASSWORD=taskpass
      - DB_NAME=tasks
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: mysql:8.0
    container_name: lab_mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: tasks
      MYSQL_USER: taskuser
      MYSQL_PASSWORD: taskpass
    ports:
      - "3306:3306"
    volumes:
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
      - db_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-prootpass"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  db_data:
```

Инициализация БД описана в db/init.sql:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 3.2. Запуск связки и проверка
Запуск многоконтейнерного окружения:

```bash
$ docker compose up --build -d
```
Проверка статуса сервисов:

```bash
$ docker compose ps
NAME          STATUS                    PORTS
lab_app       Up                        0.0.0.0:5000->5000/tcp
lab_mysql     Up (healthy)              0.0.0.0:3306->3306/tcp
```
Проверка работоспособности API через curl:

```bash
$ curl http://localhost:5000/health
{"status":"ok"}

$ curl -X POST http://localhost:5000/task \
  -H "Content-Type: application/json" \
  -d '{"name":"Тестовая задача по Docker"}'
{"id":1,"name":"Тестовая задача по Docker"}

$ curl http://localhost:5000/tasks
[{"id":1,"name":"Тестовая задача по Docker","created_at":"2026-05-22T10:20:15"}]
```
## 3.3. Проверка через браузер
Приложение доступно по адресу http://localhost:5000/tasks ))))))))
(Скриншот прилагается в архиве отчёта: Screenshot From 2026-05-22 01-49-14.png)
