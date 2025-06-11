import os
import sys
import types

# Ensure repository root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Provide minimal stubs so the app can be imported without dependencies.
sys.modules["streamlit"] = types.SimpleNamespace()
sys.modules["openai"] = types.SimpleNamespace(OpenAI=lambda: None)
sys.modules["presets"] = types.SimpleNamespace(preset_json="", preset_url="")
sys.modules["dotenv"] = types.SimpleNamespace(load_dotenv=lambda: None)
sys.modules["bs4"] = types.SimpleNamespace(BeautifulSoup=lambda *a, **k: None)
sys.modules["pandas"] = types.SimpleNamespace(DataFrame=lambda *a, **k: None)
sys.modules["requests"] = types.SimpleNamespace(get=lambda *a, **k: None)

import article_relevance_app as app

class MockChunk:
    def __init__(self, content):
        self.choices = [types.SimpleNamespace(delta=types.SimpleNamespace(content=content))]

def test_get_relevance_scores_streaming_yields_each_chunk(monkeypatch):
    chunks = [MockChunk('a'), MockChunk('b'), MockChunk(None), MockChunk('c')]
    dummy_client = types.SimpleNamespace(
        chat=types.SimpleNamespace(
            completions=types.SimpleNamespace(create=lambda *args, **kwargs: iter(chunks))
        )
    )
    monkeypatch.setattr(app, 'openai_client', dummy_client)

    result = list(app.stream_relevance_scores('text', '{}'))
    assert result == ['a', 'b', '', 'c']

