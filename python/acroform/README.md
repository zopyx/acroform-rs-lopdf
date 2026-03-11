# acroform

High-performance Python bindings for the `acroform` Rust library, enabling fast PDF form manipulation.

## Features

- 🚀 **High Performance**: Built on Rust for maximum speed
- 📝 **Form Field Reading**: List all form fields with their properties
- ✏️ **Form Filling**: Fill text fields, checkboxes, choice fields, and integers
- 💾 **Multiple I/O**: Load from files or bytes, save to files or get bytes
- 🐍 **Pythonic API**: Native Python types supported, convenient helper functions
- 🔍 **Type Hints**: Full type annotations for IDE support

## Installation

```bash
pip install acroform
```

Requires Python 3.12 or later.

## Quick Start

```python
import acroform

# Load a PDF form
doc = acroform.AcroFormDocument.from_pdf("form.pdf")

# List all fields
fields = doc.fields()
for field in fields:
    print(f"Field: {field.name} ({field.field_type})")

# Fill fields
values = {
    "name": "John Doe",
    "email": "john@example.com",
    "subscribe": True,
    "age": 30,
}
doc.fill_and_save(values, "filled_form.pdf")
```

## API Reference

### AcroFormDocument

Main class for working with PDF forms.

```python
# Load from file
doc = acroform.AcroFormDocument.from_pdf("form.pdf")

# Load from bytes
with open("form.pdf", "rb") as f:
    doc = acroform.AcroFormDocument.from_bytes(f.read())

# Get all fields
fields = doc.fields()  # Returns List[FormField]

# Fill and get bytes
pdf_bytes = doc.fill({"name": "John"})

# Fill and save to file
doc.fill_and_save({"name": "John"}, "output.pdf")
```

### FieldValue

Typed values for form fields.

```python
# Explicit creation
value = acroform.FieldValue.text("Hello")
value = acroform.FieldValue.boolean(True)
value = acroform.FieldValue.integer(42)
value = acroform.FieldValue.choice("Option 1")

# Or use native Python types (automatic conversion)
values = {
    "text_field": "Hello",      # str -> Text
    "checkbox": True,           # bool -> Boolean
    "number": 42,               # int -> Integer
}
```

### FormField

Represents a form field.

```python
field: FormField
field.name           # str: Fully qualified field name
field.field_type     # str: Type of field (TEXT, BUTTON, CHOICE, SIGNATURE)
field.current_value  # Optional[FieldValue]: Current value
field.default_value  # Optional[FieldValue]: Default value
field.flags          # int: Field flags
field.tooltip        # Optional[str]: Tooltip text
```

### Field Type Constants

```python
acroform.TEXT       # "Text" - Text field
acroform.BUTTON     # "Button" - Button/checkbox field
acroform.CHOICE     # "Choice" - Choice/radio field
acroform.SIGNATURE  # "Signature" - Signature field
```

### Convenience Functions

```python
# Fill PDF and save to file
acroform.fill_pdf("input.pdf", {"name": "John"}, "output.pdf")

# Fill PDF and get bytes
pdf_bytes = acroform.fill_pdf("input.pdf", {"name": "John"})

# Fill PDF bytes
pdf_bytes = acroform.fill_pdf_bytes(pdf_bytes, {"name": "John"})

# Get fields from file
fields = acroform.get_pdf_fields("form.pdf")

# Get fields from bytes
fields = acroform.get_pdf_fields_bytes(pdf_bytes)
```

## Examples

### Basic Form Filling

```python
import acroform

# Load document
doc = acroform.AcroFormDocument.from_pdf("form.pdf")

# Get fields to see what's available
fields = doc.fields()
for field in fields:
    print(f"{field.name}: {field.field_type}")

# Fill specific fields
values = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "newsletter": True,
    "age": 30,
}

# Save filled form
doc.fill_and_save(values, "filled.pdf")
```

### In-Memory Processing

```python
import acroform

# Load PDF into memory
with open("form.pdf", "rb") as f:
    pdf_data = f.read()

# Process in memory
doc = acroform.AcroFormDocument.from_bytes(pdf_data)
filled_pdf = doc.fill({"name": "John"})

# Use filled_pdf (bytes)
# - Send via HTTP
# - Store in database
# - etc.
```

### Web Application Example

```python
from flask import Flask, request, send_file
import acroform
import io

app = Flask(__name__)

@app.route('/fill-pdf', methods=['POST'])
def fill_pdf():
    # Get PDF and form data
    pdf_file = request.files['pdf']
    form_data = request.form.to_dict()
    
    # Fill PDF
    doc = acroform.AcroFormDocument.from_bytes(pdf_file.read())
    filled_pdf = doc.fill(form_data)
    
    # Return filled PDF
    return send_file(
        io.BytesIO(filled_pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='filled.pdf'
    )
```

## Error Handling

The library raises standard Python exceptions:

- `IOError`: File not found, permission issues, invalid PDF
- `RuntimeError`: PDF processing errors
- `TypeError`: Invalid argument types

```python
import acroform

try:
    doc = acroform.AcroFormDocument.from_pdf("nonexistent.pdf")
except IOError as e:
    print(f"Failed to load PDF: {e}")
```

## License

MIT License
