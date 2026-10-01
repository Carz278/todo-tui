#!/usr/bin/env python3
"""UI 绘制：主界面、详情页、添加页，以及 UTF-8 输入辅助。"""
import curses
from utils import (str_width, format_date, days_left, parse_date,
                   fuzzy_match)
from editor import MultiLineEditor


def get_utf8_char(stdscr):
    """读取一个完整的 UTF-8 字符（curses.getch 只给单字节）。"""
    key = stdscr.getch()
    if key < 0:
        return None
    if key < 128:
        return chr(key)
    byte = key
    if (byte & 0xE0) == 0xC0:
        need = 1
    elif (byte & 0xF0) == 0xE0:
        need = 2
    elif (byte & 0xF8) == 0xF0:
        need = 3
    else:
        return None
    buf = bytes([byte])
    for _ in range(need):
        nxt = stdscr.getch()
        if nxt < 0:
            return None
        buf += bytes([nxt])
    try:
        return buf.decode("utf-8")
    except UnicodeDecodeError:
        return None


def tr(i18n, key, **kwargs):
    """安全地从 i18n 字典取字符串并替换占位符。"""
    text = i18n.get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text


def draw_main(stdscr, tasks, selected, view_offset, settings, i18n,
              command_mode=False, search_mode=False, search_query="",
              sort_mode=0):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(0, 0, tr(i18n, "title"))
    stdscr.addstr(1, 0, tr(i18n, "help_main"))

    list_start_y = 3
    available_rows = h - list_start_y - 1
    start_index = view_offset
    end_index = min(len(tasks), view_offset + available_rows)

    for i in range(start_index, end_index):
        task = tasks[i]
        screen_y = list_start_y + (i - view_offset)
        if i == selected:
            stdscr.attron(curses.A_REVERSE)
        mark = "[*]" if task["done"] else "[ ]"

        # Priority marker
        prio = task.get("priority", 0)
        prio_str = " " * 3
        if prio == 1:
            prio_str = "*  "
        elif prio == 2:
            prio_str = "** "
        elif prio == 3:
            prio_str = "***"

        task_type = task.get("task_type", "deadline")
        if task_type == "point":
            left = days_left(task.get("event_date", ""))
            if left is None:
                dstr = ""
            elif left < 0:
                dstr = tr(i18n, "point_days_past", n=-left)
            elif left == 0:
                dstr = tr(i18n, "point_today")
            else:
                dstr = tr(i18n, "point_days_after", n=left)
        else:
            left = days_left(task.get("deadline", ""))
            if left is None:
                dstr = ""
            elif left < 0:
                dstr = tr(i18n, "days_overdue", n=-left)
            elif left == 0:
                dstr = tr(i18n, "days_today")
            else:
                dstr = tr(i18n, "days_left", n=left)

        short = task.get("short_comment", "")
        short_disp = ""
        if short:
            first = short.split("\n")[0]
            if len(first) > 20:
                first = first[:20] + "..."
            short_disp = f" ({first})"

        line = f"{mark} {prio_str} {task['name']}{short_disp}{dstr}"
        stdscr.addstr(screen_y, 0, line[:w - 1])
        if i == selected:
            stdscr.attroff(curses.A_REVERSE)

    # Bottom status
    if search_mode:
        stdscr.addstr(h - 1, 0, tr(i18n, "search_prompt") + search_query)
    elif command_mode:
        stdscr.addstr(h - 1, 0, ": ")
    else:
        sort_name = {0: "default", 1: "deadline", 2: "priority"}[sort_mode]
        stdscr.addstr(h - 1, 0,
                      tr(i18n, "task_count", n=len(tasks)) +
                      f"  |  sort: {sort_name}")
    stdscr.refresh()



