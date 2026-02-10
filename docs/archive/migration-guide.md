# Documentation Migration Guide

This guide helps you find information that was previously in scattered status reports.

---

## 📋 Old Files → New Documentation Mapping

### Status Reports → PROJECT_STATUS.md

All current status information is now in **[PROJECT_STATUS.md](./PROJECT_STATUS.md)**

| Old File | Content | New Location |
|----------|---------|--------------|
| `CURRENT_STATUS_20260123.md` | Current system status | `docs/PROJECT_STATUS.md` |
| `FINAL_STATUS_20260123.md` | Final status after fixes | `docs/PROJECT_STATUS.md` |
| `project_status_20260122.md` | R2 migration status | `docs/CHANGELOG.md` (v2.0) |
| `project_status_20260121.md` | Development progress | `docs/CHANGELOG.md` (v1.x) |
| `project_status_20260120.md` | Early development | `docs/CHANGELOG.md` (v1.x) |
| `project_status_20260118.md` | Initial setup | `docs/CHANGELOG.md` (v1.x) |

### Feature Reports → CHANGELOG.md

All completed features and changes are in **[CHANGELOG.md](./CHANGELOG.md)**

| Old File | Content | New Location |
|----------|---------|--------------|
| `COMPLETED_TASKS_20260123.md` | Completed tasks list | `docs/CHANGELOG.md` (v2.3+) |
| `FEATURES_IMPLEMENTED_20260123.md` | New features | `docs/CHANGELOG.md` (v2.3+ Added) |
| `IMPROVEMENTS_20260123.md` | System improvements | `docs/CHANGELOG.md` (v2.3+ Improved) |
| `SUCCESS_REPORT_20260123.md` | Fix success report | `docs/CHANGELOG.md` (v2.3+ Fixed) |

### Bug Reports → CHANGELOG.md + TROUBLESHOOTING.md

Bug fixes are documented in **[CHANGELOG.md](./CHANGELOG.md)**, solutions in **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)**

