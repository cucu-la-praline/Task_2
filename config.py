"""
Конфигурационные файлы для тестов API Stellar Burgers
"""

# Базовые URL
BASE_URL = "https://stellarburgers.education-services.ru"

# Пользователи
ENDPOINT_REGISTER = "/api/auth/register"
ENDPOINT_LOGIN = "/api/auth/login"
ENDPOINT_USER = "/api/auth/user"
ENDPOINT_LOGOUT = "/api/auth/logout"

# Заказы и ингредиенты
ENDPOINT_ORDERS = "/api/orders"
ENDPOINT_INGREDIENTS = "/api/ingredients"

# Полные URL для удобства (можно использовать и так)
FULL_URL_REGISTER = f"{BASE_URL}{ENDPOINT_REGISTER}"
FULL_URL_LOGIN = f"{BASE_URL}{ENDPOINT_LOGIN}"
FULL_URL_USER = f"{BASE_URL}{ENDPOINT_USER}"
FULL_URL_ORDERS = f"{BASE_URL}{ENDPOINT_ORDERS}"
FULL_URL_INGREDIENTS = f"{BASE_URL}{ENDPOINT_INGREDIENTS}"