import random
import string
from faker import Faker
#
# def generate_random_string(length=10):
#     """Генерация случайной строки"""
#     return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
#


def generate_user_data():
    """Генерация данных пользователя"""
    fake = Faker()
    return {
        "email": fake.email(),
        "password": fake.password(),
        "name": fake.first_name()
    }
