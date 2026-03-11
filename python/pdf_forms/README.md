# pdf-forms CLI

Command-line utility for PDF form manipulation using the `acroform` library.

## Installation

The CLI is included with the `acroform` package:

```bash
pip install acroform
```

## Usage

### List Form Fields

Display all form fields in a PDF:

```bash
pdf-forms list form.pdf
```

Output formats:
- `table` (default) - Human-readable table format
- `json` - JSON array with field details
- `csv` - CSV format

```bash
pdf-forms list form.pdf --format json
pdf-forms list form.pdf --format csv
```

### Show Form Information

Display summary information about a PDF form:

```bash
pdf-forms info form.pdf
```

### Fill Form Fields

Fill form fields using command-line arguments:

```bash
pdf-forms fill input.pdf output.pdf --field name="John Doe" --field email="john@example.com"
```

Fill from a JSON file:

```bash
echo '{"name": "John Doe", "age": 30}' > data.json
pdf-forms fill input.pdf output.pdf --json data.json
```

Fill from stdin (JSON):

```bash
cat data.json | pdf-forms fill input.pdf output.pdf --json -
```

Output to stdout (useful for piping):

```bash
pdf-forms fill input.pdf - --field name="John" > filled.pdf
```

## Value Types

The CLI automatically converts values to appropriate types:

- `"true"` / `"false"` → Boolean
- Numeric strings → Integer
- Other strings → Text

## Examples

### List fields and fill specific ones

```bash
# First, see what fields are available
pdf-forms list form.pdf

# Then fill them
pdf-forms fill form.pdf filled.pdf \
  --field "topmostSubform[0].Page1[0].P[0].MbrName[1]=John Doe"
```

### Batch processing with JSON

```bash
# Create a JSON file with all values
cat > values.json << 'EOF'
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "subscribe": true,
  "age": 30
}
EOF

# Fill the form
pdf-forms fill template.pdf output.pdf --json values.json
```

### Pipe to another command

```bash
pdf-forms fill input.pdf - --field name="Test" | qpdf --linearize - output.pdf
```

## Exit Codes

- `0` - Success
- `1` - Error (file not found, invalid PDF, etc.)

## License

MIT License - same as the acroform library.
