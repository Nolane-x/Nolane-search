from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import wave44


class Wave44Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def request(self, name, value):
        path = self.root / (name + ".json")
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return path

    def report(self, fn, name, value):
        result = fn(self.request(name, value))
        return result, Path(result["output_path"]).read_text(encoding="utf-8")

    def test_pantry_use_first_sorts_dates_and_avoids_safety_claims(self):
        _, output = self.report(wave44.pantry_use_first_planner, "pantry", {
            "as_of_date": "2026-11-24", "window_days": 10,
            "items": [
                {"name": "Rice", "date": "2027-01-01", "date_type": "best_before", "quantity": 2, "unit": "kg"},
                {"name": "Milk", "date": "2026-11-24", "date_type": "use_by", "location": "Fridge"},
                {"name": "Yogurt", "date": "2026-11-20", "date_type": "expiry"},
            ],
        })
        self.assertLess(output.index("Yogurt"), output.index("Milk"))
        self.assertLess(output.index("Milk"), output.index("Rice"))
        self.assertIn("does not determine whether food is safe", output)
        self.assertIn("Check the package instructions", output)

    def test_recipe_matcher_ranks_full_matches_before_missing_ingredients(self):
        _, output = self.report(wave44.pantry_recipe_matcher, "recipes", {
            "available_ingredients": ["Rice", "Egg", "Scallion"],
            "pantry_staples": ["Salt"],
            "recipes": [
                {"name": "Soup", "ingredients": ["Rice", "Egg", "Salt"]},
                {"name": "Fried rice", "ingredients": ["Rice", "Egg", "Scallion", "Salt"]},
                {"name": "Cake", "ingredients": ["Flour", "Sugar", "Egg"]},
            ],
        })
        self.assertLess(output.index("Fried rice"), output.index("Soup"))
        self.assertIn("Ready from listed ingredients", output)
        self.assertIn("Missing: flour, sugar", output)
        self.assertIn("aliases and substitutions are not guessed", output)

    def test_meal_prep_timeline_allows_passive_appliance_work_in_parallel(self):
        _, output = self.report(wave44.meal_prep_timeline_planner, "prep", {
            "start_time": "16:00",
            "tasks": [
                {"id": "chop", "name": "Chop vegetables", "duration_minutes": 10, "resource": "hands"},
                {"id": "bake", "name": "Bake vegetables", "duration_minutes": 20, "resource": "oven",
                 "attention_required": False},
                {"id": "salad", "name": "Prepare salad", "duration_minutes": 10, "resource": "hands",
                 "depends_on": ["chop"]},
                {"id": "plate", "name": "Plate dinner", "duration_minutes": 5, "resource": "hands",
                 "depends_on": ["bake", "salad"]},
            ],
        })
        self.assertIn("16:00–16:20 | Bake vegetables", output)
        self.assertIn("16:10–16:20 | Prepare salad", output)
        self.assertIn("Estimated finish: 16:25", output)

    def test_meal_prep_rejects_dependency_cycles(self):
        bad = self.request("cycle", {"start_time": "17:00", "tasks": [
            {"id": "a", "name": "A", "duration_minutes": 10, "depends_on": ["b"]},
            {"id": "b", "name": "B", "duration_minutes": 10, "depends_on": ["a"]},
        ]})
        with self.assertRaisesRegex(RuntimeError, "cycle"):
            wave44.meal_prep_timeline_planner(bad)

    def test_laundry_groups_compatible_items_and_respects_care_maximums(self):
        _, output = self.report(wave44.laundry_load_organizer, "laundry", {
            "machine_capacity_kg": 5, "target_temp_c": 40,
            "items": [
                {"name": "White shirt", "weight_kg": 0.3, "color_group": "white", "fabric_group": "normal", "drying": "air", "max_temp_c": 60},
                {"name": "White towel", "weight_kg": 1.2, "color_group": "white", "fabric_group": "towel", "drying": "tumble", "max_temp_c": 60},
                {"name": "Dark wool", "weight_kg": 0.8, "color_group": "dark", "fabric_group": "wool", "drying": "flat", "max_temp_c": 20},
                {"name": "Red shirt", "weight_kg": 0.4, "color_group": "bright", "fabric_group": "normal", "drying": "air", "max_temp_c": 30},
            ],
        })
        self.assertIn("white | normal", output)
        self.assertIn("dark | wool | dry: flat | wash at up to 20°C", output)
        self.assertIn("bright | normal | dry: air | wash at up to 30°C", output)
        self.assertIn("white | towel", output)
        self.assertNotIn("White towel", output.split("white | normal")[0])

    def test_trip_itinerary_marks_stops_that_do_not_fit(self):
        _, output = self.report(wave44.trip_itinerary_planner, "trip", {
            "start_time": "09:00", "end_time": "12:00",
            "stops": [
                {"name": "Museum", "travel_minutes_from_previous": 20, "duration_minutes": 90},
                {"name": "Park", "travel_minutes_from_previous": 15, "duration_minutes": 75},
                {"name": "Market", "travel_minutes_from_previous": 10, "duration_minutes": 60},
            ],
        })
        self.assertIn("09:00–09:20 | Travel to Museum", output)
        self.assertNotIn("Travel to Park", output)
        self.assertIn("Stops that do not fit", output)
        self.assertIn("- Park", output)
        self.assertIn("- Market", output)

    def test_vehicle_maintenance_uses_user_entered_date_and_odometer_intervals(self):
        _, output = self.report(wave44.vehicle_maintenance_planner, "vehicle", {
            "as_of_date": "2026-11-24", "current_odometer_km": 10000,
            "estimated_monthly_km": 1000, "window_days": 180,
            "maintenance": [
                {"name": "Engine oil", "last_service_date": "2026-10-24",
                 "last_service_odometer_km": 5000, "interval_months": 12, "interval_km": 5000},
            ],
        })
        self.assertIn("Engine oil", output)
        self.assertIn("odometer trigger: 10,000 km (0 km remaining)", output)
        self.assertIn("DUE NOW / OVERDUE", output)
        self.assertIn("not a substitute for manufacturer guidance", output)

    def test_document_renewal_respects_custom_notice_window(self):
        _, output = self.report(wave44.document_renewal_planner, "documents", {
            "as_of_date": "2026-11-24", "window_days": 90,
            "documents": [
                {"name": "Passport", "expiry_date": "2027-01-15", "remind_days_before": 60},
                {"name": "Insurance", "expiry_date": "2026-10-01", "remind_days_before": 30},
            ],
        })
        self.assertIn("Passport | Start/check renewal now | check renewal from 2026-11-16", output)
        self.assertIn("Insurance | EXPIRED", output)
        self.assertIn("Confirm current requirements", output)

    def test_warranty_assistant_drafts_request_and_labels_estimate(self):
        _, output = self.report(wave44.warranty_claim_assistant, "warranty", {
            "as_of_date": "2026-11-24", "product_name": "Laptop", "seller": "Example Store",
            "purchase_date": "2025-01-31", "warranty_months": 24,
            "issue_description": "The display flickers after startup.",
            "evidence": ["Purchase receipt", "Short video"], "language": "vi",
        })
        self.assertIn("Ngày kết thúc ước tính theo phép cộng tháng: 2027-01-31", output)
        self.assertIn("Bản nháp yêu cầu kiểm tra bảo hành", output)
        self.assertIn("Purchase receipt", output)
        self.assertIn("đối chiếu phiếu bảo hành", output)

    def test_rejects_duplicate_keys_invalid_time_and_bad_item_bounds(self):
        duplicate = self.root / "duplicate.json"
        duplicate.write_text('{"as_of_date":"2026-11-24","as_of_date":"2026-11-25","items":[]}', encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "valid UTF-8 JSON object"):
            wave44.pantry_use_first_planner(duplicate)
        bad_time = self.request("bad-time", {"start_time": "25:61", "tasks": [
            {"name": "Mix", "duration_minutes": 5},
        ]})
        with self.assertRaisesRegex(RuntimeError, "HH:MM"):
            wave44.meal_prep_timeline_planner(bad_time)
        bad_laundry = self.request("bad-laundry", {"machine_capacity_kg": 5, "items": [
            {"name": "Shirt", "weight_kg": 0.3, "color_group": "white", "fabric_group": "normal", "drying": "air", "max_temp_c": 95},
        ]})
        with self.assertRaisesRegex(RuntimeError, "max_temp_c"):
            wave44.laundry_load_organizer(bad_laundry)


if __name__ == "__main__":
    unittest.main()
