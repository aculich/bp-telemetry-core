#!/bin/sh
# Activate virtual environment for Blueplane Telemetry Core
# Works in both bash and zsh when sourced
#
# Usage: source scripts/activate_venv.sh
#        (from the project root directory)

# First, try current directory (most common case - user runs from project root)
if [ -d ".venv" ] && [ -f ".venv/bin/activate" ]; then
    VENV_DIR="$(pwd)/.venv"
else
    # Fallback: try to calculate from script location
    # This is more complex and may not work in all shells when sourced
    if [ -n "$BASH_VERSION" ] && [ -n "${BASH_SOURCE[0]:-}" ]; then
        # Bash: BASH_SOURCE works when sourced
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    elif [ -n "$ZSH_VERSION" ]; then
        # Zsh: when sourced, we need to use a different approach
        # Try to get script path from function context
        # If this doesn't work, user should run from project root
        if [ -f "scripts/activate_venv.sh" ]; then
            # We're likely in project root, try relative path
            SCRIPT_DIR="$(cd "$(pwd)/scripts" && pwd)"
        else
            # Last resort: try $0 (may not work when sourced)
            SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd 2>/dev/null)" || SCRIPT_DIR=""
        fi
    else
        # Other shells: try $0
        SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd 2>/dev/null)" || SCRIPT_DIR=""
    fi
    
    if [ -n "$SCRIPT_DIR" ] && [ -d "$SCRIPT_DIR" ]; then
        PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
        VENV_DIR="$PROJECT_DIR/.venv"
    else
        # Could not determine script location
        VENV_DIR=""
    fi
fi

# Check if venv exists
if [ -z "$VENV_DIR" ] || [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found!"
    echo ""
    echo "Please ensure:"
    echo "  1. You are in the project root directory (experiment/core)"
    echo "  2. The virtual environment has been created (run: ./scripts/setup_venv.sh)"
    echo ""
    echo "Current directory: $(pwd)"
    echo "Looking for: ${VENV_DIR:-.venv (in current directory)}"
    # Use return when sourced, this won't exit the shell
    return 1
fi

if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "❌ Error: Virtual environment is incomplete."
    echo "   Activation script not found at: $VENV_DIR/bin/activate"
    echo "   Try running: ./scripts/setup_venv.sh"
    # Use return when sourced, this won't exit the shell
    return 1
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"
echo "✅ Virtual environment activated: $VENV_DIR"
