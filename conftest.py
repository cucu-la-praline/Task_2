import pytest
import requests

from faker import Faker

from config import BASE_URL, FULL_URL_REGISTER, FULL_URL_USER

fake = Faker()


@pytest.fixture
def base_url():
    """Базовый URL API"""
    return BASE_URL


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

    response = requests.post(FULL_URL_REGISTER, json=user_data)
    access_token = response.json().get("accessToken")

    yield user_data, email, password, name, access_token

    if access_token:
        headers = {"Authorization": access_token}
        requests.delete(FULL_URL_USER, headers=headers)


@pytest.fixture
def auth_headers(registered_user):
    """Фикстура для получения заголовков с авторизацией"""
    user_data, email, password, name, access_token = registered_user
    return {"Authorization": access_token}


@pytest.fixture
def get_ingredients(base_url):
    """Фикстура для получения списка ингредиентов"""
    url = f"{base_url}/api/ingredients"
    response = requests.get(url=url)

    ingredients = response.json().get("data", [])
    return [ingredient["_id"] for ingredient in ingredients[:3]]


@pytest.fixture
def delete_user():
    """
    Фикстура для удаления пользователя.
    """

    def _delete_user(access_token):
        """Удалить пользователя по токену"""
        if access_token:
            headers = {"Authorization": access_token}
            response = requests.delete(FULL_URL_USER, headers=headers)
            return response.status_code == 202
        return False

    return _delete_user
