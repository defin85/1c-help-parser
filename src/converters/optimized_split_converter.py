#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конвертер для создания оптимизированной версии в разбитом виде
Приоритетные элементы разбиваются на множественные файлы
"""

import os
import sys
from typing import Dict, List, Any
from .split_converter import SplitConverter

class OptimizedSplitConverter(SplitConverter):
    """Конвертер для оптимизированной версии в разбитом виде"""
    
    def convert(self) -> None:
        """Конвертирует оптимизированные данные в разбитом виде"""
        if not self.load_data():
            print("❌ Не удалось загрузить данные")
            return
        
        output_dir = "data/optimized_split"
        os.makedirs(output_dir, exist_ok=True)
        
        # Получаем все элементы и применяем оптимизацию
        all_items = self.data.get("context_items", [])
        optimized_items = self.optimize_data(all_items)
        
        print(f"📊 Разбиваем {len(optimized_items)} оптимизированных элементов на файлы...")
        print(f"⚙️  Настройки: max_file_size_kb={self.max_file_size_kb}, max_items_per_file={self.max_items_per_file}")
        
        # Экспортируем в разбитом виде
        self.export_split(optimized_items, output_dir, "optimized")
        
        # Создаем общий индекс
        self.create_main_index(output_dir, optimized_items, "optimized_split")
        
        # Валидируем экспорт
        self.validate_export(output_dir)
        
        print(f"✅ Оптимизированный разбитый экспорт завершен: {output_dir}")
        
        # Показываем статистику
        self.show_statistics(output_dir, optimized_items, all_items)
    
    def optimize_data(self, items: List[Dict]) -> List[Dict]:
        """Применяет оптимизацию как в OptimizedContextConverter"""
        print(f"🎯 Применяем оптимизацию к {len(items)} элементам...")
        
        # Приоритеты категорий (высокий -> низкий)
        priorities = {
            'methods': 1,
            'functions': 2, 
            'operators': 3,
            'objects': 4,
            'properties': 5
        }
        
        # Максимальное количество элементов по категориям
        limits = {
            'methods': 200,
            'functions': 300,
            'operators': 50,
            'objects': 500,
            'properties': 200
        }
        
        # Сортируем элементы по важности
        sorted_items = self._sort_by_importance(items)
        
        # Выбираем элементы по лимитам
        selected_items = []
        category_counts = {}
        
        for item in sorted_items:
            category = item.get('category', 'other')
            if category not in category_counts:
                category_counts[category] = 0
            
            if category_counts[category] < limits.get(category, 100):
                selected_items.append(item)
                category_counts[category] += 1
        
        print(f"✅ Оптимизация завершена: выбрано {len(selected_items)} элементов")
        for category, count in category_counts.items():
            print(f"   {category}: {count} элементов")
        
        return selected_items
    
    def _sort_by_importance(self, items: List[Dict]) -> List[Dict]:
        """Сортирует элементы по важности"""
        def score_item(item):
            score = 0
            metadata = item.get('metadata', {})
            
            # Методы и функции важнее
            if item.get('category') in ['methods', 'functions']:
                score += 100
            
            # Наличие синтаксиса
            if metadata.get('syntax') or metadata.get('syntax_variants'):
                score += 50
            
            # Наличие параметров
            if metadata.get('parameters') or metadata.get('parameters_by_variant'):
                score += 30
            
            # Наличие примеров
            if metadata.get('example'):
                score += 20
            
            # Наличие методов
            if metadata.get('methods'):
                score += len(metadata['methods']) * 10
            
            # Длина описания
            content = item.get('content', '')
            if len(content) > 50:
                score += 10
            
            return score
        
        return sorted(items, key=score_item, reverse=True)
    
    def show_statistics(self, output_dir: str, optimized_items: List[Dict], all_items: List[Dict]):
        """Показывает статистику созданных файлов"""
        categories = self.split_by_category(optimized_items)
        
        print(f"\n📈 Статистика экспорта:")
        print(f"   Исходных элементов: {len(all_items)}")
        print(f"   Оптимизированных элементов: {len(optimized_items)}")
        print(f"   Сжатие: {len(optimized_items)/len(all_items)*100:.1f}%")
        print(f"   Категорий: {len(categories)}")
        
        total_files = 0
        for category, items in categories.items():
            chunks = self.split_into_chunks(items)
            total_files += len(chunks)
            print(f"   {category}: {len(items)} элементов → {len(chunks)} файлов")
        
        print(f"   Всего файлов: {total_files}")
        print(f"   Директория: {output_dir}") 