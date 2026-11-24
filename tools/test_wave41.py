from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import wave41


class Wave41Tests(unittest.TestCase):
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

    def test_water_bill_uses_meter_difference_and_user_entered_rate(self):
        _, report = self.report(wave41.water_bill_calculator, "water", {
            "previous_reading_m3": 120.5, "current_reading_m3": 128.5,
            "price_per_m3": 10000, "fixed_charge": 5000,
            "sewage_percent": 10, "currency": "VND",
        })
        self.assertIn("Water used: 8 m³", report)
        self.assertIn("Water charge: VND 80000", report)
        self.assertIn("Estimated bill: VND 93000", report)

    def test_mobile_data_duration_and_reset_daily_budget(self):
        _, report = self.report(wave41.mobile_data_duration_calculator, "data", {
            "allowance_gb": 20, "used_gb": 5, "daily_usage_gb": 1.5,
            "reserve_percent": 10, "days_until_reset": 10,
        })
        self.assertIn("Usable data: 13.5 GB", report)
        self.assertIn("Estimated duration at this usage: 9 days", report)
        self.assertIn("Suggested average daily limit to last until reset: 1.35 GB/day", report)
        self.assertIn("above that average daily limit", report)

    def test_solar_output_with_user_entered_peak_sun_and_loss(self):
        _, report = self.report(wave41.solar_panel_output_calculator, "solar", {
            "panel_watts": 500, "panel_count": 4, "peak_sun_hours_per_day": 4.5,
            "system_loss_percent": 20, "days": 30,
            "price_per_kwh": 2500, "currency": "VND",
        })
        self.assertIn("System size: 2 kW", report)
        self.assertIn("Estimated daily energy: 7.2 kWh", report)
        self.assertIn("Estimated energy over 30 days: 216 kWh", report)
        self.assertIn("Illustrative value at user-entered rate: VND 540000", report)

    def test_wallpaper_estimates_strips_pattern_drop_and_spare_roll(self):
        _, report = self.report(wave41.wallpaper_roll_calculator, "wallpaper", {
            "room_perimeter_m": 12, "wall_height_m": 2.5,
            "roll_width_m": 0.53, "roll_length_m": 10,
            "pattern_repeat_cm": 53, "extra_rolls": 1,
        })
        self.assertIn("Adjusted drop length: 2.65 m", report)
        self.assertIn("Vertical strips required: 23", report)
        self.assertIn("Usable drops per roll: 3", report)
        self.assertIn("Suggested rolls to buy: 9", report)

    def test_curtain_fabric_accounts_for_fullness_hem_and_pattern_repeat(self):
        _, report = self.report(wave41.curtain_fabric_calculator, "curtain", {
            "window_width_cm": 200, "window_height_cm": 240, "fabric_width_cm": 140,
            "fullness_ratio": 2, "side_allowance_cm": 30,
            "top_hem_cm": 10, "bottom_hem_cm": 20, "pattern_repeat_cm": 40,
        })
        self.assertIn("Panels/cuts required: 4", report)
        self.assertIn("Cut/drop length per panel: 280 cm", report)
        self.assertIn("Total fabric length: 11.2 metres", report)

    def test_moving_boxes_estimates_boxes_and_extra_allowance(self):
        _, report = self.report(wave41.moving_box_calculator, "moving", {
            "items_volume_m3": 8, "box_volume_l": 60,
            "usable_fill_percent": 75, "extra_boxes_percent": 10,
        })
        self.assertIn("Base boxes: 178", report)
        self.assertIn("Suggested boxes: 196", report)

    def test_event_food_and_drink_calculator_adds_buffer(self):
        _, report = self.report(wave41.event_food_calculator, "event", {
            "guests": 25, "food_grams_per_person": 250, "drink_ml_per_person": 500,
            "snack_grams_per_person": 50, "extra_percent": 10,
        })
        self.assertIn("Main food: 6.88 kg", report)
        self.assertIn("Drinks: 13.75 litres", report)
        self.assertIn("Snacks: 1.38 kg", report)

    def test_fuel_economy_calculates_consumption_and_trip_cost(self):
        _, report = self.report(wave41.fuel_economy_calculator, "fuel", {
            "distance_km": 400, "fuel_litres": 32,
            "price_per_litre": 25000, "currency": "VND",
        })
        self.assertIn("Average consumption: 8 L/100 km", report)
        self.assertIn("Equivalent economy: 12.5 km/L", report)
        self.assertIn("Estimated fuel cost: VND 800000", report)
        self.assertIn("Fuel cost per kilometre: VND 2000", report)

    def test_gas_cylinder_runtime_and_daily_usage(self):
        _, report = self.report(wave41.gas_cylinder_runtime_calculator, "gas", {
            "gas_weight_kg": 12, "consumption_grams_per_hour": 150,
            "reserve_percent": 10, "hours_per_day": 3,
        })
        self.assertIn("Usable gas estimate: 10800 g", report)
        self.assertIn("Estimated runtime: 72 hours", report)
        self.assertIn("about 24 days", report)

    def test_shipping_volumetric_weight_uses_greater_of_actual_and_dimensional(self):
        _, report = self.report(wave41.shipping_volumetric_weight_calculator, "shipping", {
            "length_cm": 50, "width_cm": 40, "height_cm": 30,
            "actual_weight_kg": 8, "volumetric_divisor": 5000,
            "price_per_kg": 20000, "currency": "VND",
        })
        self.assertIn("Volumetric weight: 12 kg", report)
        self.assertIn("Estimated billable weight: 12 kg", report)
        self.assertIn("Illustrative shipping charge at entered rate: VND 240000", report)

    def test_storage_capacity_estimates_photos_video_and_documents(self):
        _, report = self.report(wave41.storage_capacity_calculator, "storage", {
            "capacity_gb": 128, "reserve_percent": 10,
            "photo_size_mb": 4, "video_size_mb_per_minute": 150,
            "document_size_mb": 1,
        })
        self.assertIn("Usable estimate: 115.2 GB", report)
        self.assertIn("about 28,800 photos", report)
        self.assertIn("about 768 minutes of video", report)
        self.assertIn("about 115,200 documents", report)

    def test_rejects_decreasing_water_meter_readings_and_data_overuse(self):
        bad_water = self.request("bad-water", {
            "previous_reading_m3": 10, "current_reading_m3": 9, "price_per_m3": 1000,
        })
        with self.assertRaisesRegex(RuntimeError, "cannot be lower"):
            wave41.water_bill_calculator(bad_water)
        bad_data = self.request("bad-data", {
            "allowance_gb": 5, "used_gb": 6, "daily_usage_gb": 1,
        })
        with self.assertRaisesRegex(RuntimeError, "cannot exceed"):
            wave41.mobile_data_duration_calculator(bad_data)

    def test_rejects_short_wallpaper_roll_and_invalid_delivery_divisor(self):
        short_roll = self.request("short-wallpaper", {
            "room_perimeter_m": 10, "wall_height_m": 3,
            "roll_width_m": 0.5, "roll_length_m": 2,
        })
        with self.assertRaisesRegex(RuntimeError, "shorter than one"):
            wave41.wallpaper_roll_calculator(short_roll)
        bad_divisor = self.request("bad-shipping", {
            "length_cm": 10, "width_cm": 10, "height_cm": 10,
            "actual_weight_kg": 1, "volumetric_divisor": 0,
        })
        with self.assertRaisesRegex(RuntimeError, "volumetric_divisor"):
            wave41.shipping_volumetric_weight_calculator(bad_divisor)

    def test_rejects_zero_gas_consumption_and_duplicate_json_keys(self):
        bad_gas = self.request("bad-gas", {
            "gas_weight_kg": 12, "consumption_grams_per_hour": 0,
        })
        with self.assertRaisesRegex(RuntimeError, "consumption_grams_per_hour"):
            wave41.gas_cylinder_runtime_calculator(bad_gas)
        duplicate = self.root / "duplicate.json"
        duplicate.write_text('{"capacity_gb":32,"capacity_gb":64}', encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "valid UTF-8 JSON"):
            wave41.storage_capacity_calculator(duplicate)


if __name__ == "__main__":
    unittest.main()
