from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import wave46


class Wave46Tests(unittest.TestCase):
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

    def test_vehicle_fuel_log_uses_only_full_tank_to_full_tank_intervals(self):
        _, output = self.report(wave46.vehicle_fuel_log_analyzer, "fuel", {
            "currency": "VND",
            "entries": [
                {"date": "2026-01-01", "odometer_km": 10000, "litres": 40, "price_per_litre": 25000, "full_tank": True},
                {"date": "2026-01-15", "odometer_km": 10400, "litres": 20, "price_per_litre": 25000, "full_tank": False},
                {"date": "2026-02-01", "odometer_km": 10800, "litres": 40, "price_per_litre": 26000, "full_tank": True},
            ],
        })
        self.assertIn("Fuel entries: 3", output)
        self.assertIn("800 km | 60 L | 7.5 L/100 km | 13.33 km/L", output)
        self.assertIn("2026-01: 1500000 VND | 60 L | 2 fill(s)", output)
        self.assertIn("2026-02: 1040000 VND | 40 L | 1 fill(s)", output)

    def test_vehicle_fuel_log_rejects_non_increasing_odometer(self):
        bad = self.request("fuel-order", {"currency": "USD", "entries": [
            {"date": "2026-01-01", "odometer_km": 100, "litres": 5, "price_per_litre": 2, "full_tank": True},
            {"date": "2026-01-02", "odometer_km": 100, "litres": 5, "price_per_litre": 2, "full_tank": True},
        ]})
        with self.assertRaisesRegex(RuntimeError, "strictly increase"):
            wave46.vehicle_fuel_log_analyzer(bad)

    def test_vehicle_ownership_cost_groups_categories_and_cost_per_km(self):
        _, output = self.report(wave46.vehicle_ownership_cost_report, "ownership", {
            "currency": "VND", "distance_km": 10000,
            "expenses": [
                {"date": "2026-01-01", "name": "Oil", "category": "Maintenance", "amount": 1000000},
                {"date": "2026-01-20", "name": "Fuel", "category": "Fuel", "amount": 5000000},
                {"date": "2026-02-01", "name": "Insurance", "category": "Insurance", "amount": 2000000},
            ],
        })
        self.assertIn("Total recorded running cost: 8000000 VND", output)
        self.assertIn("Recorded cost per kilometre: 800 VND/km", output)
        self.assertIn("Fuel: 5000000 VND | 1 record(s)", output)
        self.assertIn("2026-01: 6000000 VND", output)

    def test_appliance_repair_replace_comparator_annualises_user_inputs(self):
        _, output = self.report(wave46.appliance_repair_replace_comparator, "repair", {
            "appliance_name": "Fridge", "currency": "USD",
            "repair_cost": 200, "expected_years_after_repair": 4, "annual_energy_cost_after_repair": 120,
            "replacement_cost": 800, "replacement_expected_life_years": 10, "replacement_annual_energy_cost": 70,
            "repair_warranty_months": 3, "replacement_warranty_months": 24,
        })
        self.assertIn("Annualised cost proxy: 170 USD/year", output)
        self.assertIn("Annualised cost proxy: 150 USD/year", output)
        self.assertIn("Replacement has the lower annualised cost proxy by 20 USD/year", output)
        self.assertIn("payback", output.lower())

    def test_home_repair_quote_comparator_ranks_scope_coverage_before_price(self):
        _, output = self.report(wave46.home_repair_quote_comparator, "quotes", {
            "project_name": "Bathroom leak", "currency": "VND",
            "required_work": [
                {"id": "pipe", "description": "Replace pipe section"},
                {"id": "seal", "description": "Reseal shower"},
            ],
            "quotes": [
                {"provider": "Cheap quote", "labour_cost": 100, "materials_cost": 50,
                 "included_work_ids": ["pipe"], "workmanship_warranty_months": 1},
                {"provider": "Complete quote", "labour_cost": 170, "materials_cost": 80,
                 "tax_percent": 10, "included_work_ids": ["pipe", "seal"], "workmanship_warranty_months": 12,
                 "estimated_days": 2},
            ],
        })
        self.assertLess(output.index("1. Complete quote"), output.index("2. Cheap quote"))
        self.assertIn("Complete quote — 275 VND", output)
        self.assertIn("Required items not marked included: seal (Reseal shower)", output)
        self.assertIn("lower price does not establish better workmanship", output)

    def test_rental_move_in_report_includes_photos_meter_readings_and_condition_counts(self):
        _, output = self.report(wave46.rental_move_in_inspection_report, "move-in", {
            "property": "Unit 12", "tenant": "Lan", "landlord_or_agent": "Owner",
            "inspection_date": "2026-11-24",
            "checks": [
                {"area": "Kitchen", "item": "Oven", "condition": "good", "evidence_refs": ["oven-1.jpg"]},
                {"area": "Bathroom", "item": "Tap", "condition": "damaged", "note": "Leaks when opened"},
                {"area": "Bedroom", "item": "Window", "condition": "not_tested"},
            ],
            "meter_readings": [{"utility": "Electricity", "reading": "12345", "unit": "kWh"}],
        })
        self.assertIn("Kitchen | Oven | good", output)
        self.assertIn("Evidence references: oven-1.jpg", output)
        self.assertIn("Electricity: 12345 kWh", output)
        self.assertIn("damaged: 1", output)
        self.assertIn("not_tested: 1", output)

    def test_rental_move_out_report_compares_labels_and_deposit_arithmetic(self):
        _, output = self.report(wave46.rental_move_out_condition_report, "move-out", {
            "property": "Unit 12", "tenant": "Lan",
            "move_in_date": "2026-01-01", "move_out_date": "2026-11-24",
            "currency": "VND", "deposit_amount": 10000000,
            "move_in_checks": [
                {"id": "wall", "area": "Living room", "item": "Wall", "condition": "good"},
                {"id": "oven", "area": "Kitchen", "item": "Oven", "condition": "worn"},
            ],
            "move_out_checks": [
                {"id": "wall", "area": "Living room", "item": "Wall", "condition": "damaged", "note": "New mark"},
                {"id": "oven", "area": "Kitchen", "item": "Oven", "condition": "worn"},
                {"id": "key", "area": "Entry", "item": "Key", "condition": "missing"},
            ],
            "proposed_deductions": [{"description": "Cleaning", "amount": 500000}],
        })
        self.assertIn("wall | Condition label changed | move-in good → move-out damaged", output)
        self.assertIn("oven | Same recorded condition", output)
        self.assertIn("key | Added at move-out", output)
        self.assertIn("Arithmetic remainder: 9500000 VND", output)
        self.assertIn("does not decide lawful deposit deductions", output)

    def test_rental_move_out_rejects_duplicate_item_ids(self):
        bad = self.request("move-out-duplicate", {
            "property": "Flat", "tenant": "A", "move_in_date": "2026-01-01", "move_out_date": "2026-02-01",
            "move_in_checks": [{"id": "1", "area": "Room", "item": "Door", "condition": "good"}],
            "move_out_checks": [
                {"id": "1", "area": "Room", "item": "Door", "condition": "good"},
                {"id": "1", "area": "Room", "item": "Wall", "condition": "worn"},
            ],
        })
        with self.assertRaisesRegex(RuntimeError, "duplicate"):
            wave46.rental_move_out_condition_report(bad)

    def test_rental_offer_cost_comparator_separates_refundable_deposit_from_cost(self):
        _, output = self.report(wave46.rental_offer_cost_comparator, "rents", {
            "currency": "VND", "lease_months": 12,
            "offers": [
                {"name": "A", "monthly_rent": 100, "monthly_utilities": 20,
                 "refundable_deposit": 200, "one_time_nonrefundable_fees": 10, "move_in_costs": 5},
                {"name": "B", "monthly_rent": 110, "monthly_utilities": 10,
                 "refundable_deposit": 100, "one_time_nonrefundable_fees": 0, "move_in_costs": 0},
            ],
        })
        self.assertIn("Estimated 12-month cost excluding refundable deposit: 1455 VND", output)
        self.assertIn("Cash required at start", output)
        self.assertIn("Lowest entered 12-month cost: B (1440 VND)", output)

    def test_appliance_service_history_reports_warranty_and_service_costs(self):
        _, output = self.report(wave46.appliance_service_history_report, "service", {
            "as_of_date": "2026-11-24",
            "appliances": [
                {"name": "Washing machine", "category": "Laundry", "currency": "VND",
                 "purchase_date": "2025-01-15", "warranty_months": 24,
                 "service_entries": [
                     {"date": "2025-10-01", "event": "Pump replacement", "cost": 800000, "downtime_days": 2},
                     {"date": "2026-05-03", "event": "Inspection", "cost": 200000, "downtime_days": 1},
                 ],
                 "next_service_due": "2026-12-01"},
            ],
        })
        self.assertIn("estimated warranty end: 2027-01-15 (within entered warranty dates)", output)
        self.assertIn("Service records: 2 | recorded service spend: 1000000 VND | recorded downtime: 3 day(s)", output)
        self.assertIn("Pump replacement (1)", output)
        self.assertIn("Next service date entered: 2026-12-01 (upcoming)", output)

    def test_rental_and_quote_inputs_reject_invalid_money_or_condition(self):
        bad_money = self.request("bad-rent", {
            "currency": "USD", "lease_months": 12,
            "offers": [{"name": "A", "monthly_rent": -10}],
        })
        with self.assertRaisesRegex(RuntimeError, "range"):
            wave46.rental_offer_cost_comparator(bad_money)
        bad_condition = self.request("bad-cond", {
            "property": "Unit", "tenant": "A", "landlord_or_agent": "B", "inspection_date": "2026-11-24",
            "checks": [{"area": "Room", "item": "Wall", "condition": "maybe"}],
        })
        with self.assertRaisesRegex(RuntimeError, "must be one of"):
            wave46.rental_move_in_inspection_report(bad_condition)


if __name__ == "__main__":
    unittest.main()
