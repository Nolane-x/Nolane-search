#!/usr/bin/env python3
"""Private GitHub-hosted execution engine for Nolane Tools."""
from __future__ import annotations
import argparse, csv, hashlib, json, mimetypes, os, posixpath, re, shutil, stat, subprocess, sys, tarfile, tempfile, unicodedata, urllib.error, urllib.parse, urllib.request, zipfile
from pathlib import Path
from html import unescape
from html.parser import HTMLParser
from typing import Any

WORKER_URL = os.environ.get("NOLANE_WORKER_URL", "https://nolane-search.nolane-file.workers.dev").rstrip("/")
MAX_INPUT = 20 * 1024 * 1024
RUNNERS = {
    "image-ocr", "image-info", "image-clean-exif", "image-compress", "image-to-pdf",
    "qr-read", "pdf-text", "pdf-info", "audio-transcribe", "audio-info",
    "video-info", "video-thumbnail", "csv-profile", "json-format",
    "office-text", "archive-inspect", "file-hash", "text-clean", "subtitle-text", "html-text",
    "audio-normalize", "video-audio", "video-gif", "image-resize", "image-webp", "image-palette",
    "pdf-compress", "pdf-to-images", "epub-text", "sqlite-inspect", "yaml-format", "xml-format",
    "code-check", "video-contact-sheet", "video-compress", "audio-subtitles", "archive-safe-extract", "xlsx-profile",
    "image-png", "csv-clean", "json-to-csv", "csv-to-xlsx", "xlsx-to-csv", "pdf-split", "audio-convert",
    "csv-to-json", "jsonl-format", "yaml-to-json", "xml-to-json", "sqlite-export", "xlsx-to-json",
    "pdf-extract-images", "archive-manifest", "text-stats", "image-grayscale",
    "pdf-merge", "pdf-metadata-clean", "pdf-outline", "image-contact-sheet", "image-duplicates", "csv-split", "csv-join", "json-schema", "json-to-yaml", "sqlite-integrity", "audio-silence-report", "video-silence-report", "video-frames", "subtitle-convert", "text-deduplicate", "text-diff", "code-size-report",
}

PIPELINE_TRANSITIONS = {
    "image-ocr": {"text-clean"}, "qr-read": {"text-clean"}, "pdf-text": {"text-clean"},
    "office-text": {"text-clean"}, "html-text": {"text-clean"}, "subtitle-text": {"text-clean"},
    "audio-transcribe": {"text-clean"}, "epub-text": {"text-clean"},
    "video-audio": {"audio-normalize","audio-transcribe","audio-subtitles","audio-info","audio-convert"},
    "audio-convert": {"audio-transcribe","audio-subtitles","audio-info"},
    "audio-normalize": {"audio-transcribe","audio-subtitles","audio-info","audio-convert"},
    "csv-clean": {"csv-profile","csv-to-xlsx"},
    "json-to-csv": {"csv-clean","csv-profile","csv-to-xlsx"},
    "csv-to-xlsx": {"xlsx-profile","xlsx-to-csv","office-text"},
    "pdf-compress": {"pdf-text","pdf-info","pdf-to-images","pdf-split"},
    "image-to-pdf": {"pdf-text","pdf-info","pdf-compress","pdf-to-images","pdf-split"},
    "image-clean-exif": {"image-info","image-compress","image-png","image-webp","image-palette","image-ocr","qr-read","image-to-pdf"},
    "image-compress": {"image-info","image-png","image-webp","image-palette","image-ocr","qr-read","image-to-pdf"},
    "image-resize": {"image-info","image-png","image-webp","image-palette","image-ocr","qr-read","image-to-pdf"},
    "image-png": {"image-info","image-compress","image-webp","image-palette","image-ocr","qr-read","image-to-pdf"},
    "image-webp": {"image-info","image-compress","image-png","image-palette","image-ocr","qr-read","image-to-pdf"},
    "video-compress": {"video-info","video-thumbnail","video-audio","video-contact-sheet","video-gif"},
    "csv-to-json": {"json-format"}, "yaml-to-json": {"json-format"}, "xml-to-json": {"json-format"},
    "xlsx-to-json": {"json-format"}, "json-format": {"json-to-csv"},
    "pdf-extract-images": {"archive-inspect","archive-safe-extract"},
    "sqlite-export": {"archive-inspect","archive-safe-extract"},
    "archive-manifest": {"csv-profile","csv-clean","csv-to-xlsx"},
    "image-grayscale": {"image-info","image-ocr","qr-read","image-to-pdf","image-png","image-webp","image-compress","image-palette"},
    "pdf-merge": {"pdf-info","pdf-text","pdf-compress","pdf-to-images","pdf-split","pdf-extract-images","pdf-metadata-clean","pdf-outline"},
    "pdf-metadata-clean": {"pdf-info","pdf-text","pdf-compress","pdf-to-images","pdf-split","pdf-extract-images","pdf-outline"},
    "pdf-outline": {"text-clean"},
    "image-contact-sheet": {"image-info","image-clean-exif","image-compress","image-resize","image-webp","image-palette","image-ocr","qr-read","image-to-pdf","image-grayscale","image-png"},
    "image-duplicates": {"csv-profile","csv-clean","csv-to-xlsx","csv-to-json"},
    "csv-split": {"archive-inspect","archive-safe-extract","archive-manifest"},
    "csv-join": {"csv-clean","csv-profile","csv-to-xlsx","csv-to-json"},
    "json-schema": {"json-format"},
    "json-to-yaml": {"yaml-format"},
    "sqlite-integrity": {"text-clean"},
    "audio-silence-report": {"text-clean"},
    "video-silence-report": {"text-clean"},
    "video-frames": {"archive-inspect","archive-safe-extract","archive-manifest"},
    "subtitle-convert": {"subtitle-text"},
    "text-deduplicate": {"text-clean","text-stats"},
    "text-diff": {"text-clean","text-stats"},
    "code-size-report": {"text-clean","text-stats"},
    "text-clean": {"text-stats","text-deduplicate"},
    "text-stats": {"text-clean"},
}

TEXT_OUTPUT_TOOLS = {"image-ocr","qr-read","pdf-text","office-text","html-text","subtitle-text","audio-transcribe","epub-text","pdf-outline","sqlite-integrity","audio-silence-report","video-silence-report","code-size-report","text-stats"}
MAX_PIPELINE_STEPS = len(RUNNERS)
MAX_PIPELINE_OUTPUT = 45 * 1024 * 1024

def api_json(url: str, method="GET", data=None, token=None):
    headers = {"accept":"application/json", "user-agent":"Nolane-Tools-Runner/1.0"}
    body = None
    if token: headers["authorization"] = "Bearer " + token
    if data is not None:
        headers["content-type"] = "application/json"
        body = json.dumps(data, ensure_ascii=False).encode()
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            raw = response.read(2_000_000)
            return json.loads(raw.decode()) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read(1200).decode("utf-8", "replace")
        raise RuntimeError(f"API HTTP {exc.code}: {detail}") from exc

def validate_pipeline(job):
    steps = job.get("pipeline")
    if steps is None:
        steps = [{"toolId": job.get("toolId")}]
    if not isinstance(steps, list) or not 1 <= len(steps) <= MAX_PIPELINE_STEPS:
        raise RuntimeError("Pipeline must contain at least one step and cannot repeat a processor.")
    ids=[]
    for item in steps:
        if not isinstance(item,dict):
            raise RuntimeError("Invalid pipeline step.")
        tool_id=item.get("toolId")
        if tool_id not in RUNNERS or tool_id in ids:
            raise RuntimeError("Unknown or repeated pipeline processor.")
        ids.append(tool_id)
    if not ids or ids[0] != job.get("toolId"):
        raise RuntimeError("The first pipeline step must match the selected tool.")
    for previous,current in zip(ids,ids[1:]):
        if current not in PIPELINE_TRANSITIONS.get(previous,set()):
            raise RuntimeError(f"Unsupported pipeline transition: {previous} -> {current}.")
    return [{"toolId":tool_id} for tool_id in ids]

def load_job(path):
    job = json.loads(Path(path).read_text(encoding="utf-8")).get("job", {})
    if not re.fullmatch(r"[0-9a-f-]{36}", str(job.get("id","")), re.I) or job.get("toolId") not in RUNNERS:
        raise RuntimeError("Invalid or unsupported tool job.")
    job["pipeline"] = validate_pipeline(job)
    return job

def download_telegram(file_id, filename):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token: raise RuntimeError("Missing TELEGRAM_BOT_TOKEN.")
    info = api_json(f"https://api.telegram.org/bot{token}/getFile?{urllib.parse.urlencode({'file_id':file_id})}")
    if not info.get("ok"): raise RuntimeError(info.get("description","Telegram getFile failed"))
    item = info.get("result") or {}
    if int(item.get("file_size") or 0) > MAX_INPUT: raise RuntimeError("Input exceeds Telegram's 20 MB getFile limit.")
    rel = str(item.get("file_path") or "")
    if not rel or rel.startswith("/") or ".." in Path(rel).parts or "\\" in rel: raise RuntimeError("Unsafe Telegram file path.")
    url = f"https://api.telegram.org/file/bot{token}/{urllib.parse.quote(rel, safe='/')}"
    safe = re.sub(r"[^A-Za-z0-9._-]+","_",Path(filename or Path(rel).name or "upload.bin").name)[:100] or "upload.bin"
    input_root = Path(os.environ.get("RUNNER_TEMP","/tmp")) / "nolane-inputs"
    input_root.mkdir(parents=True, exist_ok=True)
    dest = input_root / safe
    size=0
    with urllib.request.urlopen(urllib.request.Request(url,headers={"user-agent":"Nolane-Tools-Runner/1.0"}),timeout=60) as response, dest.open("wb") as out:
        while True:
            chunk=response.read(1024*1024)
            if not chunk: break
            size += len(chunk)
            if size > MAX_INPUT: raise RuntimeError("Downloaded input exceeds 20 MB.")
            out.write(chunk)
    if not size: raise RuntimeError("The uploaded file is empty.")
    return dest

def tool_text(text, title):
    text = text.strip() or "Không phát hiện nội dung."
    if len(text) > 2800:
        out_root=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"
        out_root.mkdir(parents=True,exist_ok=True)
        out=out_root/"nolane-result.txt"
        out.write_text(text,encoding="utf-8")
        return {"summary":f"{title}: hoàn tất, {len(text):,} ký tự. Toàn bộ kết quả được gửi kèm dưới dạng TXT.","output_path":str(out)}
    return {"summary":f"{title}\n\n{text}","output_path":""}

def cmd(name,args,timeout=180):
    exe=shutil.which(name)
    if not exe: raise RuntimeError(f"Missing runner dependency: {name}")
    return subprocess.run([exe,*args],check=True,capture_output=True,text=True,timeout=timeout).stdout.strip()

def image_ocr(p):
    from PIL import Image,ImageOps
    import pytesseract
    with Image.open(p) as raw:
        im=ImageOps.exif_transpose(raw).convert("RGB")
        im.thumbnail((9000,9000))
        text=pytesseract.image_to_string(im,lang="vie+eng",config="--psm 6")
    return tool_text(text,"OCR Việt–Anh")

def image_info(p):
    from PIL import Image
    with Image.open(p) as im:
        exif=im.getexif()
        lines=[f"File: {p.name}",f"Format: {im.format}",f"Size: {im.width} × {im.height}",f"Mode: {im.mode}",f"Bytes: {p.stat().st_size:,}",f"EXIF keys: {', '.join(map(str,exif.keys())) if exif else 'none'}"]
        for k,label in ((271,"Camera"),(272,"Model"),(274,"Orientation"),(306,"DateTime")):
            if exif.get(k): lines.append(f"{label}: {str(exif.get(k))[:100]}")
    return tool_text("\n".join(lines),"Image inspector")

def image_clean(p):
    from PIL import Image,ImageOps
    out=p.with_name(p.stem+"-clean.jpg")
    with Image.open(p) as im: ImageOps.exif_transpose(im).convert("RGB").save(out,"JPEG",quality=94,optimize=True)
    return {"summary":"Đã tạo JPEG mới, loại bỏ EXIF/GPS metadata; file gốc được giữ nguyên.","output_path":str(out)}

def image_compress(p):
    from PIL import Image,ImageOps
    out=p.with_name(p.stem+"-compressed.jpg")
    with Image.open(p) as im: ImageOps.exif_transpose(im).convert("RGB").save(out,"JPEG",quality=82,optimize=True,progressive=True)
    reduction=(1-out.stat().st_size/max(1,p.stat().st_size))*100
    return {"summary":f"Đã nén ảnh: {p.stat().st_size:,} → {out.stat().st_size:,} bytes ({reduction:.1f}% thay đổi).","output_path":str(out)}

def image_pdf(p):
    from PIL import Image,ImageOps
    out=p.with_suffix(".pdf")
    with Image.open(p) as im: ImageOps.exif_transpose(im).convert("RGB").save(out,"PDF",resolution=150)
    return {"summary":"Đã chuyển ảnh thành PDF một trang.","output_path":str(out)}

def qr_read(p):
    from PIL import Image
    from pyzbar.pyzbar import decode
    with Image.open(p) as im: found=decode(im)
    if not found: return tool_text("Không tìm thấy QR/barcode có thể giải mã.","QR / Barcode")
    return tool_text("\n".join(f"{i}. {x.type}: {x.data.decode('utf-8','replace')}" for i,x in enumerate(found,1)),"QR / Barcode")

