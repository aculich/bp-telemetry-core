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
    echo "   ⚠️  Warning: You're on develop branch."
    read -p "   Continue with develop? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "   Aborted."
        exit 0
    fi
fi

# Step 2: Check for uncommitted changes
echo ""
echo "📋 Step 1: Checking for uncommitted changes..."
if ! git diff-index --quiet HEAD --; then
    echo "   ⚠️  You have uncommitted changes:"
    git status --short
    
    if [[ "$SKIP_COMMIT" == "false" ]]; then
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
    
    if [[ "$AUTO_PUSH" == "true" ]]; then
        PUSH_ANSWER="y"
    else
        read -p "   Push to origin? (Y/n): " -n 1 -r
        echo
        PUSH_ANSWER="$REPLY"
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
    
    if [[ "$AUTO_PUSH" == "true" ]]; then
        PUSH_ANSWER="y"
    else
        read -p "   Push to origin? (Y/n): " -n 1 -r
        echo
        PUSH_ANSWER="$REPLY"
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
read -p "   Switch back to develop branch? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git checkout develop
    echo "   ✅ Switched to develop branch"
fi

echo ""
echo "✅ Development session ended!"
echo ""
echo "Summary:"
echo "   - Branch: $CURRENT_BRANCH"
echo "   - All changes committed and pushed"
echo "   - Ready for next session"
echo ""

