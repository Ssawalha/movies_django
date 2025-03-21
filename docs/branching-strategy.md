# Branching Strategy

This document outlines the branching strategy for the Amman Movies project.

## Branch Types

### Main Branches

- `master`: Development branch for integrating features
- `staging`: Staging environment for testing before production
- `production`: Production-ready code

### Supporting Branches

- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Production hotfixes
- `release/*`: Release preparation

## Branch Naming Convention

- Feature branches: `feature/description-of-feature`
- Bugfix branches: `bugfix/description-of-bug`
- Hotfix branches: `hotfix/description-of-fix`
- Release branches: `release/v1.0.0`

## Workflow

### Starting New Work

1. Create a new branch from `master`:

   ```bash
   git checkout master
   git pull origin master
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit using conventional commits:

   ```bash
   git commit -m "feat: add new feature"
   git commit -m "fix: resolve bug"
   git commit -m "docs: update documentation"
   ```

3. Push your branch:

   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request to `master`

## Pre-commit Hooks

The following pre-commit hooks are enforced:

- Code formatting (black)
- Import sorting (isort)
- Linting (flake8)
- Type checking (mypy)
- Commit message format (commitizen)

To install pre-commit hooks:

```bash
pip install -r requirements.txt
pre-commit install
```
