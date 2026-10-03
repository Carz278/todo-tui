#!/bin/bash
# install.sh - Deploy todo-tui to a Caelestia environment
# Usage: ./install.sh [--zh|--en]

set -e

# ==================== Language argument ====================
LANG_CODE="en"
for arg in "$@"; do
    case "$arg" in
        --zh|--zh-TW|--chinese) LANG_CODE="zh" ;;
        --en|--english) LANG_CODE="en" ;;
        --help|-h)
            echo "Usage: $0 [--zh|--en]"
            echo "  --zh    Use Traditional Chinese output"
            echo "  --en    Use English output (default)"
            exit 0
            ;;
    esac
done

# ==================== Colors ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ==================== Messages ====================
if [ "$LANG_CODE" = "zh" ]; then
    MSG_CHECK_ENV="检查基本环境..."
    MSG_OK="OK"
    MSG_WARN="警告"
    MSG_FAIL="失败"
    MSG_PYTHON_MISSING="未找到 python3，请先安装 Python 3。"
    MSG_PYTHON_OK="python3 已安装"
    MSG_CHECK_DEPS="检查系统 Python 依赖..."
    MSG_DEPS_MISSING="缺少系统包："
    MSG_INSTALL_NOW="是否现在安装？[Y/n] "
    MSG_DEPS_OK="系统依赖已满足"
    MSG_SKIP_DEPS="跳过系统依赖安装。"
    MSG_DETECT_ARCH="检测到 Arch 系发行版，使用 pacman 安装系统依赖..."
    MSG_DETECT_DEBIAN="检测到 Debian 系发行版，使用 apt 安装系统依赖..."
    MSG_DETECT_FEDORA="检测到 Fedora 系发行版，使用 dnf 安装系统依赖..."
    MSG_DISTRO_UNKNOWN="未识别的发行版："
    MSG_MANUAL_DEPS="请手动安装 python-dateutil 和 parsedatetime。"
    MSG_PROJECT_DIR="项目目录："
    MSG_CREATE_VENV="创建 Python venv..."
    MSG_VENV_CREATED="venv 已创建"
    MSG_VENV_EXISTS="venv 已存在，跳过创建"
    MSG_INSTALL_PY_DEPS="安装 Python 依赖到 venv..."
    MSG_PY_DEPS_OK="Python 依赖安装完成"
    MSG_NO_REQUIREMENTS="未找到 requirements.txt"
    MSG_COPY_SETTINGS="复制设置文件到 ~/.config/caelestia/..."
    MSG_SETTINGS_EXISTS="todo-settings.json 已存在，保留现有配置。"
    MSG_SETTINGS_COPIED="todo-settings.json 已复制"
    MSG_CHECK_CAELESTIA="检查 Caelestia 配置..."
    MSG_CAELESTIA_MISSING="未找到 ~/.config/caelestia/，请先安装 Caelestia。"
    MSG_CAELESTIA_OK="Caelestia 配置目录存在"
    MSG_CONFLICT_TITLE="冲突检查"
    MSG_CONFLICT_TODOIST="检测到系统里仍安装着 Todoist。"
    MSG_CONFLICT_TODOIST_WHY="这可能导致 Super+R 同时打开 Todoist 和 todo-tui。"
    MSG_CONFLICT_TODOIST_FIX="卸载命令："
    MSG_CONFLICT_TODOIST_OK="系统里没有 Todoist"
    MSG_CONFLICT_RESOLVE="请先解决上面的冲突，否则 Super+R 可能行为异常。"
    MSG_DONE_TITLE="安装完成！还需要修改 cli.json"
    MSG_STEP1="编辑 ~/.config/caelestia/cli.json"
    MSG_STEP1_DESC="   如果文件不存在，创建它；如果存在，把下面内容合并进去："
    MSG_LAST_STEP="最后一步：注销并重新登录，让配置生效。"
