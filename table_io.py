import csv
import re
import zipfile
import xml.etree.ElementTree as ET


NUMERIC_KEYS = {
    "source_width",
    "source_height",
    "target_width",
    "target_height",
    "text_x",
    "text_y",
    "font_size",
    "text_width",
    "text_rotation",
}

TEXT_KEYS = {"text", "font"}
OPENING_KEYS = {
    "door_opening",
    "source_opening",
    "target_opening",
    "source_door_opening",
    "target_door_opening",
}
BLOCK_LIST_KEYS = {"keep_blocks", "delete_blocks"}
MODEL_TEXT_KEYS = {"model", "model_name", "door_model", "model_folder", "folder_path"}
MODEL_NUMERIC_KEYS = {"model_id", "door_model_id"}
JOB_TEXT_KEYS = {"order_number", "article", "door_type"}


def normalize_key(value):
    text = str(value).strip().lower()
    compact = re.sub(r"\s+", " ", text)
    if "номер замовлення" in compact or "номер заказа" in compact:
        return "order_number"
    if "висота двер" in compact or "высота двер" in compact:
        return "target_height"
    if "ширина двер" in compact:
        return "target_width"
    if "артикул" in compact and "doorcad" in compact:
        return "model"
    if "хар.род" in compact and "двер" in compact:
        return "door_type"
    replacements = {
        "ширина": "target_width",
        "width": "target_width",
        "w": "target_width",
        "нова ширина": "target_width",
        "target_width": "target_width",
        "висота": "target_height",
        "height": "target_height",
        "h": "target_height",
        "нова висота": "target_height",
        "target_height": "target_height",
        "поточна ширина": "source_width",
        "source_width": "source_width",
        "current_width": "source_width",
        "початкова ширина": "source_width",
        "поточна висота": "source_height",
        "source_height": "source_height",
        "current_height": "source_height",
        "початкова висота": "source_height",
        "лишити": "keep_blocks",
        "keep": "keep_blocks",
        "keep_blocks": "keep_blocks",
        "видалити": "delete_blocks",
        "delete": "delete_blocks",
        "delete_blocks": "delete_blocks",
        "текст": "text",
        "text": "text",
        "door_text": "text",
        "текст x": "text_x",
        "text_x": "text_x",
        "x_text": "text_x",
        "текст y": "text_y",
        "text_y": "text_y",
        "y_text": "text_y",
        "розмір шрифту": "font_size",
        "висота тексту": "font_size",
        "font_size": "font_size",
        "text_height": "font_size",
        "шрифт": "font",
        "font": "font",
        "ширина тексту": "text_width",
        "text_width": "text_width",
        "width_factor": "text_width",
        "поворот тексту": "text_rotation",
        "text_rotation": "text_rotation",
        "rotation": "text_rotation",
        "відкривання": "door_opening",
        "початкове відкривання": "source_door_opening",
        "стартове відкривання": "source_door_opening",
        "цільове відкривання": "target_door_opening",
        "нове відкривання": "target_door_opening",
        "модель": "model",
        "назва моделі": "model",
        "model": "model",
        "model_name": "model_name",
        "door_model": "door_model",
        "id моделі": "model_id",
        "model_id": "model_id",
        "door_model_id": "door_model_id",
        "папка моделі": "model_folder",
        "model_folder": "model_folder",
        "folder_path": "folder_path",
    }
    return replacements.get(text, text)


def parse_door_opening_value(value):
    text = str(value or "").strip().lower()
    if not text:
        return None
    if text in ("right", "r", "prave") or "прав" in text or "right" in text:
        return "right"
    if text in ("left", "l", "live") or "лів" in text or "лев" in text or "left" in text:
        return "left"
    return None


def split_block_names(value):
    if value is None:
        return []
    return [part.strip() for part in re.split(r"[,;\n]+", str(value)) if part.strip()]


def read_csv_rows(path):
    for encoding in ("utf-8-sig", "cp1251", "utf-8"):
        try:
            with open(path, newline="", encoding=encoding) as f:
                return [row for row in csv.reader(f) if any(str(c).strip() for c in row)]
        except UnicodeDecodeError:
            continue
    return []


def read_xlsx_rows(path):
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

    def column_index(cell_ref):
        letters = re.match(r"[A-Za-z]+", str(cell_ref or ""))
        if not letters:
            return None
        result = 0
        for char in letters.group(0).upper():
            result = result * 26 + (ord(char) - ord("A") + 1)
        return result - 1

    with zipfile.ZipFile(path) as zf:
        shared = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in root.findall("a:si", ns):
                shared.append("".join(t.text or "" for t in si.findall(".//a:t", ns)))
        sheet_name = "xl/worksheets/sheet1.xml"
        root = ET.fromstring(zf.read(sheet_name))
        rows = []
        for row in root.findall(".//a:row", ns):
            values = []
            for cell in row.findall("a:c", ns):
                idx = column_index(cell.attrib.get("r"))
                if idx is not None:
                    while len(values) < idx:
                        values.append("")
                raw = cell.find("a:v", ns)
                text = raw.text if raw is not None else ""
                if cell.attrib.get("t") == "s" and text:
                    text = shared[int(text)]
                elif cell.attrib.get("t") == "inlineStr":
                    text = "".join(node.text or "" for node in cell.findall(".//a:t", ns))
                if idx is None or idx == len(values):
                    values.append(text)
                elif idx < len(values):
                    values[idx] = text
            if any(str(v).strip() for v in values):
                rows.append(values)
        return rows


def add_value(params, key, value, parse_numeric_text):
    if key in NUMERIC_KEYS:
        num = parse_numeric_text(value)
        if num is not None:
            params[key] = num
    elif key in MODEL_NUMERIC_KEYS:
        num = parse_numeric_text(value)
        if num is not None:
            params[key] = int(num)
    elif key in MODEL_TEXT_KEYS:
        text_value = str(value).strip()
        if text_value:
            params[key] = text_value
    elif key in JOB_TEXT_KEYS:
        text_value = str(value).strip()
        if text_value:
            params[key] = text_value
    elif key in TEXT_KEYS:
        params[key] = str(value).strip()
    elif key in OPENING_KEYS:
        opening = parse_door_opening_value(value)
        if opening:
            params[key] = opening
    elif key in BLOCK_LIST_KEYS:
        params.setdefault(key, []).extend(split_block_names(value))


def extract_table_parameters(rows, parse_numeric_text):
    params = {}
    if not rows:
        return params

    headers = [normalize_key(c) for c in rows[0]]
    if "target_width" in headers or "target_height" in headers:
        for row in rows[1:]:
            for idx, key in enumerate(headers):
                if idx < len(row):
                    add_value(params, key, row[idx], parse_numeric_text)
        return params

    for row in rows:
        if len(row) >= 2:
            add_value(params, normalize_key(row[0]), row[1], parse_numeric_text)
    return params


def extract_batch_jobs(rows, parse_numeric_text):
    if not rows:
        return []
    headers = [normalize_key(c) for c in rows[0]]
    jobs = []
    for row in rows[1:]:
        params = {}
        for idx, key in enumerate(headers):
            if idx < len(row):
                add_value(params, key, row[idx], parse_numeric_text)
        if params:
            jobs.append(params)
    if not jobs:
        single = extract_table_parameters(rows, parse_numeric_text)
        if single:
            jobs.append(single)
    return jobs
