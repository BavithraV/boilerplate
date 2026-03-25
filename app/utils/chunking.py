"""Chunking utilities."""


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> list[str]:
    """Split long text into overlapping recursive chunks."""
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    if len(cleaned) <= chunk_size:
        return [cleaned]

    effective_overlap = min(max(overlap, 0), chunk_size // 2)
    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        split_point = cleaned.rfind(" ", start, end)
        if split_point <= start:
            split_point = end
        chunk = cleaned[start:split_point].strip()
        if chunk:
            chunks.append(chunk)
        if split_point >= len(cleaned):
            break
        start = max(split_point - effective_overlap, start + 1)
    return chunks
