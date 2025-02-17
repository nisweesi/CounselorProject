import unittest
from bot.conversation_bot import ConversationBot

class TestConversationBot(unittest.TestCase):

    def setUp(self):
        """Initialize ConversationBot before each test"""
        self.bot = ConversationBot()

    def test_initial_state(self):
        """Test initial values of ConversationBot attributes"""
        self.assertEqual(self.bot.current_emotion, "neutral")
        self.assertEqual(len(self.bot.conversation_history), 0)

    def test_generate_follow_up_response(self):
        """Test follow-up response generation"""
        response = self.bot.generate_follow_up_response()
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

    def test_is_goodbye(self):
        """Test recognition of goodbye statements"""
        self.assertTrue(self.bot.is_goodbye("goodbye"))
        self.assertTrue(self.bot.is_goodbye("bye"))
        self.assertFalse(self.bot.is_goodbye("hello"))

if __name__ == "__main__":
    unittest.main()
