#!/bin/bash
# Script to import git bundle and push to GitHub
# Usage: ./push-bundle.sh procesos-construccion-honduras.bundle

set -e

BUNDLE_FILE="${1:-.}/procesos-construccion-honduras.bundle"
REPO_NAME="procesos-construccion-honduras"
BRANCH_NAME="claude/honduras-procurement-report-hv200y"
GITHUB_ORG="lancasthnd"

echo "🚀 Git Bundle Import & Push Script"
echo "===================================="
echo ""

# Check if bundle exists
if [ ! -f "$BUNDLE_FILE" ]; then
    echo "❌ Error: Bundle file not found: $BUNDLE_FILE"
    echo "   Please provide the path to procesos-construccion-honduras.bundle"
    exit 1
fi

echo "✅ Bundle file found: $BUNDLE_FILE"
echo ""

# Check if in a git repo
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    echo "   Please run this script from your local procesos-construccion-honduras directory"
    exit 1
fi

echo "📦 Importing commits from bundle..."
git bundle verify "$BUNDLE_FILE" > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Bundle verified"
else
    echo "❌ Bundle verification failed"
    exit 1
fi

echo ""
echo "🔄 Fetching commits from bundle..."
git fetch "$BUNDLE_FILE" refs/heads/$BRANCH_NAME:refs/heads/$BRANCH_NAME

echo "✅ Commits fetched"
echo ""

echo "🌿 Checking out branch: $BRANCH_NAME"
git checkout $BRANCH_NAME

echo "✅ Checked out to $BRANCH_NAME"
echo ""

# Show commits
echo "📋 Commits to push:"
git log --oneline -6
echo ""

# Verify remote
REMOTE_URL=$(git config --get remote.origin.url)
echo "🔗 Remote: $REMOTE_URL"
echo ""

# Push
echo "📤 Pushing to GitHub..."
git push -u origin $BRANCH_NAME

echo ""
echo "✅ SUCCESS! All commits pushed to GitHub"
echo "   Branch: $BRANCH_NAME"
echo "   Repo: https://github.com/$GITHUB_ORG/$REPO_NAME"
echo ""
echo "Next steps:"
echo "1. Visit: https://github.com/$GITHUB_ORG/$REPO_NAME/tree/$BRANCH_NAME"
echo "2. Create a Pull Request to merge into master"
echo ""
