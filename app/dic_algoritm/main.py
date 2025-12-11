import asyncio
import os
import datetime
from visualization import display_results
from dic_processor import DICProcessorAPI

async def run_real_test():
    """
    Обработка реальных изображений из файлов с оптимальными параметрами.
    """
    print("\n" + "=" * 60)
    print("ОБРАБОТКА РЕАЛЬНЫХ ИЗОБРАЖЕНИЙ")
    print("=" * 60)
    print("Оптимальные параметры для реальных изображений:")
    print("  - Окно: 27 пикселей (лучшее качество)")
    print("  - Шаг: 13 пикселей (детальный анализ)")
    print("  - Макс. итераций: 40 (точная сходимость)")
    
    img1_path = input("\nВведите путь к первому изображению (до деформации): ").strip()
    img2_path = input("Введите путь ко второму изображению (после деформации): ").strip()
    test_name = input("Введите название теста: ").strip()
    
    if not test_name:
        test_name = f"real_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if img1_path and img2_path and os.path.exists(img1_path) and os.path.exists(img2_path):
        print(f"\nЗагрузка изображений...")
        print(f"  Изображение 1: {os.path.basename(img1_path)}")
        print(f"  Изображение 2: {os.path.basename(img2_path)}")
        
        processor = DICProcessorAPI(results_dir="real_results")
        results = await processor.process_test_from_files_async(
            test_id=test_name,
            img1_path=img1_path,
            img2_path=img2_path,
            subset_size=27,    # Чуть больше окно для реальных изображений
            step=13,           # Меньший шаг для большего разрешения
            max_iter=40        # Больше итераций для точности
        )
        
        return results
    else:
        print("Ошибка: указанные файлы не найдены!")
        return None

async def main():
    """
    Главная функция для демонстрации работы алгоритма.
    """
    print("=" * 70)
    print("АСИНХРОННЫЙ DIC АЛГОРИТМ - ЦИФРОВАЯ КОРРЕЛЯЦИЯ ИЗОБРАЖЕНИЙ")
    print("Версия с ОПТИМАЛЬНЫМИ СРЕДНИМИ ОКНАМИ (21-31 пикселей)")
    print("=" * 70)
    print("\nПРЕИМУЩЕСТВА СРЕДНИХ ОКОН:")
    print("  ✓ Баланс скорости и точности")
    print("  ✓ Оптимальное разрешение деталей")
    print("  ✓ Стабильная сходимость алгоритма")
    print("  ✓ Минимальные шумы и артефакты")
    
    while True:
        print("\n\n" + "=" * 60)
        print("ГЛАВНОЕ МЕНЮ")
        print("=" * 60)
        print("1. Обработать реальные изображения из файлов")
        print("2. Показать список выполненных тестов")
        print("3. Выход")
        
        try:
            choice = input("\nВведите номер выбора (1-3): ").strip()
                
            if choice == "1":
                results = await run_real_test()
                if results:
                    await display_results(results)
                    
            elif choice == "2":
                processor = DICProcessorAPI(results_dir="demo_results")
                tests = await processor.list_tests()
                
                print("\n" + "=" * 60)
                print("СПИСОК ВЫПОЛНЕННЫХ ТЕСТОВ")
                print("=" * 60)
                
                if tests:
                    for i, test in enumerate(tests, 1):
                        print(f"\n{i}. {test['test_id']}")
                        print(f"   Статус: {test['status']}")
                        print(f"   Время: {test.get('timestamp', '')}")
                        if 'statistics' in test and test['statistics']:
                            stats = test['statistics']
                            if 'mean_displacement' in stats:
                                print(f"   Среднее смещение: {stats['mean_displacement']:.3f} px")
                else:
                    print("Тестов не найдено.")
                    
            elif choice == "5":
                print("\nЗавершение программы...")
                break
                
            else:
                print("Неверный выбор. Попробуйте снова.")
                
            # Пауза перед следующим шагом
            input("\nНажмите Enter для продолжения...")
            
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем.")
            break
        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("ПРОГРАММА ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())