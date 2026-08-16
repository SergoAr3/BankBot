# 🏦 BankBot

**BankBot** — асинхронный Telegram-бот, который имитирует работу небольшой банковской системы с виртуальной валютой.

Пользователи могут управлять балансом, переводить средства другим пользователям, открывать вклады, брать и погашать кредиты, получать награды за подписку на Telegram-каналы и совершать виртуальные покупки.

Проект демонстрирует работу с асинхронным Python, Telegram Bot API, PostgreSQL, Redis, SQLAlchemy, Alembic, APScheduler и Docker.

---

## ✨ Возможности

- 💰 **Виртуальный баланс**
  - регистрация пользователя при команде `/start`;
  - хранение и изменение баланса;
  - учет финансовых операций.

- 💸 **Переводы между пользователями**
  - перевод виртуальной валюты по Telegram username;
  - проверка доступного баланса;
  - уведомление получателя о переводе.

- 📈 **Вклады**
  - открытие вкладов на разные сроки;
  - расчет процентов;
  - автоматическая выплата по окончании срока;
  - просмотр активных вкладов;
  - досрочное закрытие вклада.

- 💳 **Кредиты**
  - оформление кредитов с разными сроками и лимитами;
  - учет остатка задолженности;
  - частичное и полное погашение;
  - обработка просрочки;
  - автоматические напоминания и начисления через планировщик.

- 📢 **Награды за подписки**
  - проверка подписки пользователя на заданные Telegram-каналы;
  - начисление виртуальной валюты за подписку;
  - защита от частых повторных проверок через Redis cooldown.

- 🐱 **Виртуальные покупки**
  - покупка изображений котов за виртуальную валюту;
  - сохранение информации о покупке;
  - проверка достаточности средств перед покупкой.

- ⏰ **Отложенные задачи**
  - выплаты по вкладам;
  - напоминания по кредитам;
  - обработка просроченной задолженности;
  - работа через APScheduler.

---

## 🛠 Стек технологий

| Технология | Назначение |
|---|---|
| Python 3.11 | Основной язык проекта |
| aiogram 3 | Telegram Bot framework |
| PostgreSQL | Основная база данных |
| SQLAlchemy 2 | Асинхронный ORM |
| asyncpg | Асинхронный драйвер PostgreSQL |
| Alembic | Миграции базы данных |
| Redis | Cooldown и временные данные |
| APScheduler | Отложенные и периодические задачи |
| Loguru | Логирование |
| Docker | Контейнеризация приложения |
| Docker Compose | Запуск приложения, PostgreSQL и Redis |
| Black / Flake8 / isort / pre-commit | Форматирование и контроль качества кода |

---

## 📁 Структура проекта

```text
BankBot/
├── alembic/                  # Миграции базы данных
├── app/
│   ├── constans/             # Сообщения, цены, сроки и константы
│   ├── db/
│   │   ├── requests/         # Запросы к базе данных
│   │   ├── models.py         # SQLAlchemy-модели
│   │   └── model_types.py    # Enum и типы моделей
│   │
│   ├── handlers/
│   │   ├── base.py           # /start, меню и баланс
│   │   ├── channels.py       # Награды за подписку на каналы
│   │   ├── credit.py         # Работа с кредитами
│   │   ├── deposit.py        # Работа с вкладами
│   │   ├── purchase.py       # Виртуальные покупки
│   │   └── transfer.py       # Переводы между пользователями
│   │
│   ├── keyboards/            # Inline- и Reply-клавиатуры
│   ├── middlewares/          # Middleware бота
│   └── utils/                # FSM states, scheduler tasks и утилиты
│
├── config.py                 # Настройки бота, PostgreSQL и Redis
├── main.py                   # Точка входа
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
└── alembic.ini
---

## 🚀 Запуск проекта

### 1. Клонирование репозитория

```bash
git clone https://github.com/SergoAr3/BankBot.git
cd BankBot
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
BOT_TOKEN=your_telegram_bot_token

POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=bank_bot

DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379
```

Токен Telegram-бота можно получить через [@BotFather](https://t.me/BotFather).

> Не добавляйте `.env` и токен Telegram-бота в репозиторий.

---

## 🐳 Запуск через Docker

Самый простой способ запустить проект — использовать Docker Compose.

```bash
docker compose up --build
```

Будут запущены:

- Telegram-бот;
- PostgreSQL;
- Redis.

Перед запуском приложения контейнер автоматически применяет миграции Alembic.

Запуск в фоновом режиме:

```bash
docker compose up -d --build
```

Остановка контейнеров:

```bash
docker compose down
```

---

## 💻 Локальный запуск

### 1. Создание виртуального окружения

```bash
python -m venv venv
```

Linux / macOS:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка PostgreSQL и Redis

Если сервисы запущены локально, укажите в `.env`:

```env
DB_HOST=localhost
DB_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379
```

### 4. Применение миграций

```bash
alembic upgrade head
```

или:

```bash
make migrate
```

### 5. Запуск бота

```bash
python main.py
```

---

## 🗄 Миграции базы данных

Для работы с миграциями используется **Alembic**.

Создание новой миграции:

```bash
make migration NAME="migration_name"
```

Применение всех миграций:

```bash
make migrate
```

Эквивалентная команда Alembic:

```bash
alembic upgrade head
```

---

## 🔄 Как запускается приложение

При старте `main.py`:

```text
main.py
   │
   ├── создается AsyncIOScheduler
   ├── подключаются routers
   ├── регистрируются middlewares
   ├── устанавливаются команды Telegram-бота
   ├── запускается scheduler
   └── запускается aiogram long polling
```

Основные пользовательские сценарии:

```text
Пользователь
 │
 ├── Баланс
 ├── Переводы
 ├── Вклады
 ├── Кредиты
 ├── Награды за подписки
 └── Покупки
```

---

## 🔐 Переменные окружения

| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | Токен Telegram Bot API |
| `POSTGRES_USER` | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL |
| `POSTGRES_DB` | Имя базы данных PostgreSQL |
| `DB_HOST` | Хост PostgreSQL |
| `DB_PORT` | Порт PostgreSQL |
| `REDIS_HOST` | Хост Redis |
| `REDIS_PORT` | Порт Redis |

---

## 🧹 Качество кода

В проекте используются инструменты форматирования и статического анализа:

```bash
black .
isort .
flake8 .
```

Установка pre-commit hooks:

```bash
pre-commit install
```

Запуск всех pre-commit проверок вручную:

```bash
pre-commit run --all-files
```
