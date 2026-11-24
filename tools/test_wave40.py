from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import wave40


class Wave40Tests(unittest.TestCase):
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

    def test_appliance_energy_calculates_monthly_kwh_and_cost(self):
        result, report = self.report(wave40.appliance_energy_calculator, "energy", {
            "price_per_kwh": 2000, "currency": "VND",
            "appliances": [{"name": "Fan", "watts": 100, "hours_per_day": 5, "days_per_month": 30}],
        })
        self.assertIn("Total monthly energy: 15 kWh", report)
        self.assertIn("Estimated monthly cost: VND 30000", report)
        self.assertIn("15 kWh", result["summary"])

    def test_floor_tile_estimator_rounds_up_tiles_boxes_and_cost(self):
        _, report = self.report(wave40.floor_tile_calculator, "tiles", {
            "room_length_m": 3, "room_width_m": 4,
            "tile_length_cm": 60, "tile_width_cm": 60,
            "waste_percent": 10, "tiles_per_box": 4,
            "price_per_box": 150000, "currency": "VND",
        })
        self.assertIn("Tiles required including waste: 37", report)
        self.assertIn("Boxes to buy: 10 (40 tiles)", report)
        self.assertIn("Estimated material cost: VND 1500000", report)

    def test_concrete_estimator_includes_waste_and_bag_yield(self):
        _, report = self.report(wave40.concrete_volume_calculator, "concrete", {
            "length_m": 2, "width_m": 3, "depth_m": 0.15,
            "waste_percent": 10, "bag_yield_l": 40,
            "price_per_bag": 80000, "currency": "VND",
        })
        self.assertIn("Order estimate: 0.99 m³ (990 litres)", report)
        self.assertIn("Bags required: 25", report)
        self.assertIn("Estimated bag cost: VND 2000000", report)

    def test_soil_calculator_computes_volume_and_bag_count(self):
        _, report = self.report(wave40.soil_mulch_calculator, "soil", {
            "area_m2": 10, "depth_cm": 5, "waste_percent": 10,
            "bag_volume_l": 50, "price_per_bag": 30000, "currency": "VND",
        })
        self.assertIn("Base volume: 500 litres (0.5 m³)", report)
        self.assertIn("Order estimate: 550 litres (0.55 m³)", report)
        self.assertIn("Bags required: 11", report)
        self.assertIn("Estimated bag cost: VND 330000", report)

    def test_household_budget_groups_expenses_and_calculates_surplus(self):
        _, report = self.report(wave40.household_budget_calculator, "budget", {
            "monthly_income": 20000000, "currency": "VND",
            "expenses": [
                {"name": "Rent", "category": "Needs", "monthly_amount": 6000000},
                {"name": "Groceries", "category": "Needs", "monthly_amount": 4000000},
                {"name": "Entertainment", "category": "Wants", "monthly_amount": 2000000},
            ],
        })
        self.assertIn("Planned expenses: VND 12000000", report)
        self.assertIn("- Needs: VND 10000000 (50% of income)", report)
        self.assertIn("Money remaining: VND 8000000", report)

    def test_savings_goal_calculates_months_without_interest(self):
        result, report = self.report(wave40.savings_goal_calculator, "savings", {
            "target_amount": 1000, "current_savings": 100, "monthly_contribution": 100,
            "annual_interest_rate_percent": 0, "currency": "USD",
        })
        self.assertIn("Estimated time: 9 months (0 years and 9 months)", report)
        self.assertIn("Estimated balance at that point: USD 1000", report)
        self.assertIn("9 months", result["summary"])

    def test_savings_goal_handles_interest_and_already_met_target(self):
        _, report = self.report(wave40.savings_goal_calculator, "savings-interest", {
            "target_amount": 10000, "current_savings": 1000, "monthly_contribution": 100,
            "annual_interest_rate_percent": 5, "currency": "USD",
        })
        self.assertIn("Estimated time:", report)
        _, already = self.report(wave40.savings_goal_calculator, "savings-met", {
            "target_amount": 500, "current_savings": 500, "monthly_contribution": 0,
            "annual_interest_rate_percent": 0, "currency": "USD",
        })
        self.assertIn("Estimated time: 0 months", already)

    def test_travel_budget_adds_buffer_and_per_person_breakdown(self):
        _, report = self.report(wave40.travel_budget_calculator, "travel", {
            "travelers": 3, "days": 5, "buffer_percent": 10, "currency": "USD",
            "expenses": [
                {"category": "Hotel", "total_cost": 1200},
                {"category": "Food", "total_cost": 600},
                {"category": "Transport", "total_cost": 300},
            ],
        })
        self.assertIn("Base trip budget: USD 2100", report)
        self.assertIn("Budget including buffer: USD 2310", report)
        self.assertIn("Per person: USD 770", report)
        self.assertIn("Per person per day: USD 154", report)

    def test_download_time_uses_bits_and_bytes_correctly(self):
        _, report = self.report(wave40.download_time_calculator, "download", {
            "file_size": 1, "file_size_unit": "GB",
            "speed": 100, "speed_unit": "Mbps", "overhead_percent": 10,
        })
        self.assertIn("Seconds: 88", report)
        self.assertIn("Estimated time: 0 h 1 min 28 sec", report)

    def test_work_hours_handles_overnight_shift_and_breaks(self):
        _, report = self.report(wave40.work_hours_calculator, "work", {
            "hourly_rate": 100000, "currency": "VND",
            "shifts": [
                {"label": "Day shift", "start": "09:00", "end": "17:00", "break_minutes": 60},
                {"label": "Night shift", "start": "22:00", "end": "02:00", "break_minutes": 15},
            ],
        })
        self.assertIn("Total paid hours: 10.75", report)
        self.assertIn("Estimated gross pay: VND 1075000", report)

    def test_battery_runtime_converts_mah_voltage_to_wh(self):
        _, report = self.report(wave40.battery_runtime_calculator, "battery", {
            "capacity_mah": 10000, "voltage_v": 3.7, "device_power_w": 5,
            "efficiency_percent": 80, "reserve_percent": 10,
        })
        self.assertIn("Nominal energy: 37 Wh", report)
        self.assertIn("Usable energy estimate: 26.64 Wh", report)
        self.assertIn("Estimated runtime: 5 h 19 min", report)

    def test_water_tank_rectangular_and_cylinder_shapes(self):
        _, rect = self.report(wave40.water_tank_volume_calculator, "tank-rect", {
            "shape": "rectangular", "length_m": 2, "width_m": 1.5,
            "height_m": 1, "fill_percent": 50,
        })
        self.assertIn("Full capacity: 3000 litres (3 m³)", rect)
        self.assertIn("Water at this fill level: 1500 litres", rect)
        _, cylinder = self.report(wave40.water_tank_volume_calculator, "tank-cylinder", {
            "shape": "cylinder", "radius_m": 0.5, "height_m": 1,
        })
        self.assertIn("Full capacity: 785.4 litres", cylinder)

    def test_rejects_invalid_work_time_and_mismatched_optional_parameters(self):
        bad_work = self.request("bad-work", {
            "hourly_rate": 100, "shifts": [{"start": "09:00", "end": "09:00", "break_minutes": 0}],
        })
        with self.assertRaisesRegex(RuntimeError, "less than 24 hours"):
            wave40.work_hours_calculator(bad_work)
        bad_tank = self.request("bad-tank", {"shape": "triangle"})
        with self.assertRaisesRegex(RuntimeError, "shape must be"):
            wave40.water_tank_volume_calculator(bad_tank)

    def test_rejects_duplicate_json_keys_and_unknown_download_units(self):
        duplicate = self.root / "duplicate.json"
        duplicate.write_text('{"file_size":1,"file_size":2}', encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "valid UTF-8 JSON"):
            wave40.download_time_calculator(duplicate)
        bad_units = self.request("bad-units", {
            "file_size": 1, "file_size_unit": "bucket", "speed": 1, "speed_unit": "Mbps",
        })
        with self.assertRaisesRegex(RuntimeError, "file_size_unit"):
            wave40.download_time_calculator(bad_units)


if __name__ == "__main__":
    unittest.main()
