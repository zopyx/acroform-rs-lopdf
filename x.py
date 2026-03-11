#!/usr/bin/env python3
"""Example script to demonstrate acroform usage."""

import acroform

# Get fields from a PDF
fields = acroform.get_pdf_fields("FilledForm.pdf")
print(f"Found {len(fields)} fields:")
for field in fields:
    print(f"  - {field.name}: {field.field_type} = {field.current_value}")
