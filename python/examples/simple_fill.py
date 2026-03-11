#!/usr/bin/env python3
"""Simple example of filling a PDF form using acroform.

This example demonstrates how to:
1. Load a PDF form
2. List all fields
3. Fill some fields
4. Save the filled form
"""

import acroform


def main():
    # Path to the input PDF form
    input_pdf = "tests/af8.pdf"  # Update this path as needed
    output_pdf = "filled_form.pdf"

    try:
        # Load the PDF form
        doc = acroform.AcroFormDocument.from_pdf(input_pdf)
        print(f"Loaded PDF: {input_pdf}")

        # List all fields
        fields = doc.fields()
        print(f"\nFound {len(fields)} form fields:\n")

        for field in fields:
            print(f"  Name: {field.name}")
            print(f"  Type: {field.field_type}")
            if field.current_value:
                print(f"  Current Value: {field.current_value}")
            if field.tooltip:
                print(f"  Tooltip: {field.tooltip}")
            print()

        # Prepare values to fill
        values = {}

        # Find text fields and fill them
        for field in fields:
            if field.field_type == acroform.TEXT:
                # Fill with sample text
                values[field.name] = f"Filled: {field.name}"
            elif field.field_type == acroform.BUTTON:
                # Fill checkboxes with True
                values[field.name] = True

        if values:
            print(f"Filling {len(values)} fields...")

            # Method 1: Fill and save directly
            doc.fill_and_save(values, output_pdf)
            print(f"Saved filled PDF to: {output_pdf}")

            # Method 2: Fill and get bytes
            # pdf_bytes = doc.fill(values)
            # with open(output_pdf, 'wb') as f:
            #     f.write(pdf_bytes)

            # Method 3: Use convenience function
            # acroform.fill_pdf(input_pdf, values, output_pdf)

        else:
            print("No fillable fields found.")

    except FileNotFoundError:
        print(f"Error: PDF file not found: {input_pdf}")
        print("Please update the path to point to a valid PDF form.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
