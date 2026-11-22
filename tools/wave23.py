"""Wave 23 offline domain inspectors for Nolane Tools.

These are bounded, read-only analyzers. They never execute uploaded programs,
send data to remote services, or include user payload values in reports.
"""
from __future__ import annotations

import collections
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


MAX_BYTES = 20 * 1024 * 1024
MAX_TEXT_LINES = 500_000


def _report(path: Path, slug: str, heading: str, lines: list[str]) -> dict:
    output = path.with_name(path.stem + "-" + slug + "-report.txt")
    body = heading + "\n\n" + "\n".join(lines) + "\n"
    output.write_text(body, encoding="utf-8")
    return {"summary": body[:5_500], "output_path": str(output)}


def _read_text(path: Path, limit: int = MAX_BYTES) -> str:
    if path.stat().st_size > limit:
        raise RuntimeError("Input exceeds the Wave 23 size limit.")
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeError as exc:
        raise RuntimeError("Input must be valid UTF-8 text.") from exc
    if text.count("\n") > MAX_TEXT_LINES:
        raise RuntimeError("Input exceeds the line-count limit.")
    return text


def gcode_audit(path: Path) -> dict:
    text = _read_text(path)
    commands = collections.Counter()
    parameters = collections.Counter()
    bounds = {axis: [None, None] for axis in "XYZ"}
    temperatures = []
    feed_values = []
    spindle_values = []
    lines = text.splitlines()
    if len(lines) > MAX_TEXT_LINES:
        raise RuntimeError("G-code contains too many lines.")
    numbered = 0
    checksum_markers = 0
    comment_only = 0
    for raw in lines:
        line = re.sub(r"\([^)]*\)", "", raw.split(";", 1)[0]).strip().upper()
        if not line or line == "%":
            comment_only += 1
            continue
        numbered += 1
        if "*" in line:
            checksum_markers += 1
            line = line.split("*", 1)[0]
        tokens = re.findall(r"([A-Z])\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+))", line)
        values = {}
        for letter, raw_value in tokens:
            try:
                value = float(raw_value)
            except ValueError:
                continue
            values[letter] = value
            parameters[letter] += 1
            if letter in bounds:
                low, high = bounds[letter]
                bounds[letter] = [value if low is None else min(low, value),
                                  value if high is None else max(high, value)]
            elif letter == "F":
                feed_values.append(value)
            elif letter == "S":
                spindle_values.append(value)
            elif letter in {"E", "A", "B", "C"}:
                pass
        for letter in ("G", "M"):
            if letter in values:
                command = int(values[letter])
                commands[f"{letter}{command}"] += 1
        if "S" in values and any(int(values.get("M", -1)) in {104, 109, 140, 190} for _ in (0,)):
            temperatures.append(values["S"])
    if not numbered:
        raise RuntimeError("No G-code command lines were found.")
    hazard = {
        "laser/spindle start (M3/M4)": commands["M3"] + commands["M4"],
        "spindle stop (M5)": commands["M5"],
        "emergency stop (M112)": commands["M112"],
        "direct pin control (M42)": commands["M42"],
        "homing (G28)": commands["G28"],
        "absolute mode (G90)": commands["G90"],
        "relative mode (G91)": commands["G91"],
    }
    lines_out = [
        f"Physical lines: {len(lines):,}",
        f"Non-empty command lines: {numbered:,}",
        f"Comment/blank lines: {comment_only:,}",
        f"Recognized G/M commands: {sum(commands.values()):,}",
        f"Checksum markers: {checksum_markers:,}",
        "Command frequencies: " + (", ".join(f"{key}={value}" for key, value in commands.most_common(15)) or "none"),
        "Motion-axis extents (program units; not machine-calibrated):",
    ]
    for axis, (low, high) in bounds.items():
        lines_out.append(f"  {axis}: " + (f"{low:g} to {high:g}" if low is not None else "not present"))
    lines_out.extend([
        f"Feed-rate words: {len(feed_values):,}; maximum programmed feed: {max(feed_values):g}" if feed_values else "Feed-rate words: 0",
        f"Spindle/power words: {len(spindle_values):,}; maximum S value: {max(spindle_values):g}" if spindle_values else "Spindle/power words: 0",
        "Safety-relevant command counts:",
    ])
    lines_out.extend(f"  {label}: {count:,}" for label, count in hazard.items())
    lines_out.append("Static inspection only: no toolpath simulation, machine-limit inference or code execution.")
    return _report(path, "gcode", "G-code static audit", lines_out)


def _midi_vlq(data: bytes, offset: int, end: int) -> tuple[int, int]:
    value = 0
    for _ in range(4):
        if offset >= end:
            raise ValueError("truncated variable-length quantity")
        byte = data[offset]
        offset += 1
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return value, offset
    raise ValueError("variable-length quantity exceeds four bytes")


