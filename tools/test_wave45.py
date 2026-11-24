from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

import wave45


class Wave45Tests(unittest.TestCase):
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

    def test_bank_csv_analyser_summarises_months_categories_and_possible_duplicates(self):
        path = self.root / "bank.csv"
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["Date", "Description", "Amount", "Currency", "Category"])
            writer.writerow(["2026-11-01", "Salary", "30000000", "VND", "Income"])
            writer.writerow(["2026-11-02", "Groceries", "-500000", "VND", "Food"])
            writer.writerow(["2026-11-02", "Groceries", "-500000", "VND", "Food"])
            writer.writerow(["2026-10-30", "Train", "-25", "EUR", "Travel"])
        result = wave45.bank_csv_expense_analyzer(path)
        output = Path(result["output_path"]).read_text(encoding="utf-8")
        self.assertIn("Transactions analysed: 4", output)
        self.assertIn("Possible exact duplicate rows: 1", output)
        self.assertIn("VND: income 30000000; expenses 1000000; net 29000000", output)
        self.assertIn("2026-11 | VND", output)
        self.assertIn("EUR: income 0; expenses 25; net -25", output)
        self.assertIn("Food | expenses 1000000", output)

    def test_bank_analyser_json_path_and_currency_separation(self):
        _, output = self.report(wave45.bank_csv_expense_analyzer, "transactions", {
            "transactions": [
                {"date": "2026-11-01", "description": "Rent", "amount": -500, "currency": "USD"},
                {"date": "2026-11-02", "description": "Pay", "amount": 1000, "currency": "USD"},
                {"date": "2026-11-03", "description": "Train", "amount": -40, "currency": "EUR"},
            ],
        })
        self.assertIn("USD: income 1000; expenses 500; net 500", output)
        self.assertIn("EUR: income 0; expenses 40; net -40", output)
        self.assertIn("Uncategorised", output)

    def test_cashflow_calendar_handles_month_end_and_separate_currencies(self):
        _, output = self.report(wave45.bill_cashflow_calendar_planner, "cashflow", {
            "as_of_date": "2026-01-31", "horizon_days": 60,
            "opening_balances": [{"currency": "VND", "amount": 1000000}, {"currency": "USD", "amount": 250}],
            "events": [
                {"name": "Rent", "amount": 100000, "currency": "VND", "direction": "expense",
                 "first_date": "2026-01-31", "recurrence": "monthly"},
                {"name": "Salary", "amount": 500, "currency": "USD", "direction": "income",
                 "first_date": "2026-02-01", "recurrence": "once"},
            ],
        })
        self.assertIn("2026-01-31 | Rent", output)
        self.assertIn("2026-02-28 | Rent", output)
        self.assertIn("2026-03-31 | Rent", output)
        self.assertIn("VND: opening 1000000 | income 0 | bills/expenses 300000 | projected closing 700000", output)
        self.assertIn("USD: opening 250 | income 500 | bills/expenses 0 | projected closing 750", output)

    def test_cashflow_rejects_ambiguous_recurrence_and_currency(self):
        with self.assertRaisesRegex(RuntimeError, "recurrence"):
            wave45.bill_cashflow_calendar_planner(self.request("bad-recurrence", {
                "as_of_date": "2026-11-24", "events": [
                    {"name": "Bill", "amount": 10, "currency": "USD", "direction": "expense",
                     "first_date": "2026-11-25", "recurrence": "daily"},
                ],
            }))
        with self.assertRaisesRegex(RuntimeError, "currency"):
            wave45.bill_cashflow_calendar_planner(self.request("bad-currency", {
                "as_of_date": "2026-11-24", "events": [
                    {"name": "Bill", "amount": 10, "currency": "US dollars", "direction": "expense",
                     "first_date": "2026-11-25"},
                ],
            }))

    def test_shared_expense_settler_minimises_transfers_and_respects_exclusions(self):
        _, output = self.report(wave45.shared_expense_settler, "shared", {
            "currency": "VND", "participants": ["Anna", "Binh", "Chi"],
            "expenses": [
                {"name": "Hotel", "amount": 900, "paid_by": "Anna"},
                {"name": "Taxi", "amount": 200, "paid_by": "Binh", "split_among": ["Binh", "Chi"]},
            ],
        })
        self.assertIn("Anna: 600 VND (receive)", output)
        self.assertIn("Binh: 200 VND (pay)", output)
        self.assertIn("Chi: 400 VND (pay)", output)
        self.assertIn("Binh pays Anna: 200 VND", output)
        self.assertIn("Chi pays Anna: 400 VND", output)
        self.assertEqual(output.count(" pays "), 2)

    def test_shared_expense_custom_shares_and_existing_payments(self):
        _, output = self.report(wave45.shared_expense_settler, "shares", {
            "currency": "USD", "participants": ["A", "B", "C"],
            "expenses": [
                {"name": "Dinner", "amount": 100, "paid_by": "A", "split_among": ["A", "B", "C"],
                 "shares": [{"participant": "A", "amount": 20}, {"participant": "B", "amount": 30}, {"participant": "C", "amount": 50}]},
            ],
            "settlements": [{"from": "C", "to": "A", "amount": 10}],
        })
        self.assertIn("A: 80 USD (receive)", output)
        self.assertIn("B: 30 USD (pay)", output)
        self.assertIn("C: 50 USD (pay)", output)
        self.assertIn("B pays A: 30 USD", output)
        self.assertIn("C pays A: 50 USD", output)

    def test_shared_expense_rejects_unbalanced_custom_shares(self):
        with self.assertRaisesRegex(RuntimeError, "add up exactly"):
            wave45.shared_expense_settler(self.request("bad-shares", {
                "currency": "USD", "participants": ["A", "B"],
                "expenses": [{"name": "Meal", "amount": 20, "paid_by": "A", "split_among": ["A", "B"],
                              "shares": [{"participant": "A", "amount": 10}, {"participant": "B", "amount": 5}]}],
            }))

    def test_moving_day_checklist_sorts_dates_and_flags_overdue(self):
        _, output = self.report(wave45.moving_day_checklist_planner, "move", {
            "as_of_date": "2026-11-24", "move_date": "2026-11-30",
            "tasks": [
                {"name": "Book van", "days_before_move": 14, "estimated_minutes": 30, "assignee": "Lan", "priority": "urgent"},
                {"name": "Pack books", "days_before_move": 5, "estimated_minutes": 90, "assignee": "Minh"},
                {"name": "Return keys", "days_before_move": 0, "estimated_minutes": 15, "assignee": "Lan"},
            ],
        })
        self.assertIn("2026-11-16 | Book van | OVERDUE", output)
        self.assertIn("2026-11-25 | Pack books | Upcoming", output)
        self.assertIn("2026-11-30 | Return keys | Upcoming", output)
        self.assertIn("Lan: 45 min", output)
        self.assertIn("Overdue tasks not marked complete: 1", output)

    def test_moving_box_label_maker_prioritises_open_first_and_counts_rooms(self):
        _, output = self.report(wave45.moving_box_label_maker, "boxes", {
            "boxes": [
                {"box_id": "K2", "room": "Kitchen", "contents": ["Plates"], "fragile": True},
                {"box_id": "B1", "room": "Bedroom", "contents": ["Sheets"], "open_first": True},
            ],
        })
        self.assertLess(output.index("BOX B1"), output.index("BOX K2"))
        self.assertIn("FLAGS: OPEN FIRST", output)
        self.assertIn("FLAGS: FRAGILE", output)
        self.assertIn("Kitchen: 1", output)
        self.assertIn("Bedroom: 1", output)

    def test_moving_box_duplicate_ids_are_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "Duplicate box ID"):
            wave45.moving_box_label_maker(self.request("duplicate-box", {"boxes": [
                {"box_id": "A", "room": "Kitchen", "contents": ["Cup"]},
                {"box_id": "a", "room": "Bedroom", "contents": ["Book"]},
            ]}))

    def test_return_deadline_tracker_flags_expiry_and_near_deadline(self):
        _, output = self.report(wave45.return_deadline_tracker, "returns", {
            "as_of_date": "2026-11-24", "default_remind_days": 5,
            "purchases": [
                {"product": "Headphones", "seller": "Store A", "purchase_date": "2026-11-01", "return_window_days": 14},
                {"product": "Keyboard", "seller": "Store B", "purchase_date": "2026-11-20", "return_window_days": 14},
                {"product": "Mouse", "seller": "Store C", "purchase_date": "2026-11-23", "return_window_days": 14, "return_started": True},
            ],
        })
        self.assertIn("Headphones | Store A | RETURN WINDOW MAY HAVE PASSED", output)
        self.assertIn("Keyboard | Store B | Check return now", output)
        self.assertIn("Mouse | Store C | Return already started", output)
        self.assertIn("does not determine legal eligibility", output)

    def test_gift_budget_planner_reports_remaining_and_over_budget(self):
        _, output = self.report(wave45.gift_budget_planner, "gifts", {
            "currency": "VND", "total_budget": 100,
            "recipients": [
                {"name": "A", "budget": 40, "gifts": [{"item": "Book", "price": 30, "purchased": True}]},
                {"name": "B", "budget": 40, "gifts": [{"item": "Headphones", "price": 50}]},
            ],
        })
        self.assertIn("Planned gifts: 80 VND", output)
        self.assertIn("Already purchased: 30 VND", output)
        self.assertIn("Overall budget remaining: 20 VND", output)
        self.assertIn("B | allowance 40 VND | planned 50 | purchased 0 | remaining allowance -10", output)

    def test_household_emergency_kit_uses_only_quantities_entered_by_user(self):
        _, output = self.report(wave45.household_emergency_kit_planner, "kit", {
            "household_size": 4, "days": 3,
            "items": [
                {"name": "Water", "category": "Water and food", "per_person_per_day": 2, "per_household": 1, "unit": "L", "on_hand": 10},
                {"name": "Flashlights", "category": "Lighting", "per_person_per_day": 0, "per_household": 2, "unit": "pcs", "on_hand": 1},
            ],
        })
        self.assertIn("Water: target 25 L | on hand 10 L | still needed 15 L", output)
        self.assertIn("Flashlights: target 2 pcs | on hand 1 pcs | still needed 1 pcs", output)
        self.assertIn("not an official safety standard", output)

    def test_duplicate_json_keys_and_bad_dates_are_rejected(self):
        duplicate = self.root / "duplicate.json"
        duplicate.write_text('{"as_of_date":"2026-11-24","as_of_date":"2026-11-25","purchases":[]}', encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "valid UTF-8 JSON object"):
            wave45.return_deadline_tracker(duplicate)
        with self.assertRaisesRegex(RuntimeError, "YYYY-MM-DD"):
            wave45.return_deadline_tracker(self.request("bad-date", {
                "as_of_date": "11/24/2026",
                "purchases": [{"product": "Thing", "seller": "Shop", "purchase_date": "2026-11-01", "return_window_days": 14}],
            }))


if __name__ == "__main__":
    unittest.main()
