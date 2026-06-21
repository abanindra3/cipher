from jarvis.backend.voice.wake_word import strip_wake_word


def test_strip_wake_word_accepts_aliases():
    assert strip_wake_word("cypher open Safari") == "open Safari"
    assert strip_wake_word("sifer search UPSC current affairs") == "search UPSC current affairs"


def test_strip_wake_word_ignores_non_wake_text():
    assert strip_wake_word("open Safari") == ""
