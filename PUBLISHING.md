# Publishing to PyPI Guide

## Prerequisites

1. **PyPI Account**: Create account at https://pypi.org/account/register/
2. **API Token**: Generate token at https://pypi.org/manage/account/token/
3. **Poetry Installed**: `pip install poetry`

## Initial Setup

```bash
# Configure Poetry with PyPI token
poetry config pypi-token.pypi YOUR_TOKEN_HERE

# Or use environment variable
export POETRY_PYPI_TOKEN_PYPI=YOUR_TOKEN_HERE
```

## Publishing Process

### 1. Update Version

Edit `pyproject.toml`:
```toml
[tool.poetry]
version = "0.1.1"  # Increment version
```

### 2. Update CHANGELOG.md

Add new version entry:
```markdown
## [0.1.1] - 2025-04-10

### Fixed
- Bug fixes
```

### 3. Run Tests

```bash
poetry run pytest
poetry run black --check src/
poetry run ruff check src/
```

### 4. Build Package

```bash
poetry build
```

This creates:
- `dist/ogc2qgis-0.1.1.tar.gz` (source distribution)
- `dist/ogc2qgis-0.1.1-py3-none-any.whl` (wheel)

### 5. Publish to PyPI

```bash
poetry publish
```

Or publish in one step:
```bash
poetry publish --build
```

### 6. Create Git Tag

```bash
git tag v0.1.1
git push origin v0.1.1
```

This triggers GitHub Actions to auto-publish (if configured).

## Automated Publishing with GitHub Actions

The included `.github/workflows/ci.yml` automatically publishes when you push a tag:

```bash
# Create and push tag
git tag v0.1.1
git push origin v0.1.1

# GitHub Actions will:
# 1. Run tests
# 2. Build package
# 3. Publish to PyPI
```

**Setup required**: Add `PYPI_TOKEN` as GitHub secret:
1. Go to repository Settings → Secrets → Actions
2. Add new secret: `PYPI_TOKEN` = your PyPI token

## Testing Before Publishing

### Test on TestPyPI

```bash
# Configure TestPyPI
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi YOUR_TEST_TOKEN

# Publish to TestPyPI
poetry publish -r testpypi

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ ogc2qgis
```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features, backwards compatible
- **PATCH** (0.0.1): Bug fixes

## Checklist Before Publishing

- [ ] All tests pass
- [ ] Version bumped in `pyproject.toml`
- [ ] CHANGELOG.md updated
- [ ] README.md updated (if needed)
- [ ] Code formatted with `black`
- [ ] Code linted with `ruff`
- [ ] Documentation updated
- [ ] Git committed and pushed
- [ ] Tag created (optional, for auto-publish)

## Troubleshooting

**Issue**: `File already exists`
- Solution: Increment version number

**Issue**: `Invalid token`
- Solution: Regenerate token and update configuration

**Issue**: `Package name already taken`
- Solution: Choose different name in `pyproject.toml`

## Post-Publishing

1. **Verify on PyPI**: https://pypi.org/project/ogc2qgis/
2. **Test installation**: `pip install ogc2qgis`
3. **Announce release**: Update README, create GitHub release
4. **Monitor**: Check download stats, issues

## Yanking a Release (if needed)

```bash
# Remove from PyPI (discouraged)
pip install twine
twine upload --repository pypi dist/*

# Or use Poetry (doesn't support yanking yet)
# Contact PyPI support if critical issue
```

## Resources

- PyPI: https://pypi.org/
- Poetry docs: https://python-poetry.org/docs/
- TestPyPI: https://test.pypi.org/
- Semantic Versioning: https://semver.org/
