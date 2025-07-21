# Парсер документации 1С для LLM Context

Этот проект позволяет извлекать документацию из файлов справки 1С (`.hbk`) и преобразовывать её в формат, удобный для использования с языковыми моделями (LLM).

## Возможности

- ✅ Извлечение HTML-документации из `.hbk` файлов через WinRAR
- ✅ Парсинг структурированной информации о синтаксисе BSL
- ✅ Конвертация в различные форматы для LLM
- ✅ Создание поискового индекса
- ✅ Демонстрация использования с LLM

## Структура проекта

```
1c-help-parser/
├── src/
│   ├── parsers/
│   │   ├── hbk_parser.py              # Базовый парсер .hbk файлов
│   │   └── bsl_syntax_extractor.py    # Экстрактор синтаксиса BSL
│   ├── converters/
│   │   ├── context_converter.py       # Базовый конвертер
│   │   └── optimized_context_converter.py # Оптимизированный конвертер
│   └── demos/
│       ├── llm_context_demo.py        # Демонстрация использования
│       ├── optimized_demo.py          # Демо оптимизированного контекста
│       └── optimized_demo.py          # Демо оптимизированного контекста
├── data/
│   ├── rebuilt.shcntx_ru.zip          # Восстановленный архив (38MB)
│   ├── 1c_context_optimized.json      # Оптимизированный контекст (5.2MB)
│   └── hbk_analysis.json              # Анализ структуры (2KB)
└── run.py                             # Главный скрипт
```

## Быстрый старт

### 1. Извлечение документации из .hbk файла

```bash
# Анализ структуры архива
python src/parsers/hbk_parser.py data/rebuilt.shcntx_ru.zip

# Извлечение синтаксиса BSL
python src/parsers/bsl_syntax_extractor.py data/rebuilt.shcntx_ru.zip
```

### 2. Конвертация в формат context

```bash
# Создание оптимизированного контекста (рекомендуется)
python src/converters/optimized_context_converter.py data/bsl_syntax.json


```

### 3. Демонстрация использования

```bash
# Демонстрация оптимизированного контекста
python src/demos/optimized_demo.py data/1c_context_optimized.json



# Или через главный скрипт
python run.py --demo data/1c_context_optimized.json
```

## Форматы файлов

### 1. JSON Context (`1c_context.json`)
Структурированный формат с разделением на content и metadata:

```json
{
  "metadata": {
    "source": "1C BSL Documentation",
    "generated_at": "2025-07-20T23:51:35.129026",
    "total_items": 474,
    "categories": ["objects", "properties"]
  },
  "context_items": [
    {
      "id": "objects_0",
      "title": "Глобальный контекст",
      "category": "objects",
      "content": "Краткое описание объекта",
      "metadata": {
        "filename": "objects/catalog125.html",
        "syntax": "",
        "syntax_variants": [],
        "parameters": [],
        "parameters_by_variant": {},
        "return_value": "",
        "example": "",
        "links": [],
        "collection_elements": {},
        "methods": [],
        "availability": [],
        "version": ""
      }
    }
  ]
}
```

### 2. Текстовый Context (`1c_context.txt`)
Плоский текстовый формат для LLM:

```
# Документация синтаксиса 1С (BSL)

Этот файл содержит документацию по синтаксису языка 1С:Предприятие.
Используйте эту информацию для ответов на вопросы о программировании в 1С.

================================================================================

# Глобальный контекст

## Описание
Глобальный контекст инициализируется при открытии конфигурации...
```

### 3. Поисковый индекс (`1c_search_index.json`)
Быстрый поиск по ключевым словам:

```json
{
  "metadata": {
    "source": "1C BSL Documentation",
    "generated_at": "2025-07-20T23:51:35.129026",
    "total_items": 474
  },
  "index": {
    "форма": ["objects_1", "objects_2", ...],
    "динамическийсписок": ["objects_10", "objects_11", ...],
    "выбрать": ["objects_50", "objects_51", ...]
  }
}
```

## Использование с LLM

### Пример интеграции с OpenAI API

```python
import json
import openai
from llm_context_demo import LLMContextDemo

# Загружаем контекст
demo = LLMContextDemo('1c_context.json')
demo.load_context()

# Функция для получения ответа с контекстом
def get_1c_answer(question: str) -> str:
    # Ищем релевантный контекст
    relevant_context = demo.search_context(question, max_results=3)
    
    # Формируем промпт с контекстом
    context_text = "\n\n".join([item['content'] for item in relevant_context])
    
    prompt = f"""
    Контекст из документации 1С:
    {context_text}
    
    Вопрос: {question}
    
    Ответь на основе предоставленной документации 1С:Предприятие.
    """
    
    # Отправляем запрос к LLM
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

# Пример использования
answer = get_1c_answer("Как использовать ВЫБРАТЬ в 1С?")
print(answer)
```

### Пример с локальной моделью

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Загружаем модель
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

def get_local_answer(question: str, context: str) -> str:
    # Формируем промпт
    prompt = f"Context: {context}\nQuestion: {question}\nAnswer:"
    
    # Токенизируем
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    
    # Генерируем ответ
    with torch.no_grad():
        outputs = model.generate(
            inputs, 
            max_length=200, 
            num_return_sequences=1,
            temperature=0.7
        )
    
    # Декодируем
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.split("Answer:")[-1].strip()
```

## Статистика извлеченной документации

Из файла `rebuilt.shcntx_ru.zip` (38MB) извлечено:

- **51,065 файлов** всего
- **24,979 HTML файлов** с документацией
- **22,284 ST файлов** с метаданными
- **474 элемента** с описанием синтаксиса
- **526 ключевых слов** в поисковом индексе

### Категории документации:
- **466 объектов** - основные объекты платформы 1С
- **8 свойств** - свойства объектов

### Топ-10 ключевых слов:
1. `form` (247 упоминаний)
2. `формы` (243 упоминания)
3. `расширение` (240 упоминаний)
4. `клиентского` (238 упоминаний)
5. `приложения` (238 упоминаний)

## Требования

- Python 3.7+
- BeautifulSoup4 (`pip install beautifulsoup4`)
- WinRAR (для восстановления .hbk файлов)

## Лицензия

Проект создан для образовательных целей. Документация 1С является собственностью фирмы "1С".

## Поддержка

Для вопросов и предложений создавайте issues в репозитории проекта. 