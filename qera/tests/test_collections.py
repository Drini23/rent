"""import APIClient
import status


class TestCreateCollection:
    def test_if_user_is_anonymous_return_401(self):
        client = APIClient()
        response = client.post('/http://127.0.0.1:8000/reserve/', {'name': 'serxho'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
"""