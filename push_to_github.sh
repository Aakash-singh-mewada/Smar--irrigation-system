#!/usr/bin/env bash
# Usage: ./push_to_github.sh https://github.com/<username>/smart-irrigation-system.git
set -e
[ -z "$1" ] && { echo "Usage: $0 <github-repo-url>"; exit 1; }
git init
git add .
git commit -m "Initial commit: Smart Automatic Irrigation System"
git branch -M main
git remote add origin "$1"
git push -u origin main
