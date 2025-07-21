#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшенная демонстрация результатов парсинга
Показывает возможности улучшенного парсера с поддержкой:
- Множественных вариантов синтаксиса
- Полных описаний параметров
- Детальной информации о доступности
- Точных версий
"""

import json
import sys
import argparse
from typing import Dict, List, Any

class ImprovedDemo:
    """Улучшенная демонстрация результатов парсинга"""
    
    def __init__(self, context_file: str):
        self.context_file = context_file
        self.context_data = []
        self.search_index = {}
        
    def load_context(self) -> bool:
        """Загружает контекст из файла"""
        try:
            with open(self.context_file, 'r', encoding='utf-8') as f:
                self.context_data = json.load(f)
            print(f"✅ Загружено {len(self.context_data)} элементов контекста")
            return True
        except Exception as e:
            print(f"❌ Ошибка при загрузке контекста: {e}")
            return False
    
    def load_search_index(self, index_file: str) -> bool:
        """Загружает поисковый индекс"""
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                self.search_index = json.load(f)
            print(f"✅ Загружен поисковый индекс с {len(self.search_index)} ключами")
            return True
        except Exception as e:
            print(f"⚠️  Ошибка при загрузке поискового индекса: {e}")
            return False
    
    def search_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Поиск по ключевому слову"""
        results = []
        keyword_lower = keyword.lower()
        
        for item in self.context_data:
            if (keyword_lower in item['title'].lower() or 
                keyword_lower in item['description'].lower() or
                keyword_lower in item['syntax'].lower()):
                results.append(item)
        
        return results
    
    def search_by_availability(self, availability: str) -> List[Dict[str, Any]]:
        """Поиск по доступности"""
        results = []
        availability_lower = availability.lower()
        
        for item in self.context_data:
            for item_availability in item.get('availability', []):
                if availability_lower in item_availability.lower():
                    results.append(item)
                    break
        
        return results
    
    def search_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Поиск по категории"""
        results = []
        category_lower = category.lower()
        
        for item in self.context_data:
            if category_lower in item['category'].lower():
                results.append(item)
        
        return results
    
    def search_by_version(self, version: str) -> List[Dict[str, Any]]:
        """Поиск по версии"""
        results = []
        
        for item in self.context_data:
            if item.get('version') and version in item['version']:
                results.append(item)
        
        return results
    
    def show_item_details(self, item: Dict[str, Any]) -> None:
        """Показывает детальную информацию об элементе"""
        print(f"\n{'='*80}")
        print(f"📋 {item['title']}")
        print(f"{'='*80}")
        
        print(f"📝 **Синтаксис:** {item['syntax']}")
        print(f"📄 **Описание:** {item['description']}")
        print(f"🏷️  **Категория:** {item['category']}")
        
        if item.get('availability'):
            print(f"🌐 **Доступность:** {', '.join(item['availability'])}")
        
        if item.get('version'):
            print(f"📅 **Версия:** {item['version']}")
        
        if item.get('syntax_variants'):
            print(f"\n🔄 **Варианты синтаксиса:**")
            for i, variant in enumerate(item['syntax_variants'], 1):
                print(f"  {i}. **{variant['variant_name']}**: `{variant['syntax']}`")
                
                if variant['parameters']:
                    print(f"     **Параметры:**")
                    for param in variant['parameters']:
                        optional = "(необязательный)" if param.get('optional') else "(обязательный)"
                        print(f"     - `{param['name']}` {optional}: {param.get('type', '')}")
                        if param.get('description'):
                            print(f"       {param['description']}")
        
        if item.get('return_value'):
            print(f"\n↩️  **Возвращаемое значение:** {item['return_value']}")
        
        if item.get('example'):
            print(f"\n💡 **Пример:** {item['example']}")
        
        print(f"{'='*80}")
    
    def compare_with_original(self, item: Dict[str, Any]) -> None:
        """Сравнивает с оригинальной документацией"""
        print(f"\n🔍 **Сравнение с оригиналом:**")
        
        # Проверяем множественные варианты синтаксиса
        if item.get('syntax_variants') and len(item['syntax_variants']) > 1:
            print(f"✅ Множественные варианты синтаксиса: {len(item['syntax_variants'])} вариантов")
        else:
            print(f"⚠️  Один вариант синтаксиса или отсутствует")
        
        # Проверяем описания параметров
        has_param_descriptions = False
        for variant in item.get('syntax_variants', []):
            for param in variant.get('parameters', []):
                if param.get('description'):
                    has_param_descriptions = True
                    break
        
        if has_param_descriptions:
            print(f"✅ Описания параметров присутствуют")
        else:
            print(f"⚠️  Описания параметров отсутствуют")
        
        # Проверяем детальную доступность
        if item.get('availability') and len(item['availability']) > 2:
            print(f"✅ Детальная информация о доступности: {len(item['availability'])} элементов")
        else:
            print(f"⚠️  Упрощенная информация о доступности")
        
        # Проверяем точность версии
        if item.get('version') and '8.' in item['version']:
            print(f"✅ Точная информация о версии: {item['version']}")
        else:
            print(f"⚠️  Неточная или отсутствующая информация о версии")
    
    def run_examples(self) -> None:
        """Запускает примеры поиска"""
        print("\n🚀 **Примеры поиска:**")
        
        # Поиск метода "Удалить"
        print(f"\n1️⃣ Поиск метода 'Удалить':")
        delete_results = self.search_by_keyword("Удалить")
        print(f"   Найдено: {len(delete_results)} элементов")
        
        if delete_results:
            # Показываем первый результат
            first_result = delete_results[0]
            print(f"   Первый результат: {first_result['title']}")
            
            # Показываем детали
            self.show_item_details(first_result)
            
            # Сравниваем с оригиналом
            self.compare_with_original(first_result)
        
        # Поиск по доступности "сервер"
        print(f"\n2️⃣ Поиск по доступности 'сервер':")
        server_results = self.search_by_availability("сервер")
        print(f"   Найдено: {len(server_results)} элементов")
        
        if server_results:
            print(f"   Примеры: {', '.join([r['title'] for r in server_results[:3]])}")
        
        # Поиск по категории "methods"
        print(f"\n3️⃣ Поиск по категории 'methods':")
        method_results = self.search_by_category("methods")
        print(f"   Найдено: {len(method_results)} элементов")
        
        if method_results:
            print(f"   Примеры: {', '.join([r['title'] for r in method_results[:3]])}")
        
        # Поиск по версии "8.2"
        print(f"\n4️⃣ Поиск по версии '8.2':")
        version_results = self.search_by_version("8.2")
        print(f"   Найдено: {len(version_results)} элементов")
        
        if version_results:
            print(f"   Примеры: {', '.join([r['title'] for r in version_results[:3]])}")
    
    def interactive_search(self) -> None:
        """Интерактивный поиск"""
        print(f"\n🔍 **Интерактивный поиск:**")
        print(f"Доступные команды:")
        print(f"  keyword <слово> - поиск по ключевому слову")
        print(f"  availability <доступность> - поиск по доступности")
        print(f"  category <категория> - поиск по категории")
        print(f"  version <версия> - поиск по версии")
        print(f"  quit - выход")
        
        while True:
            try:
                command = input(f"\nВведите команду: ").strip()
                
                if command.lower() == 'quit':
                    break
                
                parts = command.split(' ', 1)
                if len(parts) != 2:
                    print(f"❌ Неверный формат команды")
                    continue
                
                cmd_type, query = parts
                
                if cmd_type.lower() == 'keyword':
                    results = self.search_by_keyword(query)
                    print(f"Найдено: {len(results)} элементов")
                    if results:
                        self.show_item_details(results[0])
                
                elif cmd_type.lower() == 'availability':
                    results = self.search_by_availability(query)
                    print(f"Найдено: {len(results)} элементов")
                    if results:
                        self.show_item_details(results[0])
                
                elif cmd_type.lower() == 'category':
                    results = self.search_by_category(query)
                    print(f"Найдено: {len(results)} элементов")
                    if results:
                        self.show_item_details(results[0])
                
                elif cmd_type.lower() == 'version':
                    results = self.search_by_version(query)
                    print(f"Найдено: {len(results)} элементов")
                    if results:
                        self.show_item_details(results[0])
                
                else:
                    print(f"❌ Неизвестная команда: {cmd_type}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
    
    def show_statistics(self) -> None:
        """Показывает статистику"""
        print(f"\n📊 **Статистика:**")
        
        # Общая статистика
        print(f"Всего элементов: {len(self.context_data)}")
        
        # Статистика по категориям
        categories = {}
        for item in self.context_data:
            category = item['category']
            categories[category] = categories.get(category, 0) + 1
        
        print(f"По категориям:")
        for category, count in sorted(categories.items()):
            print(f"  {category}: {count}")
        
        # Статистика по вариантам синтаксиса
        with_variants = sum(1 for item in self.context_data if item.get('syntax_variants'))
        without_variants = len(self.context_data) - with_variants
        
        print(f"Варианты синтаксиса:")
        print(f"  С вариантами: {with_variants}")
        print(f"  Без вариантов: {without_variants}")
        
        # Статистика по доступности
        availability_stats = {}
        for item in self.context_data:
            for availability in item.get('availability', []):
                availability_stats[availability] = availability_stats.get(availability, 0) + 1
        
        print(f"По доступности (топ-5):")
        sorted_availability = sorted(availability_stats.items(), key=lambda x: x[1], reverse=True)
        for availability, count in sorted_availability[:5]:
            print(f"  {availability}: {count}")
        
        # Статистика по версиям
        version_stats = {}
        for item in self.context_data:
            if item.get('version'):
                version_stats[item['version']] = version_stats.get(item['version'], 0) + 1
        
        print(f"По версиям:")
        for version, count in sorted(version_stats.items()):
            print(f"  {version}: {count}")

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description='Улучшенная демонстрация результатов парсинга')
    parser.add_argument('context_file', help='Путь к JSON файлу с контекстом')
    parser.add_argument('--index', help='Путь к файлу поискового индекса')
    parser.add_argument('--examples', action='store_true', help='Запустить примеры')
    parser.add_argument('--interactive', action='store_true', help='Интерактивный режим')
    parser.add_argument('--stats', action='store_true', help='Показать статистику')
    
    args = parser.parse_args()
    
    if not args.context_file:
        print("❌ Не указан файл контекста")
        sys.exit(1)
    
    demo = ImprovedDemo(args.context_file)
    
    if not demo.load_context():
        sys.exit(1)
    
    if args.index:
        demo.load_search_index(args.index)
    
    print(f"🔧 Улучшенная демонстрация результатов парсинга")
    print(f"📁 Файл: {args.context_file}")
    
    if args.examples:
        demo.run_examples()
    
    if args.stats:
        demo.show_statistics()
    
    if args.interactive:
        demo.interactive_search()
    
    if not any([args.examples, args.interactive, args.stats]):
        # По умолчанию показываем статистику и примеры
        demo.show_statistics()
        demo.run_examples()

if __name__ == "__main__":
    main() 