def pdf_text(p):
    import fitz
    from PIL import Image
    import pytesseract
    doc=fitz.open(p)
    if doc.page_count>120: raise RuntimeError("PDF quá 120 trang. Hãy tách tài liệu.")
    pages=[]
    for n,page in enumerate(doc,1):
        txt=page.get_text("text").strip()
        if not txt:
            pix=page.get_pixmap(matrix=fitz.Matrix(1.6,1.6),alpha=False)
            im=Image.frombytes("RGB",[pix.width,pix.height],pix.samples)
            txt=pytesseract.image_to_string(im,lang="vie+eng",config="--psm 3").strip()
        if txt: pages.append(f"--- Trang {n} ---\n{txt}")
    return tool_text("\n\n".join(pages),"PDF text extraction · OCR scan fallback")

def pdf_info(p):
    import fitz
    doc=fitz.open(p); meta=doc.metadata or {}
    lines=[f"File: {p.name}",f"Pages: {doc.page_count}",f"Bytes: {p.stat().st_size:,}"]
    for k in ("title","author","subject","creator","producer","creationDate","modDate"):
        if meta.get(k): lines.append(f"{k}: {str(meta[k])[:200]}")
    if doc.page_count: lines.append(f"First page: {doc[0].rect.width:.1f} × {doc[0].rect.height:.1f} pt")
    return tool_text("\n".join(lines),"PDF inspector")

def ffprobe(p):
    return json.loads(cmd("ffprobe",["-v","error","-show_format","-show_streams","-of","json",str(p)],120))

def audio_info(p):
    data=ffprobe(p); fmt=data.get("format",{})
    lines=[f"File: {p.name}",f"Format: {fmt.get('format_name')}",f"Duration: {float(fmt.get('duration') or 0):.2f}s",f"Bitrate: {fmt.get('bit_rate','?')}",f"Bytes: {p.stat().st_size:,}"]
    for s in data.get("streams",[]):
        if s.get("codec_type")=="audio": lines.append(f"Audio: {s.get('codec_name')} · {s.get('sample_rate','?')} Hz · {s.get('channels','?')} channels")
    return tool_text("\n".join(lines),"Audio inspector")

def video_info(p):
    data=ffprobe(p); fmt=data.get("format",{})
    lines=[f"File: {p.name}",f"Container: {fmt.get('format_name')}",f"Duration: {float(fmt.get('duration') or 0):.2f}s",f"Bitrate: {fmt.get('bit_rate','?')}",f"Bytes: {p.stat().st_size:,}"]
    for s in data.get("streams",[]):
        if s.get("codec_type")=="video": lines.append(f"Video: {s.get('codec_name')} · {s.get('width')}×{s.get('height')} · {s.get('avg_frame_rate') or s.get('r_frame_rate')} FPS")
        if s.get("codec_type")=="audio": lines.append(f"Audio: {s.get('codec_name')} · {s.get('channels','?')} channels")
    return tool_text("\n".join(lines),"Video inspector")

def video_thumbnail(p):
    data=ffprobe(p); duration=float(data.get("format",{}).get("duration") or 0)
    if duration<=0: raise RuntimeError("Không đọc được thời lượng video.")
    at=max(.1,duration*.5); out=p.with_name(p.stem+"-thumbnail.jpg")
    cmd("ffmpeg",["-y","-ss",str(at),"-i",str(p),"-frames:v","1","-vf","scale=1280:-2","-q:v","3",str(out)],180)
    return {"summary":f"Đã trích xuất thumbnail tại {at:.1f} giây.","output_path":str(out)}

def audio_transcribe(p):
    from faster_whisper import WhisperModel
    model=WhisperModel("small",device="cpu",compute_type="int8",cpu_threads=4)
    segments,info=model.transcribe(str(p),beam_size=5,vad_filter=True)
    lines=[f"[{s.start:07.2f}–{s.end:07.2f}] {s.text.strip()}" for s in segments]
    return tool_text(f"Ngôn ngữ: {info.language} · Thời lượng: {float(info.duration or 0):.1f}s\n\n"+"\n".join(lines),"Whisper transcription")

def csv_profile(p):
    with p.open("r",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f); cols=reader.fieldnames or []; missing={c:0 for c in cols}; nums={c:[] for c in cols}; samples=[]; count=0
        for row in reader:
            count+=1
            if len(samples)<5: samples.append(row)
            for c in cols:
                v=(row.get(c) or "").strip()
                if not v: missing[c]+=1
                else:
                    try: nums[c].append(float(v.replace(",","")))
                    except ValueError: pass
            if count>=100000: break
    lines=[f"File: {p.name}",f"Rows read: {count:,}",f"Columns: {len(cols)}"]
    for c in cols[:100]:
        values=nums[c]; line=f"- {c}: missing {missing[c]} / {count}"
        if values: line+=f" · min {min(values):g}, max {max(values):g}, avg {sum(values)/len(values):g}"
        lines.append(line)
    lines.append("\nFirst rows:\n"+json.dumps(samples,ensure_ascii=False,indent=2)[:1400])
    return tool_text("\n".join(lines),"CSV profiler")

def json_format(p):
    value=json.loads(p.read_text(encoding="utf-8-sig")); pretty=json.dumps(value,ensure_ascii=False,indent=2)
    if len(pretty)>2800:
        out=p.with_name(p.stem+"-formatted.json"); out.write_text(pretty+"\n",encoding="utf-8")
        return {"summary":f"JSON hợp lệ · root={type(value).__name__} · {len(pretty):,} ký tự. Đã gửi file đã định dạng.","output_path":str(out)}
    return tool_text(pretty,"JSON hợp lệ · formatted")

def office_text(p):
    ext=p.suffix.lower(); lines=[]
    if ext==".docx":
        from docx import Document
        doc=Document(p); lines.extend(x.text for x in doc.paragraphs if x.text.strip())
        for table in doc.tables:
            for row in table.rows: lines.append(" | ".join(c.text.replace("\n"," / ") for c in row.cells))
    elif ext==".pptx":
        from pptx import Presentation
        prs=Presentation(p)
        for i,slide in enumerate(prs.slides,1):
            parts=[s.text for s in slide.shapes if getattr(s,"has_text_frame",False) and s.text.strip()]
            lines.append(f"--- Slide {i} ---\n"+"\n".join(parts))
    elif ext==".xlsx":
        from openpyxl import load_workbook
        wb=load_workbook(p,read_only=True,data_only=True)
        for sheet in wb.worksheets:
            lines.append(f"--- Sheet {sheet.title} ({sheet.max_row}x{sheet.max_column}) ---")
            for row in sheet.iter_rows(min_row=1,max_row=min(sheet.max_row,250),values_only=True):
                vals=["" if x is None else str(x)[:180] for x in row]
                if any(vals): lines.append(" | ".join(vals))
    else: raise RuntimeError("Office hỗ trợ DOCX, PPTX và XLSX.")
    return tool_text("\n".join(lines),"Office text extraction")

def archive_inspect(p):
    entries=[]
    if zipfile.is_zipfile(p):
        with zipfile.ZipFile(p) as z:
            for x in z.infolist()[:500]:
                suspicious=x.filename.startswith(("/","\\")) or ".." in Path(x.filename).parts
                entries.append(f"- {x.filename[:180]} · {x.file_size:,} bytes · compressed {x.compress_size:,}"+(" · ⚠ path traversal" if suspicious else ""))
    else:
        try:
            with tarfile.open(p,"r:*") as t:
                for x in t.getmembers()[:500]:
                    suspicious=x.name.startswith(("/","\\")) or ".." in Path(x.name).parts
                    entries.append(f"- {x.name[:180]} · {x.size:,} bytes"+(" · ⚠ path traversal" if suspicious else ""))
        except tarfile.TarError as e: raise RuntimeError("Archive không được hỗ trợ.") from e
    return tool_text(f"Archive: {p.name}\nBytes: {p.stat().st_size:,}\nItems listed: {len(entries)} (max 500)\nNo files extracted.\n"+"\n".join(entries),"Archive inspector")

def file_hash(p):
    sha=hashlib.sha256(); md5=hashlib.md5()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): sha.update(chunk); md5.update(chunk)
    mime=mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    return tool_text(f"File: {p.name}\nBytes: {p.stat().st_size:,}\nMIME: {mime}\nSHA-256: {sha.hexdigest()}\nMD5: {md5.hexdigest()}","File fingerprint")

def text_clean(p):
    raw=p.read_text(encoding="utf-8-sig",errors="replace")
    normalized=unicodedata.normalize("NFC",raw).replace("\r\n","\n").replace("\r","\n")
    normalized=re.sub("[\u200b\u200c\u200d\ufeff]","",normalized)
    lines=[line.rstrip(" \t") for line in normalized.split("\n")]
    cleaned=re.sub(r"\n{3,}","\n\n","\n".join(lines)).strip()+"\n"
    out=p.with_name(p.stem+"-cleaned"+(p.suffix.lower() or ".txt"))
    out.write_text(cleaned,encoding="utf-8")
    return {"summary":f"Đã làm sạch văn bản: {len(raw):,} → {len(cleaned):,} ký tự; chuẩn hóa Unicode NFC, newline, khoảng trắng và ký tự zero-width.","output_path":str(out)}

def subtitle_text(p):
    raw=p.read_text(encoding="utf-8-sig",errors="replace").replace("\r\n","\n").replace("\r","\n")
    lines=[]
    for line in raw.splitlines():
        value=line.strip()
        if not value or value.upper()=="WEBVTT" or value.startswith("NOTE "):
            continue
        if re.fullmatch(r"\d+",value):
            continue
        if "-->" in value and re.search(r"\d{2}:\d{2}",value):
            continue
        value=re.sub(r"<[^>]*>","",value)
        value=unescape(value).strip()
        if value and (not lines or lines[-1]!=value):
            lines.append(value)
    return tool_text("\n".join(lines),"Subtitle transcript")

class VisibleHtmlText(HTMLParser):
    BLOCK_TAGS={"address","article","aside","blockquote","br","dd","div","dl","dt","fieldset","figcaption","figure","footer","form","h1","h2","h3","h4","h5","h6","header","hr","li","main","nav","ol","p","pre","section","table","td","th","tr","ul"}
    SKIP_TAGS={"head","script","style","noscript","svg","canvas","iframe","template"}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip_depth=0
        self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag in self.SKIP_TAGS:
            self.skip_depth+=1
        elif not self.skip_depth and tag in self.BLOCK_TAGS:
            self.parts.append("\n")
    def handle_endtag(self,tag):
        if tag in self.SKIP_TAGS and self.skip_depth:
            self.skip_depth-=1
        elif not self.skip_depth and tag in self.BLOCK_TAGS:
            self.parts.append("\n")
    def handle_data(self,data):
        if not self.skip_depth:
            value=data.strip()
            if value:
                self.parts.append(value)

def html_text(p):
    parser=VisibleHtmlText()
    parser.feed(p.read_text(encoding="utf-8-sig",errors="replace"))
    parser.close()
    text=" ".join(parser.parts)
    text=re.sub(r"[ \t]+"," ",text)
    text=re.sub(r" *\n *","\n",text)
    text=re.sub(r"\n{3,}","\n\n",text).strip()
    return tool_text(text,"HTML text extraction")

def audio_normalize(p):
    out=p.with_name(p.stem+"-normalized.mp3")
    cmd("ffmpeg",["-y","-i",str(p),"-vn","-af","loudnorm=I=-16:TP=-1.5:LRA=11","-c:a","libmp3lame","-q:a","2",str(out)],600)
    return {"summary":"Đã chuẩn hóa loudness về mục tiêu -16 LUFS, true peak -1.5 dBTP và xuất MP3.","output_path":str(out)}

def video_audio(p):
    out=p.with_name(p.stem+"-audio.mp3")
    cmd("ffmpeg",["-y","-i",str(p),"-map","0:a:0","-vn","-c:a","libmp3lame","-q:a","2",str(out)],600)
    return {"summary":"Đã tách track âm thanh đầu tiên khỏi video và xuất MP3.","output_path":str(out)}

def video_gif(p):
    data=ffprobe(p)
    duration=float(data.get("format",{}).get("duration") or 0)
    if duration<=0:
        raise RuntimeError("Không đọc được thời lượng video.")
    clip=min(6.0,duration)
    start=max(0.0,(duration-clip)/2)
    out=p.with_name(p.stem+"-preview.gif")
    vf="fps=10,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
    cmd("ffmpeg",["-y","-ss",str(start),"-t",str(clip),"-i",str(p),"-vf",vf,"-loop","0",str(out)],900)
    return {"summary":f"Đã tạo GIF xem trước dài {clip:.1f} giây, 10 FPS, rộng tối đa 640 px.","output_path":str(out)}


def _guard_image_dimensions(image):
    if image.width * image.height > 80_000_000:
        raise RuntimeError("Ảnh vượt giới hạn 80 megapixel để tránh dùng quá nhiều bộ nhớ.")


def image_resize(p):
    from PIL import Image, ImageOps
    out=p.with_name(p.stem+"-resized.jpg")
    with Image.open(p) as raw:
        _guard_image_dimensions(raw)
        im=ImageOps.exif_transpose(raw)
        im.thumbnail((1920,1920),Image.Resampling.LANCZOS)
        if "A" in im.getbands():
            rgba=im.convert("RGBA")
            background=Image.new("RGB",rgba.size,"white")
            background.paste(rgba,mask=rgba.getchannel("A"))
            im=background
        else:
            im=im.convert("RGB")
        im.save(out,"JPEG",quality=86,optimize=True,progressive=True)
    return {"summary":f"Đã resize ảnh về tối đa 1920 px, giữ tỷ lệ; {p.stat().st_size:,} → {out.stat().st_size:,} bytes.","output_path":str(out)}