else
    MSG_CHECK_ENV="Checking basic environment..."
    MSG_OK="OK"
    MSG_WARN="WARN"
    MSG_FAIL="FAIL"
    MSG_PYTHON_MISSING="python3 not found. Please install Python 3."
    MSG_PYTHON_OK="python3 is installed"
    MSG_CHECK_DEPS="Checking system Python dependencies..."
    MSG_DEPS_MISSING="Missing system packages: "
    MSG_INSTALL_NOW="Install them now? [Y/n] "
    MSG_DEPS_OK="System dependencies satisfied"
    MSG_SKIP_DEPS="Skipping system dependency installation."
    MSG_DETECT_ARCH="Detected Arch-based distro, using pacman..."
    MSG_DETECT_DEBIAN="Detected Debian-based distro, using apt..."
    MSG_DETECT_FEDORA="Detected Fedora-based distro, using dnf..."
    MSG_DISTRO_UNKNOWN="Unknown distro: "
    MSG_MANUAL_DEPS="Please install python-dateutil and parsedatetime manually."
    MSG_PROJECT_DIR="Project directory: "
    MSG_CREATE_VENV="Creating Python venv..."
    MSG_VENV_CREATED="venv created"
    MSG_VENV_EXISTS="venv already exists, skipping"
    MSG_INSTALL_PY_DEPS="Installing Python dependencies into venv..."
    MSG_PY_DEPS_OK="Python dependencies installed"
    MSG_NO_REQUIREMENTS="requirements.txt not found"
    MSG_COPY_SETTINGS="Copying settings to ~/.config/caelestia/..."
    MSG_SETTINGS_EXISTS="todo-settings.json already exists, keeping current config."
    MSG_SETTINGS_COPIED="todo-settings.json copied"
    MSG_CHECK_CAELESTIA="Checking Caelestia configuration..."
    MSG_CAELESTIA_MISSING="~/.config/caelestia/ not found. Please install Caelestia first."
    MSG_CAELESTIA_OK="Caelestia config directory exists"
    MSG_CONFLICT_TITLE="Conflict check"
    MSG_CONFLICT_TODOIST="Todoist is still installed on your system."
    MSG_CONFLICT_TODOIST_WHY="This may cause Super+R to open both Todoist and todo-tui."
    MSG_CONFLICT_TODOIST_FIX="To remove it:"
    MSG_CONFLICT_TODOIST_OK="No Todoist found on the system"
    MSG_CONFLICT_RESOLVE="Please resolve the conflict above before using Super+R."
    MSG_DONE_TITLE="Installation complete. cli.json still needs to be edited."
    MSG_STEP1="Edit ~/.config/caelestia/cli.json"
    MSG_STEP1_DESC="   If it doesn't exist, create it. If it does, merge the following:"
    MSG_LAST_STEP="Last step: log out and log back in to apply changes."
fi

# ==================== Helpers ====================
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()   { echo -e "${GREEN}[ $MSG_OK ]${NC} $1"; }
warn() { echo -e "${YELLOW}[$MSG_WARN]${NC} $1"; }
err()  { echo -e "${RED}[$MSG_FAIL]${NC} $1"; }

# ==================== Distro detection ====================
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    else
        echo "unknown"
    fi
}

install_system_deps() {
    local distro
    distro=$(detect_distro)
    case "$distro" in
        arch|manjaro|endeavouros)
            info "$MSG_DETECT_ARCH"
            sudo pacman -S --needed python-dateutil python-parsedatetime
            ;;
        debian|ubuntu|linuxmint|pop)
            info "$MSG_DETECT_DEBIAN"
            sudo apt update
            sudo apt install -y python3-dateutil python3-parsedatetime
            ;;
        fedora|rhel|centos)
            info "$MSG_DETECT_FEDORA"
            sudo dnf install -y python3-dateutil python3-parsedatetime
            ;;
        *)
            warn "$MSG_DISTRO_UNKNOWN$distro"
            warn "$MSG_MANUAL_DEPS"
            return 1
            ;;
    esac
    return 0
}

# ==================== Basic checks ====================
info "$MSG_CHECK_ENV"
if ! command -v python3 &> /dev/null; then
    err "$MSG_PYTHON_MISSING"
    exit 1
