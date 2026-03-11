"""Tests for the acroform Python bindings."""

import os
import tempfile

import pytest

import acroform


# Path to a test PDF form - update this to point to an actual test file
TEST_PDF_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "tests", "af8.pdf")


class TestFieldValue:
    """Tests for FieldValue class."""

    def test_text_creation(self):
        fv = acroform.FieldValue.text("hello")
        assert fv.value() == "hello"
        assert str(fv) == "hello"
        assert "text" in repr(fv).lower()

    def test_boolean_creation(self):
        fv = acroform.FieldValue.boolean(True)
        assert fv.value() is True
        assert str(fv) == "True"

        fv = acroform.FieldValue.boolean(False)
        assert fv.value() is False
        assert str(fv) == "False"

    def test_integer_creation(self):
        fv = acroform.FieldValue.integer(42)
        assert fv.value() == 42
        assert str(fv) == "42"

    def test_choice_creation(self):
        fv = acroform.FieldValue.choice("option1")
        assert fv.value() == "option1"
        assert str(fv) == "option1"

    def test_equality(self):
        fv1 = acroform.FieldValue.text("hello")
        fv2 = acroform.FieldValue.text("hello")
        fv3 = acroform.FieldValue.text("world")

        assert fv1 == fv2
        assert fv1 != fv3
        assert fv1 != acroform.FieldValue.integer(42)

    def test_hash(self):
        fv1 = acroform.FieldValue.text("hello")
        fv2 = acroform.FieldValue.text("hello")

        assert hash(fv1) == hash(fv2)


class TestFieldType:
    """Tests for FieldType class."""

    def test_field_type_variants(self):
        assert acroform.TEXT == "Text"
        assert acroform.BUTTON == "Button"
        assert acroform.CHOICE == "Choice"
        assert acroform.SIGNATURE == "Signature"

    def test_equality(self):
        assert acroform.TEXT == acroform.TEXT
        assert acroform.TEXT != acroform.BUTTON

    def test_str(self):
        assert str(acroform.TEXT) == "Text"
        assert str(acroform.BUTTON) == "Button"

    def test_hash(self):
        assert hash(acroform.TEXT) == hash(acroform.TEXT)


class TestFormField:
    """Tests for FormField class."""

    def test_form_field_attributes(self):
        # These tests require an actual PDF
        if not os.path.exists(TEST_PDF_PATH):
            pytest.skip(f"Test PDF not found: {TEST_PDF_PATH}")

        doc = acroform.AcroFormDocument.from_pdf(TEST_PDF_PATH)
        fields = doc.fields()

        if not fields:
            pytest.skip("No fields in test PDF")

        field = fields[0]
        assert hasattr(field, "name")
        assert hasattr(field, "field_type")
        assert hasattr(field, "current_value")
        assert hasattr(field, "default_value")
        assert hasattr(field, "flags")
        assert hasattr(field, "tooltip")

        assert isinstance(field.name, str)
        assert isinstance(field.field_type, acroform.FieldType)
        assert isinstance(field.flags, int)


