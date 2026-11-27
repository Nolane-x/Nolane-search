"""Wave 47 everyday-life utilities. Tariffs and plan terms are user supplied."""
from __future__ import annotations
import json,re,uuid,zipfile
from datetime import date,datetime,timezone
from decimal import Decimal,InvalidOperation,ROUND_HALF_UP
from io import BytesIO
from pathlib import Path
from urllib.parse import urlsplit
import qrcode
from qrcode.constants import ERROR_CORRECT_M
from qrcode.exceptions import DataOverflowError
MAX_JSON_BYTES=1024*1024
MAX_QR_BYTES=1500
CENT=Decimal("0.01")

def _pairs(pairs):
    out={}
    for k,v in pairs:
        if k in out: raise ValueError("Duplicate JSON key.")
        out[k]=v
    return out

def _read(path):
    try:
        if path.stat().st_size>MAX_JSON_BYTES: raise RuntimeError("Request exceeds the 1 MiB JSON limit.")
        value=json.loads(path.read_text(encoding="utf-8-sig"),object_pairs_hook=_pairs)
    except RuntimeError: raise
    except (OSError,UnicodeError,json.JSONDecodeError,ValueError) as exc: raise RuntimeError("Upload a valid UTF-8 JSON object.") from exc
    if not isinstance(value,dict): raise RuntimeError("Request must be one JSON object.")
    return value

def _row(v,label):
    if not isinstance(v,dict): raise RuntimeError(f"{label} must be an object.")
    return v

def _list(v,label,minimum=1,maximum=100):
    if not isinstance(v,list) or not minimum<=len(v)<=maximum: raise RuntimeError(f"{label} must contain {minimum} to {maximum} items.")
    return v

def _text(v,label,maximum=160):
    if not isinstance(v,str): raise RuntimeError(f"{label} must be text.")
    out=" ".join(v.split()).strip()
    if not out or len(out)>maximum: raise RuntimeError(f"{label} must contain 1 to {maximum} characters.")
    return out

def _raw(v,label,maximum):
    if not isinstance(v,str) or not v or "\x00" in v: raise RuntimeError(f"{label} must be non-empty text without NUL characters.")
    try: size=len(v.encode("utf-8"))
    except UnicodeEncodeError: raise RuntimeError(f"{label} is not valid UTF-8 text.") from None
    if size>maximum: raise RuntimeError(f"{label} exceeds {maximum} UTF-8 bytes.")
    return v

def _optional(v,label,maximum=500):
    if v is None or v=="": return ""
    if not isinstance(v,str): raise RuntimeError(f"{label} must be text.")
    out=v.strip()
    if len(out)>maximum or any(ord(c)<32 and c not in "\t\n\r" for c in out): raise RuntimeError(f"{label} is too long or contains unsupported control characters.")
    return out

def _number(v,label,minimum=None,maximum=Decimal("1000000000000")):
    if isinstance(v,bool) or v is None: raise RuntimeError(f"{label} must be a number.")
    try: out=Decimal(str(v).strip().replace(",",""))
    except (InvalidOperation,ValueError,AttributeError): raise RuntimeError(f"{label} must be a number.") from None
    if not out.is_finite() or (minimum is not None and out<Decimal(str(minimum))) or out>maximum: raise RuntimeError(f"{label} is outside the permitted range.")
    return out

def _integer(v,label,minimum=0,maximum=100000):
    out=_number(v,label,minimum,maximum)
    if out!=out.to_integral_value(): raise RuntimeError(f"{label} must be a whole number.")
    return int(out)

def _money(v,label):
    out=_number(v,label,0); rounded=out.quantize(CENT,rounding=ROUND_HALF_UP)
    if abs(out-rounded)>Decimal("0.0000001"): raise RuntimeError(f"{label} must have no more than two decimal places.")
    return rounded

def _currency(v):
    if not isinstance(v,str) or not re.fullmatch(r"[A-Za-z]{3}",v.strip()): raise RuntimeError("currency must be a 3-character code such as VND, USD or EUR.")
    return v.strip().upper()

def _fmt(v,places=2):
    out=format(v.quantize(Decimal(1).scaleb(-places),rounding=ROUND_HALF_UP),"f")
    return out.rstrip("0").rstrip(".") if "." in out else out