def draw_detail(stdscr, task, settings, i18n):
    curses.curs_set(1)
    edit_field = 2  # 0=name, 2=short, 3=content

    name = task["name"]
    name_col = len(name)

    task_type = task.get("task_type", "deadline")
    if task_type == "point":
        date_str = task.get("event_date", "")
    else:
        date_str = task.get("deadline", "")
    date_col = len(date_str)

    short_comment = task.get("short_comment", "")
    short_col = len(short_comment)
    content_editor = MultiLineEditor(task.get("content", ""))

    saved = {
        "name": name, "date_str": date_str,
        "short": short_comment, "content": content_editor.get_text()
    }
    search_matches = []
    search_index = -1

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, tr(i18n, "detail_title"))
        stdscr.addstr(1, 0, tr(i18n, "detail_help"))

        stdscr.addstr(3, 0, tr(i18n, "name_label",
                               cur=len(name), max=settings['max_name']))
        if edit_field == 0:
            stdscr.attron(curses.A_REVERSE)
        stdscr.addstr(4, 0, name)
        if edit_field == 0:
            stdscr.attroff(curses.A_REVERSE)

        if task_type == "point":
            stdscr.addstr(6, 0, tr(i18n, "date_event"))
            stdscr.addstr(7, 0, format_date(task.get("event_date", ""),
                                            settings['date_format']))
            short_y, short_content_y, content_start_y = 9, 10, 12
        else:
            stdscr.addstr(6, 0, tr(i18n, "date_start"))
            stdscr.addstr(7, 0, format_date(task.get("start_date", ""),
                                            settings['date_format']))
            stdscr.addstr(8, 0, tr(i18n, "date_deadline"))
            stdscr.addstr(9, 0, format_date(task.get("deadline", ""),
                                            settings['date_format']))
            short_y, short_content_y, content_start_y = 11, 12, 14

        stdscr.addstr(short_y, 0,
                      tr(i18n, "short_label",
                         cur=len(short_comment),
                         max=settings['max_short_comment']))
        if edit_field == 2:
            stdscr.attron(curses.A_REVERSE)
        stdscr.addstr(short_content_y, 0, short_comment)
        if edit_field == 2:
            stdscr.attroff(curses.A_REVERSE)

        content_text = content_editor.get_text()
        stdscr.addstr(content_start_y, 0,
                      tr(i18n, "content_label",
                         cur=len(content_text),
                         max=settings['max_content']))
        if edit_field == 3:
            stdscr.attron(curses.A_REVERSE)
        h, w = stdscr.getmaxyx()
        max_rows = h - (content_start_y + 1) - 2
        start_row = max(0, content_editor.row - max_rows + 1)
        end_row = min(len(content_editor.lines), start_row + max_rows)
        for i in range(start_row, end_row):
            stdscr.addstr(content_start_y + 1 + (i - start_row), 0,
                          content_editor.lines[i][:w - 1])
        if edit_field == 3:
            stdscr.attroff(curses.A_REVERSE)

        if edit_field == 0:
            stdscr.move(4, min(str_width(name[:name_col]), 78))
        elif edit_field == 2:
            stdscr.move(short_content_y,
                        min(str_width(short_comment[:short_col]), 78))
        else:
            screen_row = content_start_y + 1 + (content_editor.row - start_row)
            stdscr.move(screen_row,
                        min(str_width(content_editor.lines[content_editor.row][:content_editor.col]), 78))

        stdscr.refresh()
        key = stdscr.getch()

        if key == 9:
            edit_field = {0: 2, 2: 3, 3: 0}[edit_field]
            continue

        if key == curses.KEY_ENTER or key in (10, 13):
            if edit_field == 3:
                content_editor.insert_newline(settings['max_content'])
            continue

        if key == ord(';'):
            stdscr.move(22, 0)
            stdscr.clrtoeol()
            stdscr.addstr(22, 0, ": ")
            stdscr.refresh()
            cmd = stdscr.getch()
            if cmd == ord('s'):
                if task_type == "point":
                    task["event_date"] = date_str
                else:
                    task["deadline"] = date_str
                task["name"] = name[:settings['max_name']]
                task["short_comment"] = short_comment[:settings['max_short_comment']]
                task["content"] = content_editor.get_text()[:settings['max_content']]
                saved = {"name": name, "date_str": date_str,
                         "short": short_comment,
                         "content": content_editor.get_text()}
                stdscr.addstr(22, 0, tr(i18n, "saved"))
                stdscr.refresh()
                curses.napms(500)
            elif cmd == ord('b'):
                current = {"name": name, "date_str": date_str,
                           "short": short_comment,
                           "content": content_editor.get_text()}
                if current != saved:
                    h, w = stdscr.getmaxyx()
                    stdscr.move(h - 1, 0)
                    stdscr.clrtoeol()
                    stdscr.addstr(h - 1, 0, tr(i18n, "confirm_save"))
                    stdscr.refresh()
                    confirm = stdscr.getch()
                    if confirm in (ord('y'), ord('Y'), 10, 13):
                        if task_type == "point":
                            task["event_date"] = date_str
                        else:
                            task["deadline"] = date_str
                        task["name"] = name[:settings['max_name']]
                        task["short_comment"] = short_comment[:settings['max_short_comment']]
                        task["content"] = content_editor.get_text()[:settings['max_content']]
                        curses.curs_set(0)
                        return True
                curses.curs_set(0)
                return False
            elif cmd == ord('/'):
                query = ""
                while True:
                    h, w = stdscr.getmaxyx()
                    stdscr.move(h - 1, 0)
                    stdscr.clrtoeol()
                    stdscr.addstr(h - 1, 0, tr(i18n, "search_prompt") + query)
                    stdscr.refresh()
                    k2 = stdscr.getch()
                    if k2 == curses.KEY_ENTER or k2 in (10, 13):
                        break
                    if k2 == 27:
                        query = ""
                        break
                    if k2 in (curses.KEY_BACKSPACE, 127, 8):
                        query = query[:-1]
                    elif 32 <= k2 <= 126:
                        query += chr(k2)
                    else:
                        ch = get_utf8_char(stdscr)
                        if ch:
                            query += ch
                if query:
                    search_matches = []
                    if query.lower() in name.lower():
                        search_matches.append(("name", 0))
                    if query.lower() in date_str.lower():
                        search_matches.append(("date", 0))
                    if query.lower() in short_comment.lower():
                        start = 0
                        while True:
                            idx = short_comment.find(query, start)
                            if idx == -1:
                                break
                            search_matches.append(("short", idx))
                            start = idx + 1
                    for r, c in content_editor.find_all(query):
                        search_matches.append(("content", (r, c)))
                    if search_matches:
                        search_index = 0
                        t = search_matches[0]
                        if t[0] == "short":
                            edit_field, short_col = 2, t[1]
                        elif t[0] == "content":
                            edit_field = 3
                            content_editor.row, content_editor.col = t[1]
            continue

        if key == ord('n') and search_matches:
            search_index = (search_index + 1) % len(search_matches)
            t = search_matches[search_index]
            if t[0] == "short":
                edit_field, short_col = 2, t[1]
            elif t[0] == "content":
                edit_field = 3
                content_editor.row, content_editor.col = t[1]
            continue
        if key == ord('N') and search_matches:
            search_index = (search_index - 1) % len(search_matches)
            t = search_matches[search_index]
            if t[0] == "short":
                edit_field, short_col = 2, t[1]
            elif t[0] == "content":
                edit_field = 3
                content_editor.row, content_editor.col = t[1]
            continue

        if key == curses.KEY_UP:
            if edit_field == 3:
                content_editor.move_up()
            continue
        if key == curses.KEY_DOWN:
            if edit_field == 3:
                content_editor.move_down()
            continue
        if key == curses.KEY_LEFT:
            if edit_field == 0 and name_col > 0:
                name_col -= 1
            elif edit_field == 2 and short_col > 0:
                short_col -= 1
            elif edit_field == 3:
                content_editor.move_left()
            continue
        if key == curses.KEY_RIGHT:
            if edit_field == 0 and name_col < len(name):
                name_col += 1
            elif edit_field == 2 and short_col < len(short_comment):
                short_col += 1
            elif edit_field == 3:
                content_editor.move_right()
            continue

        if key in (curses.KEY_BACKSPACE, 127, 8):
            if edit_field == 0 and name_col > 0:
                name = name[:name_col - 1] + name[name_col:]
                name_col -= 1
            elif edit_field == 2 and short_col > 0:
                short_comment = short_comment[:short_col - 1] + short_comment[short_col:]
                short_col -= 1
            elif edit_field == 3:
                content_editor.backspace()
            continue

        ch = None
        if 32 <= key <= 126:
            ch = chr(key)
        else:
            ch = get_utf8_char(stdscr)
        if ch:
            if edit_field == 0 and len(name) < settings['max_name']:
                name = name[:name_col] + ch + name[name_col:]
                name_col += len(ch)
            elif edit_field == 2 and len(short_comment) < settings['max_short_comment']:
                short_comment = short_comment[:short_col] + ch + short_comment[short_col:]
                short_col += len(ch)
            elif edit_field == 3:
                content_editor.insert_char(ch, settings['max_content'])



