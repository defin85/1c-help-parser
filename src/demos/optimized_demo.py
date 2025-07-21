#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Демонстрация оптимизированного контекста для 1С Help Parser
Показывает возможности поиска по критически важным полям
"""

import json
import sys
import re
from typing import List, Dict, Any


class OptimizedContextDemo:
    """Демонстрация оптимизированного контекста"""
    
    def __init__(self, context_file: str):
        self.context_file = context_file
        self.context_data = None
        self.search_index = None
        
    def load_context(self) -> bool:
        """Загружает оптимизированный контекст"""
        try:
            with open(self.context_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.context_data = data.get('items', [])
            self.search_index = data.get('search', {})
            
            print(f"Загружен оптимизированный контекст:")
            print(f"- Элементов: {len(self.context_data)}")
            print(f"- Поисковых ключей: {len(self.search_index)}")
            print(f"- Размер файла: {len(json.dumps(data, ensure_ascii=False)) / 1024:.1f}KB")
            
            return True
            
        except Exception as e:
            print(f"Ошибка загрузки контекста: {e}")
            return False
    
    def search_by_keyword(self, keyword: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Поиск по ключевому слову"""
        keyword_lower = keyword.lower()
        results = []
        
        # Поиск в индексе
        if keyword_lower in self.search_index:
            item_ids = self.search_index[keyword_lower]
            
            for item_id in item_ids[:max_results]:
                item = self.find_item_by_id(item_id)
                if item:
                    results.append(item)
        
        # Если не найдено в индексе, ищем по тексту
        if not results:
            for item in self.context_data:
                search_text = f"{item['title']} {item.get('description', '')}".lower()
                if keyword_lower in search_text:
                    results.append(item)
                    if len(results) >= max_results:
                        break
        
        return results
    
    def search_by_availability(self, availability: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Поиск по доступности"""
        availability_lower = availability.lower()
        results = []
        
        for item in self.context_data:
            item_availability = [av.lower() for av in item.get('availability', [])]
            if availability_lower in item_availability:
                results.append(item)
                if len(results) >= max_results:
                    break
        
        return results
    
    def search_by_version(self, version: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Поиск по версии"""
        results = []
        
        for item in self.context_data:
            item_version = item.get('version', '')
            if version in item_version:
                results.append(item)
                if len(results) >= max_results:
                    break
        
        return results
    
    def search_by_category(self, category: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Поиск по категории"""
        category_lower = category.lower()
        results = []
        
        for item in self.context_data:
            item_category = item.get('category', '').lower()
            if category_lower == item_category:
                results.append(item)
                if len(results) >= max_results:
                    break
        
        return results
    
    def find_item_by_id(self, item_id: str) -> Dict[str, Any]:
        """Находит элемент по ID"""
        for item in self.context_data:
            if item.get('id') == item_id:
                return item
        return None
    
    def display_item(self, item: Dict[str, Any]) -> None:
        """Отображает элемент в читаемом формате"""
        print(f"\n{'='*80}")
        print(f"📄 {item['title']}")
        print(f"{'='*80}")
        
        if item.get('syntax'):
            print(f"🔧 Синтаксис: {item['syntax']}")
        
        if item.get('description'):
            print(f"📝 Описание: {item['description']}")
        
        if item.get('parameters'):
            print(f"📋 Параметры:")
            for param in item['parameters']:
                required = "обязательный" if param.get('required', True) else "необязательный"
                print(f"  - {param['name']} ({param['type']}) - {required}")
        
        if item.get('return_value'):
            print(f"🔄 Возвращаемое значение: {item['return_value']}")
        
        if item.get('availability'):
            print(f"✅ Доступность: {', '.join(item['availability'])}")
        
        if item.get('version'):
            print(f"📅 Версия: {item['version']}")
        
        print(f"🏷️  Категория: {item.get('category', 'неизвестно')}")
    
    def display_search_results(self, results: List[Dict[str, Any]], query: str) -> None:
        """Отображает результаты поиска"""
        if not results:
            print(f"\n❌ По запросу '{query}' ничего не найдено")
            return
        
        print(f"\n🔍 Найдено {len(results)} результатов по запросу '{query}':")
        
        for i, item in enumerate(results, 1):
            print(f"\n{i}. {item['title']}")
            if item.get('description'):
                print(f"   {item['description'][:100]}...")
            if item.get('availability'):
                print(f"   Доступность: {', '.join(item['availability'])}")
    
    def interactive_search(self) -> None:
        """Интерактивный поиск"""
        print("\n🎯 Интерактивный поиск по оптимизированному контексту")
        print("Доступные типы поиска:")
        print("1. По ключевому слову (например: 'форма', 'цикл')")
        print("2. По доступности (например: 'сервер', 'клиент')")
        print("3. По версии (например: '8.2')")
        print("4. По категории (например: 'operators', 'methods')")
        print("5. Показать детали элемента по ID")
        print("0. Выход")
        
        while True:
            try:
                query = input("\n🔍 Введите запрос (или 0 для выхода): ").strip()
                
                if query == '0':
                    break
                
                if not query:
                    continue
                
                # Определяем тип поиска
                if query.lower() in ['сервер', 'клиент', 'мобильный', 'веб-клиент']:
                    results = self.search_by_availability(query)
                    self.display_search_results(results, f"доступность: {query}")
                
                elif re.match(r'\d+\.\d+', query):
                    results = self.search_by_version(query)
                    self.display_search_results(results, f"версия: {query}")
                
                elif query.lower() in ['operators', 'methods', 'objects', 'properties', 'functions']:
                    results = self.search_by_category(query)
                    self.display_search_results(results, f"категория: {query}")
                
                elif query.startswith('id:'):
                    item_id = query[3:].strip()
                    item = self.find_item_by_id(item_id)
                    if item:
                        self.display_item(item)
                    else:
                        print(f"❌ Элемент с ID '{item_id}' не найден")
                
                else:
                    results = self.search_by_keyword(query)
                    self.display_search_results(results, query)
                
                # Показать детали первого результата
                if results and len(results) > 0:
                    show_details = input(f"\n📖 Показать детали первого результата? (y/n): ").strip().lower()
                    if show_details == 'y':
                        self.display_item(results[0])
                
            except KeyboardInterrupt:
                print("\n\n👋 До свидания!")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")


def main():
    """Основная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Демонстрация оптимизированного контекста')
    parser.add_argument('context_file', help='Путь к файлу 1c_context_optimized.json')
    parser.add_argument('--examples', action='store_true', help='Показать только примеры без интерактивного режима')
    
    args = parser.parse_args()
    context_file = args.context_file
    
    if not os.path.exists(context_file):
        print(f"Файл не найден: {context_file}")
        sys.exit(1)
    
    demo = OptimizedContextDemo(context_file)
    
    if not demo.load_context():
        sys.exit(1)
    
    # Примеры поиска
    print("\n🔍 Примеры поиска:")
    
    # Поиск по ключевому слову
    results = demo.search_by_keyword("форма", 3)
    demo.display_search_results(results, "форма")
    
    # Поиск по доступности
    results = demo.search_by_availability("сервер", 3)
    demo.display_search_results(results, "доступность: сервер")
    
    # Поиск по категории
    results = demo.search_by_category("operators", 3)
    demo.display_search_results(results, "категория: operators")
    
    # Интерактивный режим (только если не указан флаг --examples)
    if not args.examples:
        demo.interactive_search()
    else:
        print("\n✅ Демонстрация завершена. Для интерактивного режима запустите:")
        print(f"python src/demos/optimized_demo.py {context_file}")


if __name__ == "__main__":
    import os
    main() 