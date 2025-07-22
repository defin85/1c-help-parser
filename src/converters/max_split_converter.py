#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конвертер для создания максимальной версии в разбитом виде
Все элементы документации разбиваются на множественные файлы
"""

import os
import sys
from typing import Dict, List, Any
from .split_converter import SplitConverter

class MaxSplitConverter(SplitConverter):
    """Конвертер для максимальной версии в разбитом виде"""
    
    def convert(self) -> None:
        """Конвертирует максимальные данные в разбитом виде"""
        if not self.load_data():
            print("❌ Не удалось загрузить данные")
            return
        
        output_dir = "data/max_split"
        os.makedirs(output_dir, exist_ok=True)
        
        # Получаем все элементы
        all_items = self.data.get("context_items", [])
        print(f"📊 Разбиваем {len(all_items)} элементов на файлы...")
        print(f"⚙️  Настройки: max_file_size_kb={self.max_file_size_kb}, max_items_per_file={self.max_items_per_file}")
        
        # Экспортируем в разбитом виде
        self.export_split(all_items, output_dir)
        
        # Создаем общий индекс
        self.create_main_index(output_dir, all_items, "max_split")
        
        # Валидируем экспорт
        self.validate_export(output_dir)
        
        print(f"✅ Максимальный разбитый экспорт завершен: {output_dir}")
        
        # Показываем статистику
        self.show_statistics(output_dir, all_items)
    
    def show_statistics(self, output_dir: str, all_items: List[Dict]):
        """Показывает статистику созданных файлов"""
        categories = self.split_by_category(all_items)
        
        print(f"\n📈 Статистика экспорта:")
        print(f"   Всего элементов: {len(all_items)}")
        print(f"   Категорий: {len(categories)}")
        
        total_files = 0
        for category, items in categories.items():
            chunks = self.split_into_chunks(items)
            total_files += len(chunks)
            print(f"   {category}: {len(items)} элементов → {len(chunks)} файлов")
        
        print(f"   Всего файлов: {total_files}")
        print(f"   Директория: {output_dir}") 