def input_with_counter(stdscr, y, prompt, max_len, i18n, allow_empty=False):
    curses.curs_set(1)
    current = ""
    while True:
        stdscr.move(y, 0)
        stdscr.clrtoeol()
        stdscr.move(y + 1, 0)
        stdscr.clrtoeol()
        counter = f"[{len(current)}/{max_len}]"
        stdscr.addstr(y, 0, prompt + counter)
        stdscr.addstr(y + 1, 0, current)
        stdscr.move(y + 1, min(str_width(current), 78))
        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_ENTER or key in (10, 13):
            if allow_empty or len(current) > 0:
                curses.curs_set(0)
                return current
            continue
        if key == ord(';'):
            stdscr.addstr(y + 2, 0, ": ")
            stdscr.clrtoeol()
            stdscr.refresh()
            cmd = stdscr.getch()
            if cmd == ord('c'):
                h, w = stdscr.getmaxyx()
                stdscr.move(h - 1, 0)
                stdscr.clrtoeol()
                stdscr.addstr(h - 1, 0, tr(i18n, "confirm_cancel"))
                stdscr.refresh()
                confirm = stdscr.getch()
                if confirm in (ord('y'), ord('Y'), 10, 13):
                    curses.curs_set(0)
                    return None
            continue
        if key == 27:
            curses.curs_set(0)
            return None
        if key in (curses.KEY_BACKSPACE, 127, 8):
            if len(current) > 0:
                current = current[:-1]
            continue
        if 32 <= key <= 126:
            if len(current) < max_len:
                current += chr(key)
            continue
        ch = get_utf8_char(stdscr)
        if ch and len(current) < max_len:
            current += ch


