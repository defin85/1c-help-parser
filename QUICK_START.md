# 🚀 Быстрый старт

## ⚡ Установка за 5 минут

### 1. Клонирование проекта
```bash
git clone <repository-url>
cd 1c-help-parser
```

### 2. Подготовка файлов

#### Конвертация .hbk в .zip
Если у вас есть исходный файл `shcntx_ru.hbk`, конвертируйте его в `rebuilt.shcntx_ru.zip`:

```bash
# Используя WinRAR (установите WinRAR с https://www.win-rar.com/)
"C:\Program Files\WinRAR\Rar.exe" r data/shcntx_ru.hbk
```

Это создаст восстановленный архив `rebuilt.shcntx_ru.zip` для парсинга.

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Проверка установки
```bash
python run.py --check
```

## 🎯 Первые шаги

### Интерактивный режим
```bash
python run.py
```

### Автоматический режим
```bash
# Автоматическая обработка (без интерактивного ввода)
python run.py --auto

# Обработка конкретного файла
python run.py --file data/rebuilt.shcntx_ru.zip




```

### Демонстрация результатов
```bash
# Демо оптимизированного контекста (рекомендуется)
python run.py --demo data/1c_context_optimized.json
```

## 📁 Структура после обработки

```
data/
├── 1c_context_optimized.json    # Оптимизированный контекст (основной продукт)
├── hbk_analysis.json            # Анализ структуры .hbk
└── extracted/                   # Извлеченные HTML файлы
```

## 🔍 Примеры использования

### Поиск в оптимизированном контексте (рекомендуется)
```python
from src.demos.optimized_demo import OptimizedContextDemo

demo = OptimizedContextDemo("data/1c_context_optimized.json")
demo.load_context()
results = demo.search_by_keyword("форма")
demo.search_by_availability("сервер")
demo.search_by_category("objects")
```

## 🛠️ Настройка

### Доступные флаги командной строки
```bash
python run.py --file data/rebuilt.shcntx_ru.zip  # Обработка конкретного файла
python run.py --demo data/1c_context_optimized.json  # Демонстрация
python run.py --check  # Проверка зависимостей
python run.py --auto  # Автоматический режим
```

### Изменение количества обрабатываемых файлов
В `src/parsers/bsl_syntax_extractor.py`:
```python
extract_all_syntax(max_files=1000)  # Увеличить лимит
```

**Или через командную строку:**
```bash
python run.py --file data/rebuilt.shcntx_ru.zip --max-files 1000
```

### Добавление новых форматов вывода
В `src/converters/optimized_context_converter.py` добавьте новые экспортеры.

## 🐛 Решение проблем

### Ошибка "BeautifulSoup4 не установлен"
```bash
pip install beautifulsoup4
```

### Ошибка "Файл не найден"
Проверьте, что ZIP файлы находятся в папке `data/`.

### Медленная обработка
Установите lxml для ускорения:
```bash
pip install lxml
```

## 📚 Дополнительные ресурсы

- [📋 Полная документация](README.md)
- [📁 Структура проекта](docs/STRUCTURE.md)
- [🔧 Инструкции по использованию](docs/README_CONTEXT.md)
- [📊 Отчеты](docs/REPORTS/)
- [📈 Информация о проекте](PROJECT_INFO.md)

## 🎉 Готово!

Теперь вы можете:
- ✅ Парсить документацию 1С
- ✅ Создавать контекст для LLM
- ✅ Искать по синтаксису
- ✅ Использовать в своих проектах

**Удачи в разработке! 🚀** 