| Old File | Content | New Location |
|----------|---------|--------------|
| `BUGFIXES_20260123.md` | Bug fixes | `docs/CHANGELOG.md` (v2.3+ Fixed) |
| `HIDDEN_FILES_FIX_FINAL.md` | Hidden files solution | `docs/TROUBLESHOOTING.md` (#2) |
| `R2_MANIFEST_FIX.md` | R2 manifest fix | `docs/TROUBLESHOOTING.md` (#1) |
| `MACOS_HIDDEN_FILES_SOLUTION.md` | macOS hidden files | `docs/TROUBLESHOOTING.md` (#2) |

### Technical Reports → ARCHITECTURE.md

System architecture and design are in **[ARCHITECTURE.md](./ARCHITECTURE.md)**

| Old File | Content | New Location |
|----------|---------|--------------|
| `20260123_PROJECT_COMPACT.md` | Project overview | `docs/ARCHITECTURE.md` |
| `20260123- Live Event Photography - 開發進度 Compact-Perplexity.md` | Development progress | `docs/ARCHITECTURE.md` |

### Usage Guides → TROUBLESHOOTING.md

Operational guides and fixes are in **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)**

| Old File | Content | New Location |
|----------|---------|--------------|
| `CLEANUP_USAGE.md` | Cleanup tool usage | `docs/TROUBLESHOOTING.md` (Maintenance Tools) |
| `PATH_VERIFICATION.md` | Path verification | `docs/TROUBLESHOOTING.md` (#4) |
| `RESTART_INSTRUCTIONS.md` | Restart instructions | `docs/TROUBLESHOOTING.md` (#4) |

### Test Reports → CHANGELOG.md

Test results are documented in **[CHANGELOG.md](./CHANGELOG.md)**

| Old File | Content | New Location |
|----------|---------|--------------|
| `TEST_RESULTS_20260123.md` | Test results | `docs/CHANGELOG.md` (v2.3+) |

---

## 🔍 Quick Reference: Where to Find Information

### I need to know...

**...current system status**
→ `docs/PROJECT_STATUS.md`

**...what changed in version X**
→ `docs/CHANGELOG.md`

**...how the system works**
→ `docs/ARCHITECTURE.md`

**...how to fix problem X**
→ `docs/TROUBLESHOOTING.md`

**...how to use the system**
→ `docs/USER_GUIDE.md` (to be created)

**...how to set up from scratch**
→ `docs/SETUP_GUIDE.md` (to be created)

**...how to deploy**
→ `docs/DEPLOYMENT_GUIDE.md` (to be created)

**...API endpoints**
→ `docs/API_REFERENCE.md` (to be created)

**...future plans**
→ `docs/DEVELOPMENT_ROADMAP.md` (existing, to be moved to docs/)

---

## 📦 What Happened to Old Files?

### Option 1: Keep as Archive (Recommended)
Old files remain in project root for historical reference but are no longer the primary documentation.

### Option 2: Move to Archive Folder
```bash
mkdir -p archive/2026-01-23
mv *_20260123.md archive/2026-01-23/
mv project_status_*.md archive/2026-01-23/
```

### Option 3: Delete After Verification
```bash
# Only after confirming all information is migrated
rm *_20260123.md
rm project_status_*.md
rm 20260123*.md
```

---

## 🎯 Benefits of New Structure

### Before (Scattered)
```
project_root/
├── CURRENT_STATUS_20260123.md
├── FINAL_STATUS_20260123.md
├── SUCCESS_REPORT_20260123.md
├── COMPLETED_TASKS_20260123.md
├── FEATURES_IMPLEMENTED_20260123.md
├── BUGFIXES_20260123.md
├── IMPROVEMENTS_20260123.md
├── TEST_RESULTS_20260123.md
├── project_status_20260122.md
├── project_status_20260121.md
├── project_status_20260120.md
├── project_status_20260118.md
├── 20260123_PROJECT_COMPACT.md
├── 20260123- Live Event Photography - 開發進度 Compact-Perplexity.md
├── HIDDEN_FILES_FIX_FINAL.md
├── R2_MANIFEST_FIX.md
├── MACOS_HIDDEN_FILES_SOLUTION.md
├── CLEANUP_USAGE.md
├── PATH_VERIFICATION.md
└── RESTART_INSTRUCTIONS.md
```

### After (Organized)
```
project_root/
└── docs/
    ├── README.md                    # Documentation index
    ├── PROJECT_STATUS.md            # Current status
    ├── CHANGELOG.md                 # Version history
    ├── ARCHITECTURE.md              # System design
    ├── TROUBLESHOOTING.md           # Problem solutions
    ├── USER_GUIDE.md                # Usage instructions
    ├── SETUP_GUIDE.md               # Setup instructions
    ├── DEPLOYMENT_GUIDE.md          # Deployment guide
    ├── API_REFERENCE.md             # API documentation
    ├── DEVELOPMENT_ROADMAP.md       # Future plans
    └── MIGRATION_GUIDE.md           # This file
```

### Advantages

1. **Single Source of Truth**: Each topic has one definitive document
2. **Easy Navigation**: Logical folder structure
3. **No Duplication**: Information appears once, not scattered
4. **Version Control**: Clear history in CHANGELOG.md
5. **Searchable**: Organized by topic, not by date
6. **Maintainable**: Update one file instead of many
7. **Onboarding**: New team members find info easily
8. **AI-Friendly**: LLMs can quickly understand structure

---

## 🔄 Migration Checklist

If you're migrating old documentation:

- [x] Create `docs/` folder
- [x] Create `docs/README.md` (index)
- [x] Create `docs/PROJECT_STATUS.md` (current status)
- [x] Create `docs/CHANGELOG.md` (version history)
- [x] Create `docs/ARCHITECTURE.md` (system design)
- [x] Create `docs/TROUBLESHOOTING.md` (solutions)
- [x] Create `docs/MIGRATION_GUIDE.md` (this file)
- [ ] Create `docs/USER_GUIDE.md` (usage)
- [ ] Create `docs/SETUP_GUIDE.md` (setup)
- [ ] Create `docs/DEPLOYMENT_GUIDE.md` (deployment)
- [ ] Create `docs/API_REFERENCE.md` (API docs)
- [ ] Move `DEVELOPMENT_ROADMAP.md` to `docs/`
- [ ] Move `OPERATION_MANUAL.md` content to `docs/USER_GUIDE.md`
- [ ] Move `R2_SETUP_GUIDE.md` to `docs/`
- [ ] Move `DEPLOYMENT_GUIDE.md` to `docs/`
- [ ] Move `MANUAL_HTML_SETTINGS_GUIDE.md` to `docs/`
- [ ] Archive or delete old status files
- [ ] Update README.md to point to `docs/`

---

## 📝 Naming Convention

### New Standard
- **UPPERCASE_WITH_UNDERSCORES.md** - Main documentation
- **lowercase-with-dashes.md** - Supporting files
- **No date prefixes** - Use git history for dates

### Examples
- ✅ `PROJECT_STATUS.md`
- ✅ `CHANGELOG.md`
- ✅ `TROUBLESHOOTING.md`
- ❌ `project_status_20260123.md`
- ❌ `CURRENT_STATUS_20260123.md`
- ❌ `20260123_PROJECT_COMPACT.md`

---

## 🎓 Best Practices

### When to Update Documentation

1. **PROJECT_STATUS.md**: When system status changes
2. **CHANGELOG.md**: When releasing a new version
3. **ARCHITECTURE.md**: When design changes
4. **TROUBLESHOOTING.md**: When new issues are discovered
5. **USER_GUIDE.md**: When workflows change
6. **API_REFERENCE.md**: When API changes

### How to Update

1. **Single Update**: Edit the relevant section
2. **Add Date**: Update "Last Updated" at top
3. **Commit**: `git commit -m "docs: update PROJECT_STATUS"`
4. **No New Files**: Don't create `PROJECT_STATUS_20260201.md`

### Version Control

- Git history provides complete change tracking
- No need for dated filenames
- Use `git log docs/PROJECT_STATUS.md` to see history
- Use `git diff` to see what changed

---

## 🚀 Next Steps

1. **Review new docs**: Read through `docs/` folder
2. **Verify completeness**: Check all old info is migrated
3. **Archive old files**: Move to `archive/` or delete
4. **Update links**: Fix any references to old files
5. **Create remaining docs**: USER_GUIDE, SETUP_GUIDE, etc.
6. **Update README**: Point to new documentation

---

**Questions? See [docs/README.md](./README.md) for documentation index.**
