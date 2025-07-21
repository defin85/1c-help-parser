#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация использования context файлов 1С с LLM
Показывает как загружать и использовать контекст для ответов на вопросы
"""

import json
import os
import sys
from typing import List, Dict, Any, Optional
import re

class LLMContextDemo:
    """Демонстрация работы с context файлами для LLM"""
    
    def __init__(self, context_file: str):
        self.context_file = context_file
        self.context_data = []
        self.search_index = {}
        
    def load_context(self) -> bool:
        """Загружает контекст из JSON файла"""
        try:
            with open(self.context_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.context_data = data.get('context_items', [])
            
            print(f"Загружено {len(self.context_data)} элементов контекста")
            return True
        except Exception as e:
            print(f"Ошибка при загрузке контекста: {e}")
            return False
    
    def load_search_index(self, index_file: str) -> bool:
        """Загружает поисковый индекс"""
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.search_index = data.get('index', {})
            
            print(f"Загружен поисковый индекс с {len(self.search_index)} ключевыми словами")
            return True
        except Exception as e:
            print(f"Ошибка при загрузке индекса: {e}")
            return False
    
    def search_context(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Ищет релевантный контекст по запросу"""
        query_words = re.findall(r'\b\w+\b', query.lower())
        relevant_items = []
        
        for item in self.context_data:
            score = 0
            title = item['title'].lower()
            content = item['content'].lower()
            
            # Подсчитываем релевантность
            for word in query_words:
                if len(word) > 2:  # Игнорируем короткие слова
                    if word in title:
                        score += 3  # Высокий вес для заголовка
                    if word in content:
                        score += 1  # Низкий вес для содержимого
            
            if score > 0:
                relevant_items.append({
                    'item': item,
                    'score': score
                })
        
        # Сортируем по релевантности
        relevant_items.sort(key=lambda x: x['score'], reverse=True)
        
        return [item['item'] for item in relevant_items[:max_results]]
    
    def generate_response(self, question: str) -> str:
        """Генерирует ответ на основе контекста (демонстрация)"""
        print(f"\nВопрос: {question}")
        
        # Ищем релевантный контекст
        relevant_context = self.search_context(question, max_results=3)
        
        if not relevant_context:
            return "Извините, не нашел релевантной информации в документации 1С."
        
        # Формируем ответ
        response_parts = []
        response_parts.append("На основе документации 1С:\n")
        
        for i, context_item in enumerate(relevant_context, 1):
            response_parts.append(f"{i}. **{context_item['title']}**")
            
            if context_item['metadata']['syntax']:
                response_parts.append(f"   Синтаксис: `{context_item['metadata']['syntax']}`")
            
            # Извлекаем описание из content
            content = context_item['content']
            description_match = re.search(r'## Описание\n(.*?)(?=\n##|\n---|\n$)', content, re.DOTALL)
            if description_match:
                description = description_match.group(1).strip()
                if len(description) > 200:
                    description = description[:200] + "..."
                response_parts.append(f"   Описание: {description}")
            
            response_parts.append("")
        
        response_parts.append("Это информация из официальной документации 1С:Предприятие.")
        
        return '\n'.join(response_parts)
    
    def interactive_mode(self):
        """Интерактивный режим для тестирования"""
        print("\n=== Интерактивный режим ===")
        print("Задавайте вопросы о 1С, нажмите Ctrl+C для выхода")
        print("Примеры вопросов:")
        print("- Как использовать ВЫБРАТЬ в 1С?")
        print("- Что такое ДинамическийСписок?")
        print("- Как работать с формами в 1С?")
        print()
        
        try:
            while True:
                question = input("Ваш вопрос: ").strip()
                if question:
                    response = self.generate_response(question)
                    print(response)
                    print("\n" + "="*60 + "\n")
        except KeyboardInterrupt:
            print("\n\nДо свидания!")
    
    def demo_questions(self):
        """Демонстрирует ответы на типичные вопросы"""
        demo_questions = [
            "Что такое ДинамическийСписок?",
            "Как работать с формами в 1С?",
            "Что такое ДанныеФормы?",
            "Как использовать коллекции в 1С?",
            "Что такое глобальный контекст?"
        ]
        
        print("=== Демонстрация ответов ===")
        
        for question in demo_questions:
            response = self.generate_response(question)
            print(response)
            print("\n" + "="*60 + "\n")

def main():
    """Основная функция"""
    if len(sys.argv) < 2:
        print("Использование: python llm_context_demo.py <путь_к_1c_context.json> [интерактивный]")
        sys.exit(1)
    
    context_file = sys.argv[1]
    interactive = len(sys.argv) > 2 and sys.argv[2] == "интерактивный"
    
    if not os.path.exists(context_file):
        print(f"Файл не найден: {context_file}")
        sys.exit(1)
    
    demo = LLMContextDemo(context_file)
    
    if not demo.load_context():
        sys.exit(1)
    
    # Загружаем поисковый индекс если есть
    index_file = "1c_search_index.json"
    if os.path.exists(index_file):
        demo.load_search_index(index_file)
    
    if interactive:
        demo.interactive_mode()
    else:
        demo.demo_questions()

if __name__ == "__main__":
    main() 