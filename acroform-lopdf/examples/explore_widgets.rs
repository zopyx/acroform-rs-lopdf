use lopdf::Document;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let doc = Document::load("tests/af8.pdf")?;
    
    // Get pages and their annotations
    let pages = doc.get_pages();
    println!("Total pages: {}", pages.len());
    
    for (page_num, page_id) in pages.iter() {
        println!("\n=== Page {} (ID: {:?}) ===", page_num, page_id);
        
        // Get page dictionary
        if let Ok(page_dict) = doc.get_dictionary(*page_id) {
            // Look for Annots array
            if let Ok(annots) = page_dict.get(b"Annots").and_then(|obj| obj.as_array()) {
                println!("  Annotations: {}", annots.len());
                
                for (idx, annot_obj) in annots.iter().enumerate() {
                    if let Ok(annot_ref) = annot_obj.as_reference() {
                        if let Ok(annot_dict) = doc.get_dictionary(annot_ref) {
                            println!("\n  Annotation {} (ref: {:?}):", idx, annot_ref);
                            
                            // Get subtype
                            if let Ok(subtype) = annot_dict.get(b"Subtype").and_then(|o| o.as_name()) {
                                println!("    Subtype: {}", String::from_utf8_lossy(subtype));
                                
                                // If it's a widget, get field info
                                if subtype == b"Widget" {
                                    // Check for field name
                                    if let Ok(name) = annot_dict.get(b"T").and_then(|o| o.as_str()) {
                                        println!("    T (name): {}", String::from_utf8_lossy(name));
                                    }
                                    
                                    // Check for field type
                                    if let Ok(ft) = annot_dict.get(b"FT").and_then(|o| o.as_name()) {
                                        println!("    FT (type): {}", String::from_utf8_lossy(ft));
                                    }
                                    
                                    // Check for value
                                    if let Ok(value) = annot_dict.get(b"V") {
                                        println!("    V (value): {:?}", value);
                                    }
                                    
                                    // Check for appearance state
                                    if let Ok(as_val) = annot_dict.get(b"AS") {
                                        println!("    AS (appearance state): {:?}", as_val);
                                    }
                                    
                                    // Check for Parent reference
                                    if let Ok(parent) = annot_dict.get(b"Parent") {
                                        println!("    Parent: {:?}", parent);
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    // Also check field structure
    println!("\n\n=== Field Structure ===");
    let catalog = doc.catalog()?;
    if let Ok(acroform_ref) = catalog.get(b"AcroForm").and_then(|o| o.as_reference()) {
        if let Ok(acroform_dict) = doc.get_dictionary(acroform_ref) {
            if let Ok(fields) = acroform_dict.get(b"Fields").and_then(|o| o.as_array()) {
                println!("Total root fields: {}", fields.len());
                
                for (idx, field_obj) in fields.iter().enumerate() {
                    if let Ok(field_ref) = field_obj.as_reference() {
                        if let Ok(field_dict) = doc.get_dictionary(field_ref) {
                            println!("\nField {} (ref: {:?}):", idx, field_ref);
                            
                            if let Ok(name) = field_dict.get(b"T").and_then(|o| o.as_str()) {
                                println!("  T: {}", String::from_utf8_lossy(name));
                            }
                            
                            if let Ok(ft) = field_dict.get(b"FT").and_then(|o| o.as_name()) {
                                println!("  FT: {}", String::from_utf8_lossy(ft));
                            }
                            
                            // Check if this field has Kids
                            if let Ok(kids) = field_dict.get(b"Kids").and_then(|o| o.as_array()) {
                                println!("  Kids: {} children", kids.len());
                                
                                // Check first kid to see if it's a widget
                                if let Some(kid_obj) = kids.first() {
                                    if let Ok(kid_ref) = kid_obj.as_reference() {
                                        if let Ok(kid_dict) = doc.get_dictionary(kid_ref) {
                                            if let Ok(subtype) = kid_dict.get(b"Subtype") {
                                                println!("    First kid has Subtype: {:?}", subtype);
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    Ok(())
}
