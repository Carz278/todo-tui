#!/usr/bin/env python3
"""工具函数：日期解析、宽度计算、模糊匹配、配置加载。"""
import os
import json
import re
import unicodedata
from datetime import date, timedelta

try:
    import parsedatetime
    HAS_PARSEDATETIME = True
except ImportError:
    HAS_PARSEDATETIME = False

try:
    from dateutil import parser as dateutil_parser
    HAS_DATEUTIL = True
except ImportError:
    HAS_DATEUTIL = False

DATA_FILE = os.path.expanduser("~/.local/share/todo/todo.json")
SETTINGS_FILE = os.path.expanduser("~/.config/caelestia/todo-settings.json")

MAX_TASKS = 500
MAX_JSON_SIZE = 1 * 1024 * 1024

DEFAULT_SETTINGS = {
    "language": "zh-TW",
    "date_format": "DD/MM/YYYY",
    "max_name": 40,
    "max_short_comment": 50,
    "max_content": 500
}


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            user = json.load(f)
        s = DEFAULT_SETTINGS.copy()
        s.update(user)
        return s
    except (json.JSONDecodeError, FileNotFoundError):
        return DEFAULT_SETTINGS.copy()


def load_i18n(lang):
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "i18n", f"{lang}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def str_width(s):
    w = 0
    for ch in s:
        w += 2 if unicodedata.east_asian_width(ch) in ('F', 'W') else 1
    return w


def parse_date(input_str, default_today=True):
    s = input_str.strip().lower()
    if not s:
        return date.today().isoformat() if default_today else ""
    today = date.today()
    relative = {
        "today": 0, "tod": 0,
        "tomorrow": 1, "tmr": 1, "tmrw": 1, "tom": 1,
        "yesterday": -1, "yest": -1, "yes": -1,
    }
    if s in relative:
        return (today + timedelta(days=relative[s])).isoformat()
    m = re.match(r'^(\d+)\s*(d|day|days|w|week|weeks|m|month|months)$', s)
    if m:
        num, unit = int(m.group(1)), m.group(2)
        if unit.startswith('d'):
            return (today + timedelta(days=num)).isoformat()
        if unit.startswith('w'):
            return (today + timedelta(weeks=num)).isoformat()
        if unit.startswith('m'):
            return (today + timedelta(days=num * 30)).isoformat()
    if HAS_PARSEDATETIME:
        cal = parsedatetime.Calendar()
        time_struct, status = cal.parse(s)
        if status > 0:
            return date(*time_struct[:3]).isoformat()
    if HAS_DATEUTIL:
        try:
            dt = dateutil_parser.parse(s, dayfirst=True, default=today.replace(day=1))
            return dt.date().isoformat()
        except (ValueError, OverflowError):
            pass
    if re.match(r'^\d{1,2}$', s):
        try:
            return today.replace(day=int(s)).isoformat()
        except ValueError:
            pass
    m = re.match(r'^(\d{1,2})/(\d{1,2})$', s)
    if m:
        try:
            return date(today.year, int(m.group(2)), int(m.group(1))).isoformat()
        except ValueError:
            pass
    return ""


def format_date(iso_str, fmt="DD/MM/YYYY"):
    if not iso_str:
        return ""
    try:
        d = date.fromisoformat(iso_str)
    except (ValueError, TypeError):
        return iso_str
    mapping = {
        "DD/MM/YYYY": "%d/%m/%Y",
        "YYYY-MM-DD": "%Y-%m-%d",
        "MM/DD/YYYY": "%m/%d/%Y",
        "DD-MM-YYYY": "%d-%m-%Y",
    }
    return d.strftime(mapping.get(fmt, "%d/%m/%Y"))


def days_left(deadline_str):
    if not deadline_str:
        return None
    try:
        return (date.fromisoformat(deadline_str) - date.today()).days
    except (ValueError, TypeError):
        return None


def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_tasks(tasks):
    if len(tasks) > MAX_TASKS:
        return (False, f"Too many tasks (max {MAX_TASKS}).")
    data = json.dumps(tasks, ensure_ascii=False, indent=2)
    if len(data.encode("utf-8")) > MAX_JSON_SIZE:
        return (False, f"Data exceeds {MAX_JSON_SIZE // 1024} KB.")
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(data)
    return (True, "")


def fuzzy_match(query, text):
    if not query:
        return False
    q, t = query.lower(), text.lower()
    i = 0
    for ch in t:
        if i < len(q) and ch == q[i]:
            i += 1
    return i == len(q)
