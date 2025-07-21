#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсер файлов справки 1С (.hbk)
Поддерживает извлечение и анализ HTML-контента из архивов справки
"""

import os
import sys
import re
from bs4 import BeautifulSoup
import json
from typing import Dict, List, Optional, Any
try:
    from .base_parser import BaseParser
except ImportError:
    from base_parser import BaseParser

class HBKParser(BaseParser):
    """Парсер файлов справки 1С"""
    
    def __init__(self, hbk_file: str):
        super().__init__(hbk_file)
        self.structure = {}
    
    def parse_html_content(self, html_content: str) -> Dict[str, Any]:
        """Парсит HTML-контент и извлекает структурированную информацию"""
        try:
            soup = super().parse_html_content(html_content)
            
            result = {
                'title': '',
                'syntax': '',
                'fields': [],
                'description': '',
                'example': '',
                'links': []
            }
            
            # Извлекаем заголовок
            title_elem = soup.find('h1', class_='V8SH_pagetitle')
            if title_elem:
                result['title'] = title_elem.get_text(strip=True)
            
            # Извлекаем синтаксис
            syntax_elem = soup.find('p', class_='V8SH_chapter')
            if syntax_elem and 'Синтаксис' in syntax_elem.get_text():
                next_elem = syntax_elem.find_next_sibling()
                if next_elem:
                    result['syntax'] = next_elem.get_text(strip=True)
            
            # Извлекаем поля
            fields_section = soup.find('p', class_='V8SH_chapter')
            if fields_section and 'Поля' in fields_section.get_text():
                for link in fields_section.find_next_siblings('a'):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    if href and text:
                        result['fields'].append({
                            'name': text,
                            'link': href
                        })
            
            # Извлекаем описание
            desc_section = soup.find('p', class_='V8SH_chapter')
            if desc_section and 'Описание' in desc_section.get_text():
                desc_elem = desc_section.find_next_sibling('p')
                if desc_elem:
                    result['description'] = desc_elem.get_text(strip=True)
            
            # Извлекаем пример
            example_section = soup.find('p', class_='V8SH_chapter')
            if example_section and 'Пример' in example_section.get_text():
                table = example_section.find_next('table')
                if table:
                    result['example'] = table.get_text(strip=True)
            
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
            print(f"Ошибка при парсинге HTML: {e}")
            return {}
    
    def analyze_structure(self) -> Dict[str, Any]:
        """Анализирует структуру архива"""
        if not self.zip_file:
            return {}
        
        structure = {
            'total_files': 0,
            'html_files': 0,
            'st_files': 0,
            'categories': {},
            'file_types': {},
            'largest_files': []
        }
        
        try:
            file_list = self.zip_file.namelist()
            structure['total_files'] = len(file_list)
            
            # Анализируем файлы
            for filename in file_list:
                file_info = self.zip_file.getinfo(filename)
                
                # Подсчитываем типы файлов
                ext = os.path.splitext(filename)[1].lower()
                structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1
                
                if ext == '.html':
                    structure['html_files'] += 1
                elif ext == '.st':
                    structure['st_files'] += 1
                
                # Анализируем категории
                parts = filename.split('/')
                if len(parts) > 1:
                    category = parts[0]
                    structure['categories'][category] = structure['categories'].get(category, 0) + 1
                
                # Сохраняем информацию о крупных файлах
                if file_info.file_size > 10000:  # Больше 10KB
                    structure['largest_files'].append({
                        'name': filename,
                        'size': file_info.file_size,
                        'compressed_size': file_info.compress_size
                    })
            
            # Сортируем крупные файлы по размеру
            structure['largest_files'].sort(key=lambda x: x['size'], reverse=True)
            structure['largest_files'] = structure['largest_files'][:10]  # Топ 10
            
            return structure
            
        except Exception as e:
            print(f"Ошибка при анализе структуры: {e}")
            return {}
    
    def extract_sample_files(self, count: int = 5) -> List[Dict[str, Any]]:
        """Извлекает и анализирует несколько примеров файлов"""
        if not self.zip_file:
            return []
        
        samples = []
        html_files = [f for f in self.zip_file.namelist() if f.endswith('.html')]
        
        for i, filename in enumerate(html_files[:count]):
            try:
                # Читаем содержимое файла
                content = self.zip_file.read(filename).decode('utf-8', errors='ignore')
                
                # Парсим HTML
                parsed = self.parse_html_content(content)
                parsed['filename'] = filename
                
                samples.append(parsed)
                
            except Exception as e:
                print(f"Ошибка при обработке файла {filename}: {e}")
        
        return samples
    
    def parse(self, **kwargs) -> Dict[str, Any]:
        """Реализация абстрактного метода parse"""
        return self.analyze_structure()

def main():
    """Основная функция для тестирования парсера"""
    if len(sys.argv) != 2:
        print("Использование: python hbk_parser.py <путь_к_hbk_файлу>")
        sys.exit(1)
    
    hbk_file = sys.argv[1]
    
    if not os.path.exists(hbk_file):
        print(f"Файл не найден: {hbk_file}")
        sys.exit(1)
    
    parser = HBKParser(hbk_file)
    
    if not parser.open_archive():
        sys.exit(1)
    
    try:
        # Анализируем структуру
        print("=== Анализ структуры архива ===")
        structure = parser.analyze_structure()
        print(f"Всего файлов: {structure.get('total_files', 0)}")
        print(f"HTML файлов: {structure.get('html_files', 0)}")
        print(f"ST файлов: {structure.get('st_files', 0)}")
        
        print("\nТипы файлов:")
        for ext, count in structure.get('file_types', {}).items():
            print(f"  {ext}: {count}")
        
        print("\nКатегории:")
        for category, count in structure.get('categories', {}).items():
            print(f"  {category}: {count}")
        
        # Извлекаем примеры
        print("\n=== Примеры файлов ===")
        samples = parser.extract_sample_files(3)
        
        for i, sample in enumerate(samples, 1):
            print(f"\nПример {i}: {sample.get('filename', 'Unknown')}")
            print(f"Заголовок: {sample.get('title', 'N/A')}")
            print(f"Синтаксис: {sample.get('syntax', 'N/A')}")
            print(f"Поля: {len(sample.get('fields', []))}")
            print(f"Описание: {sample.get('description', 'N/A')[:100]}...")
        
        # Сохраняем результаты в JSON
        results = {
            'structure': structure,
            'samples': samples
        }
        
        with open('data/hbk_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\nРезультаты сохранены в data/hbk_analysis.json")
        
    finally:
        parser.close()

if __name__ == "__main__":
    main() 