def image_webp(p):
    from PIL import Image, ImageOps
    out=p.with_name(p.stem+"-converted.webp")
    with Image.open(p) as raw:
        _guard_image_dimensions(raw)
        im=ImageOps.exif_transpose(raw)
        has_alpha=("A" in im.getbands()) or ("transparency" in im.info)
        if im.mode not in ("RGB","RGBA"):
            im=im.convert("RGBA" if has_alpha else "RGB")
        im.save(out,"WEBP",quality=84,method=6)
    return {"summary":f"Đã chuyển ảnh sang WebP; {p.stat().st_size:,} → {out.stat().st_size:,} bytes.","output_path":str(out)}

def image_palette(p):
    from PIL import Image, ImageOps
    with Image.open(p) as raw:
        _guard_image_dimensions(raw)
        im=ImageOps.exif_transpose(raw).convert("RGB")
        im.thumbnail((512,512),Image.Resampling.LANCZOS)
        quantized=im.quantize(colors=8)
        counts=sorted(quantized.getcolors(512*512) or [],reverse=True)
        palette=quantized.getpalette() or []
    total=max(1,sum(count for count,_ in counts))
    rows=[]
    for count,index in counts[:8]:
        base=index*3
        if base+2>=len(palette): continue
        color="#"+"".join(f"{v:02X}" for v in palette[base:base+3])
        rows.append(f"{color} · {count/total*100:.1f}%")
    return tool_text("Bảng màu chủ đạo (tối đa 8 màu):\n"+"\n".join(rows),"Image color palette")

def pdf_compress(p):
    import fitz
    doc=fitz.open(p)
    if doc.is_encrypted and doc.needs_pass:
        raise RuntimeError("PDF được mã hóa bằng mật khẩu; không thể nén khi chưa mở khóa.")
    if doc.page_count>200:
        raise RuntimeError("PDF quá 200 trang. Hãy chia nhỏ tài liệu trước khi nén.")
    out=p.with_name(p.stem+"-compressed.pdf")
    doc.save(str(out),garbage=4,deflate=True,clean=True,deflate_images=True,deflate_fonts=True)
    doc.close()
    before=p.stat().st_size
    after=out.stat().st_size
    change=(1-after/max(1,before))*100
    return {"summary":f"Đã tối ưu PDF không thay đổi nội dung trang: {before:,} → {after:,} bytes ({change:.1f}% thay đổi).","output_path":str(out)}

def pdf_to_images(p):
    import fitz
    from PIL import Image
    import tempfile
    doc=fitz.open(p)
    if doc.is_encrypted and doc.needs_pass:
        raise RuntimeError("PDF được mã hóa bằng mật khẩu.")
    if doc.page_count>20:
        raise RuntimeError("Chuyển PDF sang ảnh hiện giới hạn 20 trang để giữ tệp đầu ra an toàn.")
    out=p.with_name(p.stem+"-pages.zip")
    root=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"
    temp=Path(tempfile.mkdtemp(prefix="pdf-pages-",dir=root))
    try:
        with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
            for number,page in enumerate(doc,1):
                scale=min(1.3,1200/max(page.rect.width,page.rect.height))
                pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False)
                image=temp/f"page-{number:03d}.jpg"
                Image.frombytes("RGB",(pix.width,pix.height),pix.samples).save(image,"JPEG",quality=82,optimize=True)
                archive.write(image,image.name)
        pages=doc.page_count
    finally:
        doc.close()
        shutil.rmtree(temp,ignore_errors=True)
    return {"summary":f"Đã render {pages} trang PDF thành ảnh JPEG và đóng gói ZIP.","output_path":str(out)}

def epub_text(p):
    import xml.etree.ElementTree as ET
    from urllib.parse import unquote
    if not zipfile.is_zipfile(p):
        raise RuntimeError("Tệp EPUB không phải ZIP hợp lệ.")
    with zipfile.ZipFile(p) as archive:
        infos=archive.infolist()
        if len(infos)>2000 or sum(x.file_size for x in infos)>100*1024*1024:
            raise RuntimeError("EPUB vượt giới hạn 2.000 mục hoặc 100 MB giải nén.")
        names={x.filename for x in infos}
        if "META-INF/container.xml" not in names:
            raise RuntimeError("EPUB thiếu META-INF/container.xml.")
        container=ET.fromstring(archive.read("META-INF/container.xml"))
        rootfiles=container.findall(".//{*}rootfile")
        if not rootfiles:
            raise RuntimeError("Không tìm thấy package OPF trong EPUB.")
        opf_path=unquote(rootfiles[0].attrib.get("full-path",""))
        if not opf_path or opf_path.startswith("/") or ".." in Path(opf_path).parts or opf_path not in names:
            raise RuntimeError("Đường dẫn OPF trong EPUB không an toàn hoặc không tồn tại.")
        package=ET.fromstring(archive.read(opf_path))
        ns={"opf":"http://www.idpf.org/2007/opf","dc":"http://purl.org/dc/elements/1.1/"}
        title=package.findtext(".//dc:title",default=p.stem,namespaces=ns)
        author=package.findtext(".//dc:creator",default="",namespaces=ns)
        manifest={}
        base=Path(opf_path).parent
        for item in package.findall(".//opf:manifest/opf:item",ns):
            href=unquote(item.attrib.get("href","")).split("#",1)[0].split("?",1)[0]
            candidate=posixpath.normpath(posixpath.join(base.as_posix(),href))
            if candidate.startswith("../") or candidate.startswith("/") or candidate not in names:
                continue
            manifest[item.attrib.get("id","")]=candidate
        spine=package.findall(".//opf:spine/opf:itemref",ns)
        chapters=[]
        for ref in spine[:60]:
            name=manifest.get(ref.attrib.get("idref",""))
            if not name or not name.lower().endswith((".xhtml",".html",".htm")):
                continue
            data=archive.read(name)
            parser=VisibleHtmlText()
            parser.feed(data.decode("utf-8-sig","replace"))
            parser.close()
            text_value=re.sub(r"\s+"," "," ".join(parser.parts)).strip()
            if text_value:
                chapters.append(f"--- {Path(name).name} ---\n{text_value}")
    output=f"Title: {title}\nAuthor: {author or 'Unknown'}\nChapters: {len(chapters)}\n\n"+"\n\n".join(chapters)
    return tool_text(output,"EPUB reader · spine order")

def sqlite_inspect(p):
    import sqlite3
    from urllib.parse import quote
    uri="file:"+quote(str(p.resolve()),safe="/:")+"?mode=ro&immutable=1"
    connection=sqlite3.connect(uri,uri=True,timeout=5)
    try:
        connection.execute("PRAGMA query_only=ON")
        connection.set_progress_handler(lambda: 1,2_000_000)
        tables=connection.execute(
            "SELECT name,sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name LIMIT 30"
        ).fetchall()
        lines=[f"Database: {p.name}",f"Tables inspected: {len(tables)} (max 30)","Mode: read-only; no SQL from the uploaded file is executed."]
        for name,create_sql in tables:
            if create_sql and "CREATE VIRTUAL TABLE" in create_sql.upper():
                lines.append(f"\n[{name}] Virtual table skipped for safety.")
                continue
            quoted='"'+name.replace('"','""')+'"'
            try:
                count=connection.execute("SELECT COUNT(*) FROM "+quoted).fetchone()[0]
                columns=connection.execute("PRAGMA table_info("+quoted+")").fetchall()
                rows=connection.execute("SELECT * FROM "+quoted+" LIMIT 5").fetchall()
            except sqlite3.Error as exc:
                lines.append(f"\n[{name}] Inspection skipped: {str(exc)[:160]}")
                continue
            lines.append(f"\n[{name}] rows={count:,}")
            lines.append("Columns: "+", ".join(f"{c[1]} ({c[2] or 'unknown'})" for c in columns[:40]))
            lines.append("Sample: "+json.dumps(rows,ensure_ascii=False,default=str)[:1000])
        return tool_text("\n".join(lines),"SQLite database inspector")
    finally:
        connection.close()

def yaml_format(p):
    import yaml
    raw=p.read_text(encoding="utf-8-sig")
    documents=list(yaml.safe_load_all(raw))
    formatted=yaml.safe_dump_all(documents,allow_unicode=True,sort_keys=False,indent=2)
    out=p.with_name(p.stem+"-formatted.yaml")
    out.write_text(formatted,encoding="utf-8")
    return {"summary":f"YAML hợp lệ: {len(documents)} document(s), đã parse bằng SafeLoader và định dạng lại bằng SafeDumper.","output_path":str(out)}

def xml_format(p):
    import xml.etree.ElementTree as ET
    raw=p.read_text(encoding="utf-8-sig")
    if re.search(r"<!\s*(DOCTYPE|ENTITY)\b",raw,re.I):
        raise RuntimeError("XML có DTD/ENTITY bị chặn để tránh external entity và entity expansion.")
    root=ET.fromstring(raw)
    ET.indent(root,space="  ")
    out=p.with_name(p.stem+"-formatted.xml")
    ET.ElementTree(root).write(out,encoding="utf-8",xml_declaration=True)
    return {"summary":f"XML hợp lệ; root element: {root.tag}. Đã định dạng lại.","output_path":str(out)}

def code_check(p):
    ext=p.suffix.lower()
    report=[f"File: {p.name}","Uploaded code is parsed/checked only; it is never executed."]
    if ext in (".py",".pyw"):
        import ast
        ast.parse(p.read_text(encoding="utf-8-sig"),filename=p.name)
        report.append("Python: syntax OK (AST parse)")
    elif ext in (".js",".mjs",".cjs"):
        result=subprocess.run([shutil.which("node") or "node","--check",str(p)],capture_output=True,text=True,timeout=30)
        if result.returncode:
            raise RuntimeError((result.stderr or result.stdout or "JavaScript syntax error.")[-1200:])
        report.append("JavaScript: syntax OK (Node --check)")
    elif ext in (".sh",".bash"):
        result=subprocess.run([shutil.which("bash") or "bash","-n",str(p)],capture_output=True,text=True,timeout=30)
        if result.returncode:
            raise RuntimeError((result.stderr or result.stdout or "Shell syntax error.")[-1200:])
        report.append("Shell: syntax OK (bash -n)")
    elif ext in (".json",):
        value=json.loads(p.read_text(encoding="utf-8-sig"))
        report.append(f"JSON: syntax OK; root type={type(value).__name__}")
    elif ext in (".yaml",".yml"):
        import yaml
        count=sum(1 for _ in yaml.safe_load_all(p.read_text(encoding="utf-8-sig")))
        report.append(f"YAML: syntax OK; {count} document(s), SafeLoader")
    elif ext==".xml":
        import xml.etree.ElementTree as ET
        raw=p.read_text(encoding="utf-8-sig")
        if re.search(r"<!\s*(DOCTYPE|ENTITY)\b",raw,re.I):
            raise RuntimeError("XML DTD/ENTITY is disabled.")
        root=ET.fromstring(raw)
        report.append(f"XML: syntax OK; root={root.tag}")
    else:
        raise RuntimeError("code-check hỗ trợ .py, .js, .mjs, .cjs, .sh, .bash, .json, .yaml, .yml và .xml.")
    return tool_text("\n".join(report),"Code validation")

def video_contact_sheet(p):
    data=ffprobe(p)
    duration=float(data.get("format",{}).get("duration") or 0)
    if duration<=0 or duration>1800:
        raise RuntimeError("Video phải có thời lượng từ 0 đến 30 phút để tạo contact sheet.")
    out=p.with_name(p.stem+"-contact-sheet.jpg")
    rate=12/max(duration,1)
    vf=f"fps={rate:.8f},scale=320:-2,tile=4x3:padding=12:margin=8"
    cmd("ffmpeg",["-y","-i",str(p),"-vf",vf,"-frames:v","1","-q:v","3",str(out)],300)
    return {"summary":f"Đã tạo contact sheet tối đa 12 khung hình đại diện cho video dài {duration:.1f} giây.","output_path":str(out)}

def video_compress(p):
    data=ffprobe(p)
    duration=float(data.get("format",{}).get("duration") or 0)
    if duration<=0 or duration>360:
        raise RuntimeError("Nén video hiện giới hạn 6 phút để bảo đảm thời gian xử lý và dung lượng gửi.")
    out=p.with_name(p.stem+"-compressed.mp4")
    vf="scale='min(1280,iw)':'min(1280,ih)':force_original_aspect_ratio=decrease:force_divisible_by=2"
    cmd("ffmpeg",["-y","-i",str(p),"-map","0:v:0","-map","0:a?","-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","30","-maxrate","850k","-bufsize","1700k","-c:a","aac","-b:a","80k","-movflags","+faststart","-sn","-dn","-threads","2",str(out)],900)
    if out.stat().st_size>44*1024*1024:
        out.unlink(missing_ok=True)
        raise RuntimeError("Video sau nén vẫn vượt giới hạn gửi 44 MB; hãy chọn clip ngắn hơn.")
    change=(1-out.stat().st_size/max(1,p.stat().st_size))*100
    return {"summary":f"Đã nén H.264/AAC ở tối đa 1280 px, CRF 30: {p.stat().st_size:,} → {out.stat().st_size:,} bytes ({change:.1f}% thay đổi).","output_path":str(out)}

