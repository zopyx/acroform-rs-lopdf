#!/usr/bin/env python3
"""pdf-forms - Command-line utility for PDF form manipulation.

Examples:
    # List all form fields in a PDF
    pdf-forms list form.pdf

    # Fill form fields
    pdf-forms fill form.pdf output.pdf --field name="John Doe" --field email="john@example.com"

    # Fill from JSON file
    pdf-forms fill form.pdf output.pdf --json data.json

    # Fill from stdin (JSON)
    cat data.json | pdf-forms fill form.pdf output.pdf --json -

    # Output filled PDF to stdout (binary)
    pdf-forms fill form.pdf - --field name="John" > filled.pdf

"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import acroform


def cmd_list(args: argparse.Namespace) -> int:
    """List all form fields in a PDF."""
    pdf_path = Path(args.pdf)

    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}", file=sys.stderr)
        return 1

    try:
        fields = acroform.get_pdf_fields(str(pdf_path))
    except IOError as e:
        print(f"Error loading PDF: {e}", file=sys.stderr)
        return 1

    if not fields:
        print("No form fields found in PDF.")
        return 0

    # Output format selection
    if args.format == "json":
        data = []
        for field in fields:
            data.append(
                {
                    "name": field.name,
                    "type": field.field_type,
                    "current_value": field.current_value.value() if field.current_value else None,
                    "default_value": field.default_value.value() if field.default_value else None,
                    "flags": field.flags,
                    "tooltip": field.tooltip,
                }
            )
        print(json.dumps(data, indent=2))
    elif args.format == "csv":
        import csv

        writer = csv.writer(sys.stdout)
        writer.writerow(["name", "type", "current_value", "default_value", "flags", "tooltip"])
        for field in fields:
            writer.writerow(
                [
                    field.name,
                    field.field_type,
                    field.current_value.value() if field.current_value else "",
                    field.default_value.value() if field.default_value else "",
                    field.flags,
                    field.tooltip or "",
                ]
            )
    else:  # table format (default)
        # Calculate column widths
        name_width = max(len(f.name) for f in fields) + 2
        type_width = max(len(f.field_type) for f in fields) + 2

        # Header
        header = f"{'Field Name':<{name_width}} {'Type':<{type_width}} {'Current Value'}"
        print(header)
        print("-" * len(header))

        # Fields
        for field in fields:
            current = field.current_value.value() if field.current_value else ""
            print(f"{field.name:<{name_width}} {field.field_type:<{type_width}} {current}")

        print(f"\nTotal: {len(fields)} field(s)")

    return 0


def cmd_fill(args: argparse.Namespace) -> int:
    """Fill form fields in a PDF."""
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Error: Input PDF not found: {input_path}", file=sys.stderr)
        return 1

    # Collect field values
    values = {}

    # From --field arguments
    if args.field:
        for field_spec in args.field:
            if "=" not in field_spec:
                print(f"Error: Invalid field specification: {field_spec}", file=sys.stderr)
                print("Expected format: name=value", file=sys.stderr)
                return 1
            name, value = field_spec.split("=", 1)
            values[name] = value

    # From JSON file
    if args.json:
        if args.json == "-":
            # Read from stdin
            try:
                json_data = sys.stdin.read()
            except KeyboardInterrupt:
                print("Error: No JSON data provided on stdin", file=sys.stderr)
                return 1
        else:
            json_path = Path(args.json)
            if not json_path.exists():
                print(f"Error: JSON file not found: {json_path}", file=sys.stderr)
                return 1
            json_data = json_path.read_text()

        try:
            json_values = json.loads(json_data)
            if not isinstance(json_values, dict):
                print(
                    "Error: JSON data must be an object with field names as keys", file=sys.stderr
                )
                return 1
            values.update(json_values)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
            return 1

    if not values:
        print("Error: No field values provided. Use --field or --json.", file=sys.stderr)
        return 1

    # Convert string values to appropriate types
    typed_values = {}
    for name, value in values.items():
        typed_values[name] = _convert_value(value)

    # Fill the PDF
    try:
        if args.output == "-":
            # Output to stdout (binary)
            result = acroform.fill_pdf(str(input_path), typed_values)
            if result is None:
                print("Error: Failed to generate PDF", file=sys.stderr)
                return 1
            # Write binary to stdout
            sys.stdout.buffer.write(result)
        else:
            # Output to file
            output_path = Path(args.output)
            acroform.fill_pdf(str(input_path), typed_values, str(output_path))
            print(f"Filled PDF saved to: {output_path}")
    except IOError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"Error filling PDF: {e}", file=sys.stderr)
        return 1

    return 0


def _convert_value(value):
    """Convert a string value to the appropriate type."""
    # Try boolean
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lower = value.lower()
        if lower == "true":
            return True
        if lower == "false":
            return False
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
    return value


def cmd_info(args: argparse.Namespace) -> int:
    """Show information about a PDF form."""
    pdf_path = Path(args.pdf)

    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}", file=sys.stderr)
        return 1

    try:
        doc = acroform.AcroFormDocument.from_pdf(str(pdf_path))
        fields = doc.fields()
    except IOError as e:
        print(f"Error loading PDF: {e}", file=sys.stderr)
        return 1

    # Count by type
    type_counts = {}
    has_values = 0
    for field in fields:
        type_counts[field.field_type] = type_counts.get(field.field_type, 0) + 1
        if field.current_value is not None:
            has_values += 1

    print("PDF Form Information")
    print("===================")
    print(f"File: {pdf_path}")
    print(f"Total fields: {len(fields)}")
    print(f"Fields with values: {has_values}")
    print()
    print("Field Types:")
    for field_type, count in sorted(type_counts.items()):
        print(f"  {field_type}: {count}")

    return 0


def main(args: Optional[list[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="pdf-forms",
        description="Command-line utility for PDF form manipulation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pdf-forms list form.pdf
  pdf-forms list form.pdf --format json
  pdf-forms fill form.pdf output.pdf --field name="John" --field age=30
  pdf-forms fill form.pdf output.pdf --json data.json
  pdf-forms info form.pdf
        """,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {acroform.__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List all form fields in a PDF",
        description="List all form fields in a PDF form.",
    )
    list_parser.add_argument("pdf", help="Path to the PDF file")
    list_parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)",
    )
    list_parser.set_defaults(func=cmd_list)

    # Fill command
    fill_parser = subparsers.add_parser(
        "fill",
        help="Fill form fields in a PDF",
        description="Fill form fields in a PDF form and save the result.",
    )
    fill_parser.add_argument("input", help="Input PDF file path")
    fill_parser.add_argument(
        "output",
        help="Output PDF file path (use '-' for stdout)",
    )
    fill_parser.add_argument(
        "--field",
        "-f",
        action="append",
        help="Field value (format: name=value). Can be specified multiple times.",
    )
    fill_parser.add_argument(
        "--json",
        "-j",
        help="JSON file with field values (use '-' for stdin)",
    )
    fill_parser.set_defaults(func=cmd_fill)

    # Info command
    info_parser = subparsers.add_parser(
        "info",
        help="Show information about a PDF form",
        description="Show summary information about a PDF form.",
    )
    info_parser.add_argument("pdf", help="Path to the PDF file")
    info_parser.set_defaults(func=cmd_info)

    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 0

    return parsed_args.func(parsed_args)


if __name__ == "__main__":
    sys.exit(main())