def add_task(stdscr, settings, i18n):
    curses.curs_set(1)
    stdscr.clear()
    stdscr.addstr(0, 0, tr(i18n, "add_title"))
    stdscr.addstr(1, 0, tr(i18n, "add_help"))
    stdscr.addstr(3, 0, tr(i18n, "add_type"))
    stdscr.addstr(4, 0, tr(i18n, "add_type_1"))
    stdscr.addstr(5, 0, tr(i18n, "add_type_2"))
    stdscr.refresh()

    task_type = None
    while True:
        key = stdscr.getch()
        if key == ord('1'):
            task_type = "deadline"
            break
        if key == ord('2'):
            task_type = "point"
            break
        if key == ord(';'):
            cmd = stdscr.getch()
            if cmd == ord('c'):
                h, w = stdscr.getmaxyx()
                stdscr.move(h - 1, 0)
                stdscr.clrtoeol()
                stdscr.addstr(h - 1, 0, tr(i18n, "confirm_cancel"))
                stdscr.refresh()
                if stdscr.getch() in (ord('y'), ord('Y'), 10, 13):
                    curses.curs_set(0)
                    return None

    stdscr.clear()
    stdscr.addstr(0, 0, tr(i18n, "add_title"))
    stdscr.addstr(1, 0, tr(i18n, "add_help"))
    stdscr.refresh()

    name = input_with_counter(stdscr, 3, tr(i18n, "add_name"),
                              settings['max_name'], i18n, allow_empty=False)
    if name is None:
        curses.curs_set(0)
        return None

    start = ""
    deadline = ""
    event_date = ""

    if task_type == "deadline":
        start_raw = input_with_counter(stdscr, 6, tr(i18n, "add_start"),
                                       30, i18n, allow_empty=True)
        if start_raw is None:
            curses.curs_set(0)
            return None
        start = parse_date(start_raw, default_today=True)

        deadline_raw = input_with_counter(stdscr, 9, tr(i18n, "add_deadline"),
                                          30, i18n, allow_empty=True)
        if deadline_raw is None:
            curses.curs_set(0)
            return None
        deadline = parse_date(deadline_raw, default_today=False)
    else:
        event_raw = input_with_counter(stdscr, 6, tr(i18n, "add_event"),
                                       30, i18n, allow_empty=True)
        if event_raw is None:
            curses.curs_set(0)
            return None
        event_date = parse_date(event_raw, default_today=False)

    short_comment = input_with_counter(stdscr, 12, tr(i18n, "add_short"),
                                       settings['max_short_comment'], i18n,
                                       allow_empty=True)
    if short_comment is None:
        curses.curs_set(0)
        return None

    curses.curs_set(0)
    return {
        "name": name,
        "task_type": task_type,
        "start_date": start,
        "deadline": deadline,
        "event_date": event_date,
        "short_comment": short_comment,
        "content": "",
        "done": False
    }
