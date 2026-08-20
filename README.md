# DIC Analyzer

Бэкенд и веб-интерфейс для двух задач механики материалов:

1. **DIC (Digital Image Correlation)** — измерение полей смещений и деформаций
   образца по двум фотографиям: до и после нагружения. Вместо тензодатчиков —
   обычные снимки, результат — карта смещений по всей поверхности.
2. **ЭПГ (электронно-плазменная грануляция)** — расчёт и оптимизация режимов
   грануляции титановых сплавов: подбор тока и оборотов по длине электрода,
   прогноз потерь, фракционного состава и устойчивости процесса.

Обе задачи вычислительно тяжёлые, поэтому считаются не в HTTP-запросе, а в
отдельных воркерах, забирающих задания из очереди в БД.

[![Tests](https://github.com/BLAZER2283/dic/actions/workflows/tests.yml/badge.svg)](https://github.com/BLAZER2283/dic/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.12-3670A0?logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-5.1-092E20?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgresql-15-316192?logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

<!-- Скриншоты: положить файлы в docs/ и раскомментировать.
![Создание анализа](docs/screenshot-analysis.png)
![Поле смещений](docs/screenshot-displacement-field.png)
-->

## Как работает DIC

Основная часть проекта — собственная реализация корреляционного алгоритма,
без готовых DIC-библиотек.

1. Изображение «до» разбивается на сетку субобластей (subset) с заданным шагом.
2. Для каждой субобласти ищется её положение на изображении «после». Мера
   схожести — **ZNCC** (zero-mean normalized cross-correlation): она
   инвариантна к линейному изменению яркости, поэтому смена освещения между
   кадрами не превращается в ложную деформацию.
3. Пик корреляции ищется с субпиксельной точностью: координаты непрерывны,
   значения яркости берутся **билинейной интерполяцией**, а максимум ZNCC
   находится численной оптимизацией **L-BFGS-B**.
4. Постобработка отбрасывает точки с корреляцией ниже порога — там, где
   текстуры не хватило для надёжного сопоставления.

Ключевые параметры: размер субобласти, шаг сетки, число итераций,
порог корреляции.

### Чем проверяется, что алгоритм не врёт

Два свойства, которые должны выполняться всегда, вынесены в тесты
(`app/dic_algoritm/test_dic.py`):

| Проверка | Ожидание |
|---|---|
| Идентичные изображения | поле смещений ≈ 0, ZNCC ≈ 1 |
| Сдвиг на известные 2 px | измеренное `U ≈ 2.0`, `V ≈ 0.0` |

Вторая проверка — фактически калибровка: если алгоритм не находит заданный
сдвиг, доверять его результатам на реальных образцах нельзя.

## Архитектура

```
                        ┌───────────────────────────────┐
   браузер ──────────►  │  nginx :80                    │
                        │  /       → DIC SPA (Vue 3)    │
                        │  /ucrp/  → ЭПГ SPA (React)    │
                        │  /api/   → проксирование      │
                        │  /media/ → результаты         │
                        └───────────────┬───────────────┘
                                        │
                        ┌───────────────▼───────────────┐
                        │  Django 5 + DRF (gunicorn)    │
                        │  JWT, OpenAPI/Swagger, ORM    │
                        └────┬─────────────────────┬────┘
                             │                     │
                 ┌───────────▼────────┐            │
                 │   PostgreSQL 15    │            │
                 │  данные + очередь  │◄───────────┘
                 └───────┬────────┬───┘
                         │        │
          ┌──────────────▼──┐  ┌──▼───────────────────┐
          │ worker-dic      │  │ worker-ucrp          │
          │ ZNCC + L-BFGS-B │  │ расчёт режимов ЭПГ   │
          │ поля смещений   │  │ профили I и n        │
          └─────────────────┘  └──────────────────────┘
```

### Почему очередь в БД, а не Celery

Изначально фоновые задачи шли через Celery + Redis. В этом проекте от них
отказались: задач немного, они длинные (единицы минут) и требуют строгой
привязки к записи в БД со статусом. Отдельный брокер добавлял третий
контейнер и второй источник правды о состоянии задачи, ничего не давая
взамен. Сейчас статус задачи живёт в одной таблице, воркер — это management
command (`run_dic_worker`, `run_epg_worker`), которая опрашивает очередь.
Перезапуск воркера не теряет задания.

## Стек

**Backend:** Python 3.12, Django 5.1, Django REST Framework, PostgreSQL 15,
gunicorn, WhiteNoise
**Аутентификация:** JWT (djangorestframework-simplejwt) с blacklist refresh-токенов
**Вычисления:** NumPy, SciPy (L-BFGS-B), OpenCV, Pillow
**Отчёты:** ReportLab (PDF), ZIP-выгрузка результатов
**Документация API:** drf-spectacular (OpenAPI 3, Swagger UI, ReDoc)
**Frontend:** Vue 3 + Vuetify (DIC), React 18 + Recharts (ЭПГ), Vite
**Инфраструктура:** Docker Compose, nginx, GitHub Actions

## Быстрый старт

Нужен Docker 20.10+ и Docker Compose 2.0+.

```bash
git clone https://github.com/BLAZER2283/dic.git
cd dic

# 1. Конфигурация. Обязательно поменяйте пароль и SECRET_KEY.
cp .env.example .env

# 2. Сборка и запуск. Оба SPA собираются внутри образа nginx,
#    отдельная сборка фронтенда не нужна.
docker compose up --build -d

# 3. Статус
docker compose ps
```

Приложение поднимется на **http://localhost**:

| Адрес | Что там |
|---|---|
| `/` | интерфейс DIC-анализа |
| `/ucrp/` | интерфейс оптимизатора ЭПГ |
| `/api/schema/swagger-ui/` | Swagger UI — полный и актуальный список эндпоинтов |
| `/admin/` | Django admin |

Остановка — `docker compose down`, логи — `docker compose logs -f backend`.

## Тесты

74 теста: вычислительное ядро, бизнес-логика ЭПГ, модели и API
аутентификации, границы доступа к API анализов.

```bash
pip install -r requirements.txt

pytest                      # всё
pytest -m "not slow"        # без тестов ядра DIC (~13 с вместо ~40 с)
pytest -m slow              # только ядро DIC
pytest --cov=app            # с покрытием
```

Отдельная БД не нужна: без `DATABASE_URL` и `POSTGRES_HOST` Django
переключается на SQLite, а тесты ЭПГ-ядра вообще не трогают базу.

## Локальная разработка без Docker

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

cd app
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Воркеры — в отдельных терминалах:
python manage.py run_dic_worker
python manage.py run_epg_worker
```

Фронтенды поднимаются своими dev-серверами:

```bash
cd dic-frontend     && npm install && npm run dev   # :5173
cd plasma-optimizer && npm install && npm run dev   # :3000
```

## API

Канонический источник — Swagger UI на `/api/schema/swagger-ui/`
(схема: `/api/schema/`, ReDoc: `/api/schema/redoc/`). Основное:

**DIC-анализы** — `/api/analyses/`, требуют авторизации, загрузка через
`multipart/form-data`:

| Метод | Путь | Назначение |
|---|---|---|
| `GET` | `/api/analyses/` | список анализов |
| `POST` | `/api/analyses/` | создать анализ (изображения + параметры + данные образца) |
| `GET` | `/api/analyses/{id}/` | детали и статус |
| `GET` | `/api/analyses/{id}/image/` | изображение результата |
| `GET` | `/api/analyses/{id}/download/` | ZIP: изображения, JSON, статистика, PDF |
| `GET` | `/api/analyses/{id}/pdf_generate/` | PDF-отчёт |

**Расчёты ЭПГ** — `/api/calculations/` (стандартный набор ModelViewSet).

**Аутентификация** — `/api/auth/`:

| Метод | Путь | Назначение |
|---|---|---|
| `POST` | `/api/auth/register/` | регистрация, возвращает пару JWT |
| `POST` | `/api/auth/login/` | вход, возвращает пару JWT |
| `POST` | `/api/auth/logout/` | занести refresh-токен в blacklist |
| `GET` | `/api/auth/me/` | текущий пользователь |
| `POST` | `/api/auth/change-password/` | смена пароля |

## Развёртывание

`deploy.sh` разворачивает проект на чистом сервере: ставит Docker, генерирует
`.env` и конфиг nginx из `nginx/site.conf.template` (подстановка
`BACKEND_HOST` через `envsubst`), собирает образы и поднимает стек.

```bash
./deploy.sh --repo https://github.com/BLAZER2283/dic.git \
            --server-host <IP> \
            --db-password <пароль>
```

`.github/workflows/deploy.yml` выполняет это автоматически при пуше в `main`
(секреты: `SSH_PRIVATE_KEY`, `SERVER_IP`, `SERVER_USER`, `DB_PASSWORD`).

## Структура

```
├── app/                      Django-проект
│   ├── app/                  настройки, urls, middleware
│   ├── dic_api/              REST API анализов, воркер DIC
│   │   └── dic_bisnes_logik/ миксины: PDF, ZIP, изображения, синхронный прогон
│   ├── dic_algoritm/         вычислительное ядро DIC (ZNCC, L-BFGS-B)
│   ├── ucrp/                 модуль ЭПГ: модели, API, оптимизатор, воркер
│   └── authapp/              регистрация, вход, JWT
├── dic-frontend/             SPA анализа (Vue 3 + Vuetify)
├── plasma-optimizer/         SPA оптимизатора ЭПГ (React + Recharts)
├── nginx/                    site.conf и шаблон для envsubst
├── Dockerfile.backend        Django + gunicorn
├── Dockerfile.nginx          сборка обоих SPA + nginx
├── docker-compose.yml        nginx, backend, db, worker-dic, worker-ucrp
└── deploy.sh                 развёртывание на сервер
```

Тестовые наборы изображений (`Sample1.zip`, `Sample2.zip`) в репозиторий не
входят — они раздаются через [Releases](https://github.com/BLAZER2283/dic/releases).

## Лицензия

MIT — см. [LICENSE](LICENSE).
