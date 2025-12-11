#!/usr/bin/env python3
"""
Автоматический установщик DIC Analyzer
Проверяет зависимости и настраивает систему для первого запуска
"""

import sys
import os
import subprocess
import platform
import importlib
from pathlib import Path

class DICAnalyzerSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.app_dir = self.project_root / "app"
        self.venv_dir = self.project_root / "venv"

    def print_header(self, text):
        """Печать заголовка с разделителем"""
        print(f"\n{'='*60}")
        print(f" {text}")
        print(f"{'='*60}")

    def print_step(self, step_num, text):
        """Печать шага установки"""
        print(f"\n[{step_num}] {text}...")

    def check_python_version(self):
        """Проверка версии Python"""
        self.print_step("1", "Проверка версии Python")

        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"❌ Требуется Python 3.8+, установлена версия {version.major}.{version.minor}")
            return False

        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True

    def check_dependencies(self):
        """Проверка основных зависимостей"""
        self.print_step("2", "Проверка зависимостей системы")

        required_packages = [
            'numpy', 'scipy', 'matplotlib', 'PIL', 'cv2',
            'django', 'rest_framework', 'corsheaders'
        ]

        missing_packages = []

        for package in required_packages:
            try:
                if package == 'PIL':
                    importlib.import_module('PIL')
                elif package == 'cv2':
                    importlib.import_module('cv2')
                else:
                    importlib.import_module(package)
                print(f"✅ {package} - установлен")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package} - отсутствует")

        if missing_packages:
            print(f"\n⚠️  Отсутствующие пакеты: {', '.join(missing_packages)}")
            print("Установите их командой: pip install -r requarement.txt")
            return False

        print("✅ Все основные зависимости установлены")
        return True

    def setup_database(self):
        """Настройка базы данных"""
        self.print_step("3", "Настройка базы данных")

        # Проверяем настройки Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
        sys.path.insert(0, str(self.app_dir))

        try:
            import django
            django.setup()

            from django.db import connection
            cursor = connection.cursor()

            # Проверяем подключение
            cursor.execute("SELECT 1;")
            cursor.fetchone()
            cursor.close()

            print("✅ База данных настроена и доступна")
            return True

        except Exception as e:
            print(f"❌ Ошибка базы данных: {e}")
            print("Проверьте настройки в app/app/settings.py")
            return False

    def run_migrations(self):
        """Выполнение миграций"""
        self.print_step("4", "Выполнение миграций базы данных")

        try:
            # Запуск makemigrations
            result = subprocess.run([
                sys.executable, 'manage.py', 'makemigrations'
            ], cwd=str(self.app_dir), capture_output=True, text=True)

            if result.returncode != 0:
                print(f"❌ Ошибка makemigrations: {result.stderr}")
                return False

            # Запуск migrate
            result = subprocess.run([
                sys.executable, 'manage.py', 'migrate'
            ], cwd=str(self.app_dir), capture_output=True, text=True)

            if result.returncode != 0:
                print(f"❌ Ошибка migrate: {result.stderr}")
                return False

            print("✅ Миграции выполнены успешно")
            return True

        except Exception as e:
            print(f"❌ Ошибка выполнения миграций: {e}")
            return False

    def collect_static(self):
        """Сбор статических файлов"""
        self.print_step("5", "Сбор статических файлов")

        try:
            result = subprocess.run([
                sys.executable, 'manage.py', 'collectstatic', '--noinput'
            ], cwd=str(self.app_dir), capture_output=True, text=True)

            if result.returncode != 0:
                print(f"⚠️  Предупреждение при сборе статики: {result.stderr}")
                print("Это не критично для разработки")
            else:
                print("✅ Статические файлы собраны")

            return True

        except Exception as e:
            print(f"⚠️  Ошибка сбора статики: {e}")
            print("Это не критично для разработки")
            return True

    def create_superuser(self):
        """Создание суперпользователя"""
        self.print_step("6", "Создание суперпользователя")

        print("Создать суперпользователя Django? (y/n): ", end="")
        create_admin = input().strip().lower()

        if create_admin == 'y':
            try:
                # Создаем скрипт для автоматического создания пользователя
                create_user_script = '''
import os
import sys
import django

sys.path.insert(0, r"{app_dir}")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "admin123")
    print("Суперпользователь создан: admin / admin123")
else:
    print("Суперпользователь уже существует")
'''.format(app_dir=self.app_dir)

                with open('create_admin.py', 'w', encoding='utf-8') as f:
                    f.write(create_user_script)

                result = subprocess.run([
                    sys.executable, 'create_admin.py'
                ], cwd=str(self.project_root), capture_output=True, text=True)

                os.remove('create_admin.py')

                if result.returncode == 0:
                    print("✅ Суперпользователь создан")
                else:
                    print(f"❌ Ошибка создания пользователя: {result.stderr}")

            except Exception as e:
                print(f"❌ Ошибка создания пользователя: {e}")
        else:
            print("⏭️  Пропуск создания суперпользователя")

        return True

    def test_servers(self):
        """Тестирование серверов"""
        self.print_step("7", "Тестирование серверов")

        print("Запустить тестовый запуск серверов? (y/n): ", end="")
        test_servers = input().strip().lower()

        if test_servers == 'y':
            print("\n🚀 Запуск серверов для тестирования...")
            print("Django API: http://localhost:8000")
            print("Веб-приложение: http://localhost:8080/working_app.html")
            print("Нажмите Ctrl+C для остановки\n")

            try:
                # Запуск Django сервера в фоне
                django_process = subprocess.Popen([
                    sys.executable, 'manage.py', 'runserver', '8000'
                ], cwd=str(self.app_dir))

                # Запуск HTTP сервера
                http_process = subprocess.Popen([
                    sys.executable, 'run_system.py'
                ], cwd=str(self.project_root))

                # Ждем завершения
                django_process.wait()
                http_process.wait()

            except KeyboardInterrupt:
                print("\n🛑 Серверы остановлены")
            except Exception as e:
                print(f"❌ Ошибка запуска серверов: {e}")
        else:
            print("⏭️  Пропуск тестирования серверов")

        return True

    def show_summary(self):
        """Показать итоговую информацию"""
        self.print_header("Установка завершена!")

        print("\n🎉 DIC Analyzer готов к работе!")
        print("\n📋 Следующие шаги:")
        print("1. Запустите серверы: start_servers.bat")
        print("2. Откройте в браузере: http://localhost:8080/working_app.html")
        print("3. Зарегистрируйтесь и начните анализ изображений")

        print("\n🔗 Полезные ссылки:")
        print("- Веб-приложение: http://localhost:8080/working_app.html")
        print("- Django API: http://localhost:8000/api/")
        print("- Django Admin: http://localhost:8000/admin/")

        if os.path.exists(str(self.venv_dir)):
            print(f"\n💡 Виртуальное окружение активировано: {self.venv_dir}")

    def run(self):
        """Основной метод установки"""
        self.print_header("DIC Analyzer - Автоматическая установка")

        print(f"Платформа: {platform.system()} {platform.release()}")
        print(f"Python: {sys.version}")
        print(f"Рабочая директория: {self.project_root}")

        steps = [
            self.check_python_version,
            self.check_dependencies,
            self.setup_database,
            self.run_migrations,
            self.collect_static,
            self.create_superuser,
            self.test_servers
        ]

        success_count = 0
        for step_func in steps:
            try:
                if step_func():
                    success_count += 1
                else:
                    break
            except Exception as e:
                print(f"❌ Критическая ошибка: {e}")
                break

        if success_count == len(steps):
            self.show_summary()
        else:
            print(f"\n❌ Установка прервана на шаге {success_count + 1}")
            print("Исправьте ошибки и запустите setup.py снова")

        return success_count == len(steps)

def main():
    setup = DICAnalyzerSetup()
    success = setup.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
