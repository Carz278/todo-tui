#!/bin/bash

# 匹配 venv 里的 python3 进程（精确匹配，不会误杀 codium）
if pgrep -f "todo-tui/.venv/bin/python3" > /dev/null; then
    pkill -f "todo-tui/.venv/bin/python3"
else
    caelestia toggle todo
fi