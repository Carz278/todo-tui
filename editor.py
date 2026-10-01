#!/usr/bin/env python3
"""多行文本编辑器，用于详情页的详细内容。"""


class MultiLineEditor:
    def __init__(self, text=""):
        self.lines = text.split("\n") if text else [""]
        self.row = 0
        self.col = 0

    def get_text(self):
        return "\n".join(self.lines)

    def insert_char(self, ch, max_len):
        if len(self.get_text()) >= max_len:
            return
        line = self.lines[self.row]
        self.lines[self.row] = line[:self.col] + ch + line[self.col:]
        self.col += 1

    def insert_newline(self, max_len):
        if len(self.get_text()) >= max_len:
            return
        line = self.lines[self.row]
        self.lines[self.row] = line[:self.col]
        self.lines.insert(self.row + 1, line[self.col:])
        self.row += 1
        self.col = 0

    def backspace(self):
        if self.col > 0:
            line = self.lines[self.row]
            self.lines[self.row] = line[:self.col - 1] + line[self.col:]
            self.col -= 1
        elif self.row > 0:
            prev = self.lines[self.row - 1]
            self.col = len(prev)
            self.lines[self.row - 1] = prev + self.lines[self.row]
            self.lines.pop(self.row)
            self.row -= 1

    def move_up(self):
        if self.row > 0:
            self.row -= 1
            self.col = min(self.col, len(self.lines[self.row]))

    def move_down(self):
        if self.row < len(self.lines) - 1:
            self.row += 1
            self.col = min(self.col, len(self.lines[self.row]))

    def move_left(self):
        if self.col > 0:
            self.col -= 1
        elif self.row > 0:
            self.row -= 1
            self.col = len(self.lines[self.row])

    def move_right(self):
        if self.col < len(self.lines[self.row]):
            self.col += 1
        elif self.row < len(self.lines) - 1:
            self.row += 1
            self.col = 0

    def find_all(self, query):
        results = []
        if not query:
            return results
        for r, line in enumerate(self.lines):
            start = 0
            while True:
                idx = line.find(query, start)
                if idx == -1:
                    break
                results.append((r, idx))
                start = idx + 1
        return results
