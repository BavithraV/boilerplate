"""Excel extraction helpers."""

from io import BytesIO

import pandas as pd


def extract_excel_documents(file_bytes: bytes) -> list[dict]:
    """Convert an Excel workbook into sheet-level text documents."""
    excel_stream = BytesIO(file_bytes)
    workbook = pd.read_excel(excel_stream, sheet_name=None)
    documents: list[dict] = []

    for sheet_name, frame in workbook.items():
        normalized = frame.fillna("")
        row_text = []
        for _, row in normalized.iterrows():
            key_values = [f"{column}: {row[column]}" for column in normalized.columns]
            row_text.append(" | ".join(key_values))
        documents.append(
            {
                "sheet_name": sheet_name,
                "text": "\n".join(row_text),
                "columns": [str(column) for column in normalized.columns],
                "row_count": int(len(normalized.index)),
            }
        )
    return documents
