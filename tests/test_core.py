"""Tests for Glitch."""
from src.core import Glitch
def test_init(): assert Glitch().get_stats()["ops"] == 0
def test_op(): c = Glitch(); c.detect(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Glitch(); [c.detect() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Glitch(); c.detect(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Glitch(); r = c.detect(); assert r["service"] == "glitch"
