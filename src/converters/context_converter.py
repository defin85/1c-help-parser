#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конвертер документации 1С в формат context для LLM
Преобразует извлеченную документацию в удобный для LLM формат
"""

import os
import sys
import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
try:
    from .base_converter import BaseConverter
except ImportError:
    from base_converter import BaseConverter

class ContextConverter(BaseConverter):
    """Конвертер документации 1С в формат context для LLM"""
    
    def __init__(self, syntax_file: str):
        super().__init__(syntax_file)
        self.context_data = []
    
    def format_for_context(self, title: str, info: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Форматирует информацию для контекста LLM"""
        context_item = {
            'id': f"{category}_{len(self.context_data)}",
            'title': title,
            'category': category,
            'content': '',
            'metadata': {
                'filename': info.get('filename', ''),
                'syntax': info.get('syntax', ''),
                'parameters': info.get('parameters', []),
                'return_value': info.get('return_value', ''),
                'links': info.get('links', [])
            }
        }
        
        # Формируем основной контент
        content_parts = []
        
        # Заголовок
        content_parts.append(f"# {title}")
        
        # Синтаксис (поддержка множественных вариантов)
        if info.get('syntax_variants'):
            content_parts.append("\n## Синтаксис")
            for variant in info['syntax_variants']:
                content_parts.append(f"\n### {variant['variant_name']}\n```bsl\n{variant['syntax']}\n```")
        elif info.get('syntax'):
            content_parts.append(f"\n## Синтаксис\n```bsl\n{info['syntax']}\n```")
        
        # Описание
        if info.get('description'):
            description = super().clean_text(info['description'])
            content_parts.append(f"\n## Описание\n{description}")
        
        # Параметры (поддержка множественных вариантов)
        if info.get('parameters_by_variant'):
            content_parts.append("\n## Параметры")
            for variant_name, params in info['parameters_by_variant'].items():
                content_parts.append(f"\n### {variant_name}")
                for param in params:
                    optional = "(необязательный)" if param.get('optional') else "(обязательный)"
                    param_type = param.get('type', '')
                    param_desc = param.get('description', '')
                    param_line = f"- {param['name']} {optional}"
                    if param_type:
                        param_line += f": {param_type}"
                    if param_desc:
                        param_line += f" - {param_desc}"
                    content_parts.append(param_line)
        elif info.get('parameters'):
            content_parts.append("\n## Параметры")
            for param in info['parameters']:
                content_parts.append(f"- {param['name']}")
        
        # Возвращаемое значение
        if info.get('return_value'):
            return_val = super().clean_text(info['return_value'])
            content_parts.append(f"\n## Возвращаемое значение\n{return_val}")
        
        # Пример
        if info.get('example'):
            example = super().clean_text(info['example'])
            content_parts.append(f"\n## Пример\n```bsl\n{example}\n```")
        
        context_item['content'] = '\n'.join(content_parts)
        return context_item
    
    def convert_to_context(self) -> List[Dict[str, Any]]:
        """Конвертирует данные синтаксиса в формат context"""
        print("Конвертация в формат context...")
        
        if not self.load_data():
            return []
        
        for category, items in self.data.items():
            print(f"Обрабатываем категорию: {category} ({len(items)} элементов)")
            
            for title, info in items.items():
                if isinstance(info, dict) and not info.get('error'):
                    context_item = self.format_for_context(title, info, category)
                    self.context_data.append(context_item)
        
        print(f"Создано {len(self.context_data)} элементов контекста")
        return self.context_data
    
    def export_context_json(self, filename: str) -> None:
        """Экспортирует контекст в JSON формат"""
        context_export = {
            'metadata': {
                'source': '1C BSL Documentation',
                'generated_at': datetime.now().isoformat(),
                'total_items': len(self.context_data),
                'categories': list(set(item['category'] for item in self.context_data))
            },
            'context_items': self.context_data
        }
        
        self.export_json(context_export, filename)
    
    def export_context_text(self, filename: str) -> None:
        """Экспортирует контекст в текстовый формат для LLM"""
        content = "# Документация синтаксиса 1С (BSL)\n\n"
        content += "Этот файл содержит документацию по синтаксису языка 1С:Предприятие.\n"
        content += "Используйте эту информацию для ответов на вопросы о программировании в 1С.\n\n"
        content += "=" * 80 + "\n\n"
        
        for item in self.context_data:
            content += item['content']
            content += "\n\n" + "=" * 80 + "\n\n"
        
        self.export_text(content, filename)
    
    def export_context_chunks(self, chunk_size: int = 1000, output_dir: str = "data/context_chunks") -> None:
        """Экспортирует контекст в отдельные файлы-чанки"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Группируем по категориям
        categories = {}
        for item in self.context_data:
            category = item['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Создаем файлы для каждой категории
        for category, items in categories.items():
            filename = os.path.join(output_dir, f"{category}_context.txt")
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# Документация 1С: {category.title()}\n\n")
                
                for item in items:
                    f.write(item['content'])
                    f.write("\n\n" + "-" * 60 + "\n\n")
            
            print(f"Создан файл: {filename} ({len(items)} элементов)")
    
    def create_search_index(self, filename: str) -> None:
        """Создает поисковый индекс для быстрого поиска"""
        search_index = {
            'metadata': {
                'source': '1C BSL Documentation',
                'generated_at': datetime.now().isoformat(),
                'total_items': len(self.context_data)
            },
            'index': super().create_search_index(self.context_data)
        }
        
        self.export_json(search_index, filename)
    
    def convert(self, output_formats: List[str] = None) -> None:
        """Основной метод конвертации"""
        print("Начинаем конвертацию документации 1С...")
        
        # Конвертируем в контекст
        self.convert_to_context()
        
        if not self.context_data:
            print("Нет данных для конвертации")
            return
        
        # Определяем форматы вывода (по умолчанию только основные)
        if output_formats is None:
            output_formats = ['json', 'txt', 'search_index']
        
        # Экспортируем в выбранные форматы
        if 'json' in output_formats:
            self.export_context_json("data/1c_context.json")
        
        if 'txt' in output_formats:
            self.export_context_text("data/1c_context.txt")
        
        if 'chunks' in output_formats:
            self.export_context_chunks()
        
        if 'search_index' in output_formats:
            self.create_search_index("data/1c_search_index.json")
        
        if 'summary' in output_formats:
            self.create_summary("data/1c_summary.json")
        
        print("Конвертация завершена!")
    
    def create_summary(self, filename: str) -> None:
        """Создает краткое резюме документации"""
        summary = {
            'metadata': {
                'source': '1C BSL Documentation',
                'generated_at': datetime.now().isoformat(),
                'total_items': len(self.context_data)
            },
            'categories': {},
            'top_keywords': {},
            'examples': []
        }
        
        # Статистика по категориям
        for item in self.context_data:
            category = item['category']
            if category not in summary['categories']:
                summary['categories'][category] = 0
            summary['categories'][category] += 1
        
        # Собираем ключевые слова
        keywords = {}
        for item in self.context_data:
            words = re.findall(r'\b\w+\b', item['title'].lower())
            for word in words:
                if len(word) > 3:
                    keywords[word] = keywords.get(word, 0) + 1
        
        # Топ-20 ключевых слов
        top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:20]
        summary['top_keywords'] = dict(top_keywords)
        
        # Собираем примеры
        for item in self.context_data:
            if item['metadata']['syntax']:
                summary['examples'].append({
                    'title': item['title'],
                    'syntax': item['metadata']['syntax']
                })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"Резюме создано: {filename}")

def main():
    """Основная функция"""
    if len(sys.argv) < 2:
        print("Использование: python context_converter.py <путь_к_bsl_syntax.json> [форматы]")
        print("Форматы: json, txt, chunks, search_index, summary (по умолчанию: json,txt,search_index)")
        sys.exit(1)
    
    syntax_file = sys.argv[1]
    
    if not os.path.exists(syntax_file):
        print(f"Файл не найден: {syntax_file}")
        sys.exit(1)
    
    # Определяем форматы вывода
    output_formats = None
    if len(sys.argv) > 2:
        output_formats = sys.argv[2].split(',')
    
    converter = ContextConverter(syntax_file)
    
    # Запускаем конвертацию с выбранными форматами
    converter.convert(output_formats)
    
    print("\n=== Конвертация завершена ===")
    print("Созданные файлы:")
    if 'json' in output_formats:
        print("- 1c_context.json - структурированный контекст")
    if 'txt' in output_formats:
        print("- 1c_context.txt - текстовый контекст для LLM")
    if 'chunks' in output_formats:
        print("- context_chunks/ - файлы по категориям")
    if 'search_index' in output_formats:
        print("- 1c_search_index.json - поисковый индекс")
    if 'summary' in output_formats:
        print("- 1c_summary.json - краткое резюме")

if __name__ == "__main__":
    main() 