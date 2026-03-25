"""Tests for chunking utilities."""

from app.utils.chunking import chunk_text


def test_chunk_text_splits_long_input() -> None:
    """Chunking should split long input into multiple overlapping chunks."""
    text = " ".join(f"word{i}" for i in range(500))
    chunks = chunk_text(text=text, chunk_size=120, overlap=20)

    assert len(chunks) > 1
    assert all(chunk for chunk in chunks)
    assert chunks[0] != chunks[-1]
