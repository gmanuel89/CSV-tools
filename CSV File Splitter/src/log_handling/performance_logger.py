import logging
import time
import functools
from datetime import datetime
import os


# Configuration du logger de performance
def setup_performance_logger():
    logger = logging.getLogger("performance")
    logger.setLevel(logging.INFO)

    # Créer le dossier logs s'il n'existe pas
    os.makedirs("logs", exist_ok=True)

    # Handler pour fichier avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_handler = logging.FileHandler(
        f"logs/performance_{timestamp}.log", encoding="utf-8"
    )

    # Format détaillé
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Logger global
perf_logger = setup_performance_logger()


# Décorateur pour mesurer le temps d'exécution
def time_it(operation_name=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Nom de l'opération (fonction ou personnalisé)
            op_name = operation_name or f"{func.__module__}.{func.__name__}"

            start_time = time.time()
            perf_logger.info(f"START | {op_name}")

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                perf_logger.info(
                    f"SUCCESS | {op_name} | Duration: {execution_time:.4f}s"
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                perf_logger.error(
                    f"ERROR | {op_name} | Duration: {execution_time:.4f}s | Error: {str(e)}"
                )
                raise

        return wrapper

    return decorator


# Fonction pour logger manuellement des étapes
def log_step(step_name, details=""):
    perf_logger.info(f"STEP | {step_name} | {details}")


# Context manager pour mesurer des blocs de code
class TimeBlock:
    def __init__(self, block_name):
        self.block_name = block_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        perf_logger.info(f"BLOCK_START | {self.block_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        if exc_type is None:
            perf_logger.info(
                f"BLOCK_END | {self.block_name} | Duration: {execution_time:.4f}s"
            )
        else:
            perf_logger.error(
                f"BLOCK_ERROR | {self.block_name} | Duration: {execution_time:.4f}s | Error: {str(exc_val)}"
            )
