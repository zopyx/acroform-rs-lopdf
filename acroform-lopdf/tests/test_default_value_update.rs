use acroform_lopdf::{AcroFormDocument, FieldValue};
use std::collections::HashMap;

#[test]
fn test_default_value_updated_with_value() {
    // This test ensures that when we update a field value,
    // both /V (Value) and /DV (Default Value) are updated
    
    let mut doc = AcroFormDocument::from_pdf("tests/af8.pdf").expect("Failed to load PDF");
    
    // Update the field
    let mut values = HashMap::new();
    values.insert(
        "topmostSubform[0].Page1[0].P[0].MbrName[1]".to_string(),
        FieldValue::Text("TEST_NEW_VALUE".to_string()),
    );
    
    let filled_bytes = doc.fill(values).expect("Failed to fill fields");
    
    // Save to temporary file
    let temp_path = "/tmp/test_dv_update.pdf";
    std::fs::write(temp_path, &filled_bytes).expect("Failed to save filled PDF");
    
    // Use qpdf to uncompress and verify
    let output = std::process::Command::new("qpdf")
        .args(&["--stream-data=uncompress", temp_path, "/tmp/test_dv_uncompressed.pdf"])
        .output()
        .expect("Failed to run qpdf");
    
    assert!(output.status.success(), "qpdf failed to uncompress PDF");
    
    // Read the uncompressed PDF and check that both /V and /DV are updated
    let uncompressed_content = std::fs::read("/tmp/test_dv_uncompressed.pdf")
        .expect("Failed to read uncompressed PDF");
    let content_str = String::from_utf8_lossy(&uncompressed_content);
    
    // The new value should appear in UTF-16BE encoding in hex: <feff0054004500530054005f004e00450057005f00560041004c00550045>
    let utf16_hex_pattern = "<feff0054004500530054005f004e00450057005f00560041004c00550045>";
    
    // Check that the UTF-16BE hex encoded value appears in the PDF
    // (it should appear for both /V and /DV entries)
    let count = content_str.matches(utf16_hex_pattern).count();
    
    // We should have at least 4 occurrences (for /V and /DV in each of the 2 widget annotations)
    assert!(count >= 4, "Expected at least 4 occurrences of the new value (for /V and /DV in 2 widgets), but found {}", count);
    
    // Verify that OLD_VALUE no longer appears
    let old_value_count = content_str.matches("OLD_VALUE").count();
    assert_eq!(old_value_count, 0, "OLD_VALUE should not appear in the filled PDF, but found {} occurrences", old_value_count);
    
    println!("✓ Default value update test passed! Found {} occurrences of new value", count);
}
