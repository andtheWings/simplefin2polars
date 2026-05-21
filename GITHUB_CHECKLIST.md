# GitHub Publishing Checklist

Before pushing to GitHub, complete these steps:

## 1. Update Personal Information

### In `pyproject.toml`:
- [ ] Replace `youremail@example.com` with your actual email
- [ ] Replace all `yourusername` in URLs with your GitHub username

### In `README.md`:
- [ ] Replace `yourusername` in GitHub URLs with your actual username
- [ ] Verify the hex logo image path is correct

### In `INSTALL.md`:
- [ ] Replace `yourusername` in all GitHub URLs

## 2. Initialize Git Repository (if not already done)

```bash
git init
git add .
git commit -m "Initial commit"
```

## 3. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `simplefin2polars`
3. Description: "Query the SimpleFIN protocol and parse responses into Polars DataFrames"
4. Make it **Public** (or Private if preferred)
5. **DO NOT** initialize with README, .gitignore, or LICENSE (you already have these)

## 4. Push to GitHub

```bash
git remote add origin https://github.com/yourusername/simplefin2polars.git
git branch -M main
git push -u origin main
```

## 5. Configure GitHub Repository Settings

### About Section:
- Add website: Link to SimpleFIN docs if desired
- Add topics: `python`, `polars`, `simplefin`, `finance`, `banking`, `dataframe`

### Optional - Add Branch Protection:
- Go to Settings → Branches
- Add rule for `main` branch
- Consider requiring PR reviews for commits

## 6. Test Installation from GitHub

After pushing, test that others can install:

```bash
pip install git+https://github.com/yourusername/simplefin2polars.git
```

## 7. Create Initial Release (Optional)

1. Go to Releases on GitHub
2. Click "Create a new release"
3. Tag: `v0.1.0`
4. Release title: `v0.1.0 - Initial Release`
5. Describe features and functionality
6. Click "Publish release"

## Post-Publishing

- [ ] Update README with any additional badges or shields
- [ ] Consider adding CI/CD workflow (GitHub Actions)
- [ ] Add issue templates
- [ ] Add pull request template

## Future PyPI Publishing

When ready to publish to PyPI:

1. Build the package:
   ```bash
   pip install build twine
   python -m build
   ```

2. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```

3. Update README installation to:
   ```bash
   pip install simplefin2polars
   ```
