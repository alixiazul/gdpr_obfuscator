import pytest
from gdpr_obfuscator.obfuscator import Obfuscator

class TestObfuscator:

    def test_obfuscator_with_no_arguments_has_empty_pii_fields(self):
        obfuscator = Obfuscator()
        assert obfuscator.pii_fields == []

    def test_obfuscator_has_empty_pii_fields(self):
        pii_fields = []
        obfuscator = Obfuscator(pii_fields)
        assert obfuscator.pii_fields == pii_fields

    def test_obfuscator_has_pii_fields(self):
        pii_fields = ["name", "email_address"]
        obfuscator = Obfuscator(pii_fields)
        assert obfuscator.pii_fields == pii_fields