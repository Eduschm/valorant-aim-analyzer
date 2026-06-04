"""Tests for shared service logging configuration."""

from services.logging import configure_logging, get_logger


def test_configure_logging_adds_handler():
    configure_logging()
    root = get_logger().manager.root
    assert root.handlers, "Root logger should have at least one handler"


def test_get_logger_returns_same_logger_instance():
    logger1 = get_logger("services.test")
    logger2 = get_logger("services.test")
    assert logger1 is logger2
