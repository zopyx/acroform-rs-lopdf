use lopdf::Document;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let doc = Document::load("tests/af8.pdf")?;
    
    println!("=== Exploring Field and Widget Structure ===\n");
    
    let catalog = doc.catalog()?;
    if let Ok(acroform_ref) = catalog.get(b"AcroForm").and_then(|o| o.as_reference()) {
        if let Ok(acroform_dict) = doc.get_dictionary(acroform_ref) {
            if let Ok(fields) = acroform_dict.get(b"Fields").and_then(|o| o.as_array()) {
                println!("Total root fields: {}\n", fields.len());
                
                for (idx, field_obj) in fields.iter().enumerate() {
                    if let Ok(field_ref) = field_obj.as_reference() {
                        explore_field(&doc, field_ref, idx, 0)?;
                    }
                }
            }
        }
    }
    
    Ok(())
}

fn explore_field(doc: &Document, field_ref: (u32, u16), idx: usize, depth: usize) -> Result<(), Box<dyn std::error::Error>> {
    let indent = "  ".repeat(depth);
    if let Ok(field_dict) = doc.get_dictionary(field_ref) {
        println!("{}Field {} (ref: {:?}):", indent, idx, field_ref);
        
        // Field name
        if let Ok(name) = field_dict.get(b"T").and_then(|o| o.as_str()) {
            println!("{}  T (name): {}", indent, String::from_utf8_lossy(name));
        }
        
        // Field type
        if let Ok(ft) = field_dict.get(b"FT").and_then(|o| o.as_name()) {
            println!("{}  FT (type): {}", indent, String::from_utf8_lossy(ft));
        }
        
        // Value
        if let Ok(value) = field_dict.get(b"V") {
            println!("{}  V (value): {:?}", indent, value);
        }
        
        // Appearance state
        if let Ok(as_val) = field_dict.get(b"AS") {
            println!("{}  AS (appearance state): {:?}", indent, as_val);
        }
        
        // Check for Subtype (indicates widget annotation)
        if let Ok(subtype) = field_dict.get(b"Subtype") {
            println!("{}  Subtype: {:?}", indent, subtype);
        }
        
        // Check for Rect (indicates widget annotation)
        if let Ok(rect) = field_dict.get(b"Rect") {
            println!("{}  Rect: {:?}", indent, rect);
        }
        
        // Check for Parent
        if let Ok(parent) = field_dict.get(b"Parent") {
            println!("{}  Parent: {:?}", indent, parent);
        }
        
        // Check if this field has Kids
        if let Ok(kids) = field_dict.get(b"Kids").and_then(|o| o.as_array()) {
            println!("{}  Kids: {} children", indent, kids.len());
            
            for (kid_idx, kid_obj) in kids.iter().enumerate() {
                if let Ok(kid_ref) = kid_obj.as_reference() {
                    println!();
                    explore_field(doc, kid_ref, kid_idx, depth + 1)?;
                }
            }
        }
    }
    
    Ok(())
}
