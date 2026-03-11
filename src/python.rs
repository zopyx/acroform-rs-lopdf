//! Python bindings for acroform using PyO3

use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use std::collections::HashMap;

use crate::{AcroFormDocument as RustAcroFormDocument, FieldValue as RustFieldValue, FormField as RustFormField};

/// Python wrapper for AcroFormDocument
#[pyclass(name = "AcroFormDocument")]
pub struct PyAcroFormDocument {
    inner: RustAcroFormDocument,
}

#[pymethods]
impl PyAcroFormDocument {
    /// Load a PDF document from a file path
    #[staticmethod]
    fn from_pdf(path: &str) -> PyResult<Self> {
        let inner = RustAcroFormDocument::from_pdf(path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("{}", e)))?;
        Ok(Self { inner })
    }

    /// Load a PDF document from bytes
    #[staticmethod]
    fn from_bytes(data: &[u8]) -> PyResult<Self> {
        let inner = RustAcroFormDocument::from_bytes(data.to_vec())
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("{}", e)))?;
        Ok(Self { inner })
    }

    /// Get all form fields in the document
    fn fields(&self) -> PyResult<Vec<PyFormField>> {
        let fields = self
            .inner
            .fields()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("{}", e)))?;
        Ok(fields.into_iter().map(|f| PyFormField::from(f)).collect())
    }

    /// Fill form fields with values and return the modified PDF as bytes
    fn fill(&mut self, values: &Bound<'_, PyDict>) -> PyResult<Py<pyo3::types::PyBytes>> {
        let rust_values = py_dict_to_field_values(values)?;
        let bytes = self
            .inner
            .fill(rust_values)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("{}", e)))?;
        Python::with_gil(|py| Ok(pyo3::types::PyBytes::new(py, &bytes).into()))
    }

    /// Fill form fields with values and save to a file
    fn fill_and_save(&mut self, values: &Bound<'_, PyDict>, output: &str) -> PyResult<()> {
        let rust_values = py_dict_to_field_values(values)?;
        self.inner
            .fill_and_save(rust_values, output)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("{}", e)))?;
        Ok(())
    }
}

/// Python wrapper for FormField
#[pyclass(name = "FormField")]
#[derive(Clone)]
pub struct PyFormField {
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub field_type: String,
    #[pyo3(get)]
    pub current_value: Option<PyFieldValue>,
    #[pyo3(get)]
    pub default_value: Option<PyFieldValue>,
    #[pyo3(get)]
    pub flags: u32,
    #[pyo3(get)]
    pub tooltip: Option<String>,
}

impl From<RustFormField> for PyFormField {
    fn from(field: RustFormField) -> Self {
        Self {
            name: field.name,
            field_type: field.field_type.to_string(),
            current_value: field.current_value.map(PyFieldValue::from),
            default_value: field.default_value.map(PyFieldValue::from),
            flags: field.flags,
            tooltip: field.tooltip,
        }
    }
}

#[pymethods]
impl PyFormField {
    fn __repr__(&self) -> String {
        format!(
            "FormField(name='{}', field_type={}, current_value={:?}, flags={})",
            self.name, self.field_type, self.current_value, self.flags
        )
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }
}

/// Python wrapper for FieldValue - using a simple class-based approach
#[pyclass(name = "FieldValue")]
#[derive(Clone, Debug, PartialEq)]
pub enum PyFieldValue {
    Text(String),
    Boolean(bool),
    Choice(String),
    Integer(i32),
}

impl From<RustFieldValue> for PyFieldValue {
    fn from(fv: RustFieldValue) -> Self {
        match fv {
            RustFieldValue::Text(s) => PyFieldValue::Text(s),
            RustFieldValue::Boolean(b) => PyFieldValue::Boolean(b),
            RustFieldValue::Choice(s) => PyFieldValue::Choice(s),
            RustFieldValue::Integer(i) => PyFieldValue::Integer(i),
        }
    }
}

impl From<PyFieldValue> for RustFieldValue {
    fn from(fv: PyFieldValue) -> Self {
        match fv {
            PyFieldValue::Text(s) => RustFieldValue::Text(s),
            PyFieldValue::Boolean(b) => RustFieldValue::Boolean(b),
            PyFieldValue::Choice(s) => RustFieldValue::Choice(s),
            PyFieldValue::Integer(i) => RustFieldValue::Integer(i),
        }
    }
}

#[pymethods]
impl PyFieldValue {
    /// Create a text field value
    #[staticmethod]
    fn text(value: String) -> Self {
        PyFieldValue::Text(value)
    }

    /// Create a boolean field value
    #[staticmethod]
    fn boolean(value: bool) -> Self {
        PyFieldValue::Boolean(value)
    }

    /// Create a choice field value
    #[staticmethod]
    fn choice(value: String) -> Self {
        PyFieldValue::Choice(value)
    }

    /// Create an integer field value
    #[staticmethod]
    fn integer(value: i32) -> Self {
        PyFieldValue::Integer(value)
    }

