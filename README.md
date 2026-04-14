# DIC Analyzer

🎯 **Полнофункциональная система для анализа цифровых изображений с использованием DIC (Digital Image Correlation)**

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://python.org)
[![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)

## 🚀 Быстрый запуск с Docker

### Требования
- **Docker** (версия 20.10+)
- **Docker Compose** (версия 2.0+)

### Запуск
```bash
# Скачайте проект
git clone <repository-url>
cd dic

# Запустите все сервисы
docker-compose up --build -d

# Проверьте статус
docker-compose ps
```
Запуск тестов 
1 pytest dic/app/ucrp/tests.py -v
    Флаги:
     - -v — подробный вывод
     - --tb=short — короткий traceback
     - -k fraction — только тесты с "fraction"
     - -x — остановить на первой ошибке
python manage.py test ucrp.tests.TestDjangoModels -v 2
  Флаги:
     - -v 2 — подробный вывод
     - --keepdb — не удалять тестовую БД
     - --parallel — параллельный запуск
### Доступ к приложению
- **🎯 Главное приложение:** http://localhost:8080
- **🔧 Django Admin:** http://localhost:8000/admin/
- **📡 API документация:** http://localhost:8000/api/

## 📋 Функциональность

### ✅ Реализовано
- **📊 Создание DIC анализов** с загрузкой изображений
- **📋 Просмотр списка анализов** с статусами и результатами
- **📥 Скачивание результатов** в ZIP архиве (изображения + JSON + статистика + PDF отчет)
- **👤 Система авторизации** (регистрация/вход/выход)
- **🔒 CSRF защита** для безопасных запросов
- **⚡ RESTful API** для всех операций
- **📱 Современный веб-интерфейс** с Vuetify

### 🎯 Основные возможности
- Загрузка изображений before/after deformation
- Настройка параметров анализа (subset size, step, iterations, correlation)
- **Информация об образце**: наименование, материал, изготовитель, дата испытания
- Валидация входных данных
- Асинхронная обработка анализов
- Просмотр результатов и статистики
- Генерация PDF отчетов

## 🏗️ Архитектура

```
dic/
├── 🐳 docker-compose.yml          # Оркестрация сервисов
├── 🐳 Dockerfile.backend          # Django + Python
├── 🐳 Dockerfile.frontend         # Node.js HTTP сервер
├── 🔧 server.js                   # Прокси сервер с API routing
├── 📱 dic-frontend/index.html     # Веб-интерфейс (Vue.js)
├── 🐍 app/                        # Django backend
│   ├── 🔌 dic_api/               # REST API
│   ├── 🧮 dic_algoritm/          # DIC алгоритмы
│   └── ⚙️ manage.py              # Django CLI
├── 📋 requarement.txt            # Python зависимости
├── 📖 README-Docker.md           # Подробная документация
├── 🚫 .gitignore                # Исключаемые файлы
└── 🚫 .dockerignore             # Docker исключения
```

## 🗄️ Сервисы

### Database (PostgreSQL)
- **Порт:** 5432 (внутренний)
- **База данных:** `dic`
- **Пользователь:** `asa`
- **Автоматическая инициализация**

### Backend (Django)
- **Порт:** 8000 (внутренний)
- **API endpoints:** `/api/*`
- **Автоматические миграции**
- **CSRF защита**

### Frontend (Node.js HTTP Server)
- **Порт:** 8080 (внешний)
- **API проксирование** к backend
- **Статические файлы**

## 🔧 API Endpoints

### 📊 Анализы
- `GET/POST /api/analyses/` - список/создание анализов
- `GET /api/analyses/{id}/` - детали анализа
- `POST /api/analyses/{id}/cancel/` - отмена анализа
- `GET /api/analyses/{id}/download/` - скачивание ZIP результатов
- `GET /api/analyses/{id}/pdf_generate/` - генерация PDF отчета

### 👤 Аутентификация
- `POST /api/auth/register/` - регистрация пользователя
- `POST /api/auth/login/` - вход в систему
- `POST /api/auth/logout/` - выход из системы
- `GET /api/get-csrf-token/` - получение CSRF токена

## 📊 Использование

1. **🔐 Регистрация/Вход** в систему
2. **📤 Создание анализа:**
   - Выбрать изображение "до" деформации
   - Выбрать изображение "после" деформации
   - **Заполнить информацию об образце:**
     - Наименование образца
     - Материал
     - Изготовитель
     - Дата испытания
   - Настроить параметры анализа
   - Нажать "🚀 Start Analysis"
3. **📋 Просмотр результатов** в списке анализов
4. **📥 Скачивание результатов** - ZIP архив с изображениями, JSON и PDF отчетом

## 🔒 Безопасность

- ✅ CSRF защита для всех форм
- ✅ Валидация входных данных
- ✅ Безопасная обработка файлов
- ✅ Аутентификация пользователей
- ✅ CORS настройки

## 📈 Производительность

- ⚡ Асинхронная обработка анализов
- 🧮 Оптимизированные DIC алгоритмы
- 💾 Эффективное хранение результатов
- 🔄 Docker контейнеризация

## 🚀 Развертывание

### На другом ПК
```bash
# 1. Скачать проект
git clone <repository-url>
cd dic

# 2. Запустить
docker-compose up --build -d

# 3. Открыть http://localhost:8080
```

### Управление
```bash
# Остановка
docker-compose down

# Просмотр логов
docker-compose logs

# Перезапуск
docker-compose restart
```



**🎯 DIC Analyzer** - мощный инструмент для цифрового корреляционного анализа изображений с современным веб-интерфейсом и REST API.
