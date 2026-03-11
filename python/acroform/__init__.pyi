"""Type stubs for acroform - High-level PDF form manipulation library."""

from typing import Dict, List, Optional, Union, final

# Field type constants (strings for simplicity)
TEXT: str = "Text"
BUTTON: str = "Button"
CHOICE: str = "Choice"
SIGNATURE: str = "Signature"

FieldType = str

@final
class FieldValue:
    """Typed value for a form field."""

    @staticmethod
    def text(value: str) -> "FieldValue":
        """Create a text field value."""
        ...

    @staticmethod
    def boolean(value: bool) -> "FieldValue":
        """Create a boolean field value (for checkboxes)."""
        ...

    @staticmethod
    def choice(value: str) -> "FieldValue":
        """Create a choice field value (for radio buttons, list boxes, combo boxes)."""
        ...

    @staticmethod
    def integer(value: int) -> "FieldValue":
        """Create an integer field value."""
        ...

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def value(self) -> Union[str, bool, int]:
        """Get the value as a native Python type."""
        ...

@final
class FormField:
    """Represents a form field with its properties."""

    name: str
    """The fully qualified field name (e.g., "parent.child.field")"""

    field_type: str
    """The type of the field ("Text", "Button", "Choice", "Signature")"""

    current_value: Optional[FieldValue]
    """The current value of the field"""

    default_value: Optional[FieldValue]
    """The default value of the field"""

    flags: int
    """Field flags (bit field)"""

    tooltip: Optional[str]
    """Tooltip text (alternate description)"""

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

@final
class AcroFormDocument:
    """A PDF document with form fields."""

    @staticmethod
    def from_pdf(path: str) -> "AcroFormDocument":
        """Load a PDF document from a file path.

        Args:
            path: Path to the PDF file

        Returns:
            An AcroFormDocument instance

        Raises:
            IOError: If the file cannot be read or is not a valid PDF

        """
        ...

    @staticmethod
    def from_bytes(data: bytes) -> "AcroFormDocument":
        """Load a PDF document from bytes.

        Args:
            data: PDF file content as bytes

        Returns:
            An AcroFormDocument instance

        Raises:
            IOError: If the data is not a valid PDF

        """
        ...

    def fields(self) -> List[FormField]:
        """Get all form fields in the document.

        Returns:
            List of FormField objects

        """
        ...

    def fill(self, values: Dict[str, Union[FieldValue, str, bool, int]]) -> bytes:
        """Fill form fields with values and return the modified PDF as bytes.

        Args:
            values: Dictionary mapping field names to values.
                   Values can be FieldValue objects or native Python types
                   (str for text, bool for checkboxes, int for integers).

        Returns:
            The filled PDF as bytes

        Raises:
            RuntimeError: If field values cannot be filled

        """
        ...

    def fill_and_save(
        self, values: Dict[str, Union[FieldValue, str, bool, int]], output: str
    ) -> None:
        """Fill form fields with values and save to a file.

        Args:
            values: Dictionary mapping field names to values.
                   Values can be FieldValue objects or native Python types
                   (str for text, bool for checkboxes, int for integers).
            output: Path to save the filled PDF

        Raises:
            IOError: If the file cannot be written

        """
        ...

def fill_pdf(
    input_path: str,
    values: Dict[str, Union[FieldValue, str, bool, int]],
    output_path: Optional[str] = None,
) -> Optional[bytes]:
    """Fill a PDF form.

    Args:
        input_path: Path to the input PDF file
        values: Dictionary mapping field names to values
        output_path: If provided, save the filled PDF to this path.
                    If None, return the PDF bytes.

    Returns:
        PDF bytes if output_path is None, otherwise None

    Example:
        >>> # Fill and save to file
        >>> fill_pdf("form.pdf", {"name": "John"}, "output.pdf")
        >>>
        >>> # Fill and get bytes
        >>> pdf_bytes = fill_pdf("form.pdf", {"name": "John"})

    """
    ...

def fill_pdf_bytes(data: bytes, values: Dict[str, Union[FieldValue, str, bool, int]]) -> bytes:
    """Fill a PDF form from bytes.

    Args:
        data: PDF file content as bytes
        values: Dictionary mapping field names to values

    Returns:
        The filled PDF as bytes

    """
    ...

def get_pdf_fields(path: str) -> List[FormField]:
    """Get all fields from a PDF.

    Args:
        path: Path to the PDF file

    Returns:
        List of FormField objects

    """
    ...

def get_pdf_fields_bytes(data: bytes) -> List[FormField]:
    """Get all fields from PDF bytes.

    Args:
        data: PDF file content as bytes

    Returns:
        List of FormField objects

    """
    ...

__version__: str
