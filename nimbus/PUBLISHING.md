# 🚀 Publishing Nimbus to PyPI - Complete Guide

This guide will walk you through publishing Nimbus to PyPI (Python Package Index).

## ✅ Pre-Publishing Checklist

All done! ✅
- [x] Version set to 0.1.0-beta.1
- [x] README_PYPI.md created for PyPI
- [x] LICENSE file in package directory
- [x] CHANGELOG.md updated
- [x] All tests passing (7/7)
- [x] pyproject.toml has all metadata
- [x] MANIFEST.in configured

## 📦 Step 1: Install Publishing Tools

You need Poetry installed. Choose one method:

### Option A: Install Poetry (Recommended)

```powershell
# Install Poetry via PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# Add to PATH (restart terminal after this)
$env:Path += ";$env:APPDATA\Python\Scripts"

# Verify installation
poetry --version
```

### Option B: Use pip + build + twine (Alternative)

```powershell
pip install build twine
```

## 🔑 Step 2: Create PyPI Account

1. **Create account at PyPI**: https://pypi.org/account/register/
2. **Verify email**
3. **Enable 2FA** (required for publishing)
4. **Create API Token**:
   - Go to: https://pypi.org/manage/account/token/
   - Click "Add API token"
   - Token name: "nimbus-analytics"
   - Scope: "Entire account" (or create project first)
   - **SAVE THE TOKEN** - you won't see it again!

## 🧪 Step 3: Test on Test PyPI (RECOMMENDED)

Test first to avoid mistakes:

### Create Test PyPI Account
1. Go to: https://test.pypi.org/account/register/
2. Create account (separate from production PyPI)
3. Create API token: https://test.pypi.org/manage/account/token/

### Configure Poetry for Test PyPI

```powershell
cd C:\Users\Asus\Desktop\opoplp\nimbus\apps\api

# Add Test PyPI repository
poetry config repositories.test-pypi https://test.pypi.org/legacy/

# Set Test PyPI token (replace YOUR_TEST_TOKEN)
poetry config pypi-token.test-pypi pypi-YOUR_TEST_TOKEN_HERE
```

### Build and Publish to Test PyPI

```powershell
# Build the package
poetry build

# This creates:
# - dist/nimbus_analytics-0.1.0b1-py3-none-any.whl
# - dist/nimbus-analytics-0.1.0b1.tar.gz

# Publish to Test PyPI
poetry publish -r test-pypi
```

### Test Installation from Test PyPI

```powershell
# In a new terminal/environment
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ nimbus-analytics

# Test import
python -c "from nimbus.main import app; print('Success!')"
```

## 🎉 Step 4: Publish to Production PyPI

Once test succeeds:

### Configure Production PyPI

```powershell
# Set production PyPI token (replace YOUR_PRODUCTION_TOKEN)
poetry config pypi-token.pypi pypi-YOUR_PRODUCTION_TOKEN_HERE
```

### Publish!

```powershell
cd C:\Users\Asus\Desktop\opoplp\nimbus\apps\api

# Build (if not already built)
poetry build

# Publish to production PyPI
poetry publish

# ✅ Done! Package is live at: https://pypi.org/project/nimbus-analytics/
```

## 🌐 Step 5: Create GitHub Release

1. **Commit all changes**:
```powershell
cd C:\Users\Asus\Desktop\opoplp

git add .
git commit -m "chore: release v0.1.0-beta.1"
git push origin master
```

2. **Create GitHub Release**:
   - Go to: https://github.com/bahagh/nimbus/releases/new
   - **Tag**: `v0.1.0-beta.1`
   - **Title**: `v0.1.0-beta.1 - Initial Beta Release`
   - **Description**: Copy from CHANGELOG.md
   - **This is a pre-release**: ✅ Check this box
   - Click "Publish release"

## 📢 Step 6: Announce Your Launch!

### Hacker News (Show HN)

Post on: https://news.ycombinator.com/submit

**Title**: 
```
Show HN: Nimbus – Open-source alternative to Segment (backend ready, dashboard coming Q1)
```

**URL**: `https://github.com/bahagh/nimbus`

**Text**:
```
Hi HN! I built Nimbus - an open-source, self-hosted alternative to Segment and Mixpanel.

The problem: Segment charges $500-$2,000+/month. Mixpanel is similar. Most companies just need event tracking, not all the bells and whistles.

Nimbus gives you:
- Event ingestion API (10K+ events/sec)
- Real-time metrics aggregation
- Multi-tenant architecture
- JWT + HMAC authentication
- 90% cost savings (you only pay for infrastructure)
- Complete data ownership

The backend is production-ready. I'm actively building the dashboard UI (coming Q1 2026).

Stack: FastAPI, SQLAlchemy 2.0 async, PostgreSQL, Redis
License: MIT
Status: Beta (backend ready, seeking feedback)

Looking for feedback, early adopters, and contributors!

GitHub: https://github.com/bahagh/nimbus
PyPI: https://pypi.org/project/nimbus-analytics/
```

### Reddit Posts

**r/opensource**: https://reddit.com/r/opensource/submit
```
Title: [Launch] Nimbus - Open-source alternative to Segment & Mixpanel
Body: Just launched the beta! Backend API is production-ready, saves 90% compared to Segment. Dashboard coming Q1 2026. Looking for feedback!
Link: https://github.com/bahagh/nimbus
```

