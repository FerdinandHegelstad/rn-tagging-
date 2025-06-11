import os
import sys
import types

# Ensure repository root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Provide a minimal streamlit stub so Hello can be imported without dependencies.
sys.modules['streamlit'] = types.SimpleNamespace()
sys.modules['openai'] = types.SimpleNamespace(OpenAI=lambda: None)
sys.modules['presets'] = types.SimpleNamespace(preset_json='', preset_url='')

import Hello

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
    monkeypatch.setattr(Hello, 'client', dummy_client)

    result = list(Hello.get_relevance_scores_streaming('text', '{}'))
    assert result == ['a', 'b', '', 'c']

