import pytest
import requests
import allure

from config import FULL_URL_REGISTER, FULL_URL_USER, FULL_URL_LOGIN
from helpers.user_helpers import generate_user_data


@allure.feature("Тесты создания пользователя")
class TestUserCreate:

    @allure.title("Создание уникального пользователя")
    def test_create_unique_user_success(self, base_url, delete_user):
        user_data = generate_user_data()

        try:
            with allure.step("Отправить запрос на создание пользователя"):
                response = requests.post(FULL_URL_REGISTER, json=user_data)

                assert response.status_code == 200
                response_data = response.json()
                assert response_data["success"] is True
                assert "accessToken" in response_data
                assert "refreshToken" in response_data
                assert response_data["user"]["email"] == user_data["email"]
                assert response_data["user"]["name"] == user_data["name"]
        finally:
            with allure.step("Очистить данные - удалить пользователя"):
                access_token = response_data["accessToken"]
                delete_user(access_token)

    @allure.title("Создание пользователя, который уже зарегистрирован")
    def test_create_existing_user_fails(self, base_url, registered_user):
        user_data = registered_user

        with allure.step("Попытка создать уже существующего пользователя"):
            response = requests.post(FULL_URL_REGISTER, json=user_data)

            assert response.status_code == 403
            response_data = response.json()
            assert response_data["success"] is False
            assert response_data["message"] == "Email, password and name are required fields"

    @allure.title("Создание пользователя без заполнения обязательных полей")
    @pytest.mark.parametrize("missing_field", [
        "email",
        "password",
        "name"
    ])
    def test_create_user_missing_field_fails(self, base_url, missing_field):
        user_data = generate_user_data()
        user_data.pop(missing_field)

        with allure.step(f"Попытка создать пользователя без поля {missing_field}"):
            response = requests.post(FULL_URL_REGISTER, json=user_data)

            assert response.status_code == 403
            response_data = response.json()
            assert response_data["success"] is False
            assert "Email, password and name are required fields" in response_data["message"]


@allure.feature("Пользователи авторизации Пользователя")
class TestUserLogin:

    @allure.title("Логин под существующим пользователем")
    def test_login_existing_user_success(self, base_url, registered_user):
        user_data, email, password, name, _ = registered_user

        with allure.step("Отправить запрос на логин"):
            login_data = {"email": email, "password": password}
            response = requests.post(FULL_URL_LOGIN, json=login_data)

            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] is True
            assert "accessToken" in response_data
            assert "refreshToken" in response_data
            assert response_data["user"]["email"] == email
            assert response_data["user"]["name"] == name

    @allure.title("Логин с неверным email")
    def test_login_wrong_email_fails(self, urls, registered_user):
        """Проверка: неверный email → ошибка 401"""
        user_data, valid_email, password, name, _ = registered_user

        with allure.step("Попытка логина с неверным email"):
            login_data = {"email": "wrong@email.com", "password": password}
            response = requests.post(FULL_URL_LOGIN, json=login_data)

        with allure.step("Проверить код и тело ответа"):
            assert response.status_code == 401
            response_data = response.json()
            assert response_data["success"] is False
            assert response_data["message"] == "email or password are incorrect"

    @allure.title("Логин с неверным email и паролем")
    def test_login_wrong_email_and_password_fails(self, urls):
        """Проверка: неверный email и неверный пароль → ошибка 401"""
        with allure.step("Попытка логина с неверными данными"):
            login_data = {"email": "wrong@email.com", "password": "wrongpassword"}
            response = requests.post(FULL_URL_LOGIN, json=login_data)

        with allure.step("Проверить код и тело ответа"):
            assert response.status_code == 401
            response_data = response.json()
            assert response_data["success"] is False
            assert response_data["message"] == "email or password are incorrect"


@allure.feature("Тесты получения данных пользователя")
class TestUserData:

    @allure.title("Получение данных авторизованного пользователя")
    def test_get_user_data_with_auth_success(self, base_url, registered_user):
        user_data, email, password, name, access_token = registered_user

        with allure.step("Получить данные пользователя"):
            response = requests.get(FULL_URL_USER, headers={"Authorization": access_token})

        with allure.step("Проверить код и тело ответа"):
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] is True
            assert response_data["user"]["email"] == email
            assert response_data["user"]["name"] == name

    @allure.title("Получение данных неавторизованного пользователя")
    def test_get_user_data_without_auth_fails(self, base_url):

        with allure.step("Попытка получить данные без авторизации"):
            response = requests.get(FULL_URL_USER)

            assert response.status_code == 401
            response_data = response.json()
            assert response_data["success"] is False
            assert response_data["message"] == "You should be authorised"


@allure.feature("Тесты изменения данных пользователя")
class TestUserUpdate:

    @allure.title("Изменение данных пользователя с авторизацией")
    @pytest.mark.parametrize("field_to_update, new_value", [
        ("name", "NewName"),
        ("name", "AnotherName")
    ])
    def test_update_user_with_auth_success(self, base_url, registered_user, field_to_update, new_value):
        user_data, email, password, name, access_token = registered_user

        with allure.step(f"Обновить поле {field_to_update}"):
            update_data = {field_to_update: new_value}
            response = requests.patch(FULL_URL_USER,
                                      headers={"Authorization": access_token},
                                      json=update_data)

            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] is True
            assert response_data["user"][field_to_update] == new_value

    @allure.title("Изменение данных пользователя без авторизации")
    @pytest.mark.parametrize("field_to_update, new_value", [
        ("email", "newemail@test.com"),
        ("name", "NewName")
    ])
    def test_update_user_without_auth_fails(self, base_url, registered_user, field_to_update, new_value):
        with allure.step("Попытка обновить данные без авторизации"):
            update_data = {field_to_update: new_value}
            response = requests.patch(FULL_URL_USER, json=update_data)

            assert response.status_code == 401
            response_data = response.json()
            assert response_data["success"] is False
            assert response_data["message"] == "You should be authorised"


