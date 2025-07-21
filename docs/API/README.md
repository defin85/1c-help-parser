# 📚 API Документация

## 🏗️ Архитектура проекта

### Модульная структура

```
src/
├── parsers/           # Парсеры для извлечения данных
├── converters/        # Конвертеры для преобразования форматов
├── demos/             # Демонстрации и примеры использования
└── __init__.py        # Основной модуль
```

## 🔍 Парсеры (src/parsers/)

### HBKParser

**Назначение:** Парсинг .hbk архивов и анализ их структуры

**Основные методы:**
- `analyze_archive(zip_file)` - анализ структуры архива
- `extract_file_info(html_content)` - извлечение информации из HTML
- `categorize_files(files)` - категоризация файлов

**Использование:**
```python
from src.parsers import HBKParser

parser = HBKParser()
results = parser.analyze_archive("data/rebuilt.shcntx_ru.zip")
```

### BSLSyntaxExtractor

**Назначение:** Извлечение синтаксиса BSL из HTML файлов

**Основные методы:**
- `extract_all_syntax(zip_file, max_files=500)` - извлечение всего синтаксиса
- `extract_syntax_from_html(html_content)` - извлечение из HTML
- `export_to_json(filename)` - экспорт в JSON

**Использование:**
```python
from src.parsers import BSLSyntaxExtractor

extractor = BSLSyntaxExtractor()
extractor.extract_all_syntax("data/rebuilt.shcntx_ru.zip")
extractor.export_to_json("data/bsl_syntax.json")
```

## 🔄 Конвертеры (src/converters/)

### ContextConverter

**Назначение:** Базовый конвертер для создания LLM контекста

**Основные методы:**
- `convert_to_context()` - конвертация в контекст
- `export_context_json(filename)` - экспорт в JSON
- `export_context_text(filename)` - экспорт в текст
- `create_search_index(filename)` - создание поискового индекса

**Использование:**
```python
from src.converters import ContextConverter

converter = ContextConverter("data/bsl_syntax.json")
converter.convert_to_context()
converter.export_context_json("data/1c_context.json")
```

### OptimizedContextConverter

**Назначение:** Оптимизированный конвертер с критически важными полями

**Основные методы:**
- `convert_to_optimized_context()` - конвертация в оптимизированный формат
- `extract_availability(content)` - извлечение информации о доступности
- `extract_version(content)` - извлечение информации о версии
- `extract_parameters(content)` - извлечение параметров
- `create_search_index(items)` - создание оптимизированного индекса

**Использование:**
```python
from src.converters import OptimizedContextConverter

converter = OptimizedContextConverter("data/bsl_syntax.json")
converter.export_optimized_context("data/1c_context_optimized.json")
```

## 🎯 Демонстрации (src/demos/)

### OptimizedContextDemo

**Назначение:** Демонстрация оптимизированного контекста

**Основные методы:**
- `search_by_keyword(keyword)` - поиск по ключевому слову
- `search_by_availability(availability)` - поиск по доступности
- `search_by_version(version)` - поиск по версии
- `search_by_category(category)` - поиск по категории
- `interactive_search()` - интерактивный поиск

**Использование:**
```python
from src.demos import OptimizedContextDemo

demo = OptimizedContextDemo("data/1c_context_optimized.json")
demo.load_context()
results = demo.search_by_keyword("форма")
```

### LLMContextDemo

**Назначение:** Демонстрация основного контекста

**Основные методы:**
- `load_context()` - загрузка контекста
- `search_context(query)` - поиск в контексте
- `generate_answer(query, results)` - генерация ответа

**Использование:**
```python
from src.demos import LLMContextDemo

demo = LLMContextDemo("data/1c_context.json")
demo.load_context()
results = demo.search_context("ДинамическийСписок")
```

## 📊 Форматы данных

### Оптимизированный контекст (1c_context_optimized.json)

```json
{
  "metadata": {
    "source": "1C BSL Documentation",
    "generated_at": "2025-07-21T20:17:21.782634",
    "total_items": 474,
    "format": "optimized"
  },
  "items": [
    {
      "id": "уникальный_id",
      "title": "название",
      "syntax": "синтаксис",
      "description": "описание",
      "parameters": [...],
      "return_value": "возвращаемое_значение",
      "availability": ["Клиент", "Сервер"],
      "version": "8.0+",
      "category": "objects|methods|functions|operators"
    }
  ],
  "search": {
    "ключ": ["id1", "id2", ...]
  }
}
```

### Базовый контекст (1c_context.json)

```json
{
  "metadata": {
    "source": "1C BSL Documentation",
    "generated_at": "2025-07-21T20:17:21.782634",
    "total_items": 474,
    "categories": ["objects", "properties"]
  },
  "context_items": [
    {
      "id": "objects_0",
      "title": "Глобальный контекст",
      "category": "objects",
      "content": "# Глобальный контекст\n\n## Описание\n...",
      "metadata": {
        "filename": "objects/catalog125.html",
        "syntax": "",
        "parameters": [],
        "return_value": "",
        "links": []
      }
    }
  ]
}
```

## 🚀 Примеры интеграции

### Создание полного пайплайна

```python
from src.parsers import HBKParser, BSLSyntaxExtractor
from src.converters import OptimizedContextConverter
from src.demos import OptimizedContextDemo

# 1. Анализ архива
parser = HBKParser()
parser.analyze_archive("data/rebuilt.shcntx_ru.zip")

# 2. Извлечение синтаксиса
extractor = BSLSyntaxExtractor()
extractor.extract_all_syntax("data/rebuilt.shcntx_ru.zip")
extractor.export_to_json("data/bsl_syntax.json")

# 3. Создание оптимизированного контекста
converter = OptimizedContextConverter("data/bsl_syntax.json")
converter.export_optimized_context("data/1c_context_optimized.json")

# 4. Демонстрация
demo = OptimizedContextDemo("data/1c_context_optimized.json")
demo.load_context()
demo.interactive_search()
```

### Интеграция с LLM

```python
from src.demos import OptimizedContextDemo

class LLMHelper:
    def __init__(self, context_file):
        self.demo = OptimizedContextDemo(context_file)
        self.demo.load_context()
    
    def answer_question(self, question):
        # Поиск релевантной информации
        results = self.demo.search_by_keyword(question)
        
        if not results:
            return "Извините, не нашел информации по вашему вопросу."
        
        # Формирование ответа
        answer = f"Найдена информация по запросу '{question}':\n\n"
        for result in results[:3]:
            answer += f"**{result['title']}**\n"
            answer += f"Описание: {result.get('description', 'Нет описания')}\n"
            answer += f"Доступность: {', '.join(result.get('availability', []))}\n\n"
        
        return answer

# Использование
helper = LLMHelper("data/1c_context_optimized.json")
answer = helper.answer_question("Что такое ТаблицаЗначений?")
print(answer)
``` 