class TestAcroFormDocument:
    """Tests for AcroFormDocument class."""

    def test_from_pdf_not_found(self):
        with pytest.raises(IOError):
            acroform.AcroFormDocument.from_pdf("nonexistent.pdf")

    def test_from_pdf_success(self):
        if not os.path.exists(TEST_PDF_PATH):
            pytest.skip(f"Test PDF not found: {TEST_PDF_PATH}")

        doc = acroform.AcroFormDocument.from_pdf(TEST_PDF_PATH)
        assert doc is not None

    def test_from_bytes(self):
        if not os.path.exists(TEST_PDF_PATH):
            pytest.skip(f"Test PDF not found: {TEST_PDF_PATH}")

        with open(TEST_PDF_PATH, "rb") as f:
            data = f.read()

        doc = acroform.AcroFormDocument.from_bytes(data)
        assert doc is not None

    def test_fields(self):
        if not os.path.exists(TEST_PDF_PATH):
            pytest.skip(f"Test PDF not found: {TEST_PDF_PATH}")

        doc = acroform.AcroFormDocument.from_pdf(TEST_PDF_PATH)
        fields = doc.fields()

        assert isinstance(fields, list)
        for field in fields:
            assert isinstance(field, acroform.FormField)

    def test_fill_and_save(self):
        if not os.path.exists(TEST_PDF_PATH):
            pytest.skip(f"Test PDF not found: {TEST_PDF_PATH}")

        doc = acroform.AcroFormDocument.from_pdf(TEST_PDF_PATH)
        fields = doc.fields()

        # Find a text field to fill
        text_field = None
        for field in fields:
            if field.field_type == acroform.TEXT:
                text_field = field.name
                break

        if not text_field:
            pytest.skip("No text fields in test PDF")

        # Fill using FieldValue
        values = {text_field: acroform.FieldValue.text("Test Value")}

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = f.name

        try:
            doc.fill_and_save(values, output_path)
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0

            # Verify we can load it back
            filled_doc = acroform.AcroFormDocument.from_pdf(output_path)
            assert len(filled_doc.fields()) > 0
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_fill_with_native_types(self):
        if not os.path.exists(TEST_PDF_PATH):
            pytest.skip(f"Test PDF not found: {TEST_PDF_PATH}")

        doc = acroform.AcroFormDocument.from_pdf(TEST_PDF_PATH)
        fields = doc.fields()

        values = {}
        for field in fields:
            if field.field_type == acroform.TEXT:
                values[field.name] = "Native String"
                break
            elif field.field_type == acroform.FieldType.Button:
                values[field.name] = True
                break

        if values:
            pdf_bytes = doc.fill(values)
            assert isinstance(pdf_bytes, bytes)
            assert len(pdf_bytes) > 0


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_get_pdf_fields(self):
        if not os.path.exists(TEST_PDF_PATH):
            pytest.skip(f"Test PDF not found: {TEST_PDF_PATH}")

        fields = acroform.get_pdf_fields(TEST_PDF_PATH)
        assert isinstance(fields, list)

    def test_get_pdf_fields_bytes(self):
        if not os.path.exists(TEST_PDF_PATH):
            pytest.skip(f"Test PDF not found: {TEST_PDF_PATH}")

        with open(TEST_PDF_PATH, "rb") as f:
            data = f.read()

        fields = acroform.get_pdf_fields_bytes(data)
        assert isinstance(fields, list)

    def test_fill_pdf_to_file(self):
        if not os.path.exists(TEST_PDF_PATH):
            pytest.skip(f"Test PDF not found: {TEST_PDF_PATH}")

        # Get a field to fill
        fields = acroform.get_pdf_fields(TEST_PDF_PATH)
        if not fields:
            pytest.skip("No fields in test PDF")

        text_field = None
        for field in fields:
            if field.field_type == acroform.TEXT:
                text_field = field.name
                break

        if not text_field:
            pytest.skip("No text fields in test PDF")

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = f.name

        try:
            result = acroform.fill_pdf(
                TEST_PDF_PATH, 
                {text_field: "Test"}, 
                output_path
            )
            assert result is None
            assert os.path.exists(output_path)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_fill_pdf_to_bytes(self):
        if not os.path.exists(TEST_PDF_PATH):
            pytest.skip(f"Test PDF not found: {TEST_PDF_PATH}")

        # Get a field to fill
        fields = acroform.get_pdf_fields(TEST_PDF_PATH)
        if not fields:
            pytest.skip("No fields in test PDF")

        text_field = None
        for field in fields:
            if field.field_type == acroform.TEXT:
                text_field = field.name
                break

        if not text_field:
            pytest.skip("No text fields in test PDF")

        result = acroform.fill_pdf(TEST_PDF_PATH, {text_field: "Test"})
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_fill_pdf_bytes(self):
        if not os.path.exists(TEST_PDF_PATH):
            pytest.skip(f"Test PDF not found: {TEST_PDF_PATH}")

        with open(TEST_PDF_PATH, "rb") as f:
            data = f.read()

        # Get a field to fill
        fields = acroform.get_pdf_fields_bytes(data)
        if not fields:
            pytest.skip("No fields in test PDF")

        text_field = None
        for field in fields:
            if field.field_type == acroform.TEXT:
                text_field = field.name
                break

        if not text_field:
            pytest.skip("No text fields in test PDF")

        result = acroform.fill_pdf_bytes(data, {text_field: "Test"})
        assert isinstance(result, bytes)
        assert len(result) > 0


class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_pdf(self):
        with pytest.raises(IOError):
            acroform.AcroFormDocument.from_pdf("not_a_pdf.txt")

    def test_invalid_bytes(self):
        with pytest.raises(IOError):
            acroform.AcroFormDocument.from_bytes(b"not a pdf")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
