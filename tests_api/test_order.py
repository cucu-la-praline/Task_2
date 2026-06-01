import requests
import allure

from config import FULL_URL_ORDERS


@allure.feature("Тесты создания заказов")
class TestOrderCreate:

    @allure.title("Создание заказа с авторизацией")
    def test_create_order_with_auth_success(self, base_url, registered_user, auth_headers, get_ingredients):
        ingredients = get_ingredients

        with allure.step("Создать заказ с авторизацией"):
            order_data = {"ingredients": ingredients}
            response = requests.post(FULL_URL_ORDERS,
                                     headers=auth_headers,
                                     json=order_data)

            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] is True
            assert "order" in response_data

    @allure.title("Создание заказа без авторизации")
    def test_create_order_without_auth_success(self, base_url, get_ingredients):
        ingredients = get_ingredients

        with allure.step("Создать заказ без авторизации"):
            order_data = {"ingredients": ingredients}
            response = requests.post(FULL_URL_ORDERS, json=order_data)

            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] is True
            assert "order" in response_data

    @allure.title("Создание заказа с ингредиентами")
    def test_create_order_with_ingredients_success(self, base_url, get_ingredients):
        ingredients = get_ingredients

        with allure.step("Создать заказ с ингредиентами"):
            order_data = {"ingredients": ingredients}
            response = requests.post(FULL_URL_ORDERS, json=order_data)

            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] is True

    @allure.title("Создание заказа без ингредиентов")
    def test_create_order_without_ingredients_fails(self, base_url):

        with allure.step("Попытка создать заказ без ингредиентов"):
            order_data = {"ingredients": []}
            response = requests.post(FULL_URL_ORDERS, json=order_data)

            assert response.status_code == 400
            response_data = response.json()
            assert response_data["success"] is False
            assert response_data["message"] == "Ingredient ids must be provided"

    @allure.title("Создание заказа с неверным хешем ингредиентов")
    def test_create_order_with_invalid_ingredient_hash_fails(self, base_url):

        with allure.step("Попытка создать заказ с неверным хешем"):
            order_data = {"ingredients": ["invalid_hash_123", "wrong_hash_456"]}
            response = requests.post(FULL_URL_ORDERS, json=order_data)

            assert response.status_code == 500 or response.status_code == 400


@allure.feature("Тесты получения заказов")
class TestOrderGet:

    @allure.title("Получение заказов авторизованного пользователя")
    def test_get_user_orders_with_auth_success(self, base_url, registered_user, auth_headers, get_ingredients):
        ingredients = get_ingredients

        with allure.step("Создать тестовый заказ"):
            order_data = {"ingredients": ingredients}
            requests.post(f"{base_url}/api/orders", headers=auth_headers, json=order_data)

        with allure.step("Получить заказы пользователя"):
            response = requests.get(FULL_URL_ORDERS, headers=auth_headers)

            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] is True
            assert "orders" in response_data
            assert type(response_data["orders"]) is list

    @allure.title("Получение заказов неавторизованного пользователя")
    def test_get_user_orders_without_auth_fails(self, base_url):

        with allure.step("Попытка получить заказы без авторизации"):
            response = requests.get(FULL_URL_ORDERS)

            assert response.status_code == 401
            response_data = response.json()
            assert response_data["success"] is False
            assert response_data["message"] == "You should be authorised"

    @allure.title("Получение заказов пользователя с пустым списком")
    def test_get_user_orders_empty_success(self, base_url, registered_user, auth_headers):

        with allure.step("Получить заказы нового пользователя"):
            response = requests.get(FULL_URL_ORDERS, headers=auth_headers)

            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] is True
            assert "orders" in response_data
            assert response_data["orders"] == []
            assert response_data["total"] is not None
            assert response_data["totalToday"] is not None
