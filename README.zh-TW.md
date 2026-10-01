# todo-tui

專為 [Caelestia](https://github.com/caelestia-dots/caelestia) dotfiles 設計的終端待辦清單 TUI。

用以取代 Caelestia 內建笨重的 Todoist 整合。

[English README](README.md)

## 功能

- 輕量：純 Python + curses，無 GUI 依賴
- Caelestia 原生：整合 `special:todo` 工作區
- 雙語：英文與繁體中文（zh-TW）
- UTF-8 輸入：中日韓文字原生支援
- 寬容日期解析：`2026-10-05`、`05/10`、`3 days`、`tmr`、`tomorrow`
- 兩種任務類型：截止型、時間點型
- 短備註 + 詳細內容
- 模糊搜尋（`;/`）
- `;` 命令模式，避免誤觸

## 前置需求

- 已安裝 Caelestia
- Hyprland 視窗管理員
- `foot` 終端機（或修改 `cli.json` 使用其他終端機）

## 安裝

### 快速安裝

    git clone git@github.com:Carz278/todo-tui.git
    cd todo-tui
    ./install.sh

接著依照輸出的說明，修改 `hypr-vars.lua` 和 `hypr-user.lua`。

### 手動安裝

1. 安裝系統依賴：

       sudo pacman -S python-dateutil python-parsedatetime

2. 複製並建立 venv：

       git clone git@github.com:Carz278/todo-tui.git
       cd todo-tui
       python3 -m venv .venv
       source .venv/bin/activate
       pip install -r requirements.txt
       deactivate

3. 複製設定檔：

       cp todo-settings.json ~/.config/caelestia/todo-settings.json

4. 停用 Caelestia 內建的 todo 快捷鍵。編輯 `~/.config/caelestia/hypr-vars.lua`：

       return {
         kbTodoWs = "",
       }

5. 綁定自己的快捷鍵。編輯 `~/.config/caelestia/hypr-user.lua`：

       hl.bind("SUPER + R", hl.dsp.exec_cmd("/path/to/todo-tui/toggle-todo.sh"))

6. 設定 Caelestia。編輯 `~/.config/caelestia/cli.json`：

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

7. 登出後重新登入。

## 使用方式

主頁面：

- `上/下` 或 `w/s`：移動游標
- `Home` / `End`：跳到第一項 / 最後一項
- `空格`：切換完成狀態
- `回車`：進入詳情頁
- `;a`：新增任務
- `;d`：刪除任務
- `;q`：離開
- `;/`：搜尋（用上下鍵切換匹配）

詳情頁：

- `Tab`：切換欄位（任務名 → 短備註 → 詳細內容）
- `回車`：在詳細內容中換行
- `;s`：儲存
- `;b`：返回（若有未儲存變更會詢問）
- `;/`：搜尋

## 設定

編輯 `~/.config/caelestia/todo-settings.json`：

    {
      "language": "zh-TW",
      "date_format": "DD/MM/YYYY",
      "max_name": 40,
      "max_short_comment": 50,
      "max_content": 500
    }

選項：

- `language`：`en` 或 `zh-TW`
- `date_format`：`DD/MM/YYYY`、`YYYY-MM-DD`、`MM/DD/YYYY`、`DD-MM-YYYY`
- `max_*`：各欄位字數上限

## 與 Todoist 的衝突

若你先前執行過 `caelestia install`，系統裡可能還裝著 Todoist。
這會導致 `Super + R` 同時打開 Todoist 和 todo-tui。

請移除 Todoist：

    sudo pacman -Rns todoist

並確認 `~/.config/caelestia/hypr-vars.lua` 裡的 `kbTodoWs` 是空的。

## 致謝

介面與操作邏輯部分受到 Doom Emacs 啟發。

## 授權

MIT