def _write(path,suffix,body,summary):
    out=path.with_name((path.stem[:64] or "nolane")+"-"+suffix+".txt")
    out.write_text(body.rstrip()+"\n",encoding="utf-8")
    return {"summary":summary[:500],"output_path":str(out)}

def _write_bytes(path,suffix,ext,payload,summary):
    out=path.with_name((path.stem[:64] or "nolane")+"-"+suffix+ext)
    out.write_bytes(payload)
    return {"summary":summary[:500],"output_path":str(out)}

def _qr(content):
    if not 0<len(content.encode("utf-8"))<=MAX_QR_BYTES: raise RuntimeError(f"QR content must contain 1 to {MAX_QR_BYTES} UTF-8 bytes.")
    code=qrcode.QRCode(version=None,error_correction=ERROR_CORRECT_M,box_size=8,border=4)
    code.add_data(content)
    try:
        code.make(fit=True)
        image=code.make_image(fill_color="black",back_color="white").convert("RGB")
    except DataOverflowError as exc: raise RuntimeError("QR content is too large for a reliable QR code.") from exc
    buf=BytesIO(); image.save(buf,format="PNG",optimize=True); return buf.getvalue()

def qr_code_maker(path):
    d=_read(path); content=_raw(d.get("content"),"content",MAX_QR_BYTES)
    return _write_bytes(path,"qr-code",".png",_qr(content),f"Created a PNG QR code ({len(content.encode('utf-8'))} UTF-8 bytes of content).")

def _wifi_escape(v):
    return v.replace("\\","\\\\").replace(";","\\;").replace(",","\\,").replace(":","\\:")

def wifi_qr_code_maker(path):
    d=_read(path); ssid=_raw(d.get("ssid"),"ssid",32)
    if any(ord(c)<32 or ord(c)==127 for c in ssid): raise RuntimeError("SSID contains unsupported control characters.")
    security=str(d.get("security","WPA")).strip().upper()
    if security not in ("WPA","WEP","NOPASS"): raise RuntimeError("security must be WPA, WEP or nopass.")
    password=d.get("password","")
    if security=="NOPASS":
        if password not in ("",None): raise RuntimeError("Open Wi-Fi must not include a password.")
        password=""
    else:
        password=_raw(password,"password",64)
        if any(ord(c)<32 or ord(c)==127 for c in password): raise RuntimeError("Wi-Fi password contains unsupported control characters.")
        if security=="WPA" and not 8<=len(password.encode("utf-8"))<=63: raise RuntimeError("WPA password must contain 8 to 63 UTF-8 bytes.")
        if security=="WEP" and len(password) not in (5,13,10,26): raise RuntimeError("WEP password must contain 5, 13, 10 or 26 characters.")
    hidden=d.get("hidden",False)
    if not isinstance(hidden,bool): raise RuntimeError("hidden must be true or false.")
    fields=["T:"+security,"S:"+_wifi_escape(ssid)]
    if password: fields.append("P:"+_wifi_escape(password))
    if hidden: fields.append("H:true")
    return _write_bytes(path,"wifi-qr",".png",_qr("WIFI:"+";".join(fields)+";;"),"Created a Wi-Fi connection QR PNG. Keep the image private because it can contain network credentials.")

def _vcard_escape(v):
    return v.replace("\\","\\\\").replace("\r\n","\n").replace("\r","\n").replace("\n","\\n").replace(";","\\;").replace(",","\\,")

def vcard_contact_card_maker(path):
    d=_read(path); name=_text(d.get("name"),"name",120)
    phone=_optional(d.get("phone"),"phone",60); email=_optional(d.get("email"),"email",160)
    org=_optional(d.get("organisation"),"organisation",120); title=_optional(d.get("title"),"title",120)
    website=_optional(d.get("website"),"website",300); address=_optional(d.get("address"),"address",240)
    if email and not re.fullmatch(r"[^@\s]{1,80}@[^@\s]{1,120}\.[^@\s]{2,24}",email): raise RuntimeError("email does not look like a valid address.")
    if website:
        u=urlsplit(website)
        if u.scheme not in ("http","https") or not u.hostname or u.username or u.password: raise RuntimeError("website must be a public HTTP or HTTPS URL.")
    lines=["BEGIN:VCARD","VERSION:3.0","FN:"+_vcard_escape(name)]
    if phone: lines.append("TEL;TYPE=CELL:"+_vcard_escape(phone))
    if email: lines.append("EMAIL;TYPE=INTERNET:"+_vcard_escape(email))
    if org: lines.append("ORG:"+_vcard_escape(org))
    if title: lines.append("TITLE:"+_vcard_escape(title))
    if website: lines.append("URL:"+_vcard_escape(website))
    if address: lines.append("ADR;TYPE=WORK:;;"+_vcard_escape(address)+";;;;")
    lines.extend(["END:VCARD",""])
    vcf="\r\n".join(lines).encode("utf-8"); qr=_qr("\r\n".join(lines[:-1]))
    safe=re.sub(r"[^A-Za-z0-9_-]+","-",name).strip("-_")[:48] or "contact"
    archive=BytesIO()
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(safe+".vcf",vcf); z.writestr(safe+"-qr.png",qr)
        z.writestr("README.txt","This bundle contains contact data you supplied and a QR representation. Treat both files as personal information.\n")
    return _write_bytes(path,"contact-card",".zip",archive.getvalue(),"Created a ZIP with a vCard contact file and matching QR image. The bundle contains personal information; share it only with intended recipients.")

def _ical_escape(v):
    return v.replace("\\","\\\\").replace("\r\n","\n").replace("\r","\n").replace("\n","\\n").replace(";","\\;").replace(",","\\,")

def _fold_ical(v):
    chunks=[]; current=""; used=0
    for c in v:
        size=len(c.encode("utf-8"))
        if used+size>75 and current: chunks.append(current); current=" "+c; used=1+size
        else: current+=c; used+=size
    chunks.append(current); return "\r\n".join(chunks)

def _utc(v,label):
    if not isinstance(v,str): raise RuntimeError(f"{label} must be an ISO datetime with an explicit timezone offset.")
    try: dt=datetime.fromisoformat(v.replace("Z","+00:00"))
    except ValueError: raise RuntimeError(f"{label} must be an ISO datetime with an explicit timezone offset.") from None
    if dt.tzinfo is None or dt.utcoffset() is None: raise RuntimeError(f"{label} must include Z or an explicit UTC offset.")
    return dt.astimezone(timezone.utc)

def ics_calendar_maker(path):
    d=_read(path); name=_optional(d.get("calendar_name","Nolane calendar"),"calendar_name",100) or "Nolane calendar"
    events=_list(d.get("events"),"events",1,100)
    lines=["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//Nolane Search//Everyday Calendar 1.0//EN","CALSCALE:GREGORIAN","METHOD:PUBLISH","X-WR-CALNAME:"+_ical_escape(name)]
    for i,raw in enumerate(events,1):
        e=_row(raw,f"event {i}"); title=_text(e.get("title"),f"event {i} title",180); all_day=e.get("all_day",False)
        if not isinstance(all_day,bool): raise RuntimeError(f"event {i}: all_day must be true or false.")
        if all_day:
            try: start=date.fromisoformat(_text(e.get("start"),f"event {i} start",10)); end=date.fromisoformat(_text(e.get("end"),f"event {i} end",10))
            except ValueError: raise RuntimeError(f"event {i}: all-day dates must use YYYY-MM-DD.") from None
            if end<=start: raise RuntimeError(f"event {i}: all-day end is exclusive and must be after start.")
            lines.extend(["BEGIN:VEVENT","UID:"+str(uuid.uuid4())+"@nolane-search","DTSTAMP:"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),"DTSTART;VALUE=DATE:"+start.strftime("%Y%m%d"),"DTEND;VALUE=DATE:"+end.strftime("%Y%m%d")])
        else:
            start=_utc(e.get("start"),f"event {i} start"); end=_utc(e.get("end"),f"event {i} end")
            if end<=start: raise RuntimeError(f"event {i}: end must be after start.")
            lines.extend(["BEGIN:VEVENT","UID:"+str(uuid.uuid4())+"@nolane-search","DTSTAMP:"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),"DTSTART:"+start.strftime("%Y%m%dT%H%M%SZ"),"DTEND:"+end.strftime("%Y%m%dT%H%M%SZ")])
        lines.append("SUMMARY:"+_ical_escape(title))
        loc=_optional(e.get("location"),f"event {i} location",240); desc=_optional(e.get("description"),f"event {i} description",1000)
        if loc: lines.append("LOCATION:"+_ical_escape(loc))
        if desc: lines.append("DESCRIPTION:"+_ical_escape(desc))
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR"); payload=("\r\n".join(_fold_ical(x) for x in lines)+"\r\n").encode("utf-8")
    return _write_bytes(path,"calendar",".ics",payload,f"Created an iCalendar file with {len(events)} event(s). Timed events are converted to UTC; all-day end dates are exclusive.")

def _tiered(path,unit,label,suffix):
    d=_read(path); currency=_currency(d.get("currency")); usage=_number(d.get("consumption"),"consumption",0,Decimal("1000000000"))
    tiers=_list(d.get("tiers"),"tiers",1,16); parsed=[]; previous=Decimal(0)
    for i,raw in enumerate(tiers,1):
        item=_row(raw,f"tier {i}"); upper=None if item.get("up_to") is None else _number(item["up_to"],f"tier {i} up_to",Decimal("0.000001"),Decimal("1000000000"))
        if upper is not None and upper<=previous: raise RuntimeError("Tier up_to limits must strictly increase.")
        rate=_money(item.get("rate"),f"tier {i} rate"); parsed.append((upper,rate))
        if upper is not None: previous=upper
        elif i!=len(tiers): raise RuntimeError("Only the final tier may have an unlimited up_to value.")
    if parsed[-1][0] is not None: raise RuntimeError("The final tier must use up_to: null for an unlimited upper band.")
    fixed=_money(d.get("fixed_fee",0),"fixed_fee"); tax_rate=_number(d.get("tax_percent",0),"tax_percent",0,100)
    remaining=usage; lower=Decimal(0); variable=Decimal(0); breakdown=[]
    for i,(upper,rate) in enumerate(parsed,1):
        if remaining<=0: break
        capacity=remaining if upper is None else max(Decimal(0),upper-lower)
        used=min(remaining,capacity); cost=used*rate; variable+=cost; remaining-=used; breakdown.append((i,used,rate,cost))
        if upper is not None: lower=upper
    subtotal=variable+fixed; tax=(subtotal*tax_rate/Decimal(100)).quantize(CENT,rounding=ROUND_HALF_UP); total=subtotal+tax
    lines=[f"{label} bill estimate",f"Consumption: {_fmt(usage)} {unit}",f"Currency: {currency}","All tier thresholds and rates below were supplied by the user; this is arithmetic, not an official tariff lookup.",""]
    for i,used,rate,cost in breakdown: lines.append(f"Tier {i}: {_fmt(used)} {unit} × {_fmt(rate)} {currency}/{unit} = {_fmt(cost)} {currency}")
    lines.extend(["",f"Variable charge: {_fmt(variable)} {currency}",f"Fixed fee: {_fmt(fixed)} {currency}",f"Subtotal: {_fmt(subtotal)} {currency}",f"Tax / surcharge: {_fmt(tax_rate)}% = {_fmt(tax)} {currency}",f"Estimated total: {_fmt(total)} {currency}","Excludes charges, credits, subsidies and rounding rules not entered by the user."])
    return _write(path,suffix,"\n".join(lines),f"Estimated {label.lower()} bill: {_fmt(total)} {currency} for {_fmt(usage)} {unit} using user-entered tiers.")

def electricity_tier_bill_calculator(path): return _tiered(path,"kWh","Electricity","electricity-bill")
def water_tier_bill_calculator(path): return _tiered(path,"m³","Water","water-bill")

