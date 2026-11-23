from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

import wave39


class Wave39Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def request(self, name, value):
        path = self.root / (name + ".json")
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return path

    def test_bill_split_applies_tax_and_tip_then_rounds_remainder(self):
        path = self.request("bill", {
            "bill_amount": 100, "tax_percent": 10, "tip_percent": 10,
            "people": 3, "currency": "USD",
        })
        result = wave39.bill_split_calculator(path)
        report = Path(result["output_path"]).read_text()
        self.assertIn("Total bill: 120", report)
        self.assertIn("Final person's adjusted share: 40", report)

    def test_loan_zero_interest_and_extra_payment_exports_schedule(self):
        path = self.request("loan", {
            "principal": 1200, "annual_rate_percent": 0, "term_months": 12,
            "extra_monthly_payment": 0, "currency": "USD",
        })
        result = wave39.loan_payment_calculator(path)
        with Path(result["output_path"]).open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 12)
        self.assertEqual(rows[0]["payment"], "100")
        self.assertEqual(rows[-1]["closing_balance"], "0")
        self.assertIn("total interest USD 0", result["summary"])

    def test_date_calculator_counts_elapsed_and_weekdays(self):
        path = self.request("dates", {
            "start_date": "2026-11-20", "end_date": "2026-11-23",
            "include_end_date": True,
        })
        report = Path(wave39.date_calculator(path)["output_path"]).read_text()
        self.assertIn("Elapsed days (end minus start): 3", report)
        self.assertIn("Weekdays in range: 2", report)

    def test_timezone_converter_shows_both_ambiguous_dst_times(self):
        path = self.request("timezone", {
            "local_datetime": "2026-11-01T01:30:00",
            "from_timezone": "America/New_York",
            "to_timezone": "Asia/Ho_Chi_Minh",
        })
        report = Path(wave39.timezone_converter(path)["output_path"]).read_text()
        self.assertIn("Possible interpretation 1", report)
        self.assertIn("Possible interpretation 2", report)
        self.assertIn("daylight-saving transition", report)

    def test_timezone_converter_rejects_nonexistent_dst_time(self):
        path = self.request("timezone-gap", {
            "local_datetime": "2026-03-08T02:30:00",
            "from_timezone": "America/New_York",
            "to_timezone": "Asia/Ho_Chi_Minh",
        })
        with self.assertRaisesRegex(RuntimeError, "does not exist"):
            wave39.timezone_converter(path)

    def test_recipe_scaler_preserves_to_taste_and_scales_amounts(self):
        path = self.request("recipe", {
            "original_servings": 2, "target_servings": 4,
            "ingredients": [
                {"name": "flour", "amount": 250, "unit": "g"},
                {"name": "salt", "amount": "to taste", "unit": ""},
            ],
        })
        report = Path(wave39.recipe_scaler(path)["output_path"]).read_text()
        self.assertIn("500 g flour", report)
        self.assertIn("to taste", report)

    def test_grade_calculator_reports_required_average_on_remaining_weight(self):
        path = self.request("grade", {
            "components": [
                {"name": "Homework", "score": 80, "max_score": 100, "weight_percent": 40},
                {"name": "Midterm", "score": 90, "max_score": 100, "weight_percent": 30},
            ],
            "target_overall_percent": 87,
        })
        report = Path(wave39.grade_calculator(path)["output_path"]).read_text()
        self.assertIn("Remaining weight: 30%", report)
        self.assertIn("Required average across the remaining 30%: 93.33%", report)

    def test_paint_calculator_calculates_wall_area_and_half_litre_rounding(self):
        path = self.request("paint", {
            "length_m": 4, "width_m": 3, "height_m": 2.5,
            "doors_count": 1, "door_area_m2": 2,
            "windows_count": 1, "window_area_m2": 1.5,
            "coats": 2, "coverage_m2_per_liter": 10, "waste_percent": 10,
        })
        report = Path(wave39.paint_calculator(path)["output_path"]).read_text()
        self.assertIn("Gross wall area: 35 m²", report)
        self.assertIn("Paintable area: 31.5 m²", report)
        self.assertIn("Estimated paint: 6.93 litres", report)
        self.assertIn("Practical purchase estimate: about 7 litres", report)

    def test_fuel_trip_calculator_handles_round_trip_and_per_person_cost(self):
        path = self.request("fuel", {
            "distance_km": 120, "round_trip": True, "trips": 1,
            "consumption_l_per_100km": 6, "fuel_price_per_liter": 25000,
            "passengers": 3, "currency": "VND",
        })
        report = Path(wave39.fuel_trip_calculator(path)["output_path"]).read_text()
        self.assertIn("Total distance: 240 km", report)
        self.assertIn("Estimated fuel: 14.4 L", report)
        self.assertIn("Estimated fuel cost: VND 360000", report)
        self.assertIn("Estimated cost per passenger: VND 120000", report)

    def test_discount_calculator_applies_sequential_discounts_before_tax(self):
        path = self.request("discount", {
            "original_price": 100, "discount_percent": 20,
            "extra_discount_percent": 10, "tax_percent": 10,
            "quantity": 2, "currency": "USD",
        })
        report = Path(wave39.discount_calculator(path)["output_path"]).read_text()
        self.assertIn("Price after discounts: USD 72", report)
        self.assertIn("Final unit price including tax: USD 79.2", report)
        self.assertIn("Total for quantity: USD 158.4", report)

    def test_unit_price_comparator_normalizes_grams_to_kilograms(self):
        path = self.request("unit-price", {
            "currency": "VND",
            "items": [
                {"name": "Small pack", "price": 25000, "quantity": 500, "unit": "g"},
                {"name": "Large pack", "price": 46000, "quantity": 1, "unit": "kg"},
            ],
        })
        report = Path(wave39.unit_price_comparator(path)["output_path"]).read_text()
        self.assertIn("Large pack", report.split("Best unit price: ")[1])
        self.assertIn("VND 46 per g", report)
        self.assertIn("VND 50 per g", report)

    def test_rejects_duplicate_json_keys_and_mixed_comparison_units(self):
        duplicate = self.root / "duplicate.json"
        duplicate.write_text('{"bill_amount":10,"bill_amount":20}', encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "valid UTF-8 JSON"):
            wave39.bill_split_calculator(duplicate)
        mixed = self.request("mixed", {"items": [
            {"name": "Weight", "price": 5, "quantity": 1, "unit": "kg"},
            {"name": "Volume", "price": 5, "quantity": 1, "unit": "L"},
        ]})
        with self.assertRaisesRegex(RuntimeError, "same dimension"):
            wave39.unit_price_comparator(mixed)


if __name__ == "__main__":
    unittest.main()
