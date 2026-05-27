import pytest
import requests

from faker import Faker

fake = Faker()


@pytest.fixture
def base_url():
    """Базовый URL API"""
    return "https://stellarburgers.nomoreparties.site"


@pytest.fixture
def create_unique_user():
    """Фикстура создания уникального пользователя"""

    def _create_user():
        email = fake.email()
        password = fake.password()
        name = fake.first_name()

        payload = {
            "email": email,
            "password": password,
            "name": name
        }
        return payload, email, password, name

    return _create_user


@pytest.fixture
def registered_user(base_url, create_unique_user):
    """Фикстура создания и удаления зарегистрированного пользователя"""
    user_data, email, password, name = create_unique_user()

    url = f"{base_url}/api/auth/register"
    response = requests.post(url=url, json=user_data)
    access_token = response.json().get("accessToken")

    yield user_data, email, password, name, access_token

    # Удаление пользователя после теста
    if access_token:
        url = f"{base_url}/api/auth/user"
        requests.delete(url=url, headers={"Authorization": access_token})


@pytest.fixture
def auth_headers(registered_user):
    """Фикстура для получения заголовков с авторизацией"""
    access_token = registered_user
    return {"Authorization": access_token}


@pytest.fixture
def get_ingredients(base_url):
    """Фикстура для получения списка ингредиентов"""
    url = f"{base_url}/api/ingredients"
    response = requests.get(url=url)

    if response.status_code == 200:
        ingredients = response.json().get("data", [])
        if ingredients:
            return [ingredient["_id"] for ingredient in ingredients[:3]]
    return []
