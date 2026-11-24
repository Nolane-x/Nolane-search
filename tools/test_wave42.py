from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import wave42


class Wave42Tests(unittest.TestCase):
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

    def test_meal_shopping_list_scales_and_combines_ingredients(self):
        _, report = self.report(wave42.meal_shopping_list_planner, "meals", {
            "meals": [
                {"name": "Dinner", "servings": 2, "target_servings": 4, "ingredients": [
                    {"name": "Rice", "quantity": 200, "unit": "g", "category": "Pantry"},
                    {"name": "Chicken", "quantity": 300, "unit": "g", "category": "Meat"},
                ]},
                {"name": "Breakfast", "servings": 1, "target_servings": 1, "ingredients": [
                    {"name": "rice", "quantity": 100, "unit": "g", "category": "Pantry"},
                    {"name": "Eggs", "quantity": 2, "unit": "pcs", "category": "Dairy"},
                ]},
            ]
        })
        self.assertIn("Unique shopping items: 3", report)
        self.assertIn("500 g Rice", report)
        self.assertIn("600 g Chicken", report)
        self.assertIn("2 pcs Eggs", report)

    def test_trip_packing_checklist_uses_user_selected_climate_and_activities(self):
        _, report = self.report(wave42.travel_packing_checklist, "packing", {
            "days": 5, "nights": 4, "travelers": 2, "climate": "cold",
            "activities": ["hiking", "business"], "international": True,
        })
        self.assertIn("Trip length: 5 days / 4 nights", report)
        self.assertIn("2 × Warm layer / jacket", report)
        self.assertIn("2 × Hiking shoes", report)
        self.assertIn("2 × Passport / international travel document", report)
        self.assertIn("2 × Smart / formal outfit", report)

    def test_study_planner_schedules_by_deadline_within_daily_capacity(self):
        _, report = self.report(wave42.study_plan_scheduler, "study", {
            "start_date": "2026-11-24", "available_minutes_per_day": 60,
            "session_minutes": 50, "study_days": ["Tue", "Wed", "Thu"],
            "tasks": [
                {"name": "Physics revision", "due_date": "2026-11-26", "estimated_hours": 2, "priority": 4},
                {"name": "English vocabulary", "due_date": "2026-11-25", "estimated_hours": 0.5, "priority": 5},
            ],
        })
        self.assertIn("English vocabulary", report)
        self.assertIn("Physics revision", report)
        self.assertIn("Unscheduled tasks: 0", report)
        self.assertIn("Scheduled study time: 150 minutes", report)

    def test_weekly_chore_planner_distributes_tasks_between_people(self):
        _, report = self.report(wave42.weekly_chore_planner, "chores", {
            "people": ["Alex", "Sam"],
            "chores": [
                {"name": "Wash dishes", "times_per_week": 7, "duration_minutes": 20},
                {"name": "Vacuum", "times_per_week": 2, "duration_minutes": 30, "preferred_days": ["Sat", "Sun"]},
            ],
        })
        self.assertIn("Weekly household chore plan", report)
        self.assertIn("Wash dishes", report)
        self.assertIn("Vacuum", report)
        self.assertIn("Weekly workload by person", report)
        self.assertIn("Alex:", report)
        self.assertIn("Sam:", report)

    def test_subscription_cost_calculator_annualizes_mixed_billing_cycles(self):
        _, report = self.report(wave42.subscription_cost_calculator, "subscriptions", {
            "currency": "USD",
            "subscriptions": [
                {"name": "Music", "amount": 12, "billing_cycle": "monthly"},
                {"name": "Storage", "amount": 20, "billing_cycle": "quarterly"},
            ],
        })
        self.assertIn("Music: USD 12.00 / monthly", report)
        self.assertIn("Annualized: USD 144.00", report)
        self.assertIn("USD 224.00 per year", report)
        self.assertIn("USD 18.67 average per month", report)

    def test_commute_cost_calculator_handles_car_sharing_and_public_transport_pass(self):
        _, car = self.report(wave42.commute_cost_calculator, "car", {
            "mode": "car", "commute_days_per_month": 20, "currency": "VND",
            "distance_one_way_km": 10, "consumption_l_per_100km": 6.5,
            "fuel_price_per_litre": 25000, "parking_per_day": 30000, "people_sharing": 2,
        })
        self.assertIn("Fuel cost: VND 650000", car)
        self.assertIn("Total monthly commute cost: VND 1250000", car)
        self.assertIn("Estimated monthly cost per person: VND 625000", car)
        _, transit = self.report(wave42.commute_cost_calculator, "transit", {
            "mode": "public_transport", "commute_days_per_month": 20, "currency": "EUR",
            "round_trip_fare": 5, "monthly_pass_price": 75,
        })
        self.assertIn("Lower-cost option based on entered values: monthly pass", transit)
        self.assertIn("Estimated monthly transit cost: EUR 75.00", transit)

    def test_reading_plan_calculator_computes_pages_and_optional_time(self):
        _, report = self.report(wave42.reading_plan_calculator, "reading", {
            "pages_remaining": 420, "days_until_deadline": 14,
            "reading_days_per_week": 5, "pages_per_hour": 30,
        })
        self.assertIn("Reading sessions assumed: 10", report)
        self.assertIn("Suggested pace: about 42 pages per reading day", report)
        self.assertIn("Estimated reading time per session: about 84 minutes", report)

    def test_grocery_budget_planner_groups_costs_and_reports_remaining_budget(self):
        _, report = self.report(wave42.grocery_budget_planner, "groceries", {
            "currency": "VND", "budget": 100000,
            "items": [
                {"name": "Rice", "quantity": 2, "unit_price": 30000, "category": "Pantry"},
                {"name": "Milk", "quantity": 1, "unit_price": 25000, "category": "Dairy"},
            ],
        })
        self.assertIn("Estimated total: VND 85000", report)
        self.assertIn("Budget remaining: VND 15000", report)
        self.assertIn("Pantry: VND 60000", report)

    def test_rejects_invalid_study_deadline_subscription_cycle_and_duplicate_json_keys(self):
        bad_study = self.request("bad-study", {
            "start_date": "2026-11-24", "available_minutes_per_day": 60,
            "tasks": [{"name": "Late", "due_date": "2026-11-23", "estimated_hours": 1}],
        })
        with self.assertRaisesRegex(RuntimeError, "due_date"):
            wave42.study_plan_scheduler(bad_study)
        bad_subscription = self.request("bad-cycle", {
            "subscriptions": [{"name": "App", "amount": 5, "billing_cycle": "daily"}],
        })
        with self.assertRaisesRegex(RuntimeError, "billing_cycle"):
            wave42.subscription_cost_calculator(bad_subscription)
        duplicate = self.root / "duplicate.json"
        duplicate.write_text('{"budget":100,"budget":200}', encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "valid UTF-8 JSON"):
            wave42.grocery_budget_planner(duplicate)

    def test_rejects_overfilled_meal_and_invalid_commute_mode(self):
        bad_meal = self.request("bad-meal", {
            "meals": [{"name": "Soup", "servings": 0, "target_servings": 2,
                       "ingredients": [{"name": "Water", "quantity": 1, "unit": "L"}]}],
        })
        with self.assertRaisesRegex(RuntimeError, "servings"):
            wave42.meal_shopping_list_planner(bad_meal)
        bad_commute = self.request("bad-commute", {
            "mode": "teleport", "commute_days_per_month": 20, "currency": "VND",
        })
        with self.assertRaisesRegex(RuntimeError, "mode"):
            wave42.commute_cost_calculator(bad_commute)


if __name__ == "__main__":
    unittest.main()
