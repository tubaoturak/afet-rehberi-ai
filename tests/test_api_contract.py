"""API yanıt şekli — mobil UI sözleşmesi."""

from rag.api import detect_lang


def test_detect_lang_tr():
    assert detect_lang("Deprem anında ne yapmalıyım?") == "tr"


def test_detect_lang_en():
    assert detect_lang("How to stop a nosebleed?") == "en"
