#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Оптимизированный конвертер для создания компактной версии контекста
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List
from .base_converter import BaseConverter

class OptimizedContextConverter(BaseConverter):
    """Оптимизированный конвертер для создания компактной версии контекста"""
    
    def __init__(self, syntax_file: str):
        super().__init__(syntax_file)
        self.context_data = []
        
    def convert(self, output_formats: List[str] = None) -> None:
        """Конвертирует данные в оптимизированный формат"""
        if output_formats is None:
            output_formats = ['json', 'txt', 'search_index']
            
        print("Начинаем конвертацию документации 1С...")
        print("Конвертация в оптимизированный формат...")
        
        # Загружаем данные напрямую из JSON файла
        try:
            with open(self.syntax_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"Загружено {sum(len(items) for items in self.data.values())} элементов")
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
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
        
        # Сортируем категории по приоритету
        sorted_categories = sorted(self.data.keys(), key=lambda x: priorities.get(x, 999))
        
        for category in sorted_categories:
            items = self.data[category]
            limit = limits.get(category, 100)
            
            print(f"Обрабатываем категорию: {category} (лимит: {limit} элементов)")
            
            # Сортируем элементы по важности (наличие методов, синтаксиса и т.д.)
            sorted_items = self._sort_by_importance(items, limit)
            
            for title, info in sorted_items:
                if isinstance(info, dict) and not info.get('error'):
                    context_item = self._format_for_context(title, info, category)
                    self.context_data.append(context_item)
        
        print(f"Создано {len(self.context_data)} оптимизированных элементов контекста")
        
        # Экспорт в различные форматы
        if 'json' in output_formats:
            self.export_context_json('data/1c_context_optimized.json')
            
        if 'txt' in output_formats:
            self.export_context_text('data/1c_context_optimized.txt')
            
        if 'search_index' in output_formats:
            self.create_search_index('data/1c_search_index_optimized.json')
            
        print("Конвертация завершена!")
        
    def _sort_by_importance(self, items: Dict[str, Any], limit: int) -> List[tuple]:
        """Сортирует элементы по важности"""
        scored_items = []
        
        for title, info in items.items():
            score = 0
            
            # Наличие методов (высокий вес)
            if info.get('methods'):
                score += len(info['methods']) * 10
                
            # Наличие синтаксиса (средний вес)
            if info.get('syntax') or info.get('syntax_variants'):
                score += 5
                
            # Наличие параметров (средний вес)
            if info.get('parameters') or info.get('parameters_by_variant'):
                score += 3
                
            # Наличие примеров (низкий вес)
            if info.get('example'):
                score += 1
                
            # Наличие описания (базовый вес)
            if info.get('description'):
                score += 1
                
            scored_items.append((title, info, score))
        
        # Сортируем по убыванию важности
        scored_items.sort(key=lambda x: x[2], reverse=True)
        
        # Возвращаем топ элементы
        return [(title, info) for title, info, score in scored_items[:limit]]
        
    def _format_for_context(self, title: str, info: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Форматирует информацию для контекста"""
        context_item = {
            'id': f"{category}_{len(self.context_data)}",
            'title': title,
            'category': category,
            'content': '',
            'metadata': {
                'filename': info.get('filename', ''),
                'syntax': info.get('syntax', ''),
                'syntax_variants': info.get('syntax_variants', []),
                'parameters': info.get('parameters', []),
                'parameters_by_variant': info.get('parameters_by_variant', {}),
                'return_value': info.get('return_value', ''),
                'example': info.get('example', ''),
                'links': info.get('links', []),
                'collection_elements': info.get('collection_elements', {}),
                'methods': info.get('methods', []),
                'availability': info.get('availability', []),
                'version': info.get('version', '')
            }
        }
        
        # Формируем основной контент - только описание
        if info.get('description'):
            context_item['content'] = super().clean_text(info['description'])
        else:
            context_item['content'] = ""
            
        return context_item
        
    def export_context_json(self, filename: str) -> None:
        """Экспортирует контекст в JSON формат"""
        context_export = {
            'metadata': {
                'source': '1C BSL Documentation (Optimized)',
                'generated_at': datetime.now().isoformat(),
                'total_items': len(self.context_data),
                'categories': list(set(item['category'] for item in self.context_data)),
                'optimization': 'Приоритетные элементы с лимитами по категориям'
            },
            'context_items': self.context_data
        }
        
        self.export_json(context_export, filename)
        
    def export_context_text(self, filename: str) -> None:
        """Экспортирует контекст в текстовый формат для LLM"""
        content = "# Оптимизированная документация синтаксиса 1С (BSL)\n\n"
        content += "Этот файл содержит приоритетные элементы документации по синтаксису языка 1С:Предприятие.\n"
        content += "Используйте эту информацию для ответов на вопросы о программировании в 1С.\n\n"
        content += "=" * 80 + "\n\n"
        
        for item in self.context_data:
            content += item['content']
            content += "\n\n" + "=" * 80 + "\n\n"
        
        self.export_text(content, filename)
        
    def create_search_index(self, filename: str) -> None:
        """Создает поисковый индекс для быстрого поиска"""
        search_index = {
            'metadata': {
                'source': '1C BSL Documentation (Optimized)',
                'generated_at': datetime.now().isoformat(),
                'total_items': len(self.context_data)
            },
            'search_data': []
        }
        
        for item in self.context_data:
            search_item = {
                'id': item['id'],
                'title': item['title'],
                'category': item['category'],
                'content': item['content'],
                'keywords': self._extract_keywords(item)
            }
            search_index['search_data'].append(search_item)
        
        self.export_json(search_index, filename)
        
    def _extract_keywords(self, item: Dict[str, Any]) -> List[str]:
        """Извлекает ключевые слова из элемента"""
        keywords = []
        
        # Из заголовка
        keywords.extend(item['title'].lower().split())
        
        # Из контента
        if item['content']:
            keywords.extend(item['content'].lower().split())
            
        # Из методов
        for method in item['metadata'].get('methods', []):
            keywords.append(method['name'].lower())
            
        # Убираем дубликаты и короткие слова
        keywords = list(set([k for k in keywords if len(k) > 2]))
        
        return keywords[:20]  # Ограничиваем количество ключевых слов

def main():
    """Основная функция"""
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python optimized_context_converter.py <syntax_file>")
        sys.exit(1)
        
    syntax_file = sys.argv[1]
    
    if not os.path.exists(syntax_file):
        print(f"Файл не найден: {syntax_file}")
        sys.exit(1)
        
    converter = OptimizedContextConverter(syntax_file)
    converter.convert()
    
    print("\n=== Конвертация завершена ===")
    print("Созданные файлы:")
    print("- 1c_context_optimized.json - оптимизированный контекст")
    print("- 1c_context_optimized.txt - текстовый контекст")
    print("- 1c_search_index_optimized.json - поисковый индекс")

if __name__ == "__main__":
    main() 