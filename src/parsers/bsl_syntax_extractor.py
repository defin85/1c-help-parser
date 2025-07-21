#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Экстрактор синтаксиса BSL из файлов справки 1С
Извлекает структурированную информацию о синтаксисе языка 1С
"""

import os
import sys
import re
import argparse
from bs4 import BeautifulSoup
import json
from typing import Dict, List, Optional, Any
from collections import defaultdict
try:
    from .base_parser import BaseParser
except ImportError:
    from base_parser import BaseParser

class BSLSyntaxExtractor(BaseParser):
    """Экстрактор синтаксиса BSL из файлов справки 1С"""
    
    def __init__(self, hbk_file: str):
        super().__init__(hbk_file)
        self.syntax_data = {
            'objects': {},
            'methods': {},
            'properties': {},
            'functions': {},
            'operators': {},
            'keywords': {}
        }
        
        # Справочник типов для извлечения из ссылок
        self.type_mapping = {
            'def_String': {'type': 'String', 'description': 'Строковый тип данных'},
            'def_Number': {'type': 'Number', 'description': 'Числовой тип данных'},
            'def_Boolean': {'type': 'Boolean', 'description': 'Логический тип данных'},
            'def_BooleanTrue': {'type': 'Boolean', 'description': 'Логический тип данных (Истина)'},
            'def_Date': {'type': 'Date', 'description': 'Тип данных Дата'},
            'def_Time': {'type': 'Time', 'description': 'Тип данных Время'},
            'Array': {'type': 'Array', 'description': 'Массив значений'},
            'Structure': {'type': 'Structure', 'description': 'Структура данных'},
            'ValueTable': {'type': 'ValueTable', 'description': 'Таблица значений'},
            'FormDataCollectionItem': {'type': 'FormDataCollectionItem', 'description': 'Элемент коллекции данных формы'},
            'FormDataTreeItem': {'type': 'FormDataTreeItem', 'description': 'Элемент дерева данных формы'}
        }
    
    def extract_type_from_link(self, link: str) -> Dict[str, str]:
        """Извлекает тип и описание из ссылки v8help"""
        if not link:
            return {'type': '', 'description': ''}
        
        # Базовые типы языка
        if 'def_' in link:
            type_key = link.split('def_')[-1]
            if type_key in self.type_mapping:
                return self.type_mapping[type_key]
            else:
                return {'type': type_key, 'description': f'Базовый тип: {type_key}'}
        
        # Объектные типы
        elif 'objects/' in link:
            # Извлекаем имя объекта из пути
            object_path = link.split('objects/')[-1].replace('.html', '')
            object_name = object_path.split('/')[-1]
            
            if object_name in self.type_mapping:
                return self.type_mapping[object_name]
            else:
                return {'type': object_name, 'description': f'Объект: {object_name}'}
        
        return {'type': '', 'description': ''}
    
    def extract_object_methods(self, soup) -> List[Dict[str, str]]:
        """Извлекает методы объекта из документации"""
        methods = []
        
        # Ищем секцию "Методы"
        for elem in soup.find_all('p', class_='V8SH_chapter'):
            text = elem.get_text(strip=True)
            if 'Методы' in text:
                # Ищем список методов
                current = elem
                while current:
                    current = current.find_next_sibling()
                    if current and current.name == 'ul':
                        # Нашли список методов
                        for li in current.find_all('li'):
                            method_text = li.get_text(strip=True)
                            if method_text:
                                # Извлекаем название метода и английский эквивалент
                                if '(' in method_text and ')' in method_text:
                                    method_name = method_text[:method_text.find('(')].strip()
                                    english_name = method_text[method_text.find('(')+1:method_text.find(')')].strip()
                                    methods.append({
                                        'name': method_name,
                                        'english_name': english_name,
                                        'full_name': method_text
                                    })
                                else:
                                    methods.append({
                                        'name': method_text,
                                        'english_name': '',
                                        'full_name': method_text
                                    })
                        break
                    elif current and current.name == 'p' and 'V8SH_chapter' in current.get('class', []):
                        # Останавливаемся на следующем заголовке
                        break
        
        # Если методы не найдены в списке, ищем ссылки на методы
        if not methods:
            seen_methods = set()  # Для избежания дублирования
            for link in soup.find_all('a'):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if 'methods/' in href and text:
                    # Извлекаем название метода из ссылки
                    method_name = text
                    english_name = ''
                    
                    # Пытаемся найти английское название в скобках
                    if '(' in text and ')' in text:
                        method_name = text[:text.find('(')].strip()
                        english_name = text[text.find('(')+1:text.find(')')].strip()
                    
                    # Проверяем, не добавляли ли мы уже этот метод
                    method_key = f"{method_name}_{english_name}"
                    if method_key not in seen_methods:
                        methods.append({
                            'name': method_name,
                            'english_name': english_name,
                            'full_name': text
                        })
                        seen_methods.add(method_key)
        
        return methods
    
    def extract_collection_elements(self, soup) -> Dict[str, str]:
        """Извлекает информацию об элементах коллекции"""
        elements_info = {}
        
        # Ищем секцию "Элементы коллекции"
        for elem in soup.find_all('p', class_='V8SH_chapter'):
            text = elem.get_text(strip=True)
            if 'Элементы коллекции' in text:
                # Получаем весь HTML между заголовками
                html_content = ""
                current = elem
                
                while current:
                    current = current.find_next_sibling()
                    if current and current.name == 'p' and 'V8SH_chapter' in current.get('class', []):
                        # Останавливаемся на следующем заголовке
                        break
                    elif current:
                        html_content += str(current)
                
                # Парсим HTML и извлекаем текст
                if html_content:
                    section_soup = BeautifulSoup(html_content, 'html.parser')
                    full_text = section_soup.get_text(strip=True)
                    
                    # Разбиваем на предложения и фильтруем
                    sentences = []
                    for sentence in full_text.split('.'):
                        sentence = sentence.strip()
                        if sentence and not any(keyword in sentence for keyword in ['Методы', 'Описание', 'Доступность', 'См. также', 'Использование в версии']):
                            sentences.append(sentence)
                    
                    if sentences:
                        # Формируем полное описание с информацией об использовании
                        full_description = []
                        
                        # Добавляем тип элементов
                        if sentences:
                            full_description.append(sentences[0])  # Первое предложение - тип элементов
                        
                        # Добавляем информацию об обходе и индексации
                        for sentence in sentences[1:]:
                            if any(keyword in sentence for keyword in ['Для каждого', 'Из', 'Цикл', 'индекс', 'оператор']):
                                full_description.append(sentence)
                        
                        elements_info['description'] = '. '.join(full_description)
                        
                        # Дополнительно сохраняем информацию об использовании
                        usage_info = []
                        for sentence in sentences:
                            if any(keyword in sentence for keyword in ['Для каждого', 'Из', 'Цикл', 'индекс', 'оператор']):
                                usage_info.append(sentence)
                        
                        if usage_info:
                            elements_info['usage'] = '. '.join(usage_info)
                
                # Дополнительно ищем информацию об использовании во всем HTML
                full_html = str(soup)
                if 'Для каждого' in full_html:
                    # Извлекаем предложения с информацией об использовании
                    usage_sentences = []
                    
                    # Ищем предложения с ключевыми словами
                    for keyword in ['Для каждого', 'индекс', 'оператор']:
                        if keyword in full_html:
                            # Находим контекст вокруг ключевого слова
                            start = full_html.find(keyword)
                            if start > 0:
                                # Извлекаем предложение
                                sentence_start = full_html.rfind('.', 0, start) + 1
                                sentence_end = full_html.find('.', start)
                                if sentence_end > start:
                                    sentence = full_html[sentence_start:sentence_end].strip()
                                    # Очищаем от HTML тегов
                                    sentence = BeautifulSoup(sentence, 'html.parser').get_text(strip=True)
                                    # Дополнительная очистка от лишнего текста
                                    if 'html' in sentence:
                                        sentence = sentence.split('html')[-1]
                                    if '">' in sentence:
                                        sentence = sentence.split('">')[-1]
                                    if sentence and sentence not in usage_sentences:
                                        usage_sentences.append(sentence)
                    
                    if usage_sentences:
                        # Очищаем от дублирования типа элемента
                        cleaned_usage = []
                        for sentence in usage_sentences:
                            # Убираем упоминание типа элемента из начала предложения
                            if elements_info.get('description') and elements_info['description'] in sentence:
                                sentence = sentence.replace(elements_info['description'], '').strip()
                            # Убираем лишние символы в начале
                            if sentence.startswith('Для'):
                                cleaned_usage.append(sentence)
                        
                        if cleaned_usage:
                            elements_info['usage'] = '. '.join(cleaned_usage)
                break
        
        return elements_info
    
    def extract_syntax_info(self, html_content: str, filename: str) -> Dict[str, Any]:
        """Извлекает информацию о синтаксисе из HTML-файла"""
        try:
            soup = super().parse_html_content(html_content)
            
            result = {
                'filename': filename,
                'title': '',
                'syntax': '',
                'description': '',
                'parameters': [],
                'return_value': '',
                'example': '',
                'category': '',
                'links': [],
                'availability': [],
                'version': '',
                'methods': [],
                'collection_elements': {}
            }
            
            # Извлекаем заголовок
            title_elem = soup.find('h1', class_='V8SH_pagetitle')
            if title_elem:
                result['title'] = title_elem.get_text(strip=True)
            
            # Определяем категорию по пути файла
            if 'objects/' in filename:
                result['category'] = 'object'
            elif 'tables/' in filename:
                result['category'] = 'table'
            elif 'methods/' in filename:
                result['category'] = 'method'
            elif 'properties/' in filename:
                result['category'] = 'property'
            
            # Извлекаем синтаксис (поддержка множественных вариантов)
            syntax_variants = []
            current_variant = None
            
            for elem in soup.find_all('p', class_='V8SH_chapter'):
                text = elem.get_text(strip=True)
                
                if 'Вариант синтаксиса:' in text:
                    # Начинаем новый вариант
                    current_variant = text.replace('Вариант синтаксиса:', '').strip()
                    
                elif 'Синтаксис:' in text and current_variant:
                    # Ищем синтаксис для текущего варианта
                    current = elem
                    syntax_text = ""
                    while current:
                        current = current.next_sibling
                        if current and hasattr(current, 'get_text'):
                            if current.name != 'p' or 'V8SH_chapter' not in current.get('class', []):
                                syntax_text = current.get_text(strip=True)
                                if syntax_text and syntax_text != 'Параметры:':
                                    break
                        elif current and isinstance(current, str):
                            syntax_text = current.strip()
                            if syntax_text and syntax_text != 'Параметры:':
                                break
                    
                    if syntax_text:
                        syntax_variants.append({
                            'variant_name': current_variant,
                            'syntax': syntax_text
                        })
                        
                elif 'Синтаксис' in text and 'Вариант' not in text and not current_variant:
                    # Обычный синтаксис (без вариантов)
                    current = elem
                    while current:
                        current = current.next_sibling
                        if current and hasattr(current, 'get_text'):
                            if current.name != 'p' or 'V8SH_chapter' not in current.get('class', []):
                                syntax_text = current.get_text(strip=True)
                                if syntax_text and syntax_text != 'Параметры:':
                                    result['syntax'] = syntax_text
                                    break
                        elif current and isinstance(current, str):
                            syntax_text = current.strip()
                            if syntax_text and syntax_text != 'Параметры:':
                                result['syntax'] = syntax_text
                                break
                    break
            
            # Сохраняем варианты синтаксиса
            if syntax_variants:
                result['syntax_variants'] = syntax_variants
                # Используем первый вариант как основной синтаксис
                if syntax_variants:
                    result['syntax'] = syntax_variants[0]['syntax']
            
            # Извлекаем описание
            for elem in soup.find_all('p', class_='V8SH_chapter'):
                text = elem.get_text(strip=True)
                if 'Описание' in text:
                    desc_elem = elem.find_next_sibling('p')
                    if desc_elem:
                        result['description'] = desc_elem.get_text(strip=True)
                    break
            
            # Извлекаем доступность
            for elem in soup.find_all('p', class_='V8SH_chapter'):
                text = elem.get_text(strip=True)
                if 'Доступность' in text:
                    avail_elem = elem.find_next_sibling('p')
                    if avail_elem:
                        availability_text = avail_elem.get_text(strip=True)
                        # Разбиваем по запятым и очищаем
                        availability_list = [item.strip() for item in availability_text.split(',')]
                        result['availability'] = availability_list
                    break
            
            # Извлекаем параметры (поддержка множественных вариантов)
            parameters_by_variant = {}
            current_variant = None
            
            # Проходим по всем элементам и собираем параметры для каждого варианта
            for elem in soup.find_all('p', class_='V8SH_chapter'):
                text = elem.get_text(strip=True)
                
                # Определяем текущий вариант
                if 'Вариант синтаксиса:' in text:
                    current_variant = text.replace('Вариант синтаксиса:', '').strip()
                    if current_variant not in parameters_by_variant:
                        parameters_by_variant[current_variant] = []
                
                # Извлекаем параметры для текущего варианта
                if 'Параметры:' in text and current_variant:
                    # Ищем все div с классом V8SH_rubric (блоки параметров) до следующего заголовка
                    param_blocks = []
                    current = elem
                    while current:
                        current = current.find_next_sibling()
                        if current and current.name == 'div' and 'V8SH_rubric' in current.get('class', []):
                            param_blocks.append(current)
                        elif current and current.name == 'p' and 'V8SH_chapter' in current.get('class', []):
                            # Останавливаемся на следующем заголовке
                            break
                    
                    for block in param_blocks:
                        param_info = {}
                        
                        # Извлекаем имя параметра из div
                        param_text = block.get_text(strip=True)
                        if '<' in param_text and '>' in param_text:
                            # Извлекаем имя параметра между < >
                            start = param_text.find('<') + 1
                            end = param_text.find('>')
                            if start > 0 and end > start:
                                param_name = param_text[start:end]
                                param_info['name'] = param_name
                        
                        # Проверяем обязательность
                        if '(необязательный)' in param_text:
                            param_info['optional'] = True
                        else:
                            param_info['optional'] = False
                        
                        # Ищем тип параметра в следующем элементе
                        next_elem = block.find_next_sibling()
                        if next_elem:
                            type_text = next_elem.get_text(strip=True)
                            if 'Тип:' in type_text:
                                # Извлекаем тип после "Тип:"
                                type_start = type_text.find('Тип:') + 4
                                type_end = type_text.find('.', type_start)
                                if type_end > type_start:
                                    param_type = type_text[type_start:type_end].strip()
                                    param_info['type'] = param_type
                        
                        # Ищем описание параметра
                        desc_elem = block.find_next_sibling()
                        if desc_elem and desc_elem.name == 'br':
                            # Описание идет после <br>
                            desc_text = desc_elem.next_sibling
                            if desc_text:
                                param_info['description'] = desc_text.strip()
                        
                        # Ищем ссылку на тип
                        type_link = block.find_next('a')
                        if type_link:
                            link = type_link.get('href', '')
                            param_info['link'] = link
                            
                            # Извлекаем тип и описание из ссылки
                            type_info = self.extract_type_from_link(link)
                            if type_info['type']:
                                param_info['type'] = type_info['type']
                                param_info['type_description'] = type_info['description']
                        
                        if param_info.get('name'):
                            parameters_by_variant[current_variant].append(param_info)
            
            # Сохраняем параметры в правильном формате
            if parameters_by_variant:
                # Если есть варианты, сохраняем параметры по вариантам
                result['parameters_by_variant'] = parameters_by_variant
                # Для обратной совместимости сохраняем все параметры в общий список
                all_parameters = []
                for variant_params in parameters_by_variant.values():
                    all_parameters.extend(variant_params)
                result['parameters'] = all_parameters
            else:
                # Если нет вариантов, используем старую логику
                result['parameters'] = []
            
            # Извлекаем возвращаемое значение
            for elem in soup.find_all('p', class_='V8SH_chapter'):
                text = elem.get_text(strip=True)
                if 'Возвращаемое значение' in text:
                    next_elem = elem.find_next_sibling('p')
                    if next_elem:
                        result['return_value'] = next_elem.get_text(strip=True)
                    break
            
            # Извлекаем версию
            for elem in soup.find_all('p', class_='V8SH_chapter'):
                text = elem.get_text(strip=True)
                if 'Использование в версии' in text:
                    version_elem = elem.find_next_sibling('p', class_='V8SH_versionInfo')
                    if version_elem:
                        version_text = version_elem.get_text(strip=True)
                        # Извлекаем номер версии
                        if 'версии' in version_text:
                            version_start = version_text.find('версии') + 6
                            version = version_text[version_start:].strip()
                            result['version'] = version
                    break
            
            # Извлекаем пример
            for elem in soup.find_all('p', class_='V8SH_chapter'):
                text = elem.get_text(strip=True)
                if 'Пример' in text:
                    table = elem.find_next('table')
                    if table:
                        result['example'] = table.get_text(strip=True)
                    break
            
            # Извлекаем методы объекта
            result['methods'] = self.extract_object_methods(soup)
            
            # Извлекаем элементы коллекции
            result['collection_elements'] = self.extract_collection_elements(soup)
            
            # Извлекаем ссылки
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if href and href.startswith('v8help://'):
                    result['links'].append({
                        'text': link.get_text(strip=True),
                        'href': href
                    })
            
            return result
            
        except Exception as e:
            print(f"Ошибка при извлечении синтаксиса из {filename}: {e}")
            return {'filename': filename, 'error': str(e)}
    
    def categorize_syntax(self, syntax_info: Dict[str, Any]) -> None:
        """Категоризирует информацию о синтаксисе"""
        if not syntax_info or 'error' in syntax_info:
            return
        
        title = syntax_info.get('title', '')
        category = syntax_info.get('category', '')
        syntax = syntax_info.get('syntax', '')
        
        # Определяем тип по заголовку и синтаксису
        if 'Функция' in title or 'function' in title.lower():
            self.syntax_data['functions'][title] = syntax_info
        elif 'Метод' in title or 'method' in title.lower():
            self.syntax_data['methods'][title] = syntax_info
        elif 'Свойство' in title or 'property' in title.lower():
            self.syntax_data['properties'][title] = syntax_info
        elif 'Оператор' in title or 'operator' in title.lower():
            self.syntax_data['operators'][title] = syntax_info
        elif 'Ключевое слово' in title or 'keyword' in title.lower():
            self.syntax_data['keywords'][title] = syntax_info
        elif category == 'object':
            self.syntax_data['objects'][title] = syntax_info
        else:
            # По умолчанию добавляем в объекты
            self.syntax_data['objects'][title] = syntax_info
    
    def extract_all_syntax(self, max_files: int = 1000) -> Dict[str, Any]:
        """Извлекает синтаксис из всех HTML-файлов"""
        if not self.zip_file:
            return {}
        
        html_files = [f for f in self.zip_file.namelist() if f.endswith('.html')]
        
        print(f"Найдено {len(html_files)} HTML файлов")
        print(f"Обрабатываем первые {min(max_files, len(html_files))} файлов...")
        
        processed = 0
        for filename in html_files[:max_files]:
            try:
                # Читаем содержимое файла
                content = self.zip_file.read(filename).decode('utf-8', errors='ignore')
                
                # Извлекаем информацию о синтаксисе
                syntax_info = self.extract_syntax_info(content, filename)
                
                # Категоризируем
                self.categorize_syntax(syntax_info)
                
                processed += 1
                if processed % 100 == 0:
                    print(f"Обработано {processed} файлов...")
                
            except Exception as e:
                print(f"Ошибка при обработке файла {filename}: {e}")
        
        print(f"Обработка завершена. Обработано {processed} файлов.")
        
        # Подсчитываем статистику
        stats = {}
        for category, items in self.syntax_data.items():
            stats[category] = len(items)
        
        return {
            'statistics': stats,
            'data': self.syntax_data
        }
    
    def find_by_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """Ищет элементы по паттерну в заголовке или синтаксисе"""
        results = []
        pattern_lower = pattern.lower()
        
        for category, items in self.syntax_data.items():
            for title, info in items.items():
                if (pattern_lower in title.lower() or 
                    pattern_lower in info.get('syntax', '').lower() or
                    pattern_lower in info.get('description', '').lower()):
                    results.append({
                        'category': category,
                        'title': title,
                        'info': info
                    })
        
        return results
    
    def export_to_json(self, filename: str) -> None:
        """Экспортирует данные в JSON файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.syntax_data, f, ensure_ascii=False, indent=2)
        print(f"Данные экспортированы в {filename}")
    
    def export_to_markdown(self, filename: str) -> None:
        """Экспортирует данные в Markdown файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Справочник синтаксиса BSL 1С\n\n")
            
            for category, items in self.syntax_data.items():
                if items:
                    f.write(f"## {category.title()}\n\n")
                    
                    for title, info in items.items():
                        f.write(f"### {title}\n\n")
                        
                        if info.get('syntax'):
                            f.write(f"**Синтаксис:** `{info['syntax']}`\n\n")
                        
                        if info.get('description'):
                            f.write(f"**Описание:** {info['description']}\n\n")
                        
                        if info.get('parameters'):
                            f.write("**Параметры:**\n")
                            for param in info['parameters']:
                                f.write(f"- {param['name']}\n")
                            f.write("\n")
                        
                        if info.get('return_value'):
                            f.write(f"**Возвращаемое значение:** {info['return_value']}\n\n")
                        
                        if info.get('example'):
                            f.write("**Пример:**\n")
                            f.write(f"```bsl\n{info['example']}\n```\n\n")
                        
                        f.write("---\n\n")
        
        print(f"Данные экспортированы в {filename}")
    
    def parse(self, max_files: int = 1000, **kwargs) -> Dict[str, Any]:
        """Реализация абстрактного метода parse"""
        return self.extract_all_syntax(max_files)

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description='Экстрактор синтаксиса BSL из файлов справки 1С')
    parser.add_argument('hbk_file', help='Путь к .hbk файлу')
    parser.add_argument('--max-files', type=int, default=1000, help='Максимальное количество файлов для обработки')
    parser.add_argument('--output', default='data/bsl_syntax.json', help='Путь к выходному JSON файлу')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.hbk_file):
        print(f"Файл не найден: {args.hbk_file}")
        sys.exit(1)
    
    extractor = BSLSyntaxExtractor(args.hbk_file)
    
    if not extractor.open_archive():
        sys.exit(1)
    
    try:
        # Извлекаем синтаксис
        print("=== Извлечение синтаксиса BSL ===")
        results = extractor.extract_all_syntax(max_files=args.max_files)
        
        # Выводим статистику
        print("\n=== Статистика ===")
        for category, count in results['statistics'].items():
            print(f"{category}: {count}")
        
        # Экспортируем результаты
        extractor.export_to_json(args.output)
        extractor.export_to_markdown(args.output.replace('.json', '.md'))
        
        # Поиск по паттерну
        print("\n=== Поиск по паттерну 'ВЫБРАТЬ' ===")
        select_results = extractor.find_by_pattern('ВЫБРАТЬ')
        print(f"Найдено {len(select_results)} элементов:")
        for result in select_results[:5]:  # Показываем первые 5
            print(f"- {result['title']} ({result['category']})")
        
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        extractor.close()
    
    print("Готово!")

if __name__ == "__main__":
    main() 