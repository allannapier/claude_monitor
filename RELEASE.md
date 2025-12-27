# PyPI & Release Configuration

This document explains how the release process works for Claude Monitor.

## Overview

Claude Monitor is distributed through multiple channels:

1. **PyPI** - For Python developers: `pip install claude-monitor`
2. **GitHub Releases** - Pre-built binaries for macOS, Linux, and Windows (no Python required)

Both are automatically built and published when you create a release tag.

## Release Process

### Quick Release

The release process is automated via GitHub Actions. To release a new version:

1. **Update version** in `pyproject.toml` and `setup.py`:
   ```toml
   version = "1.0.1"
   ```

2. **Update** `CHANGELOG.md` with release notes

3. **Commit changes:**
   ```bash
   git add pyproject.toml setup.py CHANGELOG.md
   git commit -m "Bump version to 1.0.1"
   ```

4. **Create and push tag:**
   ```bash
   git tag v1.0.1
   git push origin main --follow-tags
   ```

That's it! GitHub Actions will automatically:
- ✅ Build and publish to PyPI
- ✅ Build executables for macOS, Linux, Windows
- ✅ Create a GitHub Release with binaries attached

### Automated Workflows

#### 1. PyPI Publishing (`publish-pypi.yml`)

**Trigger:** Push with tag matching `v*` (e.g., `v1.0.1`)

**Steps:**
1. Check out code
2. Build Python distributions (wheel + source)
3. Verify with `twine check`
4. Upload to PyPI using `PYPI_TOKEN`

**Output:** Package available on PyPI within 5-10 minutes

#### 2. Binary Builds (`build-binaries.yml`)

**Trigger:** Push with tag matching `v*` (e.g., `v1.0.1`)

**Builds on:**
- Ubuntu (Linux x86_64)
- macOS (x86_64/ARM64 universal)
- Windows (x86_64)

**Steps per platform:**
1. Check out code
2. Install dependencies
3. Build executable with PyInstaller
4. Verify executable runs
5. Upload to GitHub Release

**Output:** Three binaries available in Releases page

## Setup Requirements

### PyPI Token Setup

1. Create account at https://pypi.org (if not already done)
2. Generate an API token:
   - Settings → API Tokens → Create API Token
   - Save the token (looks like `pypi-AgEI...`)

3. Add to GitHub Secrets:
   - Go to repository Settings → Secrets and variables → Actions
   - Create new secret: `PYPI_TOKEN`
   - Paste the token value

### No Other Setup Required!

The workflows handle all other configuration:
- Virtual environments
- Dependency installation
- Cross-platform builds
- Release artifact uploads

## PyInstaller Configuration

The binary builds use a PyInstaller spec file (`claude-monitor.spec`) that:

- **Includes data files:**
  - Flask templates (`src/claude_monitor/web/templates/`)
  - Static assets (`src/claude_monitor/web/static/`)

- **Specifies hidden imports:**
  - flask, jinja2, click, rich, dateutil

- **Builds single-file executables** for easy distribution

If you add new data files or dependencies, update the spec file:

```python
datas=[
    ('src/claude_monitor/web/templates', 'templates'),
    ('src/claude_monitor/web/static', 'static'),
    # Add new paths here
],
hiddenimports=[
    'flask',
    'jinja2',
    'click',
    'rich',
    'dateutil',
    # Add new imports here
],
```

## Installation Methods

### For End-Users

**Option 1: PyPI (if Python installed)**
```bash
pip install claude-monitor
claude-monitor
```

**Option 2: Binary (no Python required)**
- Download executable from [Releases](https://github.com/allannapier/claude_monitor/releases)
- Run directly

### For Developers

```bash
git clone https://github.com/allannapier/claude_monitor
cd claude_monitor
pip install -e .
claude-monitor
```

## Troubleshooting

### Release didn't trigger

- ✅ Check tag format: must be `v*` (e.g., `v1.0.1`)
- ✅ Tag must be pushed to GitHub: `git push origin --follow-tags`
- ✅ Check Actions tab to see workflow status

### PyPI token not working

- ✅ Verify token in GitHub Secrets (Settings → Secrets)
- ✅ Token must start with `pypi-`
- ✅ Token must be in correct secret: `PYPI_TOKEN`

### Binaries failing to build

- ✅ Check GitHub Actions workflow logs (Actions tab)
- ✅ PyInstaller needs data files to exist
- ✅ Check that `src/claude_monitor/web/templates/` exists

## Version Strategy

Claude Monitor uses semantic versioning:

- **MAJOR** (e.g., `2.0.0`) - Breaking changes
- **MINOR** (e.g., `1.1.0`) - New features (backwards compatible)
- **PATCH** (e.g., `1.0.1`) - Bug fixes

For releases, update:
1. `version = "X.Y.Z"` in `pyproject.toml`
2. `version = "X.Y.Z"` in `setup.py`
3. Add entry to `CHANGELOG.md`

## Next Steps

Future enhancements:
- [ ] Add Homebrew tap for macOS: `brew tap allannapier/claude-monitor`
- [ ] Add conda-forge recipe for data science users
- [ ] Add Docker distribution
- [ ] Digital signing for binaries (macOS)

## Reference

- [PyPI Help](https://pypi.org/help/)
- [twine Documentation](https://twine.readthedocs.io/)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [GitHub Actions](https://docs.github.com/en/actions)
