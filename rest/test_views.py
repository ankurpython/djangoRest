from django.http.response import HttpResponse, JsonResponse
from django.test import TestCase
from django.utils.encoding import force_str


def signup(self, username=""):
    url = "/signup/"
    data = f'{{"username": "{username}", "password": "foo"}}'
    content_type = "application/json"
    response = self.client.post(url, data, content_type)
    self.assertIsInstance(response, HttpResponse)
    self.assertEqual(response.status_code, 200)
    return response


def login(self, username=""):
    url = "/login/"
    data = f'{{"username": "{username}", "password": "foo"}}'
    content_type = "application/json"
    response = self.client.post(url, data, content_type)
    self.assertIsInstance(response, HttpResponse)
    self.assertEqual(response.status_code, 200)
    return response


def logout(self):
    response = self.client.get("/logout/")
    self.assertIsInstance(response, HttpResponse)
    self.assertEqual(response.status_code, 200)
    return response


def create_user(self, username=""):
    signup(self, username)
    login(self, username)


class TaskViewTests(TestCase):
    def post_task(self, data, expected_status=200):
        url = "/tasks/"
        content_type = "application/json"
        response = self.client.post(url, data, content_type)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, expected_status)
        return response

    def test_post_200(self):
        """
        POST 200
        """
        signup(self, username="bar")
        create_user(self, username="foo")
        data = '{"task": "foo", "completed": false}'
        response = self.post_task(data)
        self.assertIsInstance(response, JsonResponse)
        expected = {
            "data": {
                "task": "foo",
                "completed": False,
                "id": 1,
                "user_id": 2
            }
        }
        self.assertJSONEqual(force_str(response.content), expected)

    def test_post_403_unauthenticated(self):
        """
        POST 403 -- unauthenticated
        """
        url = "/tasks/"
        data = '{"username": "foo", "password": "foo"}'
        content_type = "application/json"
        response = self.client.post(url, data, content_type)
        self.assertEqual(response.status_code, 403)

    def test_post_422(self):
        """
        POST 422
        """
        create_user(self, username="foo")
        data = '{"bad": "foo", "completed": "wrong"}'
        self.post_task(data, expected_status=422)

    def test_get_200(self):
        """
        GET 200
        """
        create_user(self, username="foo")
        data = '{"task": "foo", "completed": false}'
        response = self.post_task(data)
        data = '{"task": "bar", "completed": false}'
        response = self.post_task(data)
        logout(self)
        create_user(self, username="bar")
        data = '{"task": "baz", "completed": false}'
        response = self.post_task(data)
        logout(self)
        login(self, username="foo")
        url = "/tasks/"
        response = self.client.get(url)
        self.assertIsInstance(response, JsonResponse)
        expected = {
            "data": [
                {
                    "task": "foo",
                    "completed": False,
                    "id": 1,
                    "user_id": 1
                },
                {
                    "task": "bar",
                    "completed": False,
                    "id": 2,
                    "user_id": 1
                },
            ]
        }
        self.assertJSONEqual(force_str(response.content), expected)

    def test_get_403_unauthenticated(self):
        """
        GET 403 -- unauthenticated
        """
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 403)

    def test_post_403_unauthenticated(self):
        """
        POST 403 -- unauthenticated
        """
        data = '{"task": "bar", "completed": false}'
        self.post_task(data, expected_status=403)


class TaskDetailViewTests(TestCase):
    def post_task(self, data, expected_status=200):
        url = "/tasks/"
        content_type = "application/json"
        response = self.client.post(url, data, content_type)
        self.assertEqual(response.status_code, expected_status)
        self.assertIsInstance(response, JsonResponse)
        body = response.json()
        self.assertIn("data", body)
        self.assertIn("id", body["data"])
        return body["data"]["id"]

    def test_get_200(self):
        """
        GET 200
        """
        create_user(self, username="foo")
        data = '{"task": "foo", "completed": false}'
        pid = self.post_task(data)
        url = f"/tasks/{pid}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        expected = {
            "data": {
                "task": "foo",
                "completed": False,
                "id": 1,
                "user_id": 1
            }
        }
        self.assertJSONEqual(force_str(response.content), expected)

    def test_get_404(self):
        """
        GET 404
        """
        create_user(self, username="foo")
        url = "/tasks/42/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_delete_200(self):
        """
        DELETE 200
        """
        create_user(self, username="foo")
        data = '{"task": "foo", "completed": false}'
        pid = self.post_task(data)
        url = f"/tasks/{pid}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_delete_404(self):
        """
        DELETE 404
        """
        create_user(self, username="foo")
        url = "/tasks/42/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_put_200(self):
        """
        PUT 200
        """
        create_user(self, username="foo")
        data = '{"task": "foo", "completed": false}'
        pid = self.post_task(data)
        url = f"/tasks/{pid}/"
        data = '{"task": "bar", "completed": true}'
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(url)
        self.assertIsInstance(response, JsonResponse)
        expected = {
            "data": {
                "task": "bar",
                "completed": True,
                "id": 1,
                "user_id": 1
            }
        }
        self.assertJSONEqual(force_str(response.content), expected)

    def test_put_404(self):
        """
        PUT 404
        """
        create_user(self, username="foo")
        url = "/tasks/42/"
        response = self.client.put(url)
        self.assertEqual(response.status_code, 404)

    def test_get_403_unauthenticated(self):
        """
        GET 403 -- unauthenticated
        """
        create_user(self, username="foo")
        logout(self)
        response = self.client.get("/tasks/42/")
        self.assertEqual(response.status_code, 403)

    def test_put_403_unauthenticated(self):
        """
        PUT 403 -- unauthenticated
        """
        url = "/tasks/42/"
        data = '{"username": "foo", "password": "foo"}'
        content_type = "application/json"
        response = self.client.put(url, data, content_type)
        self.assertEqual(response.status_code, 403)

    def test_delete_403_unauthenticated(self):
        """
        DELETE 403 -- unauthenticated
        """
        response = self.client.delete("/tasks/42/")
        self.assertEqual(response.status_code, 403)

    def test_get_403_wrong_user(self):
        """
        GET 403 -- wrong user
        """
        create_user(self, username="garply")
        data = '{"task": "foo", "completed": false}'
        pid = self.post_task(data)
        logout(self)
        create_user(self, username="quux")
        response = self.client.get(f"/tasks/{pid}/")
        self.assertEqual(response.status_code, 403)

    def test_put_403_wrong_user(self):
        """
        PUT 403 -- wrong user
        """
        create_user(self, username="garply")
        data = '{"task": "foo", "completed": false}'
        pid = self.post_task(data)
        logout(self)
        create_user(self, username="quux")
        url = f"/tasks/{pid}/"
        data = '{"username": "foo", "password": "foo"}'
        content_type = "application/json"
        response = self.client.put(url, data, content_type)
        self.assertEqual(response.status_code, 403)

    def test_delete_403_wrong_user(self):
        """
        DELETE 403 -- wrong user
        """
        create_user(self, username="garply")
        data = '{"task": "foo", "completed": false}'
        pid = self.post_task(data)
        logout(self)
        create_user(self, username="quux")
        response = self.client.delete(f"/tasks/{pid}/")
        self.assertEqual(response.status_code, 403)
