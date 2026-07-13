import unittest
import logging
from src.logger import get_logger

class TestLogger(unittest.TestCase):
    def test_get_logger_initialization(self):
        """Test that get_logger returns a correctly initialized logger."""
        logger = get_logger("test_agent_logger")

        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_agent_logger")
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertFalse(logger.propagate)
        self.assertTrue(len(logger.handlers) > 0)

        # Verify handler type
        self.assertIsInstance(logger.handlers[0], logging.StreamHandler)

        # Subsequent calls should return the same logger without adding more handlers
        logger2 = get_logger("test_agent_logger")
        self.assertIs(logger, logger2)
        self.assertEqual(len(logger.handlers), 1)
