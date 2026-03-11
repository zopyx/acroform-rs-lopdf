#!/usr/bin/env python3
"""
Example of filling a PDF form in-memory using acroform.

This example demonstrates how to:
1. Load a PDF from bytes (e.g., from a database or HTTP request)
2. Fill fields
3. Get the result as bytes without writing to disk
"""

import acroform


def main():
    # Path to the input PDF form
    input_pdf = "tests/af8.pdf"  # Update this path as needed

    try:
        # Read PDF into memory
        with open(input_pdf, "rb") as f:
            pdf_bytes = f.read()
        print(f"Loaded PDF from bytes: {len(pdf_bytes)} bytes")

        # Load from bytes
        doc = acroform.AcroFormDocument.from_bytes(pdf_bytes)

        # Get fields
        fields = doc.fields()
        print(f"Found {len(fields)} form fields")

        # Prepare values to fill using different methods
        values = {
            # Using FieldValue factory methods (explicit)
            # "field_name": acroform.FieldValue.text("Hello"),
            # "checkbox": acroform.FieldValue.boolean(True),
            # "number": acroform.FieldValue.integer(42),
            # Using native Python types (convenient)
            # "field_name": "Hello",  # str -> Text
            # "checkbox": True,       # bool -> Boolean
            # "number": 42,           # int -> Integer
        }

        # Fill any text field we find
        for field in fields:
            if field.field_type == acroform.TEXT:
                values[field.name] = "Filled in memory"
                break

        if values:
            # Method 1: Using AcroFormDocument
            filled_bytes = doc.fill(values)
            print(f"Filled PDF size: {len(filled_bytes)} bytes")

            # Method 2: Using convenience function
            # filled_bytes = acroform.fill_pdf_bytes(pdf_bytes, values)

            # Now you can:
            # - Send over HTTP
            # - Store in database
            # - Save to file
            # - Process further

            # Save to verify it works
            output_pdf = "filled_in_memory.pdf"
            with open(output_pdf, "wb") as f:
                f.write(filled_bytes)
            print(f"Saved to: {output_pdf}")

            # Verify by loading it back
            verify_doc = acroform.AcroFormDocument.from_bytes(filled_bytes)
            verify_fields = verify_doc.fields()
            print(f"Verified: {len(verify_fields)} fields in filled PDF")

        else:
            print("No fillable text fields found.")

    except FileNotFoundError:
        print(f"Error: PDF file not found: {input_pdf}")
        print("Please update the path to point to a valid PDF form.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
