from __future__ import annotations
import json,tempfile,unittest,zipfile
from pathlib import Path
from PIL import Image
import wave47
class Wave47Tests(unittest.TestCase):
 def setUp(self): self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
 def tearDown(self): self.temp.cleanup()
 def request(self,n,v):
  p=self.root/(n+".json"); p.write_text(json.dumps(v,ensure_ascii=False),encoding="utf-8"); return p
 def report(self,fn,n,v):
  r=fn(self.request(n,v)); return r,Path(r["output_path"]).read_text(encoding="utf-8")
 def test_qr_png(self):
  r=wave47.qr_code_maker(self.request("q",{"content":"hello  world\nkeep spacing"})); p=Path(r["output_path"])
  self.assertTrue(p.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
  with Image.open(p) as im: self.assertEqual(im.format,"PNG"); self.assertGreater(im.width,100)
 def test_qr_validation(self):
  with self.assertRaisesRegex(RuntimeError,"non-empty text"): wave47.qr_code_maker(self.request("e",{"content":""}))
  with self.assertRaisesRegex(RuntimeError,"UTF-8 bytes"): wave47.qr_code_maker(self.request("l",{"content":"x"*1501}))
 def test_wifi_redacts_secret(self):
  r=wave47.wifi_qr_code_maker(self.request("w",{"ssid":"Home; Main","password":"secret-pass-123","security":"WPA","hidden":True}))
  self.assertTrue(Path(r["output_path"]).read_bytes().startswith(b"\x89PNG")); self.assertNotIn("secret-pass-123",r["summary"])
 def test_wifi_validates_password_and_open_mode(self):
  with self.assertRaisesRegex(RuntimeError,"8 to 63"): wave47.wifi_qr_code_maker(self.request("s",{"ssid":"Home","password":"short"}))
  self.assertTrue(Path(wave47.wifi_qr_code_maker(self.request("o",{"ssid":"Guest","security":"nopass","password":""}))["output_path"]).exists())
 def test_vcard_zip(self):
  r=wave47.vcard_contact_card_maker(self.request("c",{"name":"Lan Nguyen","phone":"+84901234567","email":"lan@example.com","website":"https://example.com"}))
  self.assertEqual(Path(r["output_path"]).suffix,".zip"); self.assertNotIn("Lan Nguyen",r["summary"])
  with zipfile.ZipFile(r["output_path"]) as z:
   v=next(x for x in z.namelist() if x.endswith(".vcf")); q=next(x for x in z.namelist() if x.endswith(".png")); b=z.read(v).decode()
   self.assertIn("FN:Lan Nguyen",b); self.assertIn("EMAIL;TYPE=INTERNET:lan@example.com",b); self.assertTrue(z.read(q).startswith(b"\x89PNG"))
 def test_vcard_website_validation(self):
  with self.assertRaisesRegex(RuntimeError,"HTTP or HTTPS"): wave47.vcard_contact_card_maker(self.request("bad",{"name":"Lan","website":"javascript:alert(1)"}))
 def test_ics_tz_and_escaping(self):
  r=wave47.ics_calendar_maker(self.request("cal",{"events":[{"title":"Study, maths; physics","start":"2026-11-27T10:00:00+07:00","end":"2026-11-27T11:30:00+07:00","description":"Bring notebook\nand pen"}]}))
  b=Path(r["output_path"]).read_bytes().decode(); self.assertIn("DTSTART:20261127T030000Z",b); self.assertIn("DTEND:20261127T043000Z",b); self.assertIn("SUMMARY:Study\\, maths\\; physics",b); self.assertTrue(b.endswith("END:VCALENDAR\r\n"))
 def test_ics_all_day_end_exclusive(self):
  r=wave47.ics_calendar_maker(self.request("a",{"events":[{"title":"Holiday","all_day":True,"start":"2026-12-01","end":"2026-12-03"}]})); b=Path(r["output_path"]).read_bytes().decode()
  self.assertIn("DTEND;VALUE=DATE:20261203",b)
  with self.assertRaisesRegex(RuntimeError,"end is exclusive"): wave47.ics_calendar_maker(self.request("bad",{"events":[{"title":"Bad","all_day":True,"start":"2026-12-03","end":"2026-12-03"}]}))
 def test_ics_rejects_noncanonical_all_day_date(self):
  with self.assertRaisesRegex(RuntimeError,"YYYY-MM-DD"):
   wave47.ics_calendar_maker(self.request("compact",{"events":[{"title":"Compact","all_day":True,"start":"20261201","end":"20261202"}]}))
 def test_ics_requires_timezone(self):
  with self.assertRaisesRegex(RuntimeError,"explicit timezone offset"): wave47.ics_calendar_maker(self.request("n",{"events":[{"title":"Meeting","start":"2026-11-27T10:00:00","end":"2026-11-27T11:00:00"}]}))
 def test_electricity_tier_bill(self):
  _,b=self.report(wave47.electricity_tier_bill_calculator,"e",{"currency":"USD","consumption":120,"fixed_fee":10,"tax_percent":10,"tiers":[{"up_to":50,"rate":2},{"up_to":100,"rate":3},{"up_to":None,"rate":4}]})
  self.assertIn("Tier 1: 50 kWh × 2 USD/kWh = 100 USD",b); self.assertIn("Tier 2: 50 kWh × 3 USD/kWh = 150 USD",b); self.assertIn("Tier 3: 20 kWh × 4 USD/kWh = 80 USD",b); self.assertIn("Estimated total: 374 USD",b)
 def test_water_tier_bill(self):
  _,b=self.report(wave47.water_tier_bill_calculator,"w",{"currency":"VND","consumption":13,"tiers":[{"up_to":10,"rate":10000},{"up_to":None,"rate":15000}]})
  self.assertIn("10 m³ × 10000 VND/m³ = 100000 VND",b); self.assertIn("3 m³ × 15000 VND/m³ = 45000 VND",b); self.assertIn("Estimated total: 145000 VND",b)
 def test_tier_limits_increase(self):
  with self.assertRaisesRegex(RuntimeError,"strictly increase"): wave47.electricity_tier_bill_calculator(self.request("t",{"currency":"USD","consumption":10,"tiers":[{"up_to":20,"rate":1},{"up_to":10,"rate":2},{"up_to":None,"rate":3}]}))
 def test_mobile_plan_comparison(self):
  _,b=self.report(wave47.mobile_data_plan_comparator,"m",{"currency":"VND","monthly_usage_gb":10,"months":2,"plans":[{"name":"Small","monthly_fee":100000,"included_gb":5,"overage_per_gb":30000},{"name":"Unlimited","monthly_fee":180000,"included_gb":None,"overage_per_gb":0}]})
  self.assertLess(b.index("1. Unlimited"),b.index("2. Small")); self.assertIn("360000 VND over 2 month(s)",b); self.assertIn("user supplied",b)
 def test_mobile_plan_requires_explicit_allowance_and_overage(self):
  with self.assertRaisesRegex(RuntimeError,"included_gb must be supplied"):
   wave47.mobile_data_plan_comparator(self.request("no-cap",{"currency":"VND","monthly_usage_gb":1,"plans":[{"name":"A","monthly_fee":1,"overage_per_gb":0},{"name":"B","monthly_fee":2,"included_gb":None,"overage_per_gb":0}]}))
  with self.assertRaisesRegex(RuntimeError,"overage_per_gb must be supplied"):
   wave47.mobile_data_plan_comparator(self.request("no-overage",{"currency":"VND","monthly_usage_gb":1,"plans":[{"name":"A","monthly_fee":1,"included_gb":1},{"name":"B","monthly_fee":2,"included_gb":None,"overage_per_gb":0}]}))
 def test_internet_plan_comparison(self):
  _,b=self.report(wave47.home_internet_plan_comparator,"i",{"currency":"USD","monthly_usage_gb":400,"months":12,"plans":[{"name":"Cheap headline","monthly_fee":20,"included_gb":200,"overage_per_gb":1,"installation_fee":50,"advertised_download_mbps":100},{"name":"Unlimited","monthly_fee":45,"included_gb":None,"overage_per_gb":0,"installation_fee":0,"router_monthly_fee":3,"advertised_download_mbps":500}]})
  self.assertLess(b.index("1. Unlimited"),b.index("2. Cheap headline")); self.assertIn("576 USD over 12 month(s)",b); self.assertIn("Advertised speed is not a measured speed test",b)
 def test_plan_comparator_requires_two(self):
  with self.assertRaisesRegex(RuntimeError,"2 to 12"): wave47.mobile_data_plan_comparator(self.request("one",{"currency":"USD","monthly_usage_gb":1,"plans":[{"name":"A","monthly_fee":1}]}))
if __name__=="__main__": unittest.main()
