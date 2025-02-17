import unittest
import json
from app import create_app

class TestFlaskAPI(unittest.TestCase):

    def setUp(self):
        """Create test client"""
        app = create_app()
        app.testing = True
        self.client = app.test_client()

    def test_start_conversation(self):
        """Test conversation start endpoint"""
        response = self.client.get("/bot/start")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("message", data)

if __name__ == "__main__":
    unittest.main()
