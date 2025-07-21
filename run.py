#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1C Help Parser - Главный скрипт запуска
"""

import os
import sys
import argparse
import json
from datetime import datetime
from pathlib import Path

def check_dependencies():
    """Проверяет наличие необходимых зависимостей"""
    try:
        import bs4
        print("✅ BeautifulSoup4 установлен")
    except ImportError:
        print("❌ BeautifulSoup4 не установлен")
        print("Установите: pip install beautifulsoup4")
        return False
    
    try:
        import lxml
        print("✅ lxml установлен")
    except ImportError:
        print("⚠️  lxml не установлен (рекомендуется для лучшей производительности)")
        print("Установите: pip install lxml")
    
    return True

def cleanup_data():
    """Очищает ненужные файлы из папки data"""
    import glob
    
    files_to_remove = [
        "data/1c_summary.json",
        "data/context_chunks/",
        "data/hbk_analysis.json"
    ]
    
    print("🧹 Очистка ненужных файлов...")
    
    for pattern in files_to_remove:
        if pattern.endswith('/'):
            # Удаляем папку
            if os.path.exists(pattern):
                import shutil
                shutil.rmtree(pattern)
                print(f"🗑️  Удалена папка: {pattern}")
        else:
            # Удаляем файл
            if os.path.exists(pattern):
                os.remove(pattern)
                print(f"🗑️  Удален файл: {pattern}")
    
    print("✅ Очистка завершена")

def run_parser(zip_file, max_files=None, use_improved=True):
    """Запускает парсинг файла"""
    print(f"🔍 Анализ структуры: {zip_file}")
    os.system(f"set PYTHONPATH=src && python src/parsers/hbk_parser.py {zip_file}")
    
    print(f"📝 Извлечение синтаксиса: {zip_file}")
    if max_files:
        os.system(f"set PYTHONPATH=src && python src/parsers/bsl_syntax_extractor.py {zip_file} --max-files {max_files}")
    else:
        os.system(f"set PYTHONPATH=src && python src/parsers/bsl_syntax_extractor.py {zip_file}")
    
    # Определяем имя JSON файла
    base_name = Path(zip_file).stem
    json_file = f"data/bsl_syntax_{base_name}.json" if "root" in base_name else "data/bsl_syntax.json"
    md_file = json_file.replace('.json', '.md')
    
    if os.path.exists(json_file):
        print(f"🔄 Создание контекста: {json_file}")
        # Создаем только основные файлы: JSON, TXT и поисковый индекс
        os.system(f"set PYTHONPATH=src && python src/converters/context_converter.py {json_file} json,txt,search_index")
        
        # Удаляем промежуточные файлы после конвертации
        if os.path.exists(json_file):
            os.remove(json_file)
            print(f"🗑️  Удален промежуточный файл: {json_file}")
        if os.path.exists(md_file):
            os.remove(md_file)
            print(f"🗑️  Удален промежуточный файл: {md_file}")
    else:
        print(f"⚠️  Файл {json_file} не найден")

def create_optimized_version():
    """Создает оптимизированную версию из полного контекста"""
    
    print("Загружаем полный контекст...")
    try:
        with open('data/1c_context.json', 'r', encoding='utf-8') as f:
            full_data = json.load(f)
        print(f"Загружено {len(full_data['context_items'])} элементов")
    except FileNotFoundError:
        print("❌ Файл data/1c_context.json не найден!")
        print("Сначала создайте полную версию: python run.py --full")
        return
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return
    
    # Приоритеты категорий (высокий -> низкий)
    priorities = {
        'methods': 1,      # Высокий приоритет
        'functions': 2,    # Высокий приоритет
        'operators': 3,    # Высокий приоритет
        'objects': 4,      # Средний приоритет
        'properties': 5    # Низкий приоритет
    }
    
    # Максимальное количество элементов по категориям
    limits = {
        'methods': 100,      # Все методы
        'functions': 100,    # Все функции
        'operators': 20,     # Все операторы
        'objects': 1000,     # Топ-1000 объектов
        'properties': 20     # Топ-20 свойств
    }
    
    # Группируем элементы по категориям
    categories = {}
    for item in full_data['context_items']:
        category = item['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    print("Группировка по категориям:")
    for category, items in categories.items():
        print(f"  {category}: {len(items)} элементов")
    
    # Сортируем категории по приоритету
    sorted_categories = sorted(categories.keys(), key=lambda x: priorities.get(x, 999))
    
    optimized_items = []
    
    for category in sorted_categories:
        items = categories[category]
        limit = limits.get(category, 100)
        
        print(f"Обрабатываем категорию: {category} (лимит: {limit} элементов)")
        
        # Сортируем элементы по важности
        scored_items = []
        for item in items:
            score = 0
            
            # Наличие методов (высокий вес)
            if item['metadata'].get('methods'):
                score += len(item['metadata']['methods']) * 10
                
            # Наличие синтаксиса (средний вес)
            if item['metadata'].get('syntax') or item['metadata'].get('syntax_variants'):
                score += 5
                
            # Наличие параметров (средний вес)
            if item['metadata'].get('parameters') or item['metadata'].get('parameters_by_variant'):
                score += 3
                
            # Наличие примеров (низкий вес)
            if item['metadata'].get('example'):
                score += 1
                
            # Наличие описания (базовый вес)
            if item['content']:
                score += 1
                
            scored_items.append((item, score))
        
        # Сортируем по убыванию важности
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        # Берем топ элементы
        top_items = [item for item, score in scored_items[:limit]]
        optimized_items.extend(top_items)
        
        print(f"  Выбрано {len(top_items)} элементов")
    
    # Создаем оптимизированный контекст
    optimized_data = {
        'metadata': {
            'source': '1C BSL Documentation (Optimized)',
            'generated_at': datetime.now().isoformat(),
            'total_items': len(optimized_items),
            'categories': list(set(item['category'] for item in optimized_items)),
            'optimization': 'Приоритетные элементы с лимитами по категориям',
            'original_size': len(full_data['context_items']),
            'compression_ratio': f"{len(optimized_items) / len(full_data['context_items']) * 100:.1f}%"
        },
        'context_items': optimized_items
    }
    
    # Сохраняем оптимизированную версию
    output_file = 'data/1c_context_optimized.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(optimized_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== Оптимизация завершена ===")
    print(f"Исходный размер: {len(full_data['context_items'])} элементов")
    print(f"Оптимизированный размер: {len(optimized_items)} элементов")
    print(f"Степень сжатия: {len(optimized_items) / len(full_data['context_items']) * 100:.1f}%")
    print(f"Файл сохранен: {output_file}")
    
    # Проверяем, что файл создался
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / 1024 / 1024
        print(f"Размер файла: {file_size:.2f} MB")
    else:
        print("ОШИБКА: Файл не создался!")
    
    # Создаем текстовую версию
    content = "# Оптимизированная документация синтаксиса 1С (BSL)\n\n"
    content += "Этот файл содержит приоритетные элементы документации по синтаксису языка 1С:Предприятие.\n"
    content += "Используйте эту информацию для ответов на вопросы о программировании в 1С.\n\n"
    content += "=" * 80 + "\n\n"
    
    for item in optimized_items:
        content += item['content']
        content += "\n\n" + "=" * 80 + "\n\n"
    
    txt_file = 'data/1c_context_optimized.txt'
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Текстовая версия сохранена: {txt_file}")

def run_demo(context_file):
    """Запускает демонстрацию"""
    if "optimized" in context_file:
        print("🚀 Демонстрация оптимизированного контекста")
        print("Запуск примеров поиска...")
        os.system(f"set PYTHONPATH=src && python src/demos/optimized_demo.py {context_file} --examples")
    elif "root" in context_file:
        print("🌐 Демонстрация файла оглавления (английский)")
        os.system(f"set PYTHONPATH=src && python src/demos/test_root_demo.py {context_file}")
    else:
        print("🇷🇺 Демонстрация основного файла (русский)")
        os.system(f"set PYTHONPATH=src && python src/demos/llm_context_demo.py {context_file}")

def main():
    parser = argparse.ArgumentParser(description="1C Help Parser - Парсер документации 1С")
    parser.add_argument("--file", "-f", help="Путь к ZIP файлу для парсинга")
    parser.add_argument("--demo", "-d", help="Путь к JSON файлу для демонстрации")
    parser.add_argument("--check", "-c", action="store_true", help="Проверить зависимости")
    parser.add_argument("--auto", action="store_true", help="Автоматический режим без интерактивного ввода")
    parser.add_argument("--full", action="store_true", help="Обработать всю документацию (все файлы)")
    parser.add_argument("--optimized", action="store_true", help="Создать оптимизированную версию (приоритетные элементы)")
    parser.add_argument("--basic", action="store_true", help="Использовать базовую версию парсера")
    
    args = parser.parse_args()
    
    print("🔧 1C Help Parser")
    print("=" * 50)
    
    # Проверка зависимостей
    if args.check:
        check_dependencies()
        return
    
    # Обработка конкретного файла
    if args.file:
        if not os.path.exists(args.file):
            print(f"❌ Файл не найден: {args.file}")
            return
        
        use_improved = not args.basic
        run_parser(args.file, use_improved=use_improved)
    
    # Демонстрация
    elif args.demo:
        if not os.path.exists(args.demo):
            print(f"❌ Файл не найден: {args.demo}")
            return
        
        run_demo(args.demo)
    
    # Автоматический режим
    elif args.auto:
        print("🤖 Автоматический режим - обработка основного файла")
        run_parser("data/rebuilt.shcntx_ru.zip")
    
    # Полная обработка
    elif args.full:
        print("🚀 Полная обработка - все файлы документации")
        run_parser("data/rebuilt.shcntx_ru.zip", max_files=None)
    
    # Оптимизированная версия
    elif args.optimized:
        print("🎯 Создание оптимизированной версии")
        create_optimized_version()
    
    # Интерактивный режим
    else:
        # Проверка зависимостей для интерактивного режима
        check_dependencies()
        
        print("\n🎯 Выберите действие:")
        print("1. Обработать документацию (shcntx_ru.zip) - первые 500 файлов")
        print("2. Обработать всю документацию (shcntx_ru.zip) - все файлы")
        print("3. Создать оптимизированную версию (приоритетные элементы)")
        print("4. Демонстрация оптимизированного контекста")
        print("5. Проверить зависимости")
        print("6. Очистить ненужные файлы")
        print("0. Выход")
        
        choice = input("\nВведите номер (0-6): ").strip()
        
        if choice == "1":
            run_parser("data/rebuilt.shcntx_ru.zip", max_files=500)
        elif choice == "2":
            run_parser("data/rebuilt.shcntx_ru.zip", max_files=None)
        elif choice == "3":
            print("🎯 Создание оптимизированной версии")
            create_optimized_version()
        elif choice == "4":
            run_demo("data/1c_context_optimized.json")
        elif choice == "5":
            print("✅ Зависимости уже проверены выше")
        elif choice == "6":
            cleanup_data()
        elif choice == "0":
            print("👋 До свидания!")
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    main() 