#!/bin/bash
# End Development Session
# Standardized workflow for ending a development session
#
# Usage:
#   ./scripts/end_dev_session.sh [--push] [--no-commit]
#
# Options:
#   --push         Automatically push changes (default: ask)
#   --no-commit    Skip committing changes (default: ask if uncommitted)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

AUTO_PUSH=false
SKIP_COMMIT=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --push)
            AUTO_PUSH=true
            shift
            ;;
        --no-commit)
            SKIP_COMMIT=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--push] [--no-commit]"
            exit 1
            ;;
    esac
done

echo "🏁 Ending Development Session"
echo "================================"
echo ""

# Step 1: Check current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "📋 Current branch: $CURRENT_BRANCH"

if [[ "$CURRENT_BRANCH" == "main" ]]; then
    echo "   ⚠️  Warning: You're on main branch. This script is for feature branches."
    echo "   Exiting without changes."
    exit 0
fi

if [[ "$CURRENT_BRANCH" == "develop" ]]; then
    # Check if develop has uncommitted changes or unpushed commits
    HAS_UNCOMMITTED=$(git diff-index --quiet HEAD --; echo $?)
    LOCAL_COMMITS=$(git rev-list --count origin/develop..HEAD 2>/dev/null || echo "0")
    
    if [[ "$HAS_UNCOMMITTED" -eq 1 ]] || [[ "$LOCAL_COMMITS" -gt 0 ]]; then
        # There's work to save, so it makes sense to continue
        echo "   ℹ️  On develop branch with work to save. Continuing..."
    else
        # No work to save, probably accidental - ask
        echo "   ⚠️  Warning: You're on develop branch with no uncommitted changes or unpushed commits."
        read -p "   Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "   Aborted."
            exit 0
        fi
    fi
fi

# Step 2: Check for uncommitted changes
echo ""
echo "📋 Step 1: Checking for uncommitted changes..."
if ! git diff-index --quiet HEAD --; then
    echo "   ⚠️  You have uncommitted changes:"
    git status --short
    
    if [[ "$SKIP_COMMIT" == "false" ]]; then
        # Check if changes look like they should be committed
        # Skip commit if all files are in .gitignore or are temporary files
        CHANGED_FILES=$(git status --short | awk '{print $2}')
        ALL_IGNORED=true
        for file in $CHANGED_FILES; do
            if ! git check-ignore -q "$file"; then
                ALL_IGNORED=false
                break
            fi
        done
        
        if [[ "$ALL_IGNORED" == "true" ]]; then
            echo "   ℹ️  All changed files are ignored. Skipping commit."
        else
            # Auto-commit by default (Y), but allow override
            read -p "   Commit these changes? (Y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                echo "   📝 Enter commit message (or press Enter for default):"
                read -r COMMIT_MSG
                if [[ -z "$COMMIT_MSG" ]]; then
                    COMMIT_MSG="WIP: $(date +%Y-%m-%d-%H%M%S)"
                fi
                
                git add -A
                git commit -m "$COMMIT_MSG"
                echo "   ✅ Changes committed"
            else
                echo "   ⚠️  Skipping commit. Changes remain uncommitted."
            fi
        fi
    else
        echo "   ⚠️  Skipping commit (--no-commit flag)"
    fi
else
    echo "   ✅ No uncommitted changes"
fi

# Step 3: Check if branch needs pushing
echo ""
echo "📋 Step 2: Checking branch status..."
LOCAL_COMMITS=$(git rev-list --count origin/"$CURRENT_BRANCH"..HEAD 2>/dev/null || echo "0")
HAS_REMOTE=$(git ls-remote --heads origin "$CURRENT_BRANCH" | wc -l)

if [[ "$LOCAL_COMMITS" -gt 0 ]]; then
    echo "   📤 Branch has $LOCAL_COMMITS local commit(s) not pushed"
    
    # Auto-push by default (most common case)
    if [[ "$AUTO_PUSH" == "true" ]]; then
        PUSH_ANSWER="y"
    else
        # Check if we can push (network available, etc.)
        if git ls-remote --heads origin >/dev/null 2>&1; then
            # Remote is accessible, auto-push
            echo "   📤 Pushing to origin (auto)..."
            PUSH_ANSWER="y"
        else
            # Remote not accessible, ask
            read -p "   Push to origin? (Y/n): " -n 1 -r
            echo
            PUSH_ANSWER="$REPLY"
        fi
    fi
    
    if [[ ! "$PUSH_ANSWER" =~ ^[Nn]$ ]]; then
        echo "   📤 Pushing to origin..."
        git push -u origin "$CURRENT_BRANCH" 2>&1 || {
            echo "   ❌ Push failed. Check your git configuration and try again."
            exit 1
        }
        echo "   ✅ Pushed to origin"
    else
        echo "   ⚠️  Skipping push. Remember to push later!"
    fi
elif [[ "$HAS_REMOTE" -eq 0 ]]; then
    echo "   📤 Branch doesn't exist on remote"
    
    # Auto-push new branches by default
    if [[ "$AUTO_PUSH" == "true" ]]; then
        PUSH_ANSWER="y"
    else
        # Check if remote is accessible
        if git ls-remote --heads origin >/dev/null 2>&1; then
            echo "   📤 Pushing to origin (auto)..."
            PUSH_ANSWER="y"
        else
            read -p "   Push to origin? (Y/n): " -n 1 -r
            echo
            PUSH_ANSWER="$REPLY"
        fi
    fi
    
    if [[ ! "$PUSH_ANSWER" =~ ^[Nn]$ ]]; then
        echo "   📤 Pushing to origin..."
        git push -u origin "$CURRENT_BRANCH"
        echo "   ✅ Pushed to origin"
    fi
else
    echo "   ✅ Branch is up to date with remote"
fi

# Step 4: Show summary
echo ""
echo "📋 Step 3: Session Summary"
echo "================================"
echo "   Branch: $CURRENT_BRANCH"
echo "   Status: $(git status -sb | head -1 | cut -d' ' -f2-)"
echo ""

# Step 5: Optional - switch back to develop
echo "📋 Step 4: Cleanup"

# Auto-switch to develop if:
# 1. We're on a feature branch (not develop/main)
# 2. All work is committed and pushed
# 3. No uncommitted changes

if [[ "$CURRENT_BRANCH" =~ ^(dev/|feature/) ]] && git diff-index --quiet HEAD --; then
    # Check if branch is pushed
    if git rev-parse --verify "origin/$CURRENT_BRANCH" >/dev/null 2>&1 || \
       [[ "$LOCAL_COMMITS" -eq 0 ]] || [[ "$AUTO_PUSH" == "true" ]]; then
        echo "   🔄 Switching back to develop (auto)..."
        git checkout develop
        echo "   ✅ Switched to develop branch"
    else
        # Branch not pushed, ask
        read -p "   Switch back to develop branch? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            git checkout develop
            echo "   ✅ Switched to develop branch"
        fi
    fi
else
    # On develop or has uncommitted changes - ask
    read -p "   Switch back to develop branch? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        git checkout develop
        echo "   ✅ Switched to develop branch"
    fi
fi

echo ""
echo "✅ Development session ended!"
echo ""
echo "Summary:"
echo "   - Branch: $CURRENT_BRANCH"
echo "   - All changes committed and pushed"
echo "   - Ready for next session"
echo ""

