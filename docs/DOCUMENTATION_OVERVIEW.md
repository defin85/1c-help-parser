# 📚 Обзор документации

## 🎯 Структура документации

### Основные файлы
- **[README.md](../README.md)** - Главная страница проекта с описанием и быстрым стартом
- **[QUICK_START.md](../QUICK_START.md)** - Пошаговое руководство по установке и использованию
- **[PROJECT_INFO.md](../PROJECT_INFO.md)** - Информация о проекте и его назначении

### Подробная документация
- **[docs/README_CONTEXT.md](README_CONTEXT.md)** - Инструкции по использованию контекстных файлов
- **[docs/STRUCTURE.md](STRUCTURE.md)** - Детальная структура проекта и компонентов
- **[docs/API/README.md](API/README.md)** - API документация для разработчиков

### Отчеты и аналитика
- **[docs/REPORTS/FINAL_REPORT.md](REPORTS/FINAL_REPORT.md)** - Финальный отчет по проекту
- **[docs/REPORTS/COMPARISON.md](REPORTS/COMPARISON.md)** - Сравнение различных подходов

## 🚀 Быстрый старт

### Для пользователей
1. **Начало работы**: [QUICK_START.md](../QUICK_START.md)
2. **Основная информация**: [README.md](../README.md)
3. **Использование результатов**: [docs/README_CONTEXT.md](README_CONTEXT.md)

### Подготовка файлов
Если у вас есть исходный файл `shcntx_ru.hbk`, конвертируйте его в `rebuilt.shcntx_ru.zip`:

```bash
# Используя WinRAR (установите WinRAR с https://www.win-rar.com/)
"C:\Program Files\WinRAR\Rar.exe" r data/shcntx_ru.hbk
```

### Для разработчиков
1. **Структура проекта**: [docs/STRUCTURE.md](STRUCTURE.md)
2. **API документация**: [docs/API/README.md](API/README.md)
3. **Технические детали**: [docs/REPORTS/FINAL_REPORT.md](REPORTS/FINAL_REPORT.md)

## 📋 Команды проекта

### Основные команды
```bash
# Интерактивный режим
python run.py

# Автоматический режим
python run.py --auto

# Обработка файла
python run.py --file data/rebuilt.shcntx_ru.zip

# Демонстрация
python run.py --demo data/1c_context_optimized.json

# Проверка зависимостей
python run.py --check
```

### Дополнительные команды
```bash
# Справка
python run.py --help

# Анализ структуры архива
python src/parsers/hbk_parser.py data/rebuilt.shcntx_ru.zip

# Извлечение синтаксиса
python src/parsers/bsl_syntax_extractor.py data/rebuilt.shcntx_ru.zip
```

## 📊 Результаты работы

### Основной продукт
- **`data/1c_context_optimized.json`** - Оптимизированный контекст для LLM (3.5MB)
- **`data/hbk_analysis.json`** - Анализ структуры архива (2KB)

### Статистика
- **Всего файлов**: ~25000 HTML файлов
- **Обрабатывается по умолчанию**: 500 файлов (настраивается)
- **Извлекаемых элементов**: ~970 объектов
- **Категории**: objects, properties, methods, functions
- **Язык**: Русский

## 🔧 Техническая информация

### Зависимости
- **BeautifulSoup4** - Парсинг HTML
- **lxml** - Ускорение парсинга
- **json** - Работа с JSON
- **zipfile** - Работа с архивами

### Архитектура
- **Парсеры** - Извлечение данных из .hbk файлов
- **Конвертеры** - Преобразование в различные форматы
- **Демо** - Примеры использования
- **Утилиты** - Вспомогательные инструменты

## 📈 История изменений

### Последние обновления
- ✅ Упрощение интерфейса - убраны избыточные опции
- ✅ Автоматический режим - добавлен флаг `--auto`
- ✅ Очистка данных - автоматическое удаление промежуточных файлов
- ✅ Оптимизация документации - убраны дублирования и устаревшая информация

### Планы развития
- 🔄 Улучшение качества парсинга
- 🔄 Добавление новых форматов вывода
- 🔄 Расширение API для интеграции
- 🔄 Улучшение производительности

## 🤝 Поддержка

### Полезные ссылки
- **[Issues](https://github.com/your-repo/issues)** - Сообщения об ошибках
- **[Discussions](https://github.com/your-repo/discussions)** - Обсуждения
- **[Wiki](https://github.com/your-repo/wiki)** - Дополнительная информация

### Контакты
- **Автор**: [Ваше имя]
- **Email**: [your-email@example.com]
- **Telegram**: [@your-username]

---

**Последнее обновление**: 2025-01-20
**Версия документации**: 2.1
**Версия проекта**: 1.1.0 