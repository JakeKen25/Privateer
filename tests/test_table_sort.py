import unittest

from privateer.table_sort import heading_text, sorted_with_blanks


class TableSortTests(unittest.TestCase):
    def test_numbers_sort_numerically_in_both_directions(self):
        rows = ["900", "19,100", "300", ""]
        self.assertEqual(sorted_with_blanks(rows, lambda row: row, numeric=True), ["300", "900", "19,100", ""])
        self.assertEqual(sorted_with_blanks(rows, lambda row: row, reverse=True, numeric=True),
                         ["19,100", "900", "300", ""])

    def test_text_is_case_insensitive_and_blanks_stay_last(self):
        rows = ["Zulu", "alpha", "Bravo", ""]
        self.assertEqual(sorted_with_blanks(rows, lambda row: row),
                         ["alpha", "Bravo", "Zulu", ""])
        self.assertEqual(sorted_with_blanks(rows, lambda row: row, reverse=True),
                         ["Zulu", "Bravo", "alpha", ""])

    def test_heading_indicates_active_direction(self):
        self.assertEqual(heading_text("Speed", False, False), "Speed")
        self.assertEqual(heading_text("Speed", True, False), "Speed ▲")
        self.assertEqual(heading_text("Speed", True, True), "Speed ▼")


if __name__ == "__main__":
    unittest.main()
