import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai import parse_preferences_with_ai


def test_empty_message_does_not_crash():
    result = parse_preferences_with_ai("")
    # Should return a dict either way — either parsed (likely all nulls) or an error dict
    assert isinstance(result, dict)


def test_nonsense_message_returns_dict_not_exception():
    result = parse_preferences_with_ai("asdkjfh aslkdjf qwoeiru")
    assert isinstance(result, dict)