    fn __repr__(&self) -> String {
        match self {
            PyFieldValue::Text(s) => format!("FieldValue.text('{}')", s),
            PyFieldValue::Boolean(b) => format!("FieldValue.boolean({})", b),
            PyFieldValue::Choice(s) => format!("FieldValue.choice('{}')", s),
            PyFieldValue::Integer(i) => format!("FieldValue.integer({})", i),
        }
    }

    fn __str__(&self) -> String {
        match self {
            PyFieldValue::Text(s) => s.clone(),
            PyFieldValue::Boolean(b) => (if *b { "True" } else { "False" }).to_string(),
            PyFieldValue::Choice(s) => s.clone(),
            PyFieldValue::Integer(i) => i.to_string(),
        }
    }

    fn __eq__(&self, other: &Bound<'_, PyAny>) -> PyResult<bool> {
        if let Ok(other) = other.extract::<PyFieldValue>() {
            Ok(self == &other)
        } else {
            Ok(false)
        }
    }

    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        let mut hasher = DefaultHasher::new();
        std::mem::discriminant(self).hash(&mut hasher);
        match self {
            PyFieldValue::Text(s) | PyFieldValue::Choice(s) => s.hash(&mut hasher),
            PyFieldValue::Boolean(b) => b.hash(&mut hasher),
            PyFieldValue::Integer(i) => i.hash(&mut hasher),
        }
        hasher.finish()
    }

    /// Get the value as a Python type
    fn value<'py>(&self, py: Python<'py>) -> Bound<'py, PyAny> {
        match self {
            PyFieldValue::Text(s) => s.clone().into_bound_py_any(py).unwrap(),
            PyFieldValue::Boolean(b) => b.into_bound_py_any(py).unwrap(),
            PyFieldValue::Choice(s) => s.clone().into_bound_py_any(py).unwrap(),
            PyFieldValue::Integer(i) => i.into_bound_py_any(py).unwrap(),
        }
    }
}

/// Convert a Python dictionary to Rust HashMap<String, RustFieldValue>
fn py_dict_to_field_values(dict: &Bound<'_, PyDict>) -> PyResult<HashMap<String, RustFieldValue>> {
    let mut result = HashMap::new();

    for (key, value) in dict.iter() {
        let key_str: String = key.extract()?;
        
        // Try to convert the value
        let field_value: RustFieldValue = if let Ok(py_field_value) = value.extract::<PyFieldValue>() {
            py_field_value.into()
        } else if let Ok(s) = value.extract::<String>() {
            RustFieldValue::Text(s)
        } else if let Ok(b) = value.extract::<bool>() {
            RustFieldValue::Boolean(b)
        } else if let Ok(i) = value.extract::<i32>() {
            RustFieldValue::Integer(i)
        } else if let Ok(i) = value.extract::<i64>() {
            RustFieldValue::Integer(i as i32)
        } else {
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                format!("Unsupported field value type for field '{}'", key_str)
            ));
        };
        
        result.insert(key_str, field_value);
    }

    Ok(result)
}

/// Convenience function to fill a PDF form from a Python dictionary
#[pyfunction]
#[pyo3(signature = (input_path, values, output_path=None))]
fn fill_pdf(input_path: &str, values: &Bound<'_, PyDict>, output_path: Option<&str>) -> PyResult<Option<Py<pyo3::types::PyBytes>>> {
    let mut doc = PyAcroFormDocument::from_pdf(input_path)?;
    
    if let Some(output) = output_path {
        doc.fill_and_save(values, output)?;
        Ok(None)
    } else {
        let bytes = doc.fill(values)?;
        Python::with_gil(|py| Ok(Some(bytes.into_pyobject(py)?.into())))
    }
}

/// Convenience function to fill a PDF form from bytes
#[pyfunction]
fn fill_pdf_bytes(data: &[u8], values: &Bound<'_, PyDict>) -> PyResult<Py<pyo3::types::PyBytes>> {
    let mut doc = PyAcroFormDocument::from_bytes(data)?;
    let bytes = doc.fill(values)?;
    Python::with_gil(|py| Ok(bytes.into_pyobject(py)?.into()))
}

/// Convenience function to get all fields from a PDF
#[pyfunction]
fn get_pdf_fields(path: &str) -> PyResult<Vec<PyFormField>> {
    let doc = PyAcroFormDocument::from_pdf(path)?;
    doc.fields()
}

/// Convenience function to get all fields from PDF bytes
#[pyfunction]
fn get_pdf_fields_bytes(data: &[u8]) -> PyResult<Vec<PyFormField>> {
    let doc = PyAcroFormDocument::from_bytes(data)?;
    doc.fields()
}

/// FieldType constants as module-level constants
#[pymodule]
fn _acroform(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyAcroFormDocument>()?;
    m.add_class::<PyFormField>()?;
    m.add_class::<PyFieldValue>()?;
    
    // Add FieldType constants
    m.add("TEXT", "Text")?;
    m.add("BUTTON", "Button")?;
    m.add("CHOICE", "Choice")?;
    m.add("SIGNATURE", "Signature")?;
    
    m.add_function(wrap_pyfunction!(fill_pdf, m)?)?;
    m.add_function(wrap_pyfunction!(fill_pdf_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(get_pdf_fields, m)?)?;
    m.add_function(wrap_pyfunction!(get_pdf_fields_bytes, m)?)?;
    Ok(())
}
