# todo-tui

A terminal todo list TUI designed for [Caelestia](https://github.com/caelestia-dots/caelestia) dotfiles.

It replaces the heavy Todoist integration in Caelestia with a lightweight alternative.

[繁體中文說明](README.zh-TW.md)

## Features

- Lightweight: pure Python + curses, no GUI toolkit
- Caelestia native: integrates with the `special:todo` workspace
- Bilingual: English and Traditional Chinese (zh-TW)
- UTF-8 input: Chinese, Japanese, Korean work natively
- Flexible dates: `2026-10-05`, `05/10`, `3 days`, `tmr`, `tomorrow`
- Two task types: deadline-based or point-event
- Short comment + detailed content
- Fuzzy search with `;/`
- `;` command mode to prevent accidental actions

## Prerequisites

- Caelestia installed
- Hyprland as window manager
- `foot` terminal (or modify `cli.json` to use another)

## Installation

### Quick install

    git clone git@github.com:Carz278/todo-tui.git
    cd todo-tui
    ./install.sh

Then follow the printed instructions to update `hypr-vars.lua` and `hypr-user.lua`.

### Manual install

1. Install system dependencies:

       sudo pacman -S python-dateutil python-parsedatetime

2. Clone and create venv:

       git clone git@github.com:Carz278/todo-tui.git
       cd todo-tui
       python3 -m venv .venv
       source .venv/bin/activate
       pip install -r requirements.txt
       deactivate

3. Copy settings:

       cp todo-settings.json ~/.config/caelestia/todo-settings.json

4. Disable Caelestia's built-in todo keybind. Edit `~/.config/caelestia/hypr-vars.lua`:

       return {
         kbTodoWs = "",
       }

5. Bind your own key. Edit `~/.config/caelestia/hypr-user.lua`:

       hl.bind("SUPER + R", hl.dsp.exec_cmd("/path/to/todo-tui/toggle-todo.sh"))

6. Configure Caelestia. Edit `~/.config/caelestia/cli.json`:

       {
         "toggles": {
           "todo": {
             "todo-tui": {
               "enable": true,
               "match": [{"class": "todo-tui"}],
               "command": [
                 "foot", "-a", "todo-tui", "-T", "Todo List",
                 "-e", "/path/to/todo-tui/.venv/bin/python3",
                 "/path/to/todo-tui/todo.py"
               ],
               "move": true
             }
           }
         }
       }

7. Log out and log back in.

## Usage

Main page:

- `Up/Down` or `w/s`: move cursor
- `Home` / `End`: jump to first / last
- `Space`: toggle done
- `Enter`: open detail page
- `;a`: add task
- `;d`: delete task
- `;q`: quit
- `;/`: search (use Up/Down to navigate)

Detail page:

- `Tab`: switch fields (name -> short comment -> content)
- `Enter`: newline in content
- `;s`: save
- `;b`: back (asks to save if unsaved)
- `;/`: search

## Configuration

Edit `~/.config/caelestia/todo-settings.json`:

    {
      "language": "en",
      "date_format": "DD/MM/YYYY",
      "max_name": 40,
      "max_short_comment": 50,
      "max_content": 500
    }

Options:

- `language`: `en` or `zh-TW`
- `date_format`: `DD/MM/YYYY`, `YYYY-MM-DD`, `MM/DD/YYYY`, `DD-MM-YYYY`
- `max_*`: character limits

## Conflict with Todoist

If you have previously run `caelestia install`, Todoist might still be installed.
This can cause `Super + R` to open both Todoist and todo-tui.

To fix, remove Todoist:

    sudo pacman -Rns todoist

And make sure `kbTodoWs` is empty in `~/.config/caelestia/hypr-vars.lua`.

## Credits

UI and interaction inspired in part by Doom Emacs.

## License

MIT
