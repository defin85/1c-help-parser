#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Базовый класс для всех конвертеров 1C Help Parser
Содержит общую функциональность для конвертации данных в различные форматы
"""

import json
import os
import sys
import re
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime

class BaseConverter(ABC):
    """Базовый класс для всех конвертеров"""
    
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.data = {}
        
    def load_data(self) -> bool:
        """Загружает данные из JSON файла"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"Загружено {len(self.data)} элементов данных")
            return True
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            return False
    
    def clean_text(self, text: str) -> str:
        """Очищает текст от лишних символов и форматирования"""
        if not text:
            return ""
        
        # Удаляем лишние пробелы и переносы строк
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Удаляем HTML-теги
        text = re.sub(r'<[^>]+>', '', text)
        
        return text
    
    def ensure_directory(self, filepath: str) -> None:
        """Создает директорию для файла, если она не существует"""
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    def export_json(self, data: Dict[str, Any], filename: str) -> None:
        """Экспортирует данные в JSON файл"""
        try:
            self.ensure_directory(filename)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Данные экспортированы в {filename}")
        except Exception as e:
            print(f"Ошибка при экспорте в JSON: {e}")
    
    def export_text(self, data: str, filename: str) -> None:
        """Экспортирует данные в текстовый файл"""
        try:
            self.ensure_directory(filename)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(data)
            print(f"Данные экспортированы в {filename}")
        except Exception as e:
            print(f"Ошибка при экспорте в текст: {e}")
    
    def create_search_index(self, items: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Создает поисковый индекс по ключевым словам"""
        search_index = {}
        
        for item in items:
            # Извлекаем ключевые слова из заголовка и содержимого
            title = item.get('title', '').lower()
            content = item.get('content', '').lower()
            
            # Разбиваем на слова
            words = re.findall(r'\b\w+\b', f"{title} {content}")
            
            # Добавляем в индекс
            for word in words:
                if len(word) > 2:  # Игнорируем короткие слова
                    if word not in search_index:
                        search_index[word] = []
                    if item.get('id') not in search_index[word]:
                        search_index[word].append(item.get('id'))
        
        return search_index
    
    @abstractmethod
    def convert(self) -> None:
        """Абстрактный метод для конвертации - должен быть реализован в наследниках"""
        pass 