**r/python**: https://reddit.com/r/python/submit
```
Title: Built an async FastAPI event analytics platform (Segment alternative)
Body: Using FastAPI + SQLAlchemy 2.0 async + PostgreSQL. 10K+ events/sec, comprehensive tests. Just published to PyPI. Would love feedback!
Link: https://github.com/bahagh/nimbus
```

**r/selfhosted**: https://reddit.com/r/selfhosted/submit
```
Title: Nimbus - Self-hosted event analytics (alternative to Segment/Mixpanel)
Body: Tired of paying $2K/month for Segment? I built an open-source alternative. Docker Compose included. MIT license.
Link: https://github.com/bahagh/nimbus
```

**r/startups**: https://reddit.com/r/startups/submit
```
Title: Built open-source analytics to save $2K/month vs Segment
Body: Sharing my journey building a self-hosted alternative to expensive SaaS analytics tools.
Link: https://github.com/bahagh/nimbus
```

### Twitter/X Thread

```
🚀 Just launched Nimbus v0.1.0-beta! 

An open-source alternative to Segment & Mixpanel.

Why? Because $2,000/month for event tracking is insane. 🧵

1/ The Problem:
- Segment: $500-$2K+/month
- Mixpanel: $1K+/month
- Your data lives on their servers
- Limited customization
- Vendor lock-in

2/ Nimbus gives you:
✅ 90% cost savings
✅ Self-hosted (own your data)
✅ Full customization (open source)
✅ Modern stack (FastAPI, async Python)

3/ What's ready NOW:
- Event ingestion API (10K+ events/sec)
- Real-time metrics
- JWT + HMAC auth
- Multi-tenant
- Docker deployment
- 100% tests passing

4/ Coming Q1 2026:
- Dashboard UI
- Client SDKs (JS, Python, iOS, Android)
- Funnel analytics
- User profiles

5/ Perfect for:
- Startups saving money
- Enterprises with compliance needs
- Developers wanting control
- Teams scaling beyond Segment

6/ Tech stack:
- FastAPI (async)
- SQLAlchemy 2.0
- PostgreSQL
- Redis
- 100% Python
- MIT License

7/ Try it:
📦 pip install nimbus-analytics
🐳 Docker Compose included
📚 Full docs
⭐ Star on GitHub

Link: https://github.com/bahagh/nimbus

8/ Looking for:
- Early adopters
- Feedback
- Contributors
- People to share with

RT if you've ever complained about Segment pricing! 😄
```

### Dev.to Article

Post on: https://dev.to/new

**Title**: "I Built an Open-Source Alternative to Segment (and It's 90% Cheaper)"

**Tags**: `opensource`, `python`, `fastapi`, `analytics`

**Body**: (Write a longer story about your journey, why you built it, tech decisions, etc.)

### LinkedIn Post

```
🚀 Excited to announce Nimbus v0.1.0-beta!

After months of development, I'm releasing an open-source alternative to Segment and Mixpanel.

💡 Why? Most companies pay $500-$2,000/month for basic event tracking. Nimbus gives you the same capabilities for ~$50/month (just infrastructure costs).

✅ What's ready:
- Production-grade API
- 10,000+ events/second
- Real-time metrics
- Enterprise security
- Docker deployment

🚧 Coming Q1 2026:
- Analytics dashboard
- Client SDKs
- Advanced features

Perfect for startups, enterprises with compliance needs, or anyone who wants to own their analytics data.

Stack: FastAPI, PostgreSQL, Redis
License: MIT (fully open source)

Check it out: https://github.com/bahagh/nimbus

Looking for feedback, early adopters, and contributors! 

#OpenSource #Python #Analytics #Startup
```

## 📊 Step 7: Track Your Success

Monitor these metrics:

### GitHub
- ⭐ Stars: https://github.com/bahagh/nimbus/stargazers
- 👁️ Watchers: Check "Insights" tab
- 🍴 Forks
- 🐛 Issues opened

### PyPI
- 📦 Downloads: https://pypistats.org/packages/nimbus-analytics
- Check after 24-48 hours

### Community
- Respond to GitHub issues quickly
- Thank people who star/fork
- Engage in discussions
- Welcome contributors

## 🎯 Success Milestones

### Week 1:
- [ ] 50 GitHub stars
- [ ] 100 PyPI downloads
- [ ] 5 issues opened
- [ ] Mentioned on Hacker News/Reddit

### Month 1:
- [ ] 200 GitHub stars
- [ ] 1,000 PyPI downloads
- [ ] 3 production deployments
- [ ] First contributor PR

### Month 3:
- [ ] 500 GitHub stars
- [ ] 5,000 PyPI downloads
- [ ] 10 contributors
- [ ] Dashboard v1 released

## 🆘 Troubleshooting

### "Name 'nimbus-analytics' is already taken"
Try alternative names:
- `nimbus-events`
- `nimbus-analytics-platform`
- `pynimbus`

### "Poetry not found"
Restart terminal after installing Poetry, or use full path:
```powershell
$env:APPDATA\Python\Scripts\poetry
```

### "Authentication failed"
- Regenerate API token
- Make sure you copied entire token (starts with `pypi-`)
- Check you're using correct repository (test vs production)

### "Package validation failed"
- Run `poetry check` to see errors
- Check README_PYPI.md exists
- Ensure LICENSE file is present

## 📞 Need Help?

- GitHub Issues: https://github.com/bahagh/nimbus/issues
- Email: baha.ghrissi@esprit.tn

---

**Ready to launch?** 🚀

```powershell
cd C:\Users\Asus\Desktop\opoplp\nimbus\apps\api
poetry build
poetry publish
```

Good luck! You're about to make analytics accessible to everyone! 🎉
