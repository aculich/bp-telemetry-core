#!/bin/bash
# Resume a development session by checking out a recent dev/session branch
#
# Usage:
#   ./scripts/resume_dev_session.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

echo "🔄 Resuming Development Session"
echo "================================"
echo ""

# Find all dev/session branches (local and remote)
# Sort by commit date (most recent first)
RECENT_BRANCHES=$(git for-each-ref \
    --sort=-committerdate \
    --format='%(refname:short)|%(committerdate:short)|%(committerdate:relative)' \
    refs/heads/dev/session-* refs/remotes/origin/dev/session-* 2>/dev/null | \
    head -10)

if [[ -z "$RECENT_BRANCHES" ]]; then
    echo "❌ No dev/session branches found."
    echo ""
    echo "Start a new session with:"
    echo "   ./scripts/start_dev_session.sh"
    exit 1
fi

# Parse branches and build selection list
declare -a BRANCH_NAMES
declare -a BRANCH_DATES
declare -a BRANCH_RELATIVES
declare -a BRANCH_REMOTES

INDEX=1
while IFS='|' read -r branch date relative; do
    # Extract branch name (remove origin/ prefix if present)
    if [[ "$branch" =~ ^origin/ ]]; then
        BRANCH_NAME="${branch#origin/}"
        IS_REMOTE=true
    else
        BRANCH_NAME="$branch"
        IS_REMOTE=false
    fi
    
    BRANCH_NAMES[$INDEX]="$BRANCH_NAME"
    BRANCH_DATES[$INDEX]="$date"
    BRANCH_RELATIVES[$INDEX]="$relative"
    BRANCH_REMOTES[$INDEX]="$IS_REMOTE"
    INDEX=$((INDEX + 1))
done <<< "$RECENT_BRANCHES"

# Display branches
echo "📋 Recent development sessions:"
echo ""

for i in $(seq 1 $((INDEX - 1))); do
    REMOTE_MARKER=""
    if [[ "${BRANCH_REMOTES[$i]}" == "true" ]]; then
        REMOTE_MARKER=" (remote)"
    fi
    
    if [[ $i -eq 1 ]]; then
        echo "   [$i] ${BRANCH_NAMES[$i]}${REMOTE_MARKER} [default]"
        echo "       ${BRANCH_DATES[$i]} (${BRANCH_RELATIVES[$i]})"
    else
        echo "   [$i] ${BRANCH_NAMES[$i]}${REMOTE_MARKER}"
        echo "       ${BRANCH_DATES[$i]} (${BRANCH_RELATIVES[$i]})"
    fi
done

echo ""
read -p "Select session to resume (1-$((INDEX - 1))) [default: 1]: " SELECTION

# Default to 1 if empty
if [[ -z "$SELECTION" ]]; then
    SELECTION=1
fi

# Validate selection
if ! [[ "$SELECTION" =~ ^[0-9]+$ ]] || [[ "$SELECTION" -lt 1 ]] || [[ "$SELECTION" -ge $INDEX ]]; then
    echo "❌ Invalid selection: $SELECTION"
    exit 1
fi

SELECTED_BRANCH="${BRANCH_NAMES[$SELECTION]}"
IS_REMOTE="${BRANCH_REMOTES[$SELECTION]}"

echo ""
echo "📋 Resuming session: $SELECTED_BRANCH"
echo ""

# Check for uncommitted changes
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "⚠️  Warning: You have uncommitted changes."
    git status --short
    echo ""
    read -p "Stash changes before switching? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        git stash push -m "Auto-stash before resuming session $(date +%Y-%m-%d-%H%M%S)"
        echo "   ✅ Changes stashed"
    else
        echo "   ⚠️  Switching with uncommitted changes..."
    fi
fi

# Checkout branch
if [[ "$IS_REMOTE" == "true" ]]; then
    # Branch exists only on remote, create local tracking branch
    echo "   Creating local tracking branch from origin/$SELECTED_BRANCH..."
    git checkout -b "$SELECTED_BRANCH" "origin/$SELECTED_BRANCH"
else
    # Branch exists locally
    git checkout "$SELECTED_BRANCH"
fi

echo "   ✅ Checked out branch: $SELECTED_BRANCH"
echo ""

# Show status
echo "📋 Current Status"
echo "================================"
echo "   Current branch: $(git rev-parse --abbrev-ref HEAD)"
echo "   Status:"
git status -sb | head -1
echo ""
echo "✅ Session resumed!"
echo ""
echo "Next steps:"
echo "   1. Continue your work"
echo "   2. When done, run: ./scripts/end_dev_session.sh"
echo ""

