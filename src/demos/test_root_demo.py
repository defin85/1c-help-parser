#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from typing import Dict, List, Any

def load_context(context_file: str) -> Dict[str, Any]:
    """Загружает контекст из JSON файла"""
    try:
        with open(context_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки контекста: {e}")
        return {}

def load_search_index(index_file: str) -> Dict[str, Any]:
    """Загружает поисковый индекс"""
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки индекса: {e}")
        return {}

def search_context(query: str, context: Dict[str, Any], search_index: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Ищет релевантную информацию в контексте"""
    query_lower = query.lower()
    results = []
    
    # Поиск по индексу
    for keyword, item_ids in search_index.get('index', {}).items():
        if query_lower in keyword or keyword in query_lower:
            for item_id in item_ids:
                # Находим элемент в контексте
                for item in context.get('context_items', []):
                    if item['id'] == item_id:
                        results.append(item)
                        break
    
    # Прямой поиск по заголовкам и содержимому
    for item in context.get('context_items', []):
        title_lower = item.get('title', '').lower()
        content_lower = item.get('content', '').lower()
        
        if (query_lower in title_lower or 
            query_lower in content_lower or
            any(word in title_lower for word in query_lower.split())):
            if item not in results:
                results.append(item)
    
    return results[:5]  # Возвращаем топ-5 результатов

def generate_answer(query: str, results: List[Dict[str, Any]]) -> str:
    """Генерирует ответ на основе найденных результатов"""
    if not results:
        return f"Извините, не нашел релевантной информации по запросу '{query}' в документации 1С."
    
    answer = f"Найдена информация по запросу '{query}':\n\n"
    
    for i, result in enumerate(results, 1):
        answer += f"{i}. **{result.get('title', 'Без названия')}**\n"
        answer += f"   Категория: {result.get('category', 'Неизвестно')}\n"
        
        content = result.get('content', '')
        if content and content != f"# {result.get('title', '')}":
            # Берем первые 200 символов описания
            desc = content.replace(f"# {result.get('title', '')}", "").strip()
            if desc:
                answer += f"   Описание: {desc[:200]}...\n"
        
        # Добавляем ссылки
        links = result.get('metadata', {}).get('links', [])
        if links:
            answer += f"   Связанные элементы: {', '.join([link.get('text', '') for link in links[:3]])}\n"
        
        answer += "\n"
    
    return answer

def main():
    if len(sys.argv) != 2:
        print("Использование: python test_root_demo.py <путь_к_1c_context.json>")
        return
    
    context_file = sys.argv[1]
    index_file = context_file.replace('1c_context.json', '1c_search_index.json')
    
    # Загружаем данные
    context = load_context(context_file)
    search_index = load_search_index(index_file)
    
    if not context or not search_index:
        print("Не удалось загрузить данные")
        return
    
    print(f"Загружено {len(context.get('context_items', []))} элементов контекста")
    print(f"Загружен поисковый индекс с {len(search_index.get('index', {}))} ключевыми словами")
    print("=== Демонстрация ответов ===\n")
    
    # Тестовые вопросы на английском
    test_questions = [
        "What is FormDataStructure?",
        "How to work with forms?",
        "What is Global context?",
        "What is DynamicList?",
        "What is ClientApplicationForm?",
        "What is Interface?",
        "What is Applied objects?",
        "What is Form data?"
    ]
    
    for question in test_questions:
        print(f"Вопрос: {question}")
        results = search_context(question, context, search_index)
        answer = generate_answer(question, results)
        print(answer)
        print("=" * 60 + "\n")

if __name__ == "__main__":
    main() 