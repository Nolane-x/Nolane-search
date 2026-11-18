#!/usr/bin/env python3
"""Private GitHub-hosted execution engine for Nolane Tools."""
from __future__ import annotations
import argparse, csv, hashlib, json, mimetypes, os, re, shutil, subprocess, sys, tarfile, unicodedata, urllib.error, urllib.parse, urllib.request, zipfile
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
    "audio-normalize", "video-audio", "video-gif",
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


TOOLS={
 "image-ocr":image_ocr,"image-info":image_info,"image-clean-exif":image_clean,"image-compress":image_compress,
 "image-to-pdf":image_pdf,"qr-read":qr_read,"pdf-text":pdf_text,"pdf-info":pdf_info,
 "audio-transcribe":audio_transcribe,"audio-info":audio_info,"video-info":video_info,"video-thumbnail":video_thumbnail,
 "csv-profile":csv_profile,"json-format":json_format,"office-text":office_text,"archive-inspect":archive_inspect,"file-hash":file_hash,"text-clean":text_clean,"subtitle-text":subtitle_text,"html-text":html_text,
 "audio-normalize":audio_normalize,"video-audio":video_audio,"video-gif":video_gif,

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
