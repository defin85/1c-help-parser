#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Базовый класс для всех парсеров 1С Help Parser
Содержит общую функциональность для работы с .hbk файлами
"""

import zipfile
import os
import sys
import re
from bs4 import BeautifulSoup
import json
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

class BaseParser(ABC):
    """Базовый класс для всех парсеров"""
    
    def __init__(self, hbk_file: str):
        self.hbk_file = hbk_file
        self.zip_file = None
        
    def open_archive(self) -> bool:
        """Открывает архив .hbk как ZIP"""
        try:
            self.zip_file = zipfile.ZipFile(self.hbk_file, 'r')
            return True
        except zipfile.BadZipFile:
            print(f"Ошибка: '{self.hbk_file}' не является корректным ZIP-архивом")
            return False
        except Exception as e:
            print(f"Ошибка при открытии архива: {e}")
            return False
    
    def list_contents(self) -> List[str]:
        """Возвращает список файлов в архиве"""
        if not self.zip_file:
            return []
        
        try:
            return self.zip_file.namelist()
        except Exception as e:
            print(f"Ошибка при получении списка файлов: {e}")
            return []
    
    def extract_file_content(self, filename: str) -> Optional[str]:
        """Извлекает содержимое файла из архива"""
        if not self.zip_file:
            return None
        
        try:
            with self.zip_file.open(filename, 'r') as f:
                content = f.read()
                # Пытаемся декодировать как UTF-8, если не получается - как cp1251
                try:
                    return content.decode('utf-8')
                except UnicodeDecodeError:
                    return content.decode('cp1251', errors='ignore')
        except Exception as e:
            print(f"Ошибка при извлечении файла {filename}: {e}")
            return None
    
    def extract_file(self, filename: str, extract_path: str = "extracted") -> Optional[str]:
        """Извлекает файл из архива на диск"""
        if not self.zip_file:
            return None
        
        try:
            os.makedirs(extract_path, exist_ok=True)
            self.zip_file.extract(filename, extract_path)
            return os.path.join(extract_path, filename)
        except Exception as e:
            print(f"Ошибка при извлечении файла {filename}: {e}")
            return None
    
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
    
    def parse_html_content(self, html_content: str) -> BeautifulSoup:
        """Парсит HTML-контент и возвращает BeautifulSoup объект"""
        try:
            return BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            print(f"Ошибка при парсинге HTML: {e}")
            return BeautifulSoup("", 'html.parser')
    
    def close(self):
        """Закрывает архив"""
        if self.zip_file:
            self.zip_file.close()
    
    @abstractmethod
    def parse(self, **kwargs) -> Dict[str, Any]:
        """Абстрактный метод для парсинга - должен быть реализован в наследниках"""
        pass 