def _subtitle_timestamp(seconds,separator):
    millis=max(0,round(float(seconds)*1000))
    hours,remain=divmod(millis,3_600_000)
    minutes,remain=divmod(remain,60_000)
    secs,millis=divmod(remain,1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{millis:03d}"

def audio_subtitles(p):
    from faster_whisper import WhisperModel
    model=WhisperModel("small",device="cpu",compute_type="int8",cpu_threads=4)
    segments,info=model.transcribe(str(p),beam_size=5,vad_filter=True)
    srt=[]; vtt=["WEBVTT",""]
    count=0
    for segment in segments:
        text_value=segment.text.strip()
        if not text_value: continue
        count+=1
        start=_subtitle_timestamp(segment.start,",")
        end=_subtitle_timestamp(segment.end,",")
        srt.extend([str(count),f"{start} --> {end}",text_value,""])
        vtt.extend([f"{_subtitle_timestamp(segment.start,'.')} --> {_subtitle_timestamp(segment.end,'.')}",text_value,""])
        if count>=5000: break
    if not count:
        raise RuntimeError("Whisper không nhận diện được lời thoại để tạo phụ đề.")
    root=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"
    out=p.with_name(p.stem+"-subtitles.zip")
    srt_path=root/(p.stem+"-transcript.srt")
    vtt_path=root/(p.stem+"-transcript.vtt")
    srt_path.write_text("\n".join(srt),encoding="utf-8")
    vtt_path.write_text("\n".join(vtt),encoding="utf-8")
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(srt_path,srt_path.name)
        archive.write(vtt_path,vtt_path.name)
    srt_path.unlink(missing_ok=True); vtt_path.unlink(missing_ok=True)
    return {"summary":f"Đã tạo phụ đề SRT và VTT bằng Whisper small · ngôn ngữ: {info.language} · {count} cue(s).","output_path":str(out)}

def _safe_archive_parts(name):
    normalized=name.replace("\\","/")
    if "\x00" in normalized or normalized.startswith("/") or re.match(r"^[A-Za-z]:",normalized):
        raise RuntimeError("Archive chứa đường dẫn tuyệt đối hoặc ký tự không an toàn.")
    parts=[part for part in normalized.split("/") if part not in ("",".")]
    if not parts or any(part==".." for part in parts):
        raise RuntimeError("Archive chứa đường dẫn traversal (..).")
    return parts


def _copy_archive_stream(source,destination,current_total,max_bytes,expected_size=None):
    written=0
    with destination.open("wb") as output:
        while True:
            chunk=source.read(1024*1024)
            if not chunk: break
            written+=len(chunk)
            if current_total+written>max_bytes:
                raise RuntimeError("Archive vượt giới hạn 150 MB dữ liệu giải nén thực tế.")
            output.write(chunk)
    if expected_size is not None and written!=expected_size:
        raise RuntimeError("Kích thước giải nén không khớp metadata của archive.")
    return written

def archive_safe_extract(p):
    root=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"
    temp=Path(tempfile.mkdtemp(prefix="archive-safe-",dir=root))
    out=p.with_name(p.stem+"-safe-extracted.zip")
    total=0; count=0
    max_files=200; max_bytes=150*1024*1024
    try:
        if zipfile.is_zipfile(p):
            with zipfile.ZipFile(p) as archive:
                for item in archive.infolist():
                    if item.is_dir(): continue
                    count+=1
                    if count>max_files or total+item.file_size>max_bytes:
                        raise RuntimeError("Archive vượt giới hạn 200 tệp hoặc 150 MB sau giải nén.")
                    if item.flag_bits & 0x1:
                        raise RuntimeError("Archive có tệp mã hóa; không thể giải nén an toàn.")
                    mode=(item.external_attr>>16)&0xFFFF
                    if stat.S_ISLNK(mode):
                        raise RuntimeError("Archive chứa symbolic link; đã từ chối giải nén.")
                    if item.file_size>2*1024*1024 and item.compress_size and item.file_size/max(1,item.compress_size)>250:
                        raise RuntimeError("Archive có tỷ lệ nén bất thường (zip bomb protection).")
                    parts=_safe_archive_parts(item.filename)
                    target=temp.joinpath(*parts)
                    target.parent.mkdir(parents=True,exist_ok=True)
                    with archive.open(item) as source:
                        total+=_copy_archive_stream(source,target,total,max_bytes,item.file_size)
        else:
            with tarfile.open(p,"r:*") as archive:
                for item in archive.getmembers():
                    if item.isdir(): continue
                    if not item.isfile():
                        raise RuntimeError("Archive TAR chứa link hoặc special file; đã từ chối giải nén.")
                    count+=1
                    if count>max_files or total+item.size>max_bytes:
                        raise RuntimeError("Archive vượt giới hạn 200 tệp hoặc 150 MB sau giải nén.")
                    parts=_safe_archive_parts(item.name)
                    source=archive.extractfile(item)
                    if source is None: continue
                    target=temp.joinpath(*parts)
                    target.parent.mkdir(parents=True,exist_ok=True)
                    with source:
                        total+=_copy_archive_stream(source,target,total,max_bytes,item.size)
        with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as packaged:
            for item in sorted(temp.rglob("*")):
                if item.is_file():
                    packaged.write(item,item.relative_to(temp).as_posix())
    except (zipfile.BadZipFile,tarfile.TarError) as exc:
        raise RuntimeError("Archive không hợp lệ hoặc không được hỗ trợ.") from exc
    finally:
        shutil.rmtree(temp,ignore_errors=True)
    return {"summary":f"Đã giải nén an toàn {count} tệp ({total:,} bytes), loại bỏ metadata/link nguy hiểm và đóng gói ZIP sạch.","output_path":str(out)}

def xlsx_profile(p):
    from openpyxl import load_workbook
    workbook=load_workbook(p,read_only=True,data_only=True)
    reports=[]
    try:
        for sheet in workbook.worksheets[:20]:
            iterator=sheet.iter_rows(values_only=True)
            header=next(iterator,None)
            if header is None:
                reports.append(f"\n[{sheet.title}] Empty sheet")
                continue
            names=[str(value).strip() if value is not None else f"Column {i+1}" for i,value in enumerate(header[:60])]
            missing=[0]*len(names); numeric=[[] for _ in names]; samples=[]; duplicates=set(); duplicate_count=0; rows=0
            for row in iterator:
                rows+=1
                values=list(row[:len(names)])
                if len(samples)<5: samples.append(values)
                key=hashlib.sha256(json.dumps(values,ensure_ascii=False,default=str).encode()).hexdigest()
                if key in duplicates: duplicate_count+=1
                else: duplicates.add(key)
                for i in range(len(names)):
                    value=values[i] if i<len(values) else None
                    if value is None or str(value).strip()=="": missing[i]+=1
                    elif isinstance(value,(int,float)) and not isinstance(value,bool): numeric[i].append(float(value))
                if rows>=10000: break
            lines=[f"\n[{sheet.title}] data rows={rows:,} · duplicate rows={duplicate_count:,}"+(" · scan capped at 10,000" if rows>=10000 else "")]
            for i,name in enumerate(names):
                line=f"- {name}: missing {missing[i]}/{rows}"
                if numeric[i]: line+=f" · numeric min={min(numeric[i]):g}, max={max(numeric[i]):g}, avg={sum(numeric[i])/len(numeric[i]):g}"
                lines.append(line)
            lines.append("Sample: "+json.dumps(samples,ensure_ascii=False,default=str)[:1200])
            reports.extend(lines)
    finally:
        workbook.close()
    return tool_text("\n".join(reports),"Excel workbook profiler")

def _spreadsheet_safe(value):
    text = "" if value is None else str(value)
    # Preserve ordinary negative numeric values while neutralizing spreadsheet formulas.
    if re.fullmatch(r"-\d+(?:\.\d+)?", text.strip()):
        return text
    if text.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + text
    return text

def image_png(p):
    from PIL import Image, ImageOps
    out=p.with_name(p.stem+"-lossless.png")
    with Image.open(p) as raw:
        _guard_image_dimensions(raw)
        im=ImageOps.exif_transpose(raw)
        if "A" in im.getbands() or "transparency" in im.info:
            im=im.convert("RGBA")
        else:
            im=im.convert("RGB")
        im.save(out,"PNG",optimize=True)
    if out.stat().st_size > 45*1024*1024:
        out.unlink(missing_ok=True)
        raise RuntimeError("PNG output exceeds the 45 MB Telegram delivery limit.")
    return {"summary":f"Đã chuyển sang PNG lossless, giữ transparency khi có thể; {p.stat().st_size:,} → {out.stat().st_size:,} bytes.","output_path":str(out)}

def csv_clean(p):
    out=p.with_name(p.stem+"-clean.csv")
    seen=set(); kept=0; removed_blank=0; removed_duplicate=0
    with p.open("r",encoding="utf-8-sig",newline="") as source:
        reader=csv.reader(source)
        headers=next(reader,None)
        if not headers: raise RuntimeError("CSV không có header.")
        if len(headers)>200: raise RuntimeError("CSV vượt quá 200 cột.")
        headers=[_spreadsheet_safe(unicodedata.normalize("NFC",str(value)).strip() or f"column_{i+1}") for i,value in enumerate(headers)]
        with out.open("w",encoding="utf-8",newline="") as target:
            writer=csv.writer(target,lineterminator="\n")
            writer.writerow(headers)
            for row in reader:
                if len(row)>200: raise RuntimeError("CSV vượt quá 200 cột.")
                values=[unicodedata.normalize("NFC",str(value)).strip() for value in row[:len(headers)]]
                values += [""] * (len(headers)-len(values))
                if not any(values): removed_blank+=1; continue
                key=tuple(values)
                if key in seen: removed_duplicate+=1; continue
                seen.add(key)
                writer.writerow([_spreadsheet_safe(value) for value in values])
                kept+=1
                if kept>100000: raise RuntimeError("CSV vượt quá 100.000 dòng dữ liệu.")
    return {"summary":f"CSV đã làm sạch: giữ {kept:,} dòng; bỏ {removed_blank:,} dòng trống và {removed_duplicate:,} dòng trùng. Spreadsheet formula prefix được escape.","output_path":str(out)}

def json_to_csv(p):
    value=json.loads(p.read_text(encoding="utf-8-sig"))
    if isinstance(value,dict) and isinstance(value.get("data"),list):
        value=value["data"]
    if not isinstance(value,list) or not value or any(not isinstance(item,dict) for item in value):
        raise RuntimeError("JSON-to-CSV yêu cầu một mảng không rỗng gồm các object; hoặc object có trường data là mảng object.")
    if len(value)>100000: raise RuntimeError("JSON array vượt quá 100.000 object.")
    headers=list(dict.fromkeys(key for item in value for key in item.keys()))[:200]
    if not headers: raise RuntimeError("Không tìm thấy trường dữ liệu trong JSON.")
    out=p.with_name(p.stem+"-converted.csv")
    with out.open("w",encoding="utf-8-sig",newline="") as target:
        writer=csv.writer(target,lineterminator="\n")
        writer.writerow([_spreadsheet_safe(header) for header in headers])
        for item in value:
            row=[]
            for key in headers:
                cell=item.get(key)
                if isinstance(cell,(dict,list)): cell=json.dumps(cell,ensure_ascii=False,separators=(",",":"))
                row.append(_spreadsheet_safe(cell))
            writer.writerow(row)
    return {"summary":f"Đã chuyển {len(value):,} object và {len(headers)} trường JSON sang CSV UTF-8.","output_path":str(out)}

def csv_to_xlsx(p):
    from openpyxl import Workbook
    out=p.with_name(p.stem+"-converted.xlsx")
    wb=Workbook(write_only=True)
    ws=wb.create_sheet("Data")
    rows=0
    with p.open("r",encoding="utf-8-sig",newline="") as source:
        reader=csv.reader(source)
        for row in reader:
            if len(row)>200: raise RuntimeError("CSV vượt quá 200 cột.")
            ws.append([_spreadsheet_safe(cell) for cell in row])
            rows+=1
            if rows>100001: raise RuntimeError("CSV vượt quá 100.000 dòng dữ liệu.")
    if rows<1: raise RuntimeError("CSV không có dữ liệu.")
    wb.save(out)
    if out.stat().st_size>45*1024*1024:
        out.unlink(missing_ok=True)
        raise RuntimeError("XLSX output exceeds the 45 MB Telegram delivery limit.")
    return {"summary":f"Đã chuyển {rows-1:,} dòng CSV thành workbook XLSX (tối đa 200 cột). Ô dữ liệu được ghi an toàn dưới dạng text.","output_path":str(out)}

def xlsx_to_csv(p):
    from openpyxl import load_workbook
    root=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"
    temp=Path(tempfile.mkdtemp(prefix="xlsx-csv-",dir=root))
    out=p.with_name(p.stem+"-sheets-csv.zip")
    workbook=load_workbook(p,read_only=True,data_only=True)
    entries=[]
    try:
        if len(workbook.worksheets)>20: raise RuntimeError("Workbook vượt quá 20 sheets.")
        for index,ws in enumerate(workbook.worksheets,1):
            target=temp/(f"sheet-{index:02d}.csv")
            rows=0
            with target.open("w",encoding="utf-8-sig",newline="") as handle:
                writer=csv.writer(handle,lineterminator="\n")
                for values in ws.iter_rows(values_only=True):
                    if len(values)>200: raise RuntimeError("Sheet vượt quá 200 cột.")
                    writer.writerow([_spreadsheet_safe(value) for value in values])
                    rows+=1
                    if rows>20001: raise RuntimeError("Sheet vượt quá 20.000 dòng.")
            safe_name=re.sub(r"[^A-Za-z0-9._-]+","_",ws.title).strip("._-")[:50] or f"sheet-{index}"
            entries.append((target,f"{index:02d}-{safe_name}.csv",rows))
    finally:
        workbook.close()
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for source,name,_rows in entries: archive.write(source,arcname=name)
    if out.stat().st_size>45*1024*1024:
        out.unlink(missing_ok=True)
        raise RuntimeError("CSV archive exceeds the 45 MB Telegram delivery limit.")
    return {"summary":f"Đã xuất {len(entries)} sheet thành CSV riêng trong ZIP: "+", ".join(f"{name} ({rows} rows)" for _,name,rows in entries[:10]),"output_path":str(out)}

def pdf_split(p):
    import fitz
    source=fitz.open(p)
    if source.is_encrypted and source.needs_pass:
        source.close()
        raise RuntimeError("PDF được mã hóa bằng mật khẩu.")
    if source.page_count<1 or source.page_count>30:
        source.close()
        raise RuntimeError("PDF split hỗ trợ từ 1 đến 30 trang.")
    root=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"
    temp=Path(tempfile.mkdtemp(prefix="pdf-split-",dir=root))
    out=p.with_name(p.stem+"-pages.zip")
    count=source.page_count
    try:
        names=[]
        for index in range(count):
            page_doc=fitz.open()
            page_doc.insert_pdf(source,from_page=index,to_page=index)
            page_path=temp/f"page-{index+1:03d}.pdf"
            page_doc.save(page_path,garbage=4,deflate=True)
            page_doc.close()
            names.append(page_path)
    finally:
        source.close()
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for name in names: archive.write(name,arcname=name.name)
    if out.stat().st_size>45*1024*1024:
        out.unlink(missing_ok=True)
        raise RuntimeError("PDF split archive exceeds the 45 MB Telegram delivery limit.")
    return {"summary":f"Đã tách PDF {count} trang thành {count} tệp PDF một trang và đóng gói ZIP.","output_path":str(out)}

def audio_convert(p):
    data=ffprobe(p)
    duration=float(data.get("format",{}).get("duration") or 0)
    if duration<=0 or duration>600:
        raise RuntimeError("Audio conversion giới hạn tối đa 10 phút.")
    out=p.with_name(p.stem+"-speech-16khz-mono.wav")
    cmd("ffmpeg",["-y","-i",str(p),"-vn","-ac","1","-ar","16000","-c:a","pcm_s16le",str(out)],900)
    if out.stat().st_size>40*1024*1024:
        out.unlink(missing_ok=True)
        raise RuntimeError("WAV output exceeds the 40 MB safety budget.")
    return {"summary":f"Đã chuyển audio {duration:.1f}s sang WAV PCM 16 kHz mono, phù hợp speech-to-text.","output_path":str(out)}



def csv_to_json(p):
    out=p.with_name(p.stem+"-converted.json")
    rows=[]
    with p.open("r",encoding="utf-8-sig",newline="") as source:
        reader=csv.reader(source)
        headers=next(reader,None)
        if not headers:
            raise RuntimeError("CSV không có header.")
        if len(headers)>200:
            raise RuntimeError("CSV vượt quá 200 cột.")
        headers=[str(value).strip() for value in headers]
        if any(not value for value in headers):
            raise RuntimeError("CSV có tên cột rỗng; hãy đặt header cho mọi cột.")
        if len({value.casefold() for value in headers})!=len(headers):
            raise RuntimeError("CSV có header trùng nhau; không thể chuyển đổi mà không làm mất dữ liệu.")
        for line_number,row in enumerate(reader,2):
            if len(row)>len(headers):
                raise RuntimeError(f"Dòng CSV {line_number} có nhiều ô hơn header.")
            row=row+[""]*(len(headers)-len(row))
            rows.append(dict(zip(headers,row)))
            if len(rows)>100000:
                raise RuntimeError("CSV vượt quá 100.000 dòng dữ liệu.")
    out.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("JSON output exceeds the 45 MB delivery limit.")
    return {"summary":f"Đã chuyển {len(rows):,} dòng và {len(headers)} cột CSV thành mảng JSON; giá trị được giữ nguyên dưới dạng chuỗi.","output_path":str(out)}

def jsonl_format(p):
    out=p.with_name(p.stem+"-formatted.jsonl")
    rendered=[]
    def reject_constant(value):
        raise ValueError("Non-standard JSON constant: "+value)
    with p.open("r",encoding="utf-8-sig") as source:
        for line_number,line in enumerate(source,1):
            if not line.strip():
                continue
            try:
                value=json.loads(line,parse_constant=reject_constant)
            except (json.JSONDecodeError,ValueError) as exc:
                raise RuntimeError(f"JSONL lỗi tại dòng {line_number}: {str(exc)[:220]}") from exc
            rendered.append(json.dumps(value,ensure_ascii=False,separators=(",",":")))
            if len(rendered)>100000:
                raise RuntimeError("JSONL vượt quá 100.000 dòng dữ liệu.")
    if not rendered:
        raise RuntimeError("JSONL không có dòng dữ liệu hợp lệ.")
    out.write_text("\n".join(rendered)+"\n",encoding="utf-8")
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("JSONL output exceeds the 45 MB delivery limit.")
    return {"summary":f"JSONL hợp lệ: {len(rendered):,} dòng đã được chuẩn hóa; dòng trống được bỏ qua.","output_path":str(out)}

def _yaml_json_value(value, depth=0, seen=None, counter=None):
    import datetime as _datetime
    if seen is None: seen=set()
    if counter is None: counter=[0]
    counter[0]+=1
    if counter[0]>100000 or depth>80:
        raise RuntimeError("YAML structure exceeds the 100,000-node or 80-level safety limit.")
    if value is None or isinstance(value,(str,bool,int)):
        return value
    if isinstance(value,float):
        if not __import__("math").isfinite(value):
            raise RuntimeError("YAML non-finite numbers cannot be represented as strict JSON.")
        return value
    if isinstance(value,(_datetime.datetime,_datetime.date,_datetime.time)):
        return value.isoformat()
    if isinstance(value,(list,tuple,dict)):
        identity=id(value)
        if identity in seen:
            raise RuntimeError("YAML recursive aliases are not supported.")
        seen.add(identity)
        try:
            if isinstance(value,dict):
                result={}
                for key,item in value.items():
                    if not isinstance(key,str):
                        raise RuntimeError("YAML mapping keys must be strings for JSON conversion.")
                    result[key]=_yaml_json_value(item,depth+1,seen,counter)
                return result
            return [_yaml_json_value(item,depth+1,seen,counter) for item in value]
        finally:
            seen.remove(identity)
    raise RuntimeError("YAML contains a value type that cannot be represented safely as JSON.")

def yaml_to_json(p):
    import yaml
    out=p.with_name(p.stem+"-converted.json")
    try:
        documents=[]
        for document in yaml.safe_load_all(p.read_text(encoding="utf-8-sig")):
            documents.append(_yaml_json_value(document))
            if len(documents)>100:
                raise RuntimeError("YAML vượt quá 100 document.")
    except yaml.YAMLError as exc:
        raise RuntimeError("YAML không hợp lệ: "+str(exc)[:500]) from exc
    value=documents[0] if len(documents)==1 else documents
    out.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("JSON output exceeds the 45 MB delivery limit.")
    return {"summary":f"Đã chuyển {len(documents)} YAML document bằng SafeLoader sang JSON; alias vòng lặp và key không phải chuỗi bị từ chối.","output_path":str(out)}

def xml_to_json(p):
    import xml.etree.ElementTree as ET
    raw=p.read_text(encoding="utf-8-sig")
    if re.search(r"<!\s*(DOCTYPE|ENTITY)\b",raw,re.I):
        raise RuntimeError("XML DTD/ENTITY is disabled.")
    try:
        root=ET.fromstring(raw)
    except ET.ParseError as exc:
        raise RuntimeError("XML không hợp lệ: "+str(exc)[:300]) from exc
    counter=[0]
    def convert(element,depth=0):
        counter[0]+=1
        if depth>80 or counter[0]>50000:
            raise RuntimeError("XML vượt giới hạn 80 cấp hoặc 50.000 node.")
        children=list(element)
        text_value=(element.text or "").strip()
        if not children and not element.attrib:
            return text_value or None
        result={}
        if element.attrib:
            result["@attributes"]={key:value for key,value in element.attrib.items()}
        for child in children:
            value=convert(child,depth+1)
            if child.tag in result:
                if not isinstance(result[child.tag],list):
                    result[child.tag]=[result[child.tag]]
                result[child.tag].append(value)
            else:
                result[child.tag]=value
        if text_value:
            result["#text"]=text_value
        return result
    value={root.tag:convert(root)}
    out=p.with_name(p.stem+"-converted.json")
    out.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("JSON output exceeds the 45 MB delivery limit.")
    return {"summary":f"Đã chuyển XML root '{root.tag}' thành JSON; giữ thuộc tính, text và phần tử lặp. DTD/ENTITY bị chặn.","output_path":str(out)}

def sqlite_export(p):
    import sqlite3
    from urllib.parse import quote
    root=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"
    temp=Path(tempfile.mkdtemp(prefix="sqlite-export-",dir=root))
    out=p.with_name(p.stem+"-tables.zip")
    uri="file:"+quote(str(p.resolve()),safe="/:")+"?mode=ro&immutable=1"
    connection=sqlite3.connect(uri,uri=True,timeout=5)
    exported=[]; total_rows=0
    try:
        connection.execute("PRAGMA query_only=ON")
        connection.set_progress_handler(lambda: 1,2_000_000)
        tables=connection.execute(
            "SELECT name,sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name LIMIT 21"
        ).fetchall()
        if len(tables)>20:
            raise RuntimeError("SQLite export hỗ trợ tối đa 20 bảng.")
        for table_index,(name,create_sql) in enumerate(tables,1):
            if create_sql and "CREATE VIRTUAL TABLE" in create_sql.upper():
                continue
            columns=connection.execute('PRAGMA table_info("'+name.replace('"','""')+'")').fetchall()
            if not columns:
                continue
            if len(columns)>200:
                raise RuntimeError(f"Bảng {name} vượt quá 200 cột.")
            safe_name=re.sub(r"[^A-Za-z0-9._-]+","_",name).strip("._-")[:55] or f"table-{table_index}"
            target=temp/(f"{table_index:02d}-{safe_name}.csv")
            quoted='"'+name.replace('"','""')+'"'
            cursor=connection.execute("SELECT * FROM "+quoted)
            count=0
            with target.open("w",encoding="utf-8-sig",newline="") as handle:
                writer=csv.writer(handle,lineterminator="\n")
                writer.writerow([_spreadsheet_safe(str(column[1])) for column in columns])
                while True:
                    batch=cursor.fetchmany(500)
                    if not batch:
                        break
                    for row in batch:
                        count+=1; total_rows+=1
                        if total_rows>100000:
                            raise RuntimeError("SQLite export vượt quá 100.000 dòng tổng cộng.")
                        values=[]
                        for value in row:
                            if isinstance(value,bytes):
                                value="hex:"+value.hex()
                            values.append(_spreadsheet_safe(value))
                        writer.writerow(values)
            exported.append((target,target.name,count))
    finally:
        connection.close()
    if not exported:
        shutil.rmtree(temp,ignore_errors=True)
        raise RuntimeError("SQLite không có bảng dữ liệu thường để xuất.")
    try:
        with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
            for source,arcname,_count in exported:
                archive.write(source,arcname=arcname)
    finally:
        shutil.rmtree(temp,ignore_errors=True)
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("SQLite export ZIP exceeds the 45 MB delivery limit.")
    return {"summary":f"Đã xuất {len(exported)} bảng SQLite và {total_rows:,} dòng thành CSV trong ZIP; database được mở chỉ đọc.","output_path":str(out)}

def xlsx_to_json(p):
    from openpyxl import load_workbook
    import datetime as _datetime
    workbook=load_workbook(p,read_only=True,data_only=True)
    output={"sheets":[]}; total_rows=0
    try:
        if len(workbook.worksheets)>20:
            raise RuntimeError("Workbook vượt quá 20 sheets.")
        for sheet_index,ws in enumerate(workbook.worksheets,1):
            rows=[]
            iterator=ws.iter_rows(values_only=True)
            header_row=next(iterator,None)
            if header_row is None:
                output["sheets"].append({"name":ws.title,"columns":[],"rows":[]})
                continue
            raw_headers=list(header_row[:200])
            headers=[]
            used=set()
            for column_index,value in enumerate(raw_headers,1):
                base=str(value).strip() if value is not None else ""
                base=base or f"Column {column_index}"
                candidate=base; suffix=2
                while candidate.casefold() in used:
                    candidate=f"{base}_{suffix}"; suffix+=1
                used.add(candidate.casefold()); headers.append(candidate)
            for row in iterator:
                total_rows+=1
                if total_rows>50000:
                    raise RuntimeError("XLSX-to-JSON vượt quá 50.000 dòng tổng cộng.")
                if len(row)>200:
                    raise RuntimeError(f"Sheet {ws.title} vượt quá 200 cột.")
                item={}
                for index,header in enumerate(headers):
                    value=row[index] if index<len(row) else None
                    if isinstance(value,(bytes,bytearray)):
                        value="hex:"+bytes(value).hex()
                    elif isinstance(value,(_datetime.datetime,_datetime.date,_datetime.time)):
                        value=value.isoformat()
                    elif value is not None and not isinstance(value,(str,int,float,bool)):
                        value=str(value)
                    item[header]=value
                rows.append(item)
            output["sheets"].append({"name":ws.title,"columns":headers,"rows":rows})
    finally:
        workbook.close()
    out=p.with_name(p.stem+"-converted.json")
    out.write_text(json.dumps(output,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("JSON output exceeds the 45 MB delivery limit.")
    return {"summary":f"Đã xuất {len(output['sheets'])} sheet và {total_rows:,} dòng thành JSON. Giá trị công thức đọc từ cache; workbook không được thực thi.","output_path":str(out)}

def pdf_extract_images(p):
    import fitz
    document=fitz.open(p)
    out=p.with_name(p.stem+"-embedded-images.zip")
    count=0; total_bytes=0; seen=set()
    try:
        if document.is_encrypted and document.needs_pass:
            raise RuntimeError("PDF được mã hóa bằng mật khẩu.")
        if document.page_count>100:
            raise RuntimeError("PDF image extraction giới hạn tối đa 100 trang.")
        with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
            for page_number,page in enumerate(document,1):
                for image_ref in page.get_images(full=True):
                    xref=int(image_ref[0])
                    if xref in seen:
                        continue
                    seen.add(xref)
                    extracted=document.extract_image(xref)
                    payload=extracted.get("image",b"")
                    if not payload:
                        continue
                    count+=1; total_bytes+=len(payload)
                    if count>100 or len(payload)>20*1024*1024 or total_bytes>120*1024*1024:
                        raise RuntimeError("PDF vượt giới hạn 100 ảnh, 20 MB mỗi ảnh hoặc 120 MB tổng ảnh.")
                    extension=re.sub(r"[^a-z0-9]","",str(extracted.get("ext","bin")).lower())[:5] or "bin"
                    archive.writestr(f"page-{page_number:03d}-image-{count:03d}.{extension}",payload)
    except Exception:
        out.unlink(missing_ok=True)
        raise
    finally:
        document.close()
    if count==0:
        out.unlink(missing_ok=True)
        raise RuntimeError("PDF không có ảnh raster nhúng để trích xuất. Tool này không render nguyên trang PDF.")
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("Extracted images ZIP exceeds the 45 MB delivery limit.")
    return {"summary":f"Đã trích {count} ảnh raster nhúng ({total_bytes:,} bytes) từ PDF và đóng gói ZIP; ảnh dùng chung được khử trùng theo xref.","output_path":str(out)}

def archive_manifest(p):
    out=p.with_name(p.stem+"-sha256-manifest.csv")
    rows=[]; total_size=0
    def digest_stream(handle,expected_size):
        digest=hashlib.sha256(); read_size=0
        while True:
            chunk=handle.read(1024*1024)
            if not chunk: break
            read_size+=len(chunk)
            if read_size>expected_size or read_size>150*1024*1024:
                raise RuntimeError("Archive member vượt kích thước khai báo hoặc giới hạn 150 MB.")
            digest.update(chunk)
        if read_size!=expected_size:
            raise RuntimeError("Archive member có kích thước thực tế không khớp metadata.")
        return digest.hexdigest()
    if zipfile.is_zipfile(p):
        with zipfile.ZipFile(p) as archive:
            infos=archive.infolist()
            if len(infos)>200:
                raise RuntimeError("Archive manifest hỗ trợ tối đa 200 mục.")
            for info in infos:
                if info.is_dir():
                    continue
                parts=_safe_archive_parts(info.filename)
                mode=(info.external_attr>>16)&0xFFFF
                file_type=stat.S_IFMT(mode)
                # Some ZIP writers store permission bits without S_IFREG; zero type bits are not special files.
                if stat.S_ISLNK(mode) or (file_type and file_type not in (stat.S_IFREG,stat.S_IFDIR)):
                    raise RuntimeError("Archive chứa symlink hoặc special file bị chặn.")
                if info.flag_bits&0x1:
                    raise RuntimeError("Archive mã hóa không được hỗ trợ.")
                if info.file_size>150*1024*1024 or (info.compress_size and info.file_size/max(1,info.compress_size)>200):
                    raise RuntimeError("Archive member vượt giới hạn kích thước hoặc compression ratio.")
                total_size+=info.file_size
                if total_size>150*1024*1024:
                    raise RuntimeError("Archive vượt 150 MB dữ liệu giải nén.")
                with archive.open(info,"r") as handle:
                    checksum=digest_stream(handle,info.file_size)
                rows.append(("/".join(parts),info.file_size,checksum))
    elif tarfile.is_tarfile(p):
        with tarfile.open(p,"r:*") as archive:
            members=archive.getmembers()
            if len(members)>200:
                raise RuntimeError("Archive manifest hỗ trợ tối đa 200 mục.")
            for member in members:
                if member.isdir():
                    continue
                if not member.isfile():
                    raise RuntimeError("TAR chứa symlink, hardlink hoặc special file bị chặn.")
                parts=_safe_archive_parts(member.name)
                if member.size<0:
                    raise RuntimeError("TAR member có kích thước không hợp lệ.")
                total_size+=member.size
                if total_size>150*1024*1024:
                    raise RuntimeError("Archive vượt 150 MB dữ liệu giải nén.")
                handle=archive.extractfile(member)
                if handle is None:
                    raise RuntimeError("Không thể đọc TAR member.")
                with handle:
                    checksum=digest_stream(handle,member.size)
                rows.append(("/".join(parts),member.size,checksum))
    else:
        raise RuntimeError("Archive manifest chỉ hỗ trợ ZIP, TAR, TGZ và TAR.GZ hợp lệ.")
    if not rows:
        raise RuntimeError("Archive không có tệp thường để tạo manifest.")
    with out.open("w",encoding="utf-8-sig",newline="") as target:
        writer=csv.writer(target,lineterminator="\n")
        writer.writerow(["path","size_bytes","sha256"])
        writer.writerows(rows)
    return {"summary":f"Đã tạo SHA-256 manifest cho {len(rows)} tệp trong archive ({total_size:,} bytes) mà không giải nén ra đĩa.","output_path":str(out)}

def text_stats(p):
    from collections import Counter
    raw=p.read_text(encoding="utf-8-sig")
    words=re.findall(r"[^\W_]+(?:['’][^\W_]+)?",raw,flags=re.UNICODE)
    normalized=[word.casefold() for word in words]
    counts=Counter(normalized)
    sentences=len(re.findall(r"[.!?。！？]+",raw))
    paragraphs=sum(1 for block in re.split(r"\n\s*\n",raw) if block.strip())
    report=[
        f"File: {p.name}",
        f"Characters (including whitespace): {len(raw):,}",
        f"Characters (excluding whitespace): {sum(not char.isspace() for char in raw):,}",
        f"Words: {len(words):,}",
        f"Unique words: {len(counts):,}",
        f"Sentences (punctuation-based estimate): {sentences:,}",
        f"Non-empty paragraphs: {paragraphs:,}",
        f"Estimated reading time at 200 words/min: {max(1,(len(words)+199)//200)} minute(s)",
        "Top terms: "+(", ".join(f"{word} ({count})" for word,count in counts.most_common(20)) if counts else "No words detected"),
        "Note: tokenization is language-neutral and does not perform Vietnamese syllable/word segmentation.",
    ]
    return tool_text("\n".join(report),"Text statistics")


def _safe_zip_members(archive, suffixes, max_files=200, max_bytes=100*1024*1024):
    selected=[]; count=0; total=0
    allowed={suffix.lower() for suffix in suffixes}
    for item in archive.infolist():
        if item.is_dir(): continue
        count+=1
        if count>max_files: raise RuntimeError(f"ZIP vượt giới hạn {max_files} tệp.")
        if item.flag_bits & 0x1: raise RuntimeError("ZIP chứa tệp mã hóa.")
        mode=(item.external_attr>>16)&0xFFFF
        file_type=stat.S_IFMT(mode)
        if file_type==stat.S_IFLNK or (file_type and file_type not in (stat.S_IFREG,stat.S_IFDIR)):
            raise RuntimeError("ZIP chứa symlink hoặc special file.")
        _safe_archive_parts(item.filename)
        total+=item.file_size
        if total>max_bytes: raise RuntimeError("ZIP vượt giới hạn dữ liệu giải nén.")
        if item.file_size>2*1024*1024 and item.compress_size and item.file_size/max(1,item.compress_size)>250:
            raise RuntimeError("ZIP có tỷ lệ nén bất thường.")
        if Path(item.filename).suffix.lower() in allowed: selected.append(item)
    return selected,total


def pdf_merge(p):
    import fitz
    if not zipfile.is_zipfile(p): raise RuntimeError("Gửi ZIP chứa các PDF cần gộp.")
    out=p.with_name(p.stem+"-merged.pdf"); merged=fitz.open(); total_pages=0; members=[]; total_bytes=0
    try:
        with zipfile.ZipFile(p) as archive:
            members,total_bytes=_safe_zip_members(archive,{".pdf"},max_files=50,max_bytes=100*1024*1024)
            if not members: raise RuntimeError("ZIP không chứa PDF.")
            members.sort(key=lambda item:item.filename.casefold())
            for item in members:
                source=fitz.open(stream=archive.read(item),filetype="pdf")
                try:
                    if source.is_encrypted and source.needs_pass: raise RuntimeError("PDF mã hóa mật khẩu: "+Path(item.filename).name)
                    total_pages+=source.page_count
                    if total_pages>300: raise RuntimeError("Tổng tài liệu vượt quá 300 trang.")
                    merged.insert_pdf(source)
                finally: source.close()
        if merged.page_count<1: raise RuntimeError("Không có trang PDF hợp lệ để gộp.")
        merged.save(str(out),garbage=4,deflate=True,clean=True)
    finally: merged.close()
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True); raise RuntimeError("PDF gộp vượt giới hạn đầu ra 45 MB.")
    return {"summary":f"Đã gộp {len(members)} PDF, tổng {total_pages} trang ({total_bytes:,} bytes ZIP), theo thứ tự tên tệp.","output_path":str(out)}


def pdf_metadata_clean(p):
    import fitz
    document=fitz.open(p)
    if document.is_encrypted and document.needs_pass:
        document.close(); raise RuntimeError("PDF được mã hóa bằng mật khẩu.")
    out=p.with_name(p.stem+"-metadata-clean.pdf")
    try:
        document.set_metadata({"title":"","author":"","subject":"","keywords":"","creator":"","producer":"","creationDate":"","modDate":"","trapped":""})
        try: document.del_xml_metadata()
        except Exception: pass
        document.save(str(out),garbage=4,deflate=True,clean=True)
    finally: document.close()
    return {"summary":"Đã xóa các trường metadata chuẩn và XML metadata khỏi PDF; nội dung trang không bị raster hóa.","output_path":str(out)}


def pdf_outline(p):
    import fitz
    document=fitz.open(p)
    try:
        if document.is_encrypted and document.needs_pass: raise RuntimeError("PDF được mã hóa bằng mật khẩu.")
        if document.page_count>500: raise RuntimeError("PDF outline giới hạn 500 trang.")
        toc=document.get_toc()
        if not toc: return tool_text("PDF không có bookmark hoặc mục lục nhúng.","PDF outline")
        rows=[f"Pages: {document.page_count}",f"Bookmarks: {len(toc)}",""]
        rows.extend("  "*(max(0,int(level)-1))+f"- {title} (page {page})" for level,title,page in toc[:5000])
        return tool_text("\n".join(rows),"PDF outline")
    finally: document.close()


def image_contact_sheet(p):
    import io
    from PIL import Image,ImageOps,ImageDraw
    if not zipfile.is_zipfile(p): raise RuntimeError("Gửi ZIP chứa các ảnh cần xem.")
    thumbnails=[]; labels=[]
    with zipfile.ZipFile(p) as archive:
        members,total=_safe_zip_members(archive,{".jpg",".jpeg",".png",".webp",".bmp",".tif",".tiff"},max_files=120,max_bytes=100*1024*1024)
        if not members: raise RuntimeError("ZIP không chứa ảnh được hỗ trợ.")
        for index,item in enumerate(members[:80],1):
            with Image.open(io.BytesIO(archive.read(item))) as raw:
                _guard_image_dimensions(raw)
                image=ImageOps.exif_transpose(raw).convert("RGB")
                image.thumbnail((232,158),Image.Resampling.LANCZOS)
                thumbnails.append(image.copy()); labels.append(f"{index:03d} {Path(item.filename).name[:46]}")
    columns=4; cell_w=260; cell_h=198; rows=(len(thumbnails)+columns-1)//columns
    sheet=Image.new("RGB",(columns*cell_w,rows*cell_h),(248,248,248)); draw=ImageDraw.Draw(sheet)
    for index,(image,label) in enumerate(zip(thumbnails,labels)):
        x=(index%columns)*cell_w; y=(index//columns)*cell_h
        sheet.paste(image,(x+(cell_w-image.width)//2,y+6+(158-image.height)//2))
        draw.text((x+8,y+168),f"Image {index+1:03d}",fill=(30,30,30))
    out=p.with_name(p.stem+"-contact-sheet.jpg")
    sheet.save(out,"JPEG",quality=88,optimize=True); sheet.close()
    for image in thumbnails: image.close()
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True); raise RuntimeError("Contact sheet vượt giới hạn đầu ra.")
    return {"summary":f"Đã tạo contact sheet cho {len(thumbnails)} ảnh ({total:,} bytes giải nén). Tệp: "+"; ".join(labels),"output_path":str(out)}


def image_duplicates(p):
    import io
    from PIL import Image,ImageOps
    if not zipfile.is_zipfile(p): raise RuntimeError("Gửi ZIP chứa bộ ảnh cần so sánh.")
    records=[]
    with zipfile.ZipFile(p) as archive:
        members,total=_safe_zip_members(archive,{".jpg",".jpeg",".png",".webp",".bmp",".tif",".tiff"},max_files=120,max_bytes=100*1024*1024)
        if not members: raise RuntimeError("ZIP không chứa ảnh hợp lệ.")
        for item in members:
            payload=archive.read(item)
            with Image.open(io.BytesIO(payload)) as raw:
                _guard_image_dimensions(raw)
                image=ImageOps.exif_transpose(raw).convert("L").resize((8,8),Image.Resampling.LANCZOS)
                pixels=list(image.getdata()); average=sum(pixels)/len(pixels)
                phash=sum((1<<index) for index,value in enumerate(pixels) if value>=average)
            records.append((item.filename,hashlib.sha256(payload).hexdigest(),phash))
    out=p.with_name(p.stem+"-image-duplicates.csv"); matches=[]
    for left in range(len(records)):
        for right in range(left+1,len(records)):
            a=records[left]; b=records[right]; distance=(a[2]^b[2]).bit_count()
            if a[1]==b[1]: matches.append((a[0],b[0],"exact-sha256",0))
            elif distance<=4: matches.append((a[0],b[0],"near-visual",distance))
    with out.open("w",encoding="utf-8-sig",newline="") as target:
        writer=csv.writer(target,lineterminator="\n"); writer.writerow(["file_a","file_b","match_type","perceptual_distance"])
        writer.writerows([(_spreadsheet_safe(a),_spreadsheet_safe(b),kind,distance) for a,b,kind,distance in matches])
    return {"summary":f"Đã phân tích {len(records)} ảnh ({total:,} bytes). Tìm thấy {len(matches)} cặp giống/gần giống; perceptual hash 8×8, ngưỡng ≤4.","output_path":str(out)}


def csv_split(p):
    import io
    out=p.with_name(p.stem+"-parts.zip"); total_rows=0; parts=0
    with p.open("r",encoding="utf-8-sig",newline="") as source,zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        reader=csv.reader(source,strict=True); header=next(reader,None)
        if not header: raise RuntimeError("CSV không có header.")
        if len(header)>200: raise RuntimeError("CSV vượt 200 cột.")
        rows=[]
        for row in reader:
            total_rows+=1
            if total_rows>100000: raise RuntimeError("CSV split hỗ trợ tối đa 100.000 dòng dữ liệu.")
            if len(row)>200: raise RuntimeError("Một dòng CSV vượt 200 cột.")
            rows.append(row)
            if len(rows)>=10000:
                parts+=1; buffer=io.StringIO(newline=""); writer=csv.writer(buffer,lineterminator="\n")
                writer.writerow(header); writer.writerows(rows); archive.writestr(f"part-{parts:03d}.csv",buffer.getvalue().encode("utf-8-sig")); rows=[]
        if rows or parts==0:
            parts+=1; buffer=io.StringIO(newline=""); writer=csv.writer(buffer,lineterminator="\n")
            writer.writerow(header); writer.writerows(rows); archive.writestr(f"part-{parts:03d}.csv",buffer.getvalue().encode("utf-8-sig"))
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True); raise RuntimeError("CSV parts ZIP vượt giới hạn đầu ra.")
    return {"summary":f"Đã chia {total_rows:,} dòng thành {parts} CSV; mỗi phần giữ header và tối đa 10.000 dòng.","output_path":str(out)}


def csv_join(p):
    import io
    if not zipfile.is_zipfile(p): raise RuntimeError("Gửi ZIP chứa các CSV cần gộp.")
    out=p.with_name(p.stem+"-joined.csv"); total_rows=0; files=0; expected_header=None
    with zipfile.ZipFile(p) as archive:
        members,total=_safe_zip_members(archive,{".csv"},max_files=100,max_bytes=100*1024*1024)
        if not members: raise RuntimeError("ZIP không chứa CSV.")
        members.sort(key=lambda item:item.filename.casefold())
        with out.open("w",encoding="utf-8-sig",newline="") as target:
            writer=csv.writer(target,lineterminator="\n")
            for item in members:
                with archive.open(item) as raw:
                    text=io.TextIOWrapper(raw,encoding="utf-8-sig",newline=""); reader=csv.reader(text,strict=True); header=next(reader,None)
                    if not header: raise RuntimeError("CSV rỗng hoặc không có header: "+Path(item.filename).name)
                    if len(header)>200: raise RuntimeError("CSV vượt 200 cột.")
                    if expected_header is None:
                        expected_header=header; writer.writerow([_spreadsheet_safe(value) for value in header])
                    elif header!=expected_header: raise RuntimeError("Header giữa các CSV không khớp: "+Path(item.filename).name)
                    for row in reader:
                        total_rows+=1
                        if total_rows>100000: raise RuntimeError("CSV join vượt 100.000 dòng tổng cộng.")
                        if len(row)>200: raise RuntimeError("Một dòng CSV vượt 200 cột.")
                        writer.writerow([_spreadsheet_safe(value) for value in row])
                files+=1
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True); raise RuntimeError("CSV joined vượt giới hạn đầu ra.")
    return {"summary":f"Đã gộp {files} CSV, {total_rows:,} dòng ({total:,} bytes giải nén); header phải khớp và ô nguy hiểm được escape.","output_path":str(out)}


def _schema_for_values(values,depth=0):
    if depth>40: raise RuntimeError("JSON schema vượt 40 cấp lồng nhau.")
    non_null=[value for value in values if value is not None]; nullable=len(non_null)!=len(values)
    if not non_null: return {"type":"null"}
    if all(isinstance(value,dict) for value in non_null):
        keys=sorted(set().union(*(value.keys() for value in non_null)))
        properties={key:_schema_for_values([value[key] for value in non_null if key in value],depth+1) for key in keys}
        required=sorted(key for key in keys if all(key in value for value in non_null))
        result={"type":"object","properties":properties,"additionalProperties":True}
        if required: result["required"]=required
    elif all(isinstance(value,list) for value in non_null):
        children=[child for value in non_null for child in value[:500]]
        result={"type":"array","items":_schema_for_values(children,depth+1) if children else {}}
    else:
        kinds=[]
        for value in non_null:
            if isinstance(value,bool): kind="boolean"
            elif isinstance(value,int): kind="integer"
            elif isinstance(value,float): kind="number"
            elif isinstance(value,str): kind="string"
            else: kind="object" if isinstance(value,dict) else "array" if isinstance(value,list) else "null"
            if kind not in kinds: kinds.append(kind)
        result={"type":kinds[0] if len(kinds)==1 else kinds}
    if nullable and result.get("type")!="null":
        value_type=result["type"]; result["type"]=value_type+["null"] if isinstance(value_type,list) else [value_type,"null"]
    return result


def json_schema(p):
    value=json.loads(p.read_text(encoding="utf-8-sig"))
    schema={"$schema":"https://json-schema.org/draft/2020-12/schema",**_schema_for_values([value])}
    out=p.with_name(p.stem+"-schema.json")
    out.write_text(json.dumps(schema,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True); raise RuntimeError("JSON Schema vượt giới hạn đầu ra.")
    return {"summary":"Đã suy luận JSON Schema 2020-12 từ cấu trúc dữ liệu; hỗ trợ nested, required và nullable.","output_path":str(out)}


def json_to_yaml(p):
    import yaml
    value=json.loads(p.read_text(encoding="utf-8-sig")); out=p.with_name(p.stem+"-converted.yaml")
    out.write_text(yaml.safe_dump(value,allow_unicode=True,sort_keys=False,default_flow_style=False),encoding="utf-8")
    return {"summary":"Đã chuyển JSON sang YAML bằng SafeDumper, giữ Unicode và thứ tự key.","output_path":str(out)}


def sqlite_integrity(p):
    from urllib.parse import quote
    import sqlite3
    uri="file:"+quote(str(p.resolve()),safe="/:")+"?mode=ro&immutable=1"
    connection=sqlite3.connect(uri,uri=True,timeout=5)
    try:
        connection.execute("PRAGMA query_only=ON")
        connection.set_progress_handler(lambda:1,2_000_000)
        integrity=[row[0] for row in connection.execute("PRAGMA integrity_check(100)").fetchmany(100)]
        foreign=list(connection.execute("PRAGMA foreign_key_check").fetchmany(100))
        tables=connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchone()[0]
        report=["SQLite integrity report",f"Tables: {tables}",f"Integrity result: {', '.join(integrity) if integrity else 'no result'}",f"Foreign-key violations: {len(foreign)}"]
        report.extend("Foreign key: "+", ".join(str(value) for value in row) for row in foreign[:20])
        report.append("Database opened read-only; no schema or data was modified.")
        report.append("STATUS: issues detected." if integrity!=["ok"] or foreign else "STATUS: integrity check passed.")
        return tool_text("\n".join(report),"SQLite integrity")
    finally: connection.close()


def _silence_report(p,media_kind):
    data=ffprobe(p); duration=float(data.get("format",{}).get("duration") or 0)
    if duration<=0 or duration>1800: raise RuntimeError("Silence analysis hỗ trợ media dài tối đa 30 phút.")
    audio=[stream for stream in data.get("streams",[]) if stream.get("codec_type")=="audio"]
    if not audio: raise RuntimeError("Video không có track audio để phân tích." if media_kind=="video" else "Không tìm thấy track audio.")
    process=subprocess.run(["ffmpeg","-hide_banner","-i",str(p),"-map","0:a:0","-af","silencedetect=noise=-35dB:d=0.4","-f","null","-"],capture_output=True,text=True,timeout=900,check=False)
    if process.returncode!=0: raise RuntimeError("FFmpeg silence detection failed: "+(process.stderr or process.stdout)[-900:])
    starts=[]; intervals=[]
    for line in (process.stderr or "").splitlines():
        match=re.search(r"silence_start:\s*([0-9.]+)",line)
        if match: starts.append(float(match.group(1)))
        match=re.search(r"silence_end:\s*([0-9.]+)",line)
        if match and starts:
            start=starts.pop(0); end=float(match.group(1)); intervals.append((start,max(start,end)))
    for start in starts: intervals.append((start,duration))
    total=sum(end-start for start,end in intervals)
    rows=[f"Media: {p.name}",f"Duration: {duration:.3f} seconds",f"Silence intervals: {len(intervals)}",f"Total detected silence: {total:.3f} seconds","Threshold: -35 dB for at least 0.4 seconds",""]
    rows.extend(f"{i}. {start:.3f}s → {end:.3f}s ({end-start:.3f}s)" for i,(start,end) in enumerate(intervals,1))
    if not intervals: rows.append("No silence interval crossed the selected threshold.")
    return tool_text("\n".join(rows),f"{media_kind.title()} silence analysis")


def audio_silence_report(p): return _silence_report(p,"audio")
def video_silence_report(p): return _silence_report(p,"video")


def video_frames(p):
    data=ffprobe(p); duration=float(data.get("format",{}).get("duration") or 0)
    if duration<=0 or duration>1800: raise RuntimeError("Frame extraction hỗ trợ video dài tối đa 30 phút.")
    root=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"
    temp=Path(tempfile.mkdtemp(prefix="video-frames-",dir=root)); out=p.with_name(p.stem+"-frames.zip")
    interval=max(1.0,duration/60.0); pattern=temp/"frame-%03d.jpg"
    try:
        cmd("ffmpeg",["-y","-i",str(p),"-vf",f"fps=1/{interval:.5f},scale='min(960,iw)':-2","-frames:v","60","-q:v","4",str(pattern)],900)
        frames=sorted(temp.glob("frame-*.jpg"))
        if not frames: raise RuntimeError("FFmpeg không trích xuất được frame.")
        with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=4) as archive:
            for frame in frames: archive.write(frame,frame.name)
    finally: shutil.rmtree(temp,ignore_errors=True)
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True); raise RuntimeError("Video frames ZIP vượt giới hạn đầu ra.")
    return {"summary":f"Đã trích {len(frames)} frame JPEG, cách đều khoảng {interval:.2f} giây trên video {duration:.1f} giây.","output_path":str(out)}


def subtitle_convert(p):
    source=p.read_text(encoding="utf-8-sig")
    is_vtt=p.suffix.lower()==".vtt" or source.lstrip().startswith("WEBVTT")
    if is_vtt:
        lines=source.replace("\r\n","\n").replace("\r","\n").split("\n")
        while lines and (not lines[0].strip() or lines[0].strip().startswith(("WEBVTT","NOTE","STYLE","REGION"))): lines.pop(0)
        rendered="\n".join(lines)
        rendered=re.sub(r"(?<!\d)(\d{2}:\d{2}:\d{2})\.(\d{3})(?!\d)",r"\1,\2",rendered)
        out=p.with_name(p.stem+"-converted.srt")
    else:
        rendered=re.sub(r"(?<!\d)(\d{2}:\d{2}:\d{2}),(\d{3})(?!\d)",r"\1.\2",source.replace("\r\n","\n").replace("\r","\n"))
        rendered="WEBVTT\n\n"+rendered.lstrip(); out=p.with_name(p.stem+"-converted.vtt")
    if not re.search(r"\d{2}:\d{2}:\d{2}[,.]\d{3}\s+-->",rendered): raise RuntimeError("Không phát hiện cue timestamp SRT/VTT hợp lệ.")
    out.write_text(rendered.rstrip()+"\n",encoding="utf-8")
    return {"summary":"Đã chuyển định dạng phụ đề "+("WebVTT → SRT" if is_vtt else "SRT → WebVTT")+"; nội dung cue được giữ nguyên.","output_path":str(out)}


def text_deduplicate(p):
    raw=p.read_text(encoding="utf-8-sig"); seen=set(); kept=[]; removed=0
    for line in raw.splitlines():
        key=unicodedata.normalize("NFC",line).strip().casefold()
        if key and key in seen: removed+=1; continue
        if key: seen.add(key)
        kept.append(line)
    out=p.with_name(p.stem+"-deduplicated"+p.suffix)
    out.write_text("\n".join(kept)+("\n" if raw.endswith(("\n","\r")) else ""),encoding="utf-8")
    return {"summary":f"Đã giữ {len(kept):,} dòng và loại {removed:,} dòng trùng (Unicode NFC, không phân biệt hoa/thường).","output_path":str(out)}


def text_diff(p):
    import difflib
    if not zipfile.is_zipfile(p): raise RuntimeError("Gửi ZIP chứa đúng hai tệp văn bản cần so sánh.")
    with zipfile.ZipFile(p) as archive:
        members,total=_safe_zip_members(archive,{".txt",".md",".log",".srt",".vtt",".json",".csv",".yaml",".yml",".xml"},max_files=20,max_bytes=10*1024*1024)
        if len(members)!=2: raise RuntimeError("ZIP phải có đúng hai tệp văn bản được hỗ trợ.")
        members.sort(key=lambda item:item.filename.casefold())
        left=archive.read(members[0]).decode("utf-8-sig").splitlines(keepends=True)
        right=archive.read(members[1]).decode("utf-8-sig").splitlines(keepends=True)
    diff="".join(difflib.unified_diff(left,right,fromfile=members[0].filename,tofile=members[1].filename,n=3))
    same=not diff
    if same: diff="Hai tệp không có khác biệt về nội dung.\n"
    out=p.with_name(p.stem+"-diff.txt"); out.write_text(diff,encoding="utf-8")
    return {"summary":f"Đã so sánh {Path(members[0].filename).name} và {Path(members[1].filename).name}; "+("không có khác biệt." if same else "unified diff được đính kèm."),"output_path":str(out)}


def code_size_report(p):
    supported={".py",".pyw",".js",".mjs",".cjs",".ts",".tsx",".jsx",".css",".html",".htm",".json",".yaml",".yml",".sh",".bash",".go",".rs",".java",".c",".cpp",".h",".hpp",".cs",".sql",".md"}
    if p.suffix.lower() not in supported: raise RuntimeError("Định dạng source file không được hỗ trợ.")
    if p.stat().st_size>5*1024*1024: raise RuntimeError("Code size report giới hạn file 5 MB.")
    lines=p.read_text(encoding="utf-8-sig").splitlines()
    blank=sum(1 for line in lines if not line.strip())
    prefix=("#","//","/*","*","--",";","<!--")
    comment=sum(1 for line in lines if line.strip() and line.lstrip().startswith(prefix))
    trailing=sum(1 for line in lines if line.rstrip()!=line)
    longest=max(((len(line),index+1) for index,line in enumerate(lines)),default=(0,0))
    report=[f"File: {p.name}",f"Bytes: {p.stat().st_size:,}",f"Total lines: {len(lines):,}",f"Blank lines: {blank:,}",f"Comment-like lines: {comment:,}",f"Non-blank non-comment lines (approx): {max(0,len(lines)-blank-comment):,}",f"Trailing whitespace: {trailing:,}",f"Longest line: {longest[0]:,} characters (line {longest[1]})","Note: comment counting uses a lightweight prefix heuristic, not a language-aware parser."]
    return tool_text("\n".join(report),"Source size report")


def image_grayscale(p):
    from PIL import Image, ImageOps
    out=p.with_name(p.stem+"-grayscale.png")
    with Image.open(p) as raw:
        _guard_image_dimensions(raw)
        oriented=ImageOps.exif_transpose(raw)
        has_alpha=("A" in oriented.getbands()) or ("transparency" in oriented.info)
        if has_alpha:
            rgba=oriented.convert("RGBA")
            gray=ImageOps.grayscale(rgba)
            gray.putalpha(rgba.getchannel("A"))
        else:
            gray=ImageOps.grayscale(oriented)
        gray.save(out,"PNG",optimize=True)
        gray.close()
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("Grayscale PNG exceeds the 45 MB delivery limit.")
    return {"summary":f"Đã chuyển ảnh {p.suffix.lower()} thành PNG thang xám; EXIF orientation được áp dụng và alpha được giữ nếu có.","output_path":str(out)}


TOOLS={
 "image-ocr":image_ocr,"image-info":image_info,"image-clean-exif":image_clean,"image-compress":image_compress,
 "image-to-pdf":image_pdf,"qr-read":qr_read,"pdf-text":pdf_text,"pdf-info":pdf_info,
 "audio-transcribe":audio_transcribe,"audio-info":audio_info,"video-info":video_info,"video-thumbnail":video_thumbnail,
 "csv-profile":csv_profile,"json-format":json_format,"office-text":office_text,"archive-inspect":archive_inspect,"file-hash":file_hash,"text-clean":text_clean,"subtitle-text":subtitle_text,"html-text":html_text,
 "audio-normalize":audio_normalize,"video-audio":video_audio,"video-gif":video_gif,
 "image-resize":image_resize,"image-webp":image_webp,"image-palette":image_palette,
 "pdf-compress":pdf_compress,"pdf-to-images":pdf_to_images,"epub-text":epub_text,"sqlite-inspect":sqlite_inspect,
 "yaml-format":yaml_format,"xml-format":xml_format,"code-check":code_check,
 "video-contact-sheet":video_contact_sheet,"video-compress":video_compress,"audio-subtitles":audio_subtitles,
 "archive-safe-extract":archive_safe_extract,"xlsx-profile":xlsx_profile,
 "image-png":image_png,"csv-clean":csv_clean,"json-to-csv":json_to_csv,"csv-to-xlsx":csv_to_xlsx,
 "xlsx-to-csv":xlsx_to_csv,"pdf-split":pdf_split,"audio-convert":audio_convert,
 "csv-to-json":csv_to_json,"jsonl-format":jsonl_format,"yaml-to-json":yaml_to_json,"xml-to-json":xml_to_json,
 "sqlite-export":sqlite_export,"xlsx-to-json":xlsx_to_json,"pdf-extract-images":pdf_extract_images,
 "archive-manifest":archive_manifest,"text-stats":text_stats,"image-grayscale":image_grayscale,
 "pdf-merge":pdf_merge, "pdf-metadata-clean":pdf_metadata_clean, "pdf-outline":pdf_outline, "image-contact-sheet":image_contact_sheet, "image-duplicates":image_duplicates, "csv-split":csv_split, "csv-join":csv_join, "json-schema":json_schema, "json-to-yaml":json_to_yaml, "sqlite-integrity":sqlite_integrity, "audio-silence-report":audio_silence_report, "video-silence-report":video_silence_report, "video-frames":video_frames, "subtitle-convert":subtitle_convert, "text-deduplicate":text_deduplicate, "text-diff":text_diff, "code-size-report":code_size_report,
}


def _runner_output_path(raw_path, root):
    if not raw_path:
        return None
    candidate=Path(raw_path)
    if candidate.is_symlink():
        raise RuntimeError("Pipeline output symlinks are not allowed.")
    resolved=candidate.resolve(strict=True)
    if resolved.parent != root or not resolved.is_file():
        raise RuntimeError("Pipeline output must be a regular file inside the private runner input directory.")
    if resolved.stat().st_size > MAX_PIPELINE_OUTPUT:
        raise RuntimeError("Pipeline intermediate output exceeds 45 MB.")
    return resolved

def run_tool_pipeline(job, source, root):
    steps=validate_pipeline(job)
    current=source
    summaries=[]
    for index,step in enumerate(steps):
        tool_id=step["toolId"]
        result=TOOLS[tool_id](current)
        if not isinstance(result,dict):
            raise RuntimeError(f"Processor {tool_id} returned an invalid result.")
        summary=str(result.get("summary","")).strip()
        output=_runner_output_path(result.get("output_path",""),root)
        is_last=index==len(steps)-1
        if output:
            current=output
        elif not is_last:
            next_id=steps[index+1]["toolId"]
            if next_id != "text-clean" or tool_id not in TEXT_OUTPUT_TOOLS:
                raise RuntimeError(f"Processor {tool_id} did not produce a file for the next pipeline step.")
            current=root/f"pipeline-step-{index+1}.txt"
            current.write_text(summary or "Không phát hiện nội dung.",encoding="utf-8")
        summaries.append(f"Step {index+1}/{len(steps)} · {tool_id}: {summary or 'completed'}")
    final_output=str(_runner_output_path(result.get("output_path",""),root) or "")
    total_summary="\n\n".join(summaries)
    return {"summary":total_summary[:6000],"output_path":final_output}

def cmd_fetch(args):
    secret=os.environ.get("TELEGRAM_WEBHOOK_SECRET")
    if not secret: raise RuntimeError("Missing TELEGRAM_WEBHOOK_SECRET.")
    data=api_json(WORKER_URL+"/internal/tools/runner?job_id="+urllib.parse.quote(args.job_id),token=secret)
    Path(args.output).write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")

def cmd_download(args):
    job=load_job(Path(args.job_file))
    source=download_telegram(job["fileId"],job.get("fileName") or "upload.bin")
    Path(args.output).write_text(str(source),encoding="utf-8")

def cmd_run(args):
    job=load_job(Path(args.job_file))
    source=Path(Path(args.input_path_file).read_text(encoding="utf-8").strip())
    root=(Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs").resolve()
    if source.is_symlink():
        raise RuntimeError("Input file symlinks are not allowed.")
    resolved=source.resolve(strict=True)
    if resolved.parent != root or not resolved.is_file():
        raise RuntimeError("Input file is outside the private runner input directory.")
    result=run_tool_pipeline(job,resolved,root)
    summary=str(result.get("summary",""))
    output=result.get("output_path","")
    if output:
        candidate=Path(output)
        try:
            root_resolved=root.resolve()
            if not candidate.is_symlink():
                resolved_output=candidate.resolve(strict=True)
                if resolved_output.parent==root_resolved and resolved_output.is_file() and resolved_output.suffix.lower() in {".txt",".md",".csv",".json",".xml",".yaml",".yml",".srt",".vtt",".html"}:
                    preview=resolved_output.read_text(encoding="utf-8-sig",errors="replace")[:3800].strip()
                    if preview:
                        summary += "\n\nNội dung trích xuất (trích đoạn tối đa 3.800 ký tự; tệp đầy đủ được gửi kèm):\n" + preview
        except (OSError,UnicodeError):
            pass
    Path(args.output).write_text(json.dumps({"summary":summary[:6000],"output_path":output},ensure_ascii=False),encoding="utf-8")

def send_document(chat_id,path,caption):
    token=os.environ["TELEGRAM_BOT_TOKEN"]; boundary="----NolaneToolBoundary-31d9"
    fields=[]
    def text_field(name,value):
        fields.append((f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n").encode())
    text_field("chat_id",str(chat_id)); text_field("caption",caption[:850])
    filename=Path(path).name.replace('"',"_")[:120]
    head=(f"--{boundary}\r\nContent-Disposition: form-data; name=\"document\"; filename=\"{filename}\"\r\nContent-Type: application/octet-stream\r\n\r\n").encode()
    body=b"".join(fields)+head+Path(path).read_bytes()+f"\r\n--{boundary}--\r\n".encode()
    req=urllib.request.Request(f"https://api.telegram.org/bot{token}/sendDocument",data=body,headers={"content-type":f"multipart/form-data; boundary={boundary}"},method="POST")
    with urllib.request.urlopen(req,timeout=90) as r:
        result=json.loads(r.read(1_000_000).decode())
    if not result.get("ok"): raise RuntimeError(result.get("description","Telegram sendDocument failed."))

def callback(job_id,payload):
    secret=os.environ.get("TELEGRAM_WEBHOOK_SECRET")
    if not secret: raise RuntimeError("Missing TELEGRAM_WEBHOOK_SECRET.")
    return api_json(WORKER_URL+"/internal/tools/runner",method="POST",data={"job_id":job_id,**payload},token=secret)

def cmd_complete(args):
    # Re-fetch authoritative metadata after untrusted file processing has finished.
    token=os.environ.get("TELEGRAM_WEBHOOK_SECRET")
    if not token: raise RuntimeError("Missing TELEGRAM_WEBHOOK_SECRET.")
    job_data=api_json(
        WORKER_URL+"/internal/tools/runner?job_id="+urllib.parse.quote(args.job_id),
        token=token,
    )
    job=job_data.get("job")
    if not isinstance(job,dict) or job.get("id")!=args.job_id:
        raise RuntimeError("Worker returned an invalid or mismatched tool job.")
    result=json.loads(Path(args.result_file).read_text(encoding="utf-8"))
    output=result.get("output_path")
    if output:
        root=(Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs").resolve()
        candidate=Path(output)
        if candidate.is_symlink():
            raise RuntimeError("Tool output symlinks are not allowed.")
        p=candidate.resolve(strict=True)
        if p.parent!=root or not p.is_file() or p.stat().st_size>45*1024*1024:
            raise RuntimeError("Tool output must be a regular file inside the private runner input directory and stay under 45 MB.")
        send_document(int(job["chatId"]),p,"Nolane Tools · "+job["toolId"])
    callback(args.job_id,{"status":"completed","summary":result.get("summary","Đã hoàn thành.")})

def cmd_fail(args):
    try: callback(args.job_id,{"status":"failed","error":args.message[:1000]})
    except Exception as exc: print(f"Unable to report failure: {exc}",file=sys.stderr)


def main():
    parser=argparse.ArgumentParser(); sub=parser.add_subparsers(dest="cmd",required=True)
    p=sub.add_parser("fetch"); p.add_argument("job_id"); p.add_argument("output"); p.set_defaults(func=cmd_fetch)
    p=sub.add_parser("download"); p.add_argument("job_file"); p.add_argument("output"); p.set_defaults(func=cmd_download)
    p=sub.add_parser("run"); p.add_argument("job_file"); p.add_argument("input_path_file"); p.add_argument("output"); p.set_defaults(func=cmd_run)
    p=sub.add_parser("complete"); p.add_argument("job_id"); p.add_argument("result_file"); p.set_defaults(func=cmd_complete)
    p=sub.add_parser("fail"); p.add_argument("job_id"); p.add_argument("--message",default="Tool runner failed; see Actions logs."); p.set_defaults(func=cmd_fail)
    args=parser.parse_args()
    try: args.func(args)
    except Exception as exc:
        print(f"Nolane Tools error: {exc}",file=sys.stderr)
        sys.exit(1)

if __name__=="__main__": main()
