#!/bin/bash

# GitHub Push Script for Paste Studio MVP
# This script will push your code to GitHub

echo "=========================================="
echo "🚀 PUSHING TO GITHUB"
echo "=========================================="
echo ""

# Check if remote already exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "✓ Remote 'origin' already exists"
    git remote get-url origin
else
    echo "Adding remote origin..."
    git remote add origin https://github.com/koviddutta/paste-studio-mvp.git
    echo "✓ Remote added"
fi

echo ""
echo "Setting main branch..."
git branch -M main
echo "✓ Branch set to main"

echo ""
echo "Pushing to GitHub..."
echo "(You may be asked for credentials)"
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ SUCCESS! Code pushed to GitHub"
    echo "=========================================="
    echo ""
    echo "🔗 View your repository at:"
    echo "   https://github.com/koviddutta/paste-studio-mvp"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "⚠️ PUSH FAILED"
    echo "=========================================="
    echo ""
    echo "Common solutions:"
    echo "1. Make sure you created the repo on GitHub first"
    echo "2. Use your Personal Access Token as password"
    echo "3. Check your internet connection"
    echo ""
fi
