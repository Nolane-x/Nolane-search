from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import wave43


class Wave43Tests(unittest.TestCase):
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

    def test_habit_history_reports_streaks_and_window_adherence(self):
        _, report = self.report(wave43.habit_history_analyzer, "habits", {
            "as_of_date": "2026-11-24", "window_days": 7,
            "habits": [{
                "name": "Read", "target_days_per_week": 5,
                "check_ins": ["2026-11-21", "2026-11-22", "2026-11-23", "2026-11-24"],
            }],
        })
        self.assertIn("Check-ins in window: 4 / 5 target", report)
        self.assertIn("Target completion: 80%", report)
        self.assertIn("Current streak: 4 day(s)", report)
        self.assertIn("Longest recorded streak: 4 day(s)", report)

    def test_plant_care_scheduler_marks_overdue_tasks_without_making_care_claims(self):
        _, report = self.report(wave43.plant_care_scheduler, "plants", {
            "as_of_date": "2026-11-24", "window_days": 14,
            "plants": [{
                "name": "Monstera",
                "care_tasks": [
                    {"task": "Water", "last_done": "2026-11-20", "every_days": 3},
                    {"task": "Rotate pot", "last_done": "2026-11-22", "every_days": 14},
                ],
            }],
        })
        self.assertIn("2026-11-23 | Monstera | Water", report)
        self.assertIn("OVERDUE by 1 day(s)", report)
        self.assertIn("2026-12-06 | Monstera | Rotate pot", report)

    def test_garden_bed_capacity_uses_user_supplied_spacing(self):
        _, report = self.report(wave43.garden_bed_capacity_calculator, "garden", {
            "beds": [{
                "name": "Raised bed", "length_m": 2, "width_m": 1,
                "plant_spacing_cm": 30, "row_spacing_cm": 25,
            }],
        })
        self.assertIn("Rows: 4", report)
        self.assertIn("Plants per row: 6", report)
        self.assertIn("Estimated capacity: 24 plant(s)", report)
        self.assertIn("Estimated total planting capacity: 24 plant(s)", report)

    def test_home_inventory_reports_currency_totals_and_warranty_dates(self):
        _, report = self.report(wave43.home_inventory_report, "inventory", {
            "as_of_date": "2026-11-24", "currency": "USD",
            "items": [{
                "name": "Laptop", "category": "Electronics", "quantity": 2,
                "purchase_price_per_item": 100, "purchase_date": "2025-11-24",
                "warranty_months": 12, "expected_life_months": 24,
                "location": "Desk",
            }],
        })
        self.assertIn("USD 200.00", report)
        self.assertIn("Warranty: active; through 2026-11-24", report)
        self.assertIn("Expected service-life date entered by user: 2027-11-24", report)
        self.assertIn("Location: Desk", report)

    def test_home_maintenance_scheduler_finds_overdue_and_next_cycle(self):
        _, report = self.report(wave43.home_maintenance_scheduler, "maintenance", {
            "as_of_date": "2026-11-24", "window_days": 60,
            "tasks": [{
                "name": "Clean air filter", "last_completed": "2026-10-24",
                "every_days": 30, "estimated_minutes": 20, "priority": 4,
            }],
        })
        self.assertIn("OVERDUE since 2026-11-23 by 1 day(s)", report)
        self.assertIn("next cycle 2026-12-23", report)

    def test_pet_routine_planner_generates_weekday_checklists(self):
        _, report = self.report(wave43.pet_routine_planner, "pets", {
            "start_date": "2026-11-24", "days": 4,
            "pets": [{
                "name": "Milo",
                "routines": [
                    {"task": "Walk", "time": "08:00", "days_of_week": ["Tue", "Thu"], "note": "Short walk"},
                    {"task": "Brush", "time": "18:00", "days_of_week": ["Wed"]},
                ],
            }],
        })
        self.assertIn("2026-11-24 (Tue)", report)
        self.assertIn("08:00 | Milo | Walk", report)
        self.assertIn("2026-11-25 (Wed)", report)
        self.assertIn("18:00 | Milo | Brush", report)
        self.assertIn("2026-11-26 (Thu)", report)

    def test_event_seating_planner_keeps_groups_together_and_respects_avoid_pairs(self):
        _, report = self.report(wave43.event_seating_planner, "seating", {
            "tables": [{"name": "Table A", "seats": 4}, {"name": "Table B", "seats": 2}],
            "guest_groups": [
                {"name": "Family", "guests": ["Alice", "Ben"]},
                {"name": "Friends", "guests": ["Cara", "Dan"]},
                {"name": "Solo", "guests": ["Eli"]},
            ],
            "avoid_pairs": [["Alice", "Cara"]],
        })
        self.assertIn("Assigned guests: 5/5", report)
        self.assertIn("Table A", report)
        self.assertIn("Alice", report)
        self.assertIn("Cara", report)
        self.assertIn("Unassigned guests: 0", report)

    def test_spaced_review_scheduler_uses_confidence_intervals_and_overdue_status(self):
        _, report = self.report(wave43.spaced_review_scheduler, "review", {
            "as_of_date": "2026-11-24", "planning_days": 14,
            "topics": [
                {"name": "Chemistry", "last_reviewed": "2026-11-20", "confidence": 3},
                {"name": "History", "last_reviewed": "2026-11-01", "confidence": 5},
            ],
        })
        self.assertIn("2026-11-24 | Chemistry | confidence 3/5 | interval 4 day(s) | Review today", report)
        self.assertIn("OVERDUE by 9 day(s)", report)
        self.assertIn("simple planner, not the FSRS algorithm", report)

    def test_rejects_duplicate_guests_and_future_habit_checkins(self):
        duplicate_guests = self.request("duplicate-guests", {
            "tables": [{"name": "A", "seats": 4}],
            "guest_groups": [
                {"name": "One", "guests": ["Alice"]},
                {"name": "Two", "guests": ["alice"]},
            ],
        })
        with self.assertRaisesRegex(RuntimeError, "Guest appears more than once"):
            wave43.event_seating_planner(duplicate_guests)
        future = self.request("future-checkin", {
            "as_of_date": "2026-11-24",
            "habits": [{"name": "Read", "check_ins": ["2026-11-25"]}],
        })
        with self.assertRaisesRegex(RuntimeError, "cannot be after"):
            wave43.habit_history_analyzer(future)

    def test_rejects_invalid_plant_interval_pet_time_and_spacing(self):
        bad_plant = self.request("bad-plant", {
            "as_of_date": "2026-11-24",
            "plants": [{"name": "Fern", "care_tasks": [{"task": "Water", "last_done": "2026-11-20", "every_days": 0}]}],
        })
        with self.assertRaisesRegex(RuntimeError, "every_days"):
            wave43.plant_care_scheduler(bad_plant)
        bad_pet = self.request("bad-pet", {
            "start_date": "2026-11-24", "pets": [
                {"name": "Milo", "routines": [{"task": "Walk", "time": "25:99"}]},
            ],
        })
        with self.assertRaisesRegex(RuntimeError, "HH:MM"):
            wave43.pet_routine_planner(bad_pet)
        bad_garden = self.request("bad-garden", {
            "beds": [{"name": "Box", "length_m": 1, "width_m": 1, "plant_spacing_cm": 10, "row_spacing_cm": 10, "edge_margin_cm": 60}],
        })
        with self.assertRaisesRegex(RuntimeError, "no usable planting area"):
            wave43.garden_bed_capacity_calculator(bad_garden)


if __name__ == "__main__":
    unittest.main()
