#!/bin/bash
# install.sh — 一键部署 todo-tui 到 Caelestia 环境
# 用法: ./install.sh

set -e  # 遇到错误立即退出

# ==================== 颜色 ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()   { echo -e "${GREEN}[ OK ]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[FAIL]${NC} $1"; }

# ==================== 发行版检测 ====================
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
            info "检测到 Arch 系发行版，使用 pacman 安装系统依赖..."
            sudo pacman -S --needed python-dateutil python-parsedatetime
            ;;
        debian|ubuntu|linuxmint|pop)
            info "检测到 Debian 系发行版，使用 apt 安装系统依赖..."
            sudo apt update
            sudo apt install -y python3-dateutil python3-parsedatetime
            ;;
        fedora|rhel|centos)
            info "检测到 Fedora 系发行版，使用 dnf 安装系统依赖..."
            sudo dnf install -y python3-dateutil python3-parsedatetime
            ;;
        *)
            warn "未识别的发行版: $distro"
            warn "请手动安装以下 Python 库："
            warn "  - python-dateutil"
            warn "  - parsedatetime"
            warn "你可以尝试：pip install python-dateutil parsedatetime"
            return 1
            ;;
    esac
    return 0
}

# ==================== 基本检查 ====================
info "检查基本环境..."

if ! command -v python3 &> /dev/null; then
    err "未找到 python3，请先安装 Python 3。"
    exit 1
fi
ok "python3 已安装"

# ==================== 系统依赖 ====================
info "检查系统 Python 依赖..."

# 检查是否已安装（仅 Arch 可直接用 pacman -Q）
if command -v pacman &> /dev/null; then
    MISSING=()
    for pkg in python-dateutil python-parsedatetime; do
        if ! pacman -Q "$pkg" &> /dev/null; then
            MISSING+=("$pkg")
        fi
    done

    if [ ${#MISSING[@]} -gt 0 ]; then
        warn "缺少系统包：${MISSING[*]}"
        read -p "是否现在安装？[Y/n] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            install_system_deps
        else
            warn "跳过系统依赖安装。"
        fi
    else
        ok "系统依赖已满足"
    fi
else
    warn "未检测到 pacman，尝试自动安装系统依赖..."
    install_system_deps || true
fi

# ==================== 项目路径 ====================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
info "项目目录: $SCRIPT_DIR"

# ==================== 创建 venv ====================
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    info "创建 Python venv..."
    python3 -m venv "$SCRIPT_DIR/.venv"
    ok "venv 已创建"
else
    ok "venv 已存在，跳过创建"
fi

# ==================== 安装 Python 依赖到 venv ====================
info "安装 Python 依赖到 venv..."
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    "$SCRIPT_DIR/.venv/bin/pip" install --upgrade pip --quiet
    "$SCRIPT_DIR/.venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" --quiet
    ok "Python 依赖安装完成"
else
    err "未找到 requirements.txt"
    exit 1
fi

# ==================== 复制设置文件 ====================
info "复制设置文件到 ~/.config/caelestia/..."
mkdir -p "$HOME/.config/caelestia"
if [ -f "$HOME/.config/caelestia/todo-settings.json" ]; then
    warn "todo-settings.json 已存在，保留现有配置。"
    warn "如需重置，请手动复制：cp $SCRIPT_DIR/todo-settings.json ~/.config/caelestia/todo-settings.json"
else
    cp "$SCRIPT_DIR/todo-settings.json" "$HOME/.config/caelestia/todo-settings.json"
    ok "todo-settings.json 已复制"
fi

# ==================== 检查 Caelestia ====================
info "检查 Caelestia 配置..."
CAELESTIA_DIR="$HOME/.config/caelestia"
if [ ! -d "$CAELESTIA_DIR" ]; then
    err "未找到 ~/.config/caelestia/，请先安装 Caelestia："
    err "  https://github.com/caelestia-dots/caelestia"
    exit 1
fi
ok "Caelestia 配置目录存在"

# ==================== 打印配置指南 ====================
PROJECT_DIR="$SCRIPT_DIR"

echo
echo "============================================"
echo "  安装完成！还需要手动修改两个文件"
echo "============================================"
echo
echo -e "${YELLOW}1. 编辑 ~/.config/caelestia/cli.json${NC}"
echo "   （如果文件不存在，创建它；如果已存在，把 todo 部分合并进去）"
echo
echo "   复制以下内容："
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
echo -e "${YELLOW}2. 编辑 ~/.config/caelestia/hypr-user.lua${NC}"
echo "   （加入下面这行）"
echo
echo "    hl.bind(\"SUPER + R\", hl.dsp.exec_cmd(\"$PROJECT_DIR/toggle-todo.sh\"))"
echo
echo "============================================"
echo -e "${GREEN}最后一步：注销并重新登录，让配置生效。${NC}"
echo "============================================"
echo
echo -e "如果遇到问题，请查看 README.md 或提 issue。"
echo
