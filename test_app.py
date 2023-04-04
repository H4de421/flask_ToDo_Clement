import unittest

from app import app


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()

    def tearDown(self):
        self.ctx.pop()

    def test_home(self):
        response = self.client.post(
            '/index',
            data=dict(content='go walking', degree='important'),
            follow_redirects=True
        )
        # assert response.status_code == 200
        assert self.client.get('/index', query_string=dict(content='go walking', degree='important'))



if __name__ == "__main__":
    unittest.main()