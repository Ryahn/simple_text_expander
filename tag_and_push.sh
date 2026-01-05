#!/bin/bash

# Script to create a new git tag by incrementing the current tag and push it
# Assumes git add and git commit have already been done
# Usage: ./tag_and_push.sh [--major|--minor|--patch]
# Default: --patch

set -e  # Exit on error

# Determine which version component to increment
INCREMENT_TYPE="patch"
if [ "$1" = "--major" ]; then
    INCREMENT_TYPE="major"
elif [ "$1" = "--minor" ]; then
    INCREMENT_TYPE="minor"
elif [ "$1" = "--patch" ]; then
    INCREMENT_TYPE="patch"
elif [ -n "$1" ]; then
    echo "Error: Unknown argument '$1'"
    echo "Usage: $0 [--major|--minor|--patch]"
    exit 1
fi

# Get the latest tag
LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

if [ -z "$LATEST_TAG" ]; then
    # No tags exist, start with v1.0.0
    NEW_TAG="v1.0.0"
    echo "No existing tags found. Creating initial tag: $NEW_TAG"
else
    # Remove 'v' prefix if present for processing
    VERSION=${LATEST_TAG#v}
    
    # Split version into major.minor.patch
    IFS='.' read -ra VERSION_PARTS <<< "$VERSION"
    MAJOR=${VERSION_PARTS[0]:-0}
    MINOR=${VERSION_PARTS[1]:-0}
    PATCH=${VERSION_PARTS[2]:-0}
    
    # Increment based on type (following semver rules)
    case $INCREMENT_TYPE in
        major)
            MAJOR=$((MAJOR + 1))
            MINOR=0
            PATCH=0
            ;;
        minor)
            MINOR=$((MINOR + 1))
            PATCH=0
            ;;
        patch)
            PATCH=$((PATCH + 1))
            ;;
    esac
    
    # Reconstruct version with 'v' prefix
    NEW_TAG="v${MAJOR}.${MINOR}.${PATCH}"
    echo "Latest tag: $LATEST_TAG"
    echo "Incrementing: $INCREMENT_TYPE"
    echo "Creating new tag: $NEW_TAG"
fi

# Create the tag
git tag "$NEW_TAG"

# Push the tag to remote
echo "Pushing tag $NEW_TAG to remote..."
git push origin "$NEW_TAG"

echo "Successfully created and pushed tag: $NEW_TAG"