def mobile_data_plan_comparator(path):
    d=_read(path); currency=_currency(d.get("currency")); usage=_number(d.get("monthly_usage_gb"),"monthly_usage_gb",0,100000)
    months=_integer(d.get("months",1),"months",1,36); plans=_list(d.get("plans"),"plans",2,12); rows=[]
    for i,raw in enumerate(plans,1):
        p=_row(raw,f"plan {i}"); name=_text(p.get("name"),f"plan {i} name",100)
        fee=_money(p.get("monthly_fee"),f"{name} monthly_fee"); addon=_money(p.get("monthly_addons",0),f"{name} monthly_addons"); activation=_money(p.get("activation_fee",0),f"{name} activation_fee")
        included=None if p.get("included_gb") is None else _number(p["included_gb"],f"{name} included_gb",0,100000)
        overage=_money(p.get("overage_per_gb",0),f"{name} overage_per_gb"); extra=Decimal(0) if included is None else max(Decimal(0),usage-included)
        monthly=fee+addon+extra*overage; total=monthly*months+activation; effective=total/(usage*months) if usage>0 else None
        rows.append({"name":name,"monthly":monthly,"activation":activation,"total":total,"effective":effective,"included":included,"extra":extra})
    rows.sort(key=lambda x:(x["total"],x["name"].casefold()))
    lines=["Mobile data plan cost comparison",f"Monthly usage: {_fmt(usage)} GB",f"Comparison period: {months} month(s) | Currency: {currency}","Plan prices and terms are user supplied; no live provider price, coverage or speed data is fetched.",""]
    for rank,r in enumerate(rows,1):
        allowance="unlimited (as entered)" if r["included"] is None else f"{_fmt(r['included'])} GB included"
        lines.extend([f"{rank}. {r['name']} — {_fmt(r['total'])} {currency} over {months} month(s)",f"   Monthly modeled cost: {_fmt(r['monthly'])} {currency} | {allowance} | excess: {_fmt(r['extra'])} GB",f"   Activation: {_fmt(r['activation'])} {currency}"+(f" | effective: {_fmt(r['effective'])} {currency}/used GB" if r["effective"] is not None else "")])
    lines.extend(["","Lowest modeled total is not a recommendation about coverage, speed, fair-use limits, throttling, contract terms or support."])
    return _write(path,"mobile-plan-comparison","\n".join(lines),f"Compared {len(rows)} mobile plans; lowest modeled entered cost is {_fmt(rows[0]['total'])} {currency}.")

def home_internet_plan_comparator(path):
    d=_read(path); currency=_currency(d.get("currency")); usage=_number(d.get("monthly_usage_gb"),"monthly_usage_gb",0,100000)
    months=_integer(d.get("months",12),"months",1,60); plans=_list(d.get("plans"),"plans",2,12); rows=[]
    for i,raw in enumerate(plans,1):
        p=_row(raw,f"plan {i}"); name=_text(p.get("name"),f"plan {i} name",100)
        fee=_money(p.get("monthly_fee"),f"{name} monthly_fee"); router=_money(p.get("router_monthly_fee",0),f"{name} router_monthly_fee")
        install=_money(p.get("installation_fee",0),f"{name} installation_fee"); equipment=_money(p.get("equipment_purchase_fee",0),f"{name} equipment_purchase_fee")
        speed=_number(p.get("advertised_download_mbps"),f"{name} advertised_download_mbps",Decimal("0.001"),10000000)
        cap=None if p.get("included_gb") is None else _number(p["included_gb"],f"{name} included_gb",0,100000)
        overage=_money(p.get("overage_per_gb",0),f"{name} overage_per_gb"); extra=Decimal(0) if cap is None else max(Decimal(0),usage-cap)
        monthly=fee+router+extra*overage; total=monthly*months+install+equipment; unit_cost=total/(speed*months)
        rows.append({"name":name,"monthly":monthly,"total":total,"speed":speed,"unit_cost":unit_cost,"extra":extra,"setup":install+equipment,"cap":cap})
    rows.sort(key=lambda x:(x["total"],x["name"].casefold()))
    lines=["Home internet plan cost comparison",f"Monthly usage: {_fmt(usage)} GB | Period: {months} month(s) | Currency: {currency}","Fees, caps and advertised speeds are user supplied. Advertised speed is not a measured speed test.",""]
    for rank,r in enumerate(rows,1):
        cap="unlimited (as entered)" if r["cap"] is None else f"{_fmt(r['cap'])} GB included"
        lines.extend([f"{rank}. {r['name']} — {_fmt(r['total'])} {currency} over {months} month(s)",f"   Modeled monthly: {_fmt(r['monthly'])} {currency} | {cap} | excess: {_fmt(r['extra'])} GB",f"   Advertised download: {_fmt(r['speed'])} Mbps | setup: {_fmt(r['setup'])} {currency}",f"   Cost per advertised Mbps-month: {_fmt(r['unit_cost'])} {currency}"])
    lines.extend(["","Excludes outages, congestion, Wi-Fi conditions, upload speed, latency, traffic management and contract exit charges unless entered."])
    return _write(path,"internet-plan-comparison","\n".join(lines),f"Compared {len(rows)} home internet plans; lowest modeled entered cost is {_fmt(rows[0]['total'])} {currency}.")
