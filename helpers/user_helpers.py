from faker import Faker


def generate_user_data():
    """Генерация данных пользователя"""
    fake = Faker()
    return {
        "email": fake.email(),
        "password": fake.password(),
        "name": fake.first_name()
    }
