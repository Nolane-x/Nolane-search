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
}

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

def load_job(path):
    job = json.loads(Path(path).read_text(encoding="utf-8")).get("job", {})
    if not re.fullmatch(r"[0-9a-f-]{36}", str(job.get("id","")), re.I) or job.get("toolId") not in RUNNERS:
        raise RuntimeError("Invalid or unsupported tool job.")
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


def image_resize(p):
    from PIL import Image, ImageOps
    out=p.with_name(p.stem+"-resized.jpg")
    with Image.open(p) as raw:
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
        im=ImageOps.exif_transpose(raw)
        if im.mode not in ("RGB","RGBA"):
            im=im.convert("RGBA" if "A" in im.getbands() else "RGB")
        im.save(out,"WEBP",quality=84,method=6)
    return {"summary":f"Đã chuyển ảnh sang WebP; {p.stat().st_size:,} → {out.stat().st_size:,} bytes.","output_path":str(out)}

def image_palette(p):
    from PIL import Image, ImageOps
    with Image.open(p) as raw:
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
                pix.save(str(image),jpg_quality=82)
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
    cmd("ffmpeg",["-y","-i",str(p),"-map","0:v:0","-map","0:a?","-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","30","-maxrate","1000k","-bufsize","2000k","-c:a","aac","-b:a","96k","-movflags","+faststart","-sn","-dn","-threads","2",str(out)],900)
    if out.stat().st_size>44*1024*1024:
        out.unlink(missing_ok=True)
        raise RuntimeError("Video sau nén vẫn vượt giới hạn gửi 44 MB; hãy chọn clip ngắn hơn.")
    change=(1-out.stat().st_size/max(1,p.stat().st_size))*100
    return {"summary":f"Đã nén H.264/AAC ở tối đa 720p/1280 px, CRF 30: {p.stat().st_size:,} → {out.stat().st_size:,} bytes ({change:.1f}% thay đổi).","output_path":str(out)}

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
                    count+=1; total+=item.file_size
                    if count>max_files or total>max_bytes:
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
                    with archive.open(item) as source,target.open("wb") as destination:
                        shutil.copyfileobj(source,destination,1024*1024)
        else:
            with tarfile.open(p,"r:*") as archive:
                for item in archive.getmembers():
                    if item.isdir(): continue
                    if not item.isfile():
                        raise RuntimeError("Archive TAR chứa link hoặc special file; đã từ chối giải nén.")
                    count+=1; total+=item.size
                    if count>max_files or total>max_bytes:
                        raise RuntimeError("Archive vượt giới hạn 200 tệp hoặc 150 MB sau giải nén.")
                    parts=_safe_archive_parts(item.name)
                    source=archive.extractfile(item)
                    if source is None: continue
                    target=temp.joinpath(*parts)
                    target.parent.mkdir(parents=True,exist_ok=True)
                    with source,target.open("wb") as destination:
                        shutil.copyfileobj(source,destination,1024*1024)
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
}

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
    result=TOOLS[job["toolId"]](resolved)
    Path(args.output).write_text(json.dumps({"summary":str(result.get("summary",""))[:6000],"output_path":result.get("output_path","")},ensure_ascii=False),encoding="utf-8")

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