fi
ok "$MSG_PYTHON_OK"

# ==================== System dependencies ====================
info "$MSG_CHECK_DEPS"
if command -v pacman &> /dev/null; then
    MISSING=()
    for pkg in python-dateutil python-parsedatetime; do
        if ! pacman -Q "$pkg" &> /dev/null; then
            MISSING+=("$pkg")
        fi
    done
    if [ ${#MISSING[@]} -gt 0 ]; then
        warn "$MSG_DEPS_MISSING${MISSING[*]}"
        read -p "$MSG_INSTALL_NOW" -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            install_system_deps
        else
            warn "$MSG_SKIP_DEPS"
        fi
    else
        ok "$MSG_DEPS_OK"
    fi
else
    warn "$MSG_DISTRO_UNKNOWN"
    install_system_deps || true
fi

# ==================== Project path ====================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
info "$MSG_PROJECT_DIR$SCRIPT_DIR"

# ==================== Create venv ====================
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    info "$MSG_CREATE_VENV"
    python3 -m venv "$SCRIPT_DIR/.venv"
    ok "$MSG_VENV_CREATED"
else
    ok "$MSG_VENV_EXISTS"
fi

# ==================== Install Python dependencies ====================
info "$MSG_INSTALL_PY_DEPS"
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    "$SCRIPT_DIR/.venv/bin/pip" install --upgrade pip --quiet
    "$SCRIPT_DIR/.venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" --quiet
    ok "$MSG_PY_DEPS_OK"
else
    err "$MSG_NO_REQUIREMENTS"
    exit 1
fi

# ==================== Copy settings ====================
info "$MSG_COPY_SETTINGS"
mkdir -p "$HOME/.config/caelestia"
if [ -f "$HOME/.config/caelestia/todo-settings.json" ]; then
    warn "$MSG_SETTINGS_EXISTS"
else
    cp "$SCRIPT_DIR/todo-settings.json" "$HOME/.config/caelestia/todo-settings.json"
    ok "$MSG_SETTINGS_COPIED"
fi

# ==================== Check Caelestia ====================
info "$MSG_CHECK_CAELESTIA"
CAELESTIA_DIR="$HOME/.config/caelestia"
if [ ! -d "$CAELESTIA_DIR" ]; then
    err "$MSG_CAELESTIA_MISSING"
    exit 1
fi
ok "$MSG_CAELESTIA_OK"

# ==================== Conflict check ====================
echo
echo "============================================"
echo "  $MSG_CONFLICT_TITLE"
echo "============================================"
echo

CONFLICT_FOUND=0

if command -v todoist &> /dev/null || pacman -Q todoist &> /dev/null 2>&1; then
    warn "$MSG_CONFLICT_TODOIST"
    warn "$MSG_CONFLICT_TODOIST_WHY"
    echo
    echo "  $MSG_CONFLICT_TODOIST_FIX"
    echo "    sudo pacman -Rns todoist"
    echo
    CONFLICT_FOUND=1
else
    ok "$MSG_CONFLICT_TODOIST_OK"
fi

if [ "$CONFLICT_FOUND" = "1" ]; then
    warn "$MSG_CONFLICT_RESOLVE"
fi

# ==================== Print guide ====================
PROJECT_DIR="$SCRIPT_DIR"
echo
echo "============================================"
echo "  $MSG_DONE_TITLE"
echo "============================================"
echo
echo "$MSG_STEP1"
echo "$MSG_STEP1_DESC"
echo
cat <<CLI_EOF
{
  "toggles": {
    "todo": {
      "todo-tui": {
        "enable": true,
        "match": [{"class": "todo-tui"}],
        "command": [
          "foot", "-a", "todo-tui", "-T", "Todo List",
          "-e", "$PROJECT_DIR/.venv/bin/python3",
          "$PROJECT_DIR/todo.py"
        ],
        "move": true
      }
    }
  }
}
CLI_EOF
echo
echo "============================================"
echo "  $MSG_LAST_STEP"
echo "============================================"
echo
