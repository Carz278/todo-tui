# todo-tui

> **A terminal todo list TUI designed specifically for [Caelestia](https://github.com/caelestia-dots/caelestia) dotfiles.**

`todo-tui` replaces the heavy Todoist integration in Caelestia with a lightweight, customizable alternative. It integrates directly with Caelestia's `special:todo` workspace, `cli.json` toggle mechanism, and `hypr-user.lua` keybind override.

## Features

- **Lightweight**: pure Python + curses
- **Caelestia friendly**: integrates with the `special:todo` workspace
- **Bilingual**: English and Traditional Chinese (zh-TW)
- **UTF-8 support**: Chinese input works natively
- **Flexible dates**: `2026-10-05`, `05/10`, `3 days`, `tmr`, `tomorrow`
- **Two task types**: deadline-based or point-event
- **Short comment + detailed content**
- **Search**: fuzzy matching with `;/`
- **`;` command mode** to prevent accidental actions

## Installation
### Quick install

    git clone https://github.com/Carz278/todo-tui.git
    cd todo-tui
    ./install.sh

Then follow the printed instructions to update `cli.json` and `hypr-user.lua`.


### 1. System dependencies

    sudo pacman -S python-dateutil python-parsedatetime

### 2. Clone this repository

    git clone https://github.com/YOUR_USERNAME/todo-tui.git
    cd todo-tui

### 3. Create a venv and install Python dependencies

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    deactivate

### 4. Copy settings template

    mkdir -p ~/.config/caelestia
    cp todo-settings.json ~/.config/caelestia/todo-settings.json

### 5. Configure Caelestia

Edit `~/.config/caelestia/cli.json`:

    {
      "toggles": {
        "todo": {
          "todo-tui": {
            "enable": true,
            "match": [{"class": "todo-tui"}],
            "command": [
              "foot", "-a", "todo-tui", "-T", "Todo List",
              "-e", "/home/YOUR_USER/Projects/todo-tui/.venv/bin/python3",
              "/home/YOUR_USER/Projects/todo-tui/todo.py"
            ],
            "move": true
          }
        }
      }
    }

Edit `~/.config/caelestia/hypr-user.lua`:

    hl.bind("SUPER + R", hl.dsp.exec_cmd("/home/YOUR_USER/Projects/todo-tui/toggle-todo.sh"))

### 6. Log out and log back in

## Usage

- `Super + R` — open/close
- `Up/Down` or `w/s` — move cursor
- `Space` — toggle done
- `Enter` — open detail page
- `;a` — add task
- `;d` — delete current task
- `;q` — quit
- `;/` — search (use Up/Down to navigate)

### Detail page

- `Tab` — switch fields (name -> short -> content)
- `Enter` — newline in content
- `;s` — save
- `;b` — back (asks to save if unsaved)
- `;/` — search

## Configuration

Edit `~/.config/caelestia/todo-settings.json`:

    {
      "language": "zh-TW",
      "date_format": "DD/MM/YYYY",
      "max_name": 40,
      "max_short_comment": 50,
      "max_content": 500
    }

- `language`: `en` or `zh-TW`
- `date_format`: `DD/MM/YYYY`, `YYYY-MM-DD`, `MM/DD/YYYY`, `DD-MM-YYYY`

## License

MIT

## ⚠️ Conflict with Caelestia's default Todoist

If you've already run `caelestia install`, your Caelestia setup may already include a Todoist integration that uses the same `Super+R` keybind and `special:todo` workspace.

To avoid conflicts, you must do **both** of these:

1. **Disable Caelestia's default keybind** in `~/.config/caelestia/hypr-vars.lua`:

       return {
         kbTodoWs = "",
       }

2. **Override the keybind** in `~/.config/caelestia/hypr-user.lua`:

       hl.bind("SUPER + R", hl.dsp.exec_cmd("/path/to/todo-tui/toggle-todo.sh"))

Without step 1, pressing `Super+R` will try to launch Todoist (which may not even exist) and your todo-tui simultaneously, causing windows to stack.
