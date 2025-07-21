#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Оптимизированный конвертер контекста для 1С Help Parser
Создает компактный, но полный контекст с критически важными полями
"""

import json
import re
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup


class OptimizedContextConverter:
    """Оптимизированный конвертер для создания компактного контекста"""
    
    def __init__(self, syntax_file: str):
        self.syntax_file = syntax_file
        self.context_data = []
        
    def load_syntax_data(self) -> bool:
        """Загружает данные синтаксиса из JSON файла"""
        try:
            with open(self.syntax_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Преобразуем данные в единый формат
            self.context_data = []
            
            if 'items' in data:
                self.context_data = data['items']
            elif 'context_items' in data:
                self.context_data = data['context_items']
            elif 'objects' in data:
                # Формат bsl_syntax.json
                for category, items in data.items():
                    if isinstance(items, dict):
                        for item_id, item_data in items.items():
                            if isinstance(item_data, dict):
                                item_data['id'] = item_id
                                item_data['category'] = category
                                self.context_data.append(item_data)
            else:
                self.context_data = data
                
            print(f"Загружено {len(self.context_data)} элементов")
            return True
            
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            return False
    
    def extract_availability(self, content: str) -> List[str]:
        """Извлекает информацию о доступности из контента"""
        availability = []
        
        # Поиск по ключевым словам
        availability_keywords = [
            "Сервер", "Клиент", "Мобильное приложение", "Мобильный автономный сервер",
            "Внешнее соединение", "Толстый клиент", "Тонкий клиент", "Веб-клиент"
        ]
        
        content_lower = content.lower()
        for keyword in availability_keywords:
            if keyword.lower() in content_lower:
                availability.append(keyword)
        
        # Если не найдено, возвращаем общий доступ
        if not availability:
            availability = ["Клиент", "Сервер"]
            
        return availability
    
    def extract_version(self, content: str) -> str:
        """Извлекает информацию о версии из контента"""
        # Поиск паттернов версий
        version_patterns = [
            r"версии\s+(\d+\.\d+)",
            r"версии\s+(\d+\.\d+\.\d+)",
            r"(\d+\.\d+)\+",
            r"начиная с версии\s+(\d+\.\d+)",
            r"доступен.*версии\s+(\d+\.\d+)"
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1) + "+"
        
        return "8.0+"  # Версия по умолчанию
    
    def extract_parameters(self, content: str) -> List[Dict[str, Any]]:
        """Извлекает параметры из контента"""
        parameters = []
        
        # Поиск секции параметров
        param_section = re.search(r'параметр[ы]*:(.*?)(?=возвращаемое|описание|доступность|$)', 
                                 content, re.IGNORECASE | re.DOTALL)
        
        if param_section:
            param_text = param_section.group(1)
            
            # Поиск отдельных параметров
            param_matches = re.findall(r'<([^>]+)>\s*\(([^)]+)\)[^:]*:\s*([^.\n]+)', param_text)
            
            for param_name, param_type, param_desc in param_matches:
                parameters.append({
                    "name": param_name.strip(),
                    "type": param_type.strip(),
                    "required": "необязательный" not in param_desc.lower(),
                    "description": param_desc.strip()
                })
        
        return parameters
    
    def extract_return_value(self, content: str) -> str:
        """Извлекает возвращаемое значение из контента"""
        return_patterns = [
            r'возвращаемое значение[^:]*:\s*([^.\n]+)',
            r'тип[^:]*:\s*([^.\n]+)',
            r'результат[^:]*:\s*([^.\n]+)'
        ]
        
        for pattern in return_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def extract_syntax(self, content: str) -> str:
        """Извлекает синтаксис из контента"""
        syntax_patterns = [
            r'синтаксис[^:]*:\s*([^.\n]+)',
            r'([а-яё]+\([^)]*\))',  # Русские функции
            r'([a-z]+\([^)]*\))',   # Английские функции
        ]
        
        for pattern in syntax_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def determine_category(self, title: str, content: str) -> str:
        """Определяет категорию элемента"""
        title_lower = title.lower()
        content_lower = content.lower()
        
        # Операторы
        operators = ['для', 'пока', 'если', 'выбор', 'прервать', 'продолжить', 'возврат']
        if any(op in title_lower for op in operators):
            return "operators"
        
        # Функции
        if any(word in title_lower for word in ['функция', 'function']):
            return "functions"
        
        # Методы
        if '.' in title or any(word in content_lower for word in ['метод', 'method']):
            return "methods"
        
        # Объекты
        if any(word in title_lower for word in ['объект', 'object', 'форма', 'form']):
            return "objects"
        
        # Свойства
        if any(word in title_lower for word in ['свойство', 'property', 'реквизит']):
            return "properties"
        
        return "other"
    
    def clean_text(self, text: str) -> str:
        """Очищает текст от лишних символов"""
        if not text:
            return ""
        
        # Убираем лишние пробелы и переносы
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def process_parameters(self, parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Обрабатывает параметры, добавляя информацию о типах"""
        processed_params = []
        
        for param in parameters:
            processed_param = {
                'name': param.get('name', ''),
                'optional': param.get('optional', False),
                'description': param.get('description', '')
            }
            
            # Добавляем тип если есть
            if 'type' in param:
                processed_param['type'] = param['type']
                processed_param['type_description'] = param.get('type_description', '')
            
            # Сохраняем ссылку как дополнительную информацию
            if 'link' in param:
                processed_param['link'] = param['link']
            
            processed_params.append(processed_param)
        
        return processed_params
    
    def format_optimized_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Форматирует элемент в оптимизированном формате"""
        # Получаем данные
        title = item.get('title', '')
        description = item.get('description', '')
        syntax = item.get('syntax', '')
        parameters = item.get('parameters', [])
        return_value = item.get('return_value', '')
        category = item.get('category', '')
        
        # Если есть content, извлекаем из него
        content = item.get('content', '')
        if content:
            syntax = self.extract_syntax(content) or syntax
            description = self.clean_text(content.split('\n')[0] if content else "") or description
            extracted_params = self.extract_parameters(content) or parameters
            return_value = self.extract_return_value(content) or return_value
            availability = self.extract_availability(content)
            version = self.extract_version(content)
        else:
            # Используем значения по умолчанию
            availability = ["Клиент", "Сервер"]
            version = "8.0+"
            extracted_params = parameters
        
        # Обрабатываем параметры для добавления информации о типах
        processed_parameters = self.process_parameters(extracted_params)
        
        # Определяем категорию если не задана
        if not category:
            category = self.determine_category(title, content)
        
        return {
            "id": item.get('id', ''),
            "title": title,
            "syntax": syntax,
            "description": description,
            "parameters": processed_parameters,
            "return_value": return_value,
            "availability": availability,
            "version": version,
            "category": category
        }
    
    def create_search_index(self, items: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Создает оптимизированный поисковый индекс"""
        search_index = {}
        
        for item in items:
            item_id = item['id']
            
            # Поиск по названию и описанию
            search_text = f"{item['title']} {item.get('description', '')}"
            words = re.findall(r'\b\w+\b', search_text.lower())
            
            for word in words:
                if len(word) > 2:  # Игнорируем короткие слова
                    if word not in search_index:
                        search_index[word] = []
                    if item_id not in search_index[word]:
                        search_index[word].append(item_id)
            
            # Поиск по доступности
            for availability in item.get('availability', []):
                availability_lower = availability.lower()
                if availability_lower not in search_index:
                    search_index[availability_lower] = []
                if item_id not in search_index[availability_lower]:
                    search_index[availability_lower].append(item_id)
            
            # Поиск по версии
            version = item.get('version', '')
            if version:
                if version not in search_index:
                    search_index[version] = []
                if item_id not in search_index[version]:
                    search_index[version].append(item_id)
            
            # Поиск по категории
            category = item.get('category', '')
            if category:
                if category not in search_index:
                    search_index[category] = []
                if item_id not in search_index[category]:
                    search_index[category].append(item_id)
            
            # Поиск по типам параметров
            for param in item.get('parameters', []):
                param_type = param.get('type', '')
                if param_type:
                    type_lower = param_type.lower()
                    if type_lower not in search_index:
                        search_index[type_lower] = []
                    if item_id not in search_index[type_lower]:
                        search_index[type_lower].append(item_id)
        
        return search_index
    
    def convert_to_optimized_context(self) -> Dict[str, Any]:
        """Конвертирует данные в оптимизированный контекст"""
        print("Конвертация в оптимизированный формат...")
        
        # Форматируем все элементы
        optimized_items = []
        for item in self.context_data:
            optimized_item = self.format_optimized_item(item)
            optimized_items.append(optimized_item)
        
        # Создаем поисковый индекс
        search_index = self.create_search_index(optimized_items)
        
        # Создаем результат
        result = {
            "metadata": {
                "source": "1C BSL Documentation",
                "generated_at": datetime.now().isoformat(),
                "total_items": len(optimized_items),
                "format": "optimized"
            },
            "items": optimized_items,
            "search": search_index
        }
        
        return result
    
    def export_optimized_context(self, filename: str) -> None:
        """Экспортирует оптимизированный контекст"""
        context = self.convert_to_optimized_context()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(context, f, ensure_ascii=False, indent=2)
        
        print(f"Оптимизированный контекст экспортирован в {filename}")
        print(f"Размер: {os.path.getsize(filename) / 1024:.1f}KB")
        print(f"Элементов: {len(context['items'])}")
        print(f"Поисковых ключей: {len(context['search'])}")


def main():
    """Основная функция"""
    if len(sys.argv) != 2:
        print("Использование: python optimized_context_converter.py <путь_к_bsl_syntax.json>")
        sys.exit(1)
    
    syntax_file = sys.argv[1]
    
    if not os.path.exists(syntax_file):
        print(f"Файл не найден: {syntax_file}")
        sys.exit(1)
    
    converter = OptimizedContextConverter(syntax_file)
    
    if not converter.load_syntax_data():
        sys.exit(1)
    
    # Экспортируем оптимизированный контекст
    converter.export_optimized_context('data/1c_context_optimized.json')
    
    print("\n=== Оптимизация завершена ===")
    print("Создан файл: data/1c_context_optimized.json")
    print("Формат: Оптимизированный с критически важными полями")


if __name__ == "__main__":
    main() 