#!/bin/bash
git branch -D new-branch-to-save-current-commits
git checkout master
git branch new-branch-to-save-current-commits
git fetch --all
git reset --hard origin/master
git branch -D new-branch-to-save-current-commits

