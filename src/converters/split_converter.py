#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Базовый класс для разбивки данных на множественные файлы
Оптимизирован для Cursor IDE и других редакторов
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base_converter import BaseConverter
from abc import abstractmethod

class SplitConverter(BaseConverter):
    """Базовый класс для разбивки данных на множественные файлы"""
    
    def __init__(self, input_file: str, max_file_size_kb: int = 50, max_items_per_file: int = 50, verbose: bool = False):
        super().__init__(input_file, verbose)
        self.max_file_size_kb = max_file_size_kb
        self.max_items_per_file = max_items_per_file
    
    def split_by_category(self, data: List[Dict]) -> Dict[str, List[Dict]]:
        """Разбивает данные по категориям"""
        categories = {}
        for item in data:
            category = item.get('category', 'other')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        return categories
    
    def split_into_chunks(self, items: List[Dict]) -> List[List[Dict]]:
        """Разбивает элементы на чанки по размеру и количеству"""
        chunks = []
        current_chunk = []
        current_size = 0
        
        for item in items:
            item_size = len(json.dumps(item, ensure_ascii=False))
            
            # Проверяем лимиты
            if (len(current_chunk) >= self.max_items_per_file or 
                current_size + item_size > self.max_file_size_kb * 1024):
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = []
                    current_size = 0
            
            current_chunk.append(item)
            current_size += item_size
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def export_split(self, data: List[Dict], output_dir: str, prefix: str = ""):
        """Экспортирует данные в разбитом виде"""
        categories = self.split_by_category(data)
        
        for category, items in categories.items():
            category_dir = os.path.join(output_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            
            chunks = self.split_into_chunks(items)
            
            for i, chunk in enumerate(chunks):
                filename = f"{category}_{i+1:03d}.json"
                if prefix:
                    filename = f"{prefix}_{filename}"
                
                filepath = os.path.join(category_dir, filename)
                self.export_json({"items": chunk, "metadata": {
                    "category": category,
                    "chunk": i+1,
                    "total_chunks": len(chunks),
                    "items_count": len(chunk),
                    "created_at": datetime.now().isoformat()
                }}, filepath)
            
            # Создаем индекс для категории
            index_file = os.path.join(category_dir, f"{category}_index.json")
            self.export_json({
                "category": category,
                "total_items": len(items),
                "total_chunks": len(chunks),
                "chunks": [f"{category}_{i+1:03d}.json" for i in range(len(chunks))],
                "created_at": datetime.now().isoformat()
            }, index_file)
        
        # Показываем сводку экспорта (если не verbose режим)
        if not self.verbose:
            self.show_export_summary()
    
    def create_main_index(self, output_dir: str, all_items: List[Dict], mode: str):
        """Создает общий индекс всех файлов"""
        categories = self.split_by_category(all_items)
        
        index = {
            "total_items": len(all_items),
            "categories": {},
            "created_at": datetime.now().isoformat(),
            "mode": mode,
            "settings": {
                "max_file_size_kb": self.max_file_size_kb,
                "max_items_per_file": self.max_items_per_file
            }
        }
        
        for category, items in categories.items():
            chunks = self.split_into_chunks(items)
            index["categories"][category] = {
                "items_count": len(items),
                "chunks_count": len(chunks),
                "files": [f"{category}_{i+1:03d}.json" for i in range(len(chunks))]
            }
        
        index_file = os.path.join(output_dir, "main_index.json")
        self.export_json(index, index_file)
    
    def validate_export(self, output_dir: str):
        """Проверяет созданные файлы на соответствие лимитам с группировкой предупреждений"""
        print(f"🔍 Валидация экспорта в {output_dir}...")
        
        # Статистика для группировки
        total_files = 0
        valid_files = 0
        size_warnings = []
        lines_warnings = []
        
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith('.json') and not file.endswith('_index.json'):
                    file_path = os.path.join(root, file)
                    size_kb = os.path.getsize(file_path) / 1024
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                    
                    total_files += 1
                    
                    # Проверяем лимиты
                    if size_kb > self.max_file_size_kb:
                        size_warnings.append((file_path, size_kb))
                    elif lines > 500:
                        lines_warnings.append((file_path, lines))
                    else:
                        valid_files += 1
        
        # Выводим общую статистику
        print(f"📊 Статистика валидации:")
        print(f"   Всего файлов: {total_files}")
        print(f"   ✅ Валидных: {valid_files}")
        print(f"   ⚠️  Превышение размера: {len(size_warnings)}")
        print(f"   ⚠️  Превышение строк: {len(lines_warnings)}")
        
        # Группируем предупреждения по категориям
        if size_warnings:
            print(f"\n⚠️  Файлы с превышением размера ({self.max_file_size_kb}KB):")
            self._group_warnings(size_warnings, "размер", lambda x: x[1])
        
        if lines_warnings:
            print(f"\n⚠️  Файлы с превышением строк (500):")
            self._group_warnings(lines_warnings, "строки", lambda x: x[1])
        
        if not size_warnings and not lines_warnings:
            print(f"✅ Все файлы соответствуют лимитам!")
    
    def _group_warnings(self, warnings: List[tuple], warning_type: str, value_extractor):
        """Группирует предупреждения по категориям и диапазонам"""
        if not warnings:
            return
        
        # Группируем по категориям
        categories = {}
        for file_path, value in warnings:
            category = file_path.split(os.sep)[-2] if len(file_path.split(os.sep)) > 1 else "unknown"
            if category not in categories:
                categories[category] = []
            categories[category].append((file_path, value))
        
        # Выводим по категориям
        for category, items in sorted(categories.items()):
            print(f"   📁 {category}: {len(items)} файлов")
            
            # Группируем по диапазонам значений
            ranges = self._group_by_ranges(items, value_extractor)
            for range_name, range_items in ranges.items():
                if len(range_items) <= 3:
                    # Показываем все файлы если их мало
                    for file_path, value in range_items:
                        filename = os.path.basename(file_path)
                        print(f"      {filename}: {value:.1f}{'KB' if warning_type == 'размер' else ''}")
                else:
                    # Показываем статистику если файлов много
                    avg_value = sum(value_extractor(item) for item in range_items) / len(range_items)
                    print(f"      {range_name}: {len(range_items)} файлов (среднее: {avg_value:.1f}{'KB' if warning_type == 'размер' else ''})")
    
    def _group_by_ranges(self, items: List[tuple], value_extractor) -> Dict[str, List[tuple]]:
        """Группирует элементы по диапазонам значений"""
        ranges = {
            "50-60": [],
            "60-70": [],
            "70-80": [],
            "80-90": [],
            "90+": []
        }
        
        for item in items:
            value = value_extractor(item)
            if value <= 60:
                ranges["50-60"].append(item)
            elif value <= 70:
                ranges["60-70"].append(item)
            elif value <= 80:
                ranges["70-80"].append(item)
            elif value <= 90:
                ranges["80-90"].append(item)
            else:
                ranges["90+"].append(item)
        
        # Убираем пустые диапазоны
        return {k: v for k, v in ranges.items() if v}
    
    @abstractmethod
    def convert(self) -> None:
        """Абстрактный метод для конвертации - должен быть реализован в наследниках"""
        pass 