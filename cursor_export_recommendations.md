# Рекомендации по доработке 1c-help-parser для Cursor

## Проблема

Текущий парсер создает файлы, которые слишком большие для индексации в Cursor:
- `1c_context.json` - 42MB, 1M+ строк
- `1c_search_index.json` - 7MB, 313K строк  
- `1c_context_optimized.json` - 5.2MB, 118K строк

**Ограничения Cursor:**
- Максимум 400 строк на файл для редактирования
- Рекомендуется <50KB на файл для индексации
- Максимум ~1MB текста для @ ссылок

## Решение: Режим экспорта для Cursor

### 1. Добавить новый режим экспорта

```python
# Новый режим экспорта: cursor_mode
def export_for_cursor(data, output_dir):
    """
    Экспорт данных в формате, оптимизированном для Cursor/VS Code
    - Разбивка по категориям
    - Ограничение размера файлов (max 50KB, 500 строк)
    - Структурированные JSON файлы
    """
    categories = group_by_category(data)
    
    for category, items in categories.items():
        # Разбиваем большие категории на части
        chunks = split_into_chunks(items, max_items=50, max_size_kb=50)
        
        for i, chunk in enumerate(chunks):
            filename = f"{category}_{i+1:03d}.json"
            export_chunk(chunk, output_dir / filename)
```

### 2. Структура выходных файлов

```
docs_search/
├── cursor_export/
│   ├── functions/
│   │   ├── functions_001.json (50 элементов)
│   │   ├── functions_002.json (50 элементов)
│   │   └── functions_index.json (оглавление)
│   ├── objects/
│   │   ├── objects_001.json (50 элементов)
│   │   ├── objects_002.json (50 элементов)
│   │   └── ...
│   ├── methods/
│   │   └── methods_001.json (все методы)
│   ├── properties/
│   │   └── properties_001.json (все свойства)
│   └── operators/
│       └── operators_001.json (все операторы)
```

### 3. Оптимизация содержимого файлов

```python
def optimize_for_cursor(item):
    """
    Оптимизация элемента для Cursor:
    - Сокращение описаний до 200-300 символов
    - Удаление HTML-тегов
    - Структурированные метаданные
    """
    return {
        "id": item["id"],
        "title": item["title"],
        "category": item["category"],
        "summary": truncate_content(item["content"], 300),
        "full_content": item["content"],  # для детального поиска
        "keywords": extract_keywords(item["content"]),
        "related": find_related_items(item)
    }
```

### 4. Создание поискового индекса

```python
def create_cursor_search_index(data):
    """
    Создание легкого поискового индекса для быстрого поиска
    """
    index = {
        "functions": {},
        "objects": {},
        "methods": {},
        "properties": {},
        "operators": {}
    }
    
    for item in data:
        category = item["category"]
        if category not in index:
            continue
            
        # Индексируем по ключевым словам
        keywords = extract_keywords(item["title"] + " " + item["content"])
        for keyword in keywords:
            if keyword not in index[category]:
                index[category][keyword] = []
            index[category][keyword].append(item["id"])
    
    return index
```

### 5. Конфигурация экспорта

```yaml
# config.yaml
cursor_export:
  max_file_size_kb: 50
  max_items_per_file: 50
  max_content_length: 300
  categories:
    - functions
    - objects
    - methods
    - properties
    - operators
  output_structure:
    - by_category: true
    - create_index: true
    - include_metadata: true
```

### 6. Добавить CLI опции

```python
# В main.py добавить:
parser.add_argument('--cursor-mode', action='store_true', 
                   help='Export optimized for Cursor/IDE')
parser.add_argument('--max-file-size', type=int, default=50,
                   help='Max file size in KB for Cursor mode')
parser.add_argument('--max-items-per-file', type=int, default=50,
                   help='Max items per file for Cursor mode')
```

### 7. Создание .cursorignore автоматически

```python
def generate_cursor_ignore(output_dir):
    """
    Автоматически создает .cursorignore с правильными исключениями
    """
    ignore_content = """
# Автоматически сгенерировано 1c-help-parser
# Исключаем большие файлы из индексации Cursor
docs_search/1c_context.json
docs_search/1c_search_index.json
docs_search/1c_context_optimized.json

# Разрешаем индексацию оптимизированных файлов
!docs_search/cursor_export/
!docs_search/cursor_export/**/*.json
"""
    
    with open(output_dir / ".cursorignore", "w", encoding="utf-8") as f:
        f.write(ignore_content)
```

### 8. Метрики и валидация

```python
def validate_cursor_export(output_dir):
    """
    Проверка созданных файлов на соответствие лимитам Cursor
    """
    for file_path in output_dir.rglob("*.json"):
        size_kb = file_path.stat().st_size / 1024
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = len(f.readlines())
        
        if size_kb > 50:
            print(f"WARNING: {file_path} too large ({size_kb:.1f}KB)")
        if lines > 500:
            print(f"WARNING: {file_path} too many lines ({lines})")
```

### 9. Интеграция с существующим кодом

```python
# В основной функции экспорта:
if args.cursor_mode:
    print("Exporting in Cursor-optimized mode...")
    export_for_cursor(data, output_dir / "cursor_export")
    create_cursor_search_index(data, output_dir / "cursor_export")
    generate_cursor_ignore(output_dir)
    validate_cursor_export(output_dir / "cursor_export")
    print("Cursor export completed!")
```

### 10. Документация и примеры

Создать README с примерами использования:

```bash
# Экспорт для Cursor
python 1c_help_parser.py --cursor-mode --max-file-size 30 --max-items-per-file 30

# Результат: docs_search/cursor_export/ с файлами <50KB и <500 строк
```

## Преимущества такого подхода

1. **Соответствие лимитам Cursor** - файлы <50KB и <500 строк
2. **Лучшая работа AI** - точный поиск по конкретным темам
3. **Структурированная организация** - файлы по категориям
4. **Быстрая индексация** - каждый файл обрабатывается быстро
5. **Сохранение всей информации** - данные не теряются, а структурируются

## Реализация

Эти доработки позволят парсеру создавать файлы, идеально подходящие для индексации в Cursor, сохраняя при этом всю полезную информацию из документации 1С! 