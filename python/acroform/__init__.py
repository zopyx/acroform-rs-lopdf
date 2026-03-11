"""
acroform - High-level PDF form manipulation library

This module provides Python bindings for the acroform Rust library,
allowing you to read and fill PDF forms (AcroForms).

Example:
    >>> import acroform
    >>> 
    >>> # Load a PDF with form fields
    >>> doc = acroform.AcroFormDocument.from_pdf("form.pdf")
    >>> 
    >>> # List all fields
    >>> fields = doc.fields()
    >>> for field in fields:
    ...     print(f"Field: {field.name} ({field.field_type})")
    ... 
    >>> # Fill fields
    >>> values = {
    ...     "name": acroform.FieldValue.text("John Doe"),
    ...     "age": acroform.FieldValue.integer(30),
    ...     "subscribe": acroform.FieldValue.boolean(True),
    ... }
    >>> doc.fill_and_save(values, "filled_form.pdf")
    >>> 
    >>> # Or get bytes
    >>> pdf_bytes = doc.fill(values)

Convenience functions are also available:
    >>> # Fill a PDF and save to file
    >>> acroform.fill_pdf("form.pdf", {"name": "John"}, "output.pdf")
    >>> 
    >>> # Fill a PDF and get bytes
    >>> pdf_bytes = acroform.fill_pdf("form.pdf", {"name": "John"})
    >>> 
    >>> # Get fields from a PDF
    >>> fields = acroform.get_pdf_fields("form.pdf")
"""

from acroform._acroform import (
    AcroFormDocument,
    FieldValue,
    FormField,
    fill_pdf,
    fill_pdf_bytes,
    get_pdf_fields,
    get_pdf_fields_bytes,
    # Field type constants
    TEXT,
    BUTTON,
    CHOICE,
    SIGNATURE,
)

__version__ = "0.2.0"

# Backwards compatibility alias
FieldType = str

__all__ = [
    "AcroFormDocument",
    "FieldValue",
    "FormField",
    "FieldType",
    "fill_pdf",
    "fill_pdf_bytes",
    "get_pdf_fields",
    "get_pdf_fields_bytes",
    # Field type constants
    "TEXT",
    "BUTTON",
    "CHOICE",
    "SIGNATURE",
]
