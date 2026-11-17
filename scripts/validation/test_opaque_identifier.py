"""Tests for the CSPRNG-backed opaque identifier generator."""
import unittest
from unittest.mock import patch

from opaque_identifier import generate_opaque_id, is_canonical_opaque_id


class OpaqueIdentifierTests(unittest.TestCase):
    def test_generated_identifier_is_canonical_uuid4(self):
        value = generate_opaque_id()
        self.assertTrue(is_canonical_opaque_id(value))

    def test_generated_identifiers_are_unique_in_a_large_sample(self):
        values = [generate_opaque_id() for _ in range(10_000)]
        self.assertEqual(len(values), len(set(values)))
        self.assertTrue(all(is_canonical_opaque_id(value) for value in values))

    def test_generator_sets_uuid4_version_and_rfc_variant_bits(self):
        with patch("opaque_identifier.secrets.token_bytes", return_value=bytes(16)):
            self.assertEqual(generate_opaque_id(), "00000000-0000-4000-8000-000000000000")

    def test_generator_rejects_wrong_random_source_length(self):
        with patch("opaque_identifier.secrets.token_bytes", return_value=bytes(15)):
            with self.assertRaisesRegex(RuntimeError, "exactly 16 bytes"):
                generate_opaque_id()

    def test_validator_rejects_noncanonical_or_non_uuid4_values(self):
        for value in (None, 7, "not-a-uuid", "00000000-0000-0000-0000-000000000000",
                      "00000000-0000-4000-8000-00000000000A"):
            self.assertFalse(is_canonical_opaque_id(value))


if __name__ == "__main__":
    unittest.main(verbosity=2)
