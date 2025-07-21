"""
Модуль конвертеров для преобразования данных в LLM контекст
"""

from .base_converter import BaseConverter
from .context_converter import ContextConverter
from .optimized_context_converter import OptimizedContextConverter

__all__ = ['BaseConverter', 'ContextConverter', 'OptimizedContextConverter'] 