def midi_audit(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        raise RuntimeError("MIDI file exceeds 20 MiB.")
    if len(data) < 14 or data[:4] != b"MThd":
        raise RuntimeError("Not a Standard MIDI File (missing MThd header).")
    header_length = int.from_bytes(data[4:8], "big")
    if header_length < 6 or 8 + header_length > len(data):
        raise RuntimeError("Invalid MIDI header length.")
    fmt = int.from_bytes(data[8:10], "big")
    track_count = int.from_bytes(data[10:12], "big")
    division = int.from_bytes(data[12:14], "big")
    if fmt not in (0, 1, 2) or not 1 <= track_count <= 512:
        raise RuntimeError("Unsupported MIDI format or track count.")
    if (division & 0x7FFF) == 0:
        raise RuntimeError("Invalid MIDI time division.")
    offset = 8 + header_length
    note_on = note_off = tempo_events = sysex_events = meta_events = 0
    channels = set()
    max_tick = 0
    track_lengths = []
    for _track in range(track_count):
        if offset + 8 > len(data) or data[offset:offset + 4] != b"MTrk":
            raise RuntimeError("MIDI track chunk is missing or truncated.")
        chunk_length = int.from_bytes(data[offset + 4:offset + 8], "big")
        start = offset + 8
        end = start + chunk_length
        if end > len(data):
            raise RuntimeError("MIDI track chunk exceeds the file boundary.")
        offset = end
        cursor = start
        tick = 0
        running_status = None
        event_limit = 2_000_000
        events = 0
        while cursor < end:
            events += 1
            if events > event_limit:
                raise RuntimeError("MIDI track exceeds the event-count limit.")
            delta, cursor = _midi_vlq(data, cursor, end)
            tick += delta
            if cursor >= end:
                raise RuntimeError("Truncated MIDI event.")
            first = data[cursor]
            if first & 0x80:
                status = first
                cursor += 1
                if status < 0xF0:
                    running_status = status
            else:
                if running_status is None:
                    raise RuntimeError("MIDI running status appears before a channel status.")
                status = running_status
            if status == 0xFF:
                if cursor + 2 > end:
                    raise RuntimeError("Truncated MIDI meta event.")
                meta_type = data[cursor]
                cursor += 1
                length, cursor = _midi_vlq(data, cursor, end)
                if cursor + length > end:
                    raise RuntimeError("MIDI meta event exceeds its track.")
                if meta_type == 0x51 and length == 3:
                    tempo_events += 1
                meta_events += 1
                cursor += length
                running_status = None
            elif status in (0xF0, 0xF7):
                length, cursor = _midi_vlq(data, cursor, end)
                if cursor + length > end:
                    raise RuntimeError("MIDI SysEx event exceeds its track.")
                cursor += length
                sysex_events += 1
                running_status = None
            elif 0x80 <= status <= 0xEF:
                kind = status >> 4
                channel = status & 0x0F
                channels.add(channel + 1)
                size = 1 if kind in (0xC, 0xD) else 2
                if cursor + size > end:
                    raise RuntimeError("Truncated MIDI channel event.")
                first_data = data[cursor]
                if first_data >= 0x80 or (size == 2 and data[cursor + 1] >= 0x80):
                    raise RuntimeError("Invalid MIDI channel data byte.")
                if kind == 0x9 and size == 2 and data[cursor + 1] > 0:
                    note_on += 1
                elif kind == 0x8 or (kind == 0x9 and size == 2 and data[cursor + 1] == 0):
                    note_off += 1
                cursor += size
            else:
                raise RuntimeError("Unsupported or malformed MIDI system event.")
        track_lengths.append(tick)
        max_tick = max(max_tick, tick)
    if offset != len(data):
        trailing = data[offset:]
        if any(trailing):
            raise RuntimeError("Unexpected non-padding bytes after the MIDI track chunks.")
    division_kind = "SMPTE" if division & 0x8000 else f"{division} ticks per quarter note"
    lines_out = [
        f"Format: {fmt}",
        f"Tracks: {track_count:,}",
        f"Time division: {division_kind}",
        f"Channels used: {len(channels):,}",
        f"Note-on events: {note_on:,}",
        f"Note-off events: {note_off:,}",
        f"Tempo meta events: {tempo_events:,}",
        f"Other meta events: {meta_events - tempo_events:,}",
        f"System-exclusive events: {sysex_events:,}",
        f"Longest track duration: {max_tick:,} ticks",
        "No MIDI messages were played; this is a structural file inspection, not audio rendering.",
    ]
    return _report(path, "midi", "Standard MIDI File audit", lines_out)


def _xml_bytes(path: Path, allow_mxl: bool = False) -> bytes:
    if path.stat().st_size > MAX_BYTES:
        raise RuntimeError("XML input exceeds 20 MiB.")
    raw = path.read_bytes()
    if allow_mxl and path.suffix.lower() == ".mxl":
        try:
            with zipfile.ZipFile(path) as archive:
                members = archive.infolist()
                if len(members) > 50 or sum(item.file_size for item in members) > 80 * 1024 * 1024:
                    raise RuntimeError("Compressed MusicXML exceeds archive limits.")
                for item in members:
                    name = item.filename.replace("\\", "/")
                    mode = (item.external_attr >> 16) & 0xFFFF
                    if name.startswith("/") or ".." in name.split("/") or (mode & 0o170000) == 0o120000 or item.flag_bits & 1:
                        raise RuntimeError("Unsafe or encrypted MusicXML archive member.")
                container = next((item for item in members if item.filename == "META-INF/container.xml"), None)
                if container is None:
                    raise RuntimeError("MXL container.xml is missing.")
                container_data = archive.read(container)
                if b"<!DOCTYPE" in container_data.upper() or b"<!ENTITY" in container_data.upper():
                    raise RuntimeError("DTD and entity declarations are not allowed.")
                root = ET.fromstring(container_data)
                rootfile = next((element.attrib.get("full-path") for element in root.iter()
                                 if element.tag.rsplit("}", 1)[-1] == "rootfile"), None)
                if not rootfile or rootfile not in archive.namelist():
                    raise RuntimeError("MXL score rootfile is missing.")
                raw = archive.read(rootfile)
        except (zipfile.BadZipFile, ET.ParseError) as exc:
            raise RuntimeError("Invalid compressed MusicXML package.") from exc
    if len(raw) > MAX_BYTES:
        raise RuntimeError("Expanded MusicXML exceeds 20 MiB.")
    upper = raw.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise RuntimeError("DTD and entity declarations are not allowed.")
    return raw


def musicxml_audit(path: Path) -> dict:
    raw = _xml_bytes(path, allow_mxl=True)
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise RuntimeError("MusicXML document is malformed.") from exc
    local = lambda tag: tag.rsplit("}", 1)[-1].lower()
    counts = collections.Counter(local(element.tag) for element in root.iter())
    part_ids = {element.attrib.get("id") for element in root.iter() if local(element.tag) == "score-part"}
    part_refs = [element.attrib.get("id") for element in root.iter() if local(element.tag) == "part"]
    missing_refs = sum(1 for item in part_refs if item and item not in part_ids)
    tempo = sum(1 for element in root.iter() if local(element.tag) == "sound" and "tempo" in element.attrib)
    metronome = counts["metronome"]
    lines_out = [
        f"Root element: {local(root.tag)}",
        f"Part definitions: {len(part_ids):,}",
        f"Part bodies: {len(part_refs):,}",
        f"Measures: {counts['measure']:,}",
        f"Notes: {counts['note']:,}",
        f"Rests: {counts['rest']:,}",
        f"Time-signature events: {counts['time']:,}",
        f"Key-signature events: {counts['key']:,}",
        f"Metronome marks: {metronome:,}",
        f"Explicit sound tempo events: {tempo:,}",
        f"Part references without a matching score-part ID: {missing_refs:,}",
        "Score titles, lyrics, instrument names and note text are not included in this report.",
    ]
    return _report(path, "musicxml", "MusicXML structural audit", lines_out)


def _bib_entries(text: str) -> list[tuple[str, str]]:
    entries = []
    index = 0
    while index < len(text):
        at = text.find("@", index)
        if at < 0:
            break
        match = re.match(r"@([A-Za-z]+)\s*([({])", text[at:])
        if not match:
            index = at + 1
            continue
        kind = match.group(1).lower()
        opener = match.group(2)
        closer = "}" if opener == "{" else ")"
        body_start = at + match.end()
        depth = 1
        quoted = False
        escaped = False
        cursor = body_start
        while cursor < len(text):
            char = text[cursor]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = not quoted
            elif not quoted and char == opener:
                depth += 1
            elif not quoted and char == closer:
                depth -= 1
                if depth == 0:
                    break
            cursor += 1
        if depth != 0:
            raise RuntimeError("BibTeX entry has unbalanced braces or parentheses.")
        body = text[body_start:cursor]
        index = cursor + 1
        if kind in {"comment", "preamble", "string"}:
            continue
        fields = []
        part_start = 0
        brace_depth = 0
        quoted = False
        escaped = False
        for pos, char in enumerate(body):
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = not quoted
            elif not quoted and char == "{":
                brace_depth += 1
            elif not quoted and char == "}":
                brace_depth = max(0, brace_depth - 1)
            elif not quoted and brace_depth == 0 and char == ",":
                fields.append(body[part_start:pos])
                part_start = pos + 1
        fields.append(body[part_start:])
        key = fields[0].strip().split(",", 1)[0].strip() if fields else ""
        names = set()
        for item in fields[1:]:
            field_match = re.match(r"\s*([A-Za-z][A-Za-z0-9_-]*)\s*=", item)
            if field_match:
                names.add(field_match.group(1).lower())
        entries.append((kind, key + "\0" + ",".join(sorted(names))))
    return entries


def bibtex_audit(path: Path) -> dict:
    text = _read_text(path, 10 * 1024 * 1024)
    entries = _bib_entries(text)
    keys = []
    duplicates = 0
    missing_title = missing_author = missing_year = 0
    for kind, packed in entries:
        key, _, field_string = packed.partition("\0")
        fields = set(filter(None, field_string.split(",")))
        if key:
            keys.append(key.casefold())
        if kind in {"article", "book", "inproceedings", "incollection", "phdthesis", "mastersthesis"}:
            missing_title += "title" not in fields
            missing_author += not ({"author", "editor"} & fields)
            missing_year += "year" not in fields
    duplicates = len(keys) - len(set(keys))
    dois = re.findall(r"(?i)\bdoi\s*=\s*[{\"]\s*([^}\"\\s,]+)", text)
    doi_duplicates = len(dois) - len({value.casefold() for value in dois})
    lines_out = [
        f"Bibliographic entries: {len(entries):,}",
        f"Unique citation keys: {len(set(keys)):,}",
        f"Duplicate citation keys: {duplicates:,}",
        f"Entries missing title (required-entry types): {missing_title:,}",
        f"Entries missing author/editor: {missing_author:,}",
        f"Entries missing year: {missing_year:,}",
        f"Repeated DOI values: {doi_duplicates:,}",
        "Citation keys, author names, titles, venues and DOI values are withheld.",
    ]
    return _report(path, "bibtex", "BibTeX collection audit", lines_out)


def nmea_track_audit(path: Path) -> dict:
    text = _read_text(path, 10 * 1024 * 1024)
    valid = invalid = missing = malformed = position_sentences = coordinate_errors = 0
    kinds = collections.Counter()
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if not line.startswith("$"):
            malformed += 1
            continue
        body, marker, checksum = line.partition("*")
        if not marker:
            missing += 1
        elif len(checksum) < 2 or not re.fullmatch(r"[0-9A-Fa-f]{2}", checksum[:2]):
            invalid += 1
        else:
            expected = 0
            for char in body[1:]:
                expected ^= ord(char)
            if expected == int(checksum[:2], 16):
                valid += 1
            else:
                invalid += 1
        fields = body[1:].split(",")
        sentence = fields[0][-3:].upper() if fields else "???"
        kinds[sentence] += 1
        if sentence in {"RMC", "GGA"}:
            position_sentences += 1
            try:
                if sentence == "RMC":
                    lat, ns, lon, ew = fields[3:7]
                else:
                    lat, ns, lon, ew = fields[2:6]
                def coord(value: str, hemi: str, width: int) -> float:
                    raw = float(value)
                    degrees = int(raw // 100)
                    minutes = raw - degrees * 100
                    if minutes >= 60 or degrees > (90 if width == 2 else 180) or hemi not in ({"N", "S"} if width == 2 else {"E", "W"}):
                        raise ValueError("coordinate")
                    result = degrees + minutes / 60
                    return -result if hemi in {"S", "W"} else result
                latitude = coord(lat, ns, 2)
                longitude = coord(lon, ew, 3)
                if abs(latitude) > 90 or abs(longitude) > 180:
                    coordinate_errors += 1
            except (ValueError, IndexError):
                coordinate_errors += 1
    if not valid + invalid + missing + malformed:
        raise RuntimeError("No NMEA sentence records were found.")
    lines_out = [
        f"Records: {valid + invalid + missing + malformed:,}",
        f"Checksum valid: {valid:,}",
        f"Checksum invalid: {invalid:,}",
        f"Checksum missing: {missing:,}",
        f"Malformed/non-sentence lines: {malformed:,}",
        f"RMC/GGA position-bearing records: {position_sentences:,}",
        f"RMC/GGA coordinate-format or range issues: {coordinate_errors:,}",
        "Sentence-type counts: " + (", ".join(f"{key}={value}" for key, value in kinds.most_common(20)) or "none"),
        "Coordinates, timestamps, route points and receiver identifiers are never reported.",
    ]
    return _report(path, "nmea", "NMEA GNSS log audit", lines_out)


def _walk_tasks(value, findings: collections.Counter, state: dict, depth: int = 0):
    if depth > 80 or state["nodes"] > 100_000:
        raise RuntimeError("Ansible YAML structure exceeds analysis limits.")
    state["nodes"] += 1
    if isinstance(value, list):
        for child in value:
            _walk_tasks(child, findings, state, depth + 1)
    elif isinstance(value, dict):
        if any(key in value for key in ("shell", "command", "raw", "script")):
            for module in ("shell", "command", "raw", "script"):
                if module in value:
                    findings[module] += 1
        if value.get("become") is True:
            findings["become"] += 1
        if value.get("no_log") is not True and any(key in value for key in ("shell", "command", "raw", "script")):
            findings["command_without_no_log"] += 1
        if value.get("ignore_errors") is True or value.get("ignore_unreachable") is True:
            findings["ignored_errors"] += 1
        for module in ("apt", "yum", "dnf", "package"):
            config = value.get(module)
            if isinstance(config, dict) and not any(key in config for key in ("version", "state")):
                findings["package_without_version_or_state"] += 1
        for child in value.values():
            if isinstance(child, (dict, list)):
                _walk_tasks(child, findings, state, depth + 1)


def ansible_playbook_audit(path: Path) -> dict:
    text = _read_text(path, 10 * 1024 * 1024)
    if text.count("&") + text.count("*") > 2_000:
        raise RuntimeError("Ansible YAML alias/reference count exceeds the safe limit.")
    try:
        import yaml
        docs = list(yaml.safe_load_all(text))
    except Exception as exc:
        raise RuntimeError("Ansible YAML could not be parsed safely.") from exc
    findings = collections.Counter()
    state = {"nodes": 0}
    plays = tasks = handlers = 0
    for doc in docs:
        if doc is None:
            continue
        if not isinstance(doc, list):
            raise RuntimeError("Ansible playbook documents must contain a list of plays.")
        plays += len(doc)
        for play in doc:
            if not isinstance(play, dict):
                findings["non_object_play"] += 1
                continue
            for key in ("tasks", "pre_tasks", "post_tasks"):
                if isinstance(play.get(key), list):
                    tasks += len(play[key])
            if isinstance(play.get("handlers"), list):
                handlers += len(play["handlers"])
            _walk_tasks(play, findings, state)
    lines_out = [
        f"Playbooks/documents: {len([doc for doc in docs if doc is not None]):,}",
        f"Plays: {plays:,}",
        f"Top-level task entries: {tasks:,}",
        f"Handler entries: {handlers:,}",
        f"Analyzed YAML nodes: {state['nodes']:,}",
        "Static findings (counts only):",
    ]
    lines_out.extend(f"  {key}: {value:,}" for key, value in sorted(findings.items()))
    lines_out.append("Heuristic review only; tasks, templates, roles and Ansible modules were not executed.")
    return _report(path, "ansible", "Ansible playbook static audit", lines_out)


def prometheus_rules_audit(path: Path) -> dict:
    text = _read_text(path, 5 * 1024 * 1024)
    try:
        import yaml
        document = yaml.safe_load(text)
    except Exception as exc:
        raise RuntimeError("Prometheus rules YAML could not be parsed safely.") from exc
    if not isinstance(document, dict) or not isinstance(document.get("groups", []), list):
        raise RuntimeError("Prometheus rules must contain a groups list.")
    groups = document.get("groups", [])
    group_names = []
    rules = alerts = records = missing_expr = missing_severity = missing_summary = missing_description = 0
    for group in groups:
        if not isinstance(group, dict):
            continue
        name = group.get("name")
        if isinstance(name, str) and name:
            group_names.append(name)
        for rule in group.get("rules", []) if isinstance(group.get("rules"), list) else []:
            if not isinstance(rule, dict):
                continue
            alerts += bool(rule.get("alert"))
            records += bool(rule.get("record"))
            rules += 1
            missing_expr += not isinstance(rule.get("expr"), str) or not rule.get("expr", "").strip()
            if rule.get("alert"):
                labels = rule.get("labels") if isinstance(rule.get("labels"), dict) else {}
                annotations = rule.get("annotations") if isinstance(rule.get("annotations"), dict) else {}
                missing_severity += "severity" not in labels
                missing_summary += "summary" not in annotations
                missing_description += "description" not in annotations
    duplicate_groups = len(group_names) - len(set(group_names))
    lines_out = [
        f"Rule groups: {len(groups):,}",
        f"Unique group names: {len(set(group_names)):,}",
        f"Duplicate group names: {duplicate_groups:,}",
        f"Rules: {rules:,}",
        f"Alerting rules: {alerts:,}",
        f"Recording rules: {records:,}",
        f"Rules missing expression: {missing_expr:,}",
        f"Alert rules missing severity label: {missing_severity:,}",
        f"Alert rules missing summary annotation: {missing_summary:,}",
        f"Alert rules missing description annotation: {missing_description:,}",
        "PromQL expressions are not parsed or evaluated; alert names, labels and query text are withheld.",
    ]
    return _report(path, "prometheus", "Prometheus rules static audit", lines_out)


def grafana_dashboard_audit(path: Path) -> dict:
    text = _read_text(path, 10 * 1024 * 1024)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Grafana dashboard JSON is malformed.") from exc
    dashboard = data.get("dashboard", data) if isinstance(data, dict) else None
    if not isinstance(dashboard, dict):
        raise RuntimeError("Expected a Grafana dashboard JSON object.")
    panel_ids = []
    panel_types = collections.Counter()
    datasource_refs = 0
    query_targets = 0
    variables = 0
    repeated_panel_ids = 0
    public_flags = 0
    stack = list(dashboard.get("panels", [])) if isinstance(dashboard.get("panels"), list) else []
    node_count = 0
    while stack:
        panel = stack.pop()
        node_count += 1
        if node_count > 20_000:
            raise RuntimeError("Grafana dashboard exceeds the panel-count limit.")
        if not isinstance(panel, dict):
            continue
        if "id" in panel:
            panel_ids.append(str(panel.get("id")))
        if isinstance(panel.get("type"), str):
            panel_types[panel["type"]] += 1
        datasource_refs += "datasource" in panel
        targets = panel.get("targets")
        if isinstance(targets, list):
            query_targets += len(targets)
        nested = panel.get("panels")
        if isinstance(nested, list):
            stack.extend(nested)
    templating = dashboard.get("templating")
    if isinstance(templating, dict) and isinstance(templating.get("list"), list):
        variables = len(templating["list"])
    repeated_panel_ids = len(panel_ids) - len(set(panel_ids))
    public_flags = int(bool(dashboard.get("isPublic"))) + int(bool(dashboard.get("publicDashboardEnabled")))
    lines_out = [
        f"Dashboard JSON schema version: {dashboard.get('schemaVersion') if isinstance(dashboard.get('schemaVersion'), int) else 'not specified'}",
        f"Panels (including nested rows): {len(panel_ids):,}",
        f"Duplicate panel IDs: {repeated_panel_ids:,}",
        f"Panel types: " + (", ".join(f"{key}={value}" for key, value in panel_types.most_common(20)) or "none"),
        f"Panel datasource references: {datasource_refs:,}",
        f"Query target objects: {query_targets:,}",
        f"Template variables: {variables:,}",
        f"Explicit public-dashboard flags: {public_flags:,}",
        f"Dashboard annotations: {len(dashboard.get('annotations', {}).get('list', [])) if isinstance(dashboard.get('annotations'), dict) and isinstance(dashboard.get('annotations', {}).get('list'), list) else 0:,}",
        "Dashboard title, UID, datasource URLs, query expressions, variables and text-panel contents are withheld.",
    ]
    return _report(path, "grafana", "Grafana dashboard static audit", lines_out)


def hdf5_audit(path: Path) -> dict:
    if path.stat().st_size > MAX_BYTES:
        raise RuntimeError("HDF5 input exceeds 20 MiB.")
    try:
        import h5py
        with h5py.File(path, "r") as handle:
            groups = datasets = compressed = chunked = external_links = 0
            total_elements = max_dimensions = max_rank = 0
            dtype_kinds = collections.Counter()
            stack = [handle]
            visited = set()
            while stack:
                group = stack.pop()
                try:
                    token = hash(group.id)
                except Exception:
                    token = id(group)
                if token in visited:
                    continue
                visited.add(token)
                groups += int(group.name != "/")
                if groups + datasets > 20_000:
                    raise RuntimeError("HDF5 object-count limit exceeded.")
                for name in group:
                    link = group.get(name, getlink=True)
                    if isinstance(link, h5py.ExternalLink):
                        external_links += 1
                        continue
                    if not isinstance(link, h5py.HardLink):
                        continue
                    obj = group.get(name)
                    if isinstance(obj, h5py.Group):
                        stack.append(obj)
                    elif isinstance(obj, h5py.Dataset):
                        datasets += 1
                        shape = obj.shape or ()
                        count = 1
                        for dimension in shape:
                            count *= int(dimension)
                        total_elements += count
                        max_rank = max(max_rank, len(shape))
                        max_dimensions = max(max_dimensions, max(shape, default=0))
                        dtype_kinds[str(obj.dtype.kind)] += 1
                        compressed += bool(obj.compression or obj.scaleoffset is not None)
                        chunked += bool(obj.chunks)
            lines_out = [
                f"Groups: {groups:,}",
                f"Datasets: {datasets:,}",
                f"Total declared elements (metadata estimate): {total_elements:,}",
                f"Maximum dataset rank: {max_rank:,}",
                f"Maximum dimension length: {max_dimensions:,}",
                f"Compressed datasets: {compressed:,}",
                f"Chunked datasets: {chunked:,}",
                f"External links skipped: {external_links:,}",
                "Dataset dtype-kind counts: " + (", ".join(f"{key}={value}" for key, value in sorted(dtype_kinds.items())) or "none"),
                "Dataset/group names, attributes and data values are never read into the report.",
            ]
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("HDF5 file could not be inspected safely.") from exc
    return _report(path, "hdf5", "HDF5 scientific-data metadata audit", lines_out)


def avro_schema_audit(path: Path) -> dict:
    text = _read_text(path, 10 * 1024 * 1024)
    try:
        schema = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Avro schema JSON is malformed.") from exc
    counts = collections.Counter()
    issues = collections.Counter()
    named = set()
    def walk(node, depth=0):
        if depth > 100 or counts["nodes"] > 100_000:
            raise RuntimeError("Avro schema nesting or node count exceeds the limit.")
        counts["nodes"] += 1
        if isinstance(node, list):
            seen = set()
            for branch in node:
                marker = json.dumps(branch, sort_keys=True, ensure_ascii=False)
                if marker in seen:
                    issues["duplicate_union_branch"] += 1
                seen.add(marker)
                walk(branch, depth + 1)
        elif isinstance(node, dict):
            kind = node.get("type")
            if kind == "record":
                counts["records"] += 1
                fields = node.get("fields")
                if not isinstance(fields, list):
                    issues["record_without_fields_array"] += 1
                    fields = []
                field_names = []
                for field in fields:
                    if not isinstance(field, dict):
                        issues["invalid_field_definition"] += 1
                        continue
                    name = field.get("name")
                    if isinstance(name, str):
                        field_names.append(name)
                        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                            issues["invalid_field_name"] += 1
                    else:
                        issues["field_missing_name"] += 1
                    if "type" in field:
                        walk(field["type"], depth + 1)
                    else:
                        issues["field_missing_type"] += 1
                    if "default" in field and isinstance(field.get("type"), list) and field["type"] and field["type"][0] == "null" and field["default"] is not None:
                        issues["union_default_mismatch_candidate"] += 1
                issues["duplicate_field_names"] += len(field_names) - len(set(field_names))
            elif kind == "enum":
                counts["enums"] += 1
                symbols = node.get("symbols") if isinstance(node.get("symbols"), list) else []
                issues["duplicate_enum_symbols"] += len(symbols) - len(set(str(item) for item in symbols))
            elif kind == "fixed":
                counts["fixed"] += 1
                if not isinstance(node.get("size"), int) or node["size"] <= 0:
                    issues["invalid_fixed_size"] += 1
            elif isinstance(kind, str):
                if kind == "array":
                    counts["arrays"] += 1
                    if "items" in node:
                        walk(node["items"], depth + 1)
                    else:
                        issues["array_missing_items"] += 1
                elif kind == "map":
                    counts["maps"] += 1
                    if "values" in node:
                        walk(node["values"], depth + 1)
                    else:
                        issues["map_missing_values"] += 1
                elif kind not in {"null", "boolean", "int", "long", "float", "double", "bytes", "string"}:
                    counts["named_references"] += 1
            else:
                issues["object_missing_type"] += 1
        elif isinstance(node, str):
            if node not in {"null", "boolean", "int", "long", "float", "double", "bytes", "string"}:
                counts["named_references"] += 1
        else:
            issues["invalid_schema_node"] += 1
    walk(schema)
    lines_out = [
        f"Schema nodes visited: {counts['nodes']:,}",
        f"Record definitions: {counts['records']:,}",
        f"Enum definitions: {counts['enums']:,}",
        f"Fixed definitions: {counts['fixed']:,}",
        f"Array definitions: {counts['arrays']:,}",
        f"Map definitions: {counts['maps']:,}",
        f"Named type references: {counts['named_references']:,}",
        "Structural issue counts (not a complete Avro specification validator):",
    ]
    lines_out.extend(f"  {key}: {value:,}" for key, value in sorted(issues.items()))
    lines_out.append("Record/type/field names and default values are withheld.")
    return _report(path, "avro", "Avro schema structural audit", lines_out)


def graphql_schema_audit(path: Path) -> dict:
    text = _read_text(path, 10 * 1024 * 1024)
    try:
        from graphql import parse, build_ast_schema, validate_schema
        document = parse(text, no_location=False)
        schema = build_ast_schema(document)
        errors = validate_schema(schema)
    except Exception as exc:
        raise RuntimeError("GraphQL SDL could not be parsed or built as a schema.") from exc
    definitions = collections.Counter()
    fields = arguments = enum_values = deprecated = 0
    for definition in document.definitions:
        kind = type(definition).__name__
        definitions[kind] += 1
        definition_fields = getattr(definition, "fields", None)
        if definition_fields:
            fields += len(definition_fields)
            for field in definition_fields:
                arguments += len(getattr(field, "arguments", None) or [])
                deprecated += any(getattr(directive, "name", None) and directive.name.value == "deprecated"
                                  for directive in (getattr(field, "directives", None) or []))
        values = getattr(definition, "values", None)
        if values:
            enum_values += len(values)
    types = schema.type_map
    lines_out = [
        f"SDL definitions: {len(document.definitions):,}",
        f"Schema type-map entries (including introspection types): {len(types):,}",
        f"Object/interface/input fields: {fields:,}",
        f"Field arguments: {arguments:,}",
        f"Enum values: {enum_values:,}",
        f"Deprecated field definitions: {deprecated:,}",
        f"Schema validation errors: {len(errors):,}",
        "Definition kinds: " + (", ".join(f"{key}={value}" for key, value in sorted(definitions.items())) or "none"),
        "Type, field, argument names, default values and descriptions are withheld.",
        "Schema validation only; no resolver, query or mutation was executed.",
    ]
    return _report(path, "graphql", "GraphQL SDL schema audit", lines_out)


def protobuf_schema_audit(path: Path) -> dict:
    text = _read_text(path, 10 * 1024 * 1024)
    # Replace comments before lexical checks; strings are not interpreted or evaluated.
    clean = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    clean = re.sub(r"(?m)//.*$", " ", clean)
    syntax = re.findall(r"\bsyntax\s*=\s*['\"](proto[23])['\"]\s*;", clean)
    package_count = len(re.findall(r"\bpackage\s+[A-Za-z_][\w.] *\s*;".replace(" ", ""), clean))
    messages = re.findall(r"\bmessage\s+([A-Za-z_]\w*)\s*\{", clean)
    enums = re.findall(r"\benum\s+([A-Za-z_]\w*)\s*\{", clean)
    services = len(re.findall(r"\bservice\s+[A-Za-z_]\w*\s*\{", clean))
    imports = len(re.findall(r"\bimport\s+(?:public\s+|weak\s+)?['\"][^'\"]+['\"]\s*;", clean))
    field_matches = re.findall(
        r"(?m)^\s*(?:(?:optional|required|repeated)\s+)?(?:map\s*<[^;{}]+>|[A-Za-z_][\w.]*?)\s+([A-Za-z_]\w*)\s*=\s*(\d+)\s*(?:\[[^\]]*\])?\s*;",
        clean,
    )
    numbers = [int(number) for _, number in field_matches]
    field_names = [name for name, _ in field_matches]
    invalid_numbers = sum(1 for number in numbers if number < 1 or number > 536_870_911 or 19_000 <= number <= 19_999)
    reserved_numbers = len(re.findall(r"\breserved\s+[^;]+;", clean))
    oneofs = len(re.findall(r"\boneof\s+[A-Za-z_]\w*\s*\{", clean))
    rpc = len(re.findall(r"\brpc\s+[A-Za-z_]\w*\s*\(", clean))
    syntax_label = syntax[0] if syntax else "not declared or invalid"
    balanced = clean.count("{") == clean.count("}") and clean.count("[") == clean.count("]")
    lines_out = [
        f"Syntax declaration: {syntax_label}",
        f"Package declarations: {package_count:,}",
        f"Message declarations: {len(messages):,}",
        f"Enum declarations: {len(enums):,}",
        f"Service declarations: {services:,}",
        f"RPC declarations: {rpc:,}",
        f"Field declarations recognized: {len(field_matches):,}",
        f"Duplicate field names (file-wide heuristic): {len(field_names) - len(set(field_names)):,}",
        f"Field numbers outside the legal range or in the implementation-reserved band: {invalid_numbers:,}",
        f"Reserved declarations: {reserved_numbers:,}",
        f"Oneof declarations: {oneofs:,}",
        f"Import declarations: {imports:,}",
        f"Balanced braces/brackets: {balanced}",
        "This is a conservative structural scan, not protoc compilation or full descriptor validation; field names and imports are withheld.",
    ]
    return _report(path, "protobuf", "Protocol Buffers schema audit", lines_out)
