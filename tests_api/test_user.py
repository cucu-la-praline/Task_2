import pytest
import requests
import allure

from helpers.user_helpers import generate_user_data


@allure.feature("Тесты создания пользователя")
class TestUserCreate:

    @allure.title("Создание уникального пользователя")
    def test_create_unique_user_success(self, base_url):
        user_data = generate_user_data()

        with allure.step("Отправить запрос на создание пользователя"):
            response = requests.post(f"{base_url}/api/auth/register", json=user_data)

            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] is True
            assert "accessToken" in response_data
            assert "refreshToken" in response_data
            assert response_data["user"]["email"] == user_data["email"]
            assert response_data["user"]["name"] == user_data["name"]

        with allure.step("Очистить данные - удалить пользователя"):
            access_token = response_data["accessToken"]
            requests.delete(f"{base_url}/api/auth/user", headers={"Authorization": access_token})

    @allure.title("Создание пользователя, который уже зарегистрирован")
    def test_create_existing_user_fails(self, base_url, registered_user):
        user_data = registered_user

        with allure.step("Попытка создать уже существующего пользователя"):
            response = requests.post(f"{base_url}/api/auth/register", json=user_data)

            assert response.status_code == 403
            response_data = response.json()
            assert response_data["success"] is False
            assert response_data["message"] == "User already exists"

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
            response = requests.post(f"{base_url}/api/auth/register", json=user_data)

            assert response.status_code == 403
            response_data = response.json()
            assert response_data["success"] is False
            assert "email, password and name are required fields" in response_data["message"]


@allure.feature("Пользователи авторизации Пользователя")
class TestUserLogin:

    @allure.title("Логин под существующим пользователем")
    def test_login_existing_user_success(self, base_url, registered_user):
        user_data, email, password, name, _ = registered_user

        with allure.step("Отправить запрос на логин"):
            login_data = {"email": email, "password": password}
            response = requests.post(f"{base_url}/api/auth/login", json=login_data)

            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] is True
            assert "accessToken" in response_data
            assert "refreshToken" in response_data
            assert response_data["user"]["email"] == email
            assert response_data["user"]["name"] == name

    @allure.title("Логин с неверным логином и паролем")
    @pytest.mark.parametrize("email, password", [
        ("wrong@email.com", "wrongpassword"),
        ("wrong@email.com", None),
        (None, "wrongpassword")
    ])
    def test_login_wrong_credentials_fails(self, base_url, registered_user, email, password):
        user_data, valid_email, valid_password = registered_user

        with allure.step("Попытка логина с неверными данными"):
            login_data = {
                "email": email if email else valid_email,
                "password": password if password else valid_password + "wrong"
            }
            if not email:
                login_data["email"] = "wrong@email.com"
            if not password:
                login_data["password"] = "wrongpassword"

            response = requests.post(f"{base_url}/api/auth/login", json=login_data)

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
            response = requests.get(f"{base_url}/api/auth/user", headers={"Authorization": access_token})

        with allure.step("Проверить код и тело ответа"):
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] is True
            assert response_data["user"]["email"] == email
            assert response_data["user"]["name"] == name

    @allure.title("Получение данных неавторизованного пользователя")
    def test_get_user_data_without_auth_fails(self, base_url):

        with allure.step("Попытка получить данные без авторизации"):
            response = requests.get(f"{base_url}/api/auth/user")

            assert response.status_code == 401
            response_data = response.json()
            assert response_data["success"] is False
            assert response_data["message"] == "You should be authorised"


@allure.feature("Тесты изменения данных пользователя")
class TestUserUpdate:

    @allure.title("Изменение данных пользователя с авторизацией")
    @pytest.mark.parametrize("field_to_update, new_value", [
        ("email", "newemail@test.com"),
        ("name", "NewName"),
        ("email", "another@test.com"),
        ("name", "AnotherName")
    ])
    def test_update_user_with_auth_success(self, base_url, registered_user, field_to_update, new_value):
        user_data, email, password, name, access_token = registered_user

        with allure.step(f"Обновить поле {field_to_update}"):
            update_data = {field_to_update: new_value}
            response = requests.patch(f"{base_url}/api/auth/user",
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
            response = requests.patch(f"{base_url}/api/auth/user", json=update_data)

            assert response.status_code == 401
            response_data = response.json()
            assert response_data["success"] is False
            assert response_data["message"] == "You should be authorised"


