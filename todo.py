#!/usr/bin/env python3
"""todo-tui main entry: load config, i18n, tasks, run main loop."""
import curses
from utils import (load_settings, load_i18n, load_tasks, save_tasks,
                   fuzzy_match)
from ui import draw_main, draw_detail, add_task, tr


def sort_tasks(tasks, mode):
    """Return a sorted copy of tasks according to mode.

    mode: 0 = default (as stored), 1 = by deadline, 2 = by priority
    """
    if mode == 0:
        return tasks

    if mode == 1:
        # by deadline ascending; tasks without deadline go last
        def key(t):
            d = t.get("deadline", "") or t.get("event_date", "")
            return (d == "", d)
        return sorted(tasks, key=key)

    if mode == 2:
        # by priority descending (3 -> 0)
        return sorted(tasks, key=lambda t: -t.get("priority", 0))

    return tasks


def main(stdscr):
    settings = load_settings()
    i18n = load_i18n(settings.get("language", "en"))
    tasks = load_tasks()

    curses.curs_set(0)
    stdscr.keypad(True)

    selected = 0
    view_offset = 0
    command_mode = False
    search_mode = False
    search_query = ""
    search_matches = []
    search_index = -1
    sort_mode = 0  # 0=default, 1=deadline, 2=priority

    while True:
        # Sort a working copy for display
        display_tasks = sort_tasks(tasks, sort_mode)

        h, w = stdscr.getmaxyx()
        list_start_y = 3
        available_rows = h - list_start_y - 1

        if selected < view_offset:
            view_offset = selected
        elif selected >= view_offset + available_rows:
            view_offset = selected - available_rows + 1
        if view_offset < 0:
            view_offset = 0
        if view_offset > max(0, len(display_tasks) - available_rows):
            view_offset = max(0, len(display_tasks) - available_rows)

        draw_main(stdscr, display_tasks, selected, view_offset, settings,
                  i18n, command_mode, search_mode, search_query, sort_mode)
        key = stdscr.getch()

        # ============ Search mode ============
        if search_mode:
            if key == curses.KEY_ENTER or key in (10, 13):
                search_mode = False
                search_query = ""
                continue
            if key == curses.KEY_DOWN and search_matches:
                search_index = (search_index + 1) % len(search_matches)
                selected = search_matches[search_index]
                continue
            if key == curses.KEY_UP and search_matches:
                search_index = (search_index - 1) % len(search_matches)
                selected = search_matches[search_index]
                continue
            if key == 27:
                search_mode = False
                search_query = ""
                search_matches = []
                search_index = -1
                continue
            if key in (curses.KEY_BACKSPACE, 127, 8):
                search_query = search_query[:-1]
            elif 32 <= key <= 126:
                search_query += chr(key)
            else:
                from ui import get_utf8_char
                ch = get_utf8_char(stdscr)
                if ch:
                    search_query += ch
            if search_query:
                search_matches = []
                for i, task in enumerate(display_tasks):
                    if fuzzy_match(search_query, task["name"]) or \
                       fuzzy_match(search_query, task.get("short_comment", "")):
                        search_matches.append(i)
                if search_matches:
                    search_index = 0
                    selected = search_matches[0]
            continue

        # ============ Command mode ============
        if command_mode:
            command_mode = False
            if key == ord('a'):
                h, w = stdscr.getmaxyx()
                stdscr.move(h - 1, 0)
                stdscr.clrtoeol()
                stdscr.addstr(h - 1, 0, tr(i18n, "confirm_add"))
                stdscr.refresh()
                if stdscr.getch() in (ord('y'), ord('Y'), 10, 13):
                    new_task = add_task(stdscr, settings, i18n)
                    if new_task:
                        tasks.append(new_task)
                        ok, msg = save_tasks(tasks)
                        if not ok:
                            tasks.pop()
                            stdscr.move(h - 1, 0)
                            stdscr.clrtoeol()
                            stdscr.addstr(h - 1, 0, f"Error: {msg}")
                            stdscr.refresh()
                            curses.napms(1500)
            elif key == ord('d'):
                if display_tasks:
                    h, w = stdscr.getmaxyx()
                    stdscr.move(h - 1, 0)
                    stdscr.clrtoeol()
                    stdscr.addstr(h - 1, 0, tr(i18n, "confirm_delete"))
                    stdscr.refresh()
                    if stdscr.getch() in (ord('y'), ord('Y'), 10, 13):
                        target = display_tasks[selected]
                        tasks.remove(target)
                        if selected >= len(display_tasks) - 1 and selected > 0:
                            selected -= 1
                        save_tasks(tasks)
            elif key == ord('q'):
                h, w = stdscr.getmaxyx()
                stdscr.move(h - 1, 0)
                stdscr.clrtoeol()
                stdscr.addstr(h - 1, 0, tr(i18n, "confirm_quit"))
                stdscr.refresh()
                if stdscr.getch() in (ord('y'), ord('Y'), 10, 13):
                    break
            elif key == ord('/'):
                search_mode = True
                search_query = ""
                search_matches = []
                search_index = -1
            elif key == ord('s'):
                sort_mode = (sort_mode + 1) % 3
            elif key == ord('p'):
                if display_tasks:
                    target = display_tasks[selected]
                    cur = target.get("priority", 0)
                    target["priority"] = (cur + 1) % 4
                    save_tasks(tasks)
            continue

        # ============ Normal mode ============
        if key == ord(';'):
            command_mode = True
            continue

        if key == curses.KEY_HOME:
            selected = 0
        elif key == curses.KEY_END:
            if display_tasks:
                selected = len(display_tasks) - 1
        elif key in (curses.KEY_UP, ord('w')):
            if display_tasks:
                selected = len(display_tasks) - 1 if selected == 0 else selected - 1
        elif key in (curses.KEY_DOWN, ord('s')):
            if display_tasks:
                selected = 0 if selected == len(display_tasks) - 1 else selected + 1
        elif key == ord(' '):
            if display_tasks:
                target = display_tasks[selected]
                target["done"] = not target["done"]
                save_tasks(tasks)
        elif key == curses.KEY_ENTER or key in (10, 13):
            if display_tasks:
                target = display_tasks[selected]
                result = draw_detail(stdscr, target, settings, i18n)
                if result:
                    save_tasks(tasks)


if __name__ == "__main__":
    curses.wrapper(main)
