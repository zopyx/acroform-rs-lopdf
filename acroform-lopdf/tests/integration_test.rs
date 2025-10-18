use acroform_lopdf::{AcroFormDocument, FieldValue};
use std::collections::HashMap;

#[test]
fn test_load_and_list_fields() {
    let doc = AcroFormDocument::from_pdf("tests/af8.pdf").expect("Failed to load PDF");

    let fields = doc.fields().expect("Failed to get fields");

    // Print all fields for debugging
    for field in &fields {
        println!("Field: {} ({})", field.name, field.field_type);
        if let Some(ref value) = field.current_value {
            println!("  Current value: {:?}", value);
        }
        if let Some(ref tooltip) = field.tooltip {
            println!("  Tooltip: {}", tooltip);
        }
    }

    // Should have at least one field
    assert!(!fields.is_empty(), "No fields found in the PDF");
}

#[test]
fn test_load_from_bytes() {
    let bytes = std::fs::read("tests/af8.pdf").expect("Failed to read PDF file");
    let doc = AcroFormDocument::from_bytes(bytes).expect("Failed to load PDF from bytes");

    let fields = doc.fields().expect("Failed to get fields");
    assert!(!fields.is_empty(), "No fields found in the PDF");
}

#[test]
fn test_fill_and_save() {
    let mut doc = AcroFormDocument::from_pdf("tests/af8.pdf").expect("Failed to load PDF");

    // Get the fields first
    let fields = doc.fields().expect("Failed to get fields");

    // Fill with test values
    let mut values = HashMap::new();

    // Try to fill the first text field we find
    for field in fields {
        match field.field_type {
            acroform_lopdf::FieldType::Text => {
                values.insert(
                    field.name.clone(),
                    FieldValue::Text("Test Value".to_string()),
                );
                break;
            }
            _ => {}
        }
    }

    if !values.is_empty() {
        let bytes = doc.fill(values).expect("Failed to fill fields");
        assert!(!bytes.is_empty(), "Filled PDF is empty");

        // Save to a temporary location
        std::fs::write("/tmp/filled_test.pdf", bytes).expect("Failed to write filled PDF");

        // Verify we can load it back
        let filled_doc =
            AcroFormDocument::from_pdf("/tmp/filled_test.pdf").expect("Failed to load filled PDF");
        let filled_fields = filled_doc
            .fields()
            .expect("Failed to get fields from filled PDF");
        assert!(!filled_fields.is_empty(), "No fields in filled PDF");
    }
}
