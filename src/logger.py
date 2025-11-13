"""
Módulo de utilidades para logging
Configura el sistema de logging para la aplicación.
"""
import logging
import os
from datetime import datetime
from colorama import Fore, Style, init

# Inicializar colorama para Windows
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Formateador personalizado con colores para consola."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


def setup_logger(name: str, log_file: str = None, level: str = 'INFO'):
    """
    Configura y retorna un logger.
    
    Args:
        name: Nombre del logger
        log_file: Ruta del archivo de log (opcional)
        level: Nivel de logging
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Evitar duplicación de handlers
    if logger.handlers:
        return logger
    
    # Formato
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_fmt = '%Y-%m-%d %H:%M:%S'
    
    # Handler para consola con colores
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter(fmt, date_fmt))
    logger.addHandler(console_handler)
    
    # Handler para archivo (sin colores)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(fmt, date_fmt))
        logger.addHandler(file_handler)
    
    return logger
