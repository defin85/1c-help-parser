#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1C Help Parser - Главный скрипт запуска
"""

import os
import sys
import argparse
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

def run_parser(zip_file, max_files=500, use_improved=True):
    """Запускает парсинг файла"""
    print(f"🔍 Анализ структуры: {zip_file}")
    os.system(f"set PYTHONPATH=src && python src/parsers/hbk_parser.py {zip_file}")
    
    print(f"📝 Извлечение синтаксиса: {zip_file}")
    os.system(f"set PYTHONPATH=src && python src/parsers/bsl_syntax_extractor.py {zip_file} --max-files {max_files}")
    
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
    
    # Интерактивный режим
    else:
        # Проверка зависимостей для интерактивного режима
        check_dependencies()
        
        print("\n🎯 Выберите действие:")
        print("1. Обработать документацию (shcntx_ru.zip)")
        print("2. Демонстрация оптимизированного контекста")
        print("3. Проверить зависимости")
        print("4. Очистить ненужные файлы")
        print("0. Выход")
        
        choice = input("\nВведите номер (0-4): ").strip()
        
        if choice == "1":
            run_parser("data/rebuilt.shcntx_ru.zip")
        elif choice == "2":
            run_demo("data/1c_context_optimized.json")
        elif choice == "3":
            print("✅ Зависимости уже проверены выше")
        elif choice == "4":
            cleanup_data()
        elif choice == "0":
            print("👋 До свидания!")
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    main() 