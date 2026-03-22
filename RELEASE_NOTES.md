# Release Notes Template

Use this template for creating release notes. Copy and fill in the appropriate sections for each release.

---

## [VERSION] - YYYY-MM-DD

### Download

- [Release Assets](https://github.com/launchapp-dev/ao-skill-devops/releases/tag/vVERSION)
- [Installation Guide](../README.md#installation)

---

### Breaking Changes

> ⚠️ **Important**: Review these changes carefully before upgrading.

- [Breaking change description with migration guide]

---

### Added

Features added in this release.

#### New Generators

| Generator | Description |
|-----------|-------------|
| [Generator name] | [Brief description] |

#### New Capabilities

| Capability | Description |
|------------|-------------|
| [Capability] | [Description] |

#### Enhancements

- [Enhancement description]
- [Another enhancement]

---

### Changed

Changes to existing functionality.

#### Generator Updates

| Generator | Change | Migration |
|-----------|--------|-----------|
| [Generator] | [What changed] | [How to migrate] |

#### Configuration Changes

- [Configuration change description]

#### Deprecations

> ⚠️ **Deprecation Notice**: These features will be removed in a future release.

| Feature | Deprecated | Removal | Replacement |
|---------|------------|---------|-------------|
| [Feature] | v[X.Y] | v[X.Y] | [Replacement] |

---

### Fixed

Bug fixes and corrections.

| Issue | Description | PR |
|-------|-------------|-----|
| [#XXX](https://github.com/launchapp-dev/ao-skill-devops/issues/XXX) | [Issue description] | [#YYY](https://github.com/launchapp-dev/ao-skill-devops/pull/YYY) |
| [#XXX](https://github.com/launchapp-dev/ao-skill-devops/issues/XXX) | [Issue description] | [#YYY](https://github.com/launchapp-dev/ao-skill-devops/pull/YYY) |

---

### Security

Security-related fixes and updates.

| CVE | Description | Severity | Fix |
|-----|-------------|----------|-----|
| [CVE-XXXX-XXXXX](link) | [Description] | [Critical/High/Medium/Low] | [Fix description] |

---

### Removed

Features removed in this release.

| Feature | Description | Migration |
|---------|-------------|-----------|
| [Feature] | [Description] | [Migration path] |

---

### Documentation

Documentation updates and additions.

- [Documentation update]
- [Another update]

---

### Dependencies

Updated dependencies.

| Package | Version | Type | Notes |
|---------|---------|------|-------|
| [package] | [old] → [new] | [dev/prod] | [Notes] |

---

### Contributors

Thank you to our contributors for this release!

<a href="https://github.com/launchapp-dev/ao-skill-devops/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=launchapp-dev/ao-skill-devops" />
</a>

---

### Installation

#### AO CLI

```bash
# Update to latest version
npm update -g @launchapp-dev/ao-cli

# Verify installation
ao --version
```

#### Node.js SDK

```bash
# npm
npm update @launchapp-dev/ao-skill-devops

# yarn
yarn upgrade @launchapp-dev/ao-skill-devops

# pnpm
pnpm update @launchapp-dev/ao-skill-devops
```

#### Python SDK

```bash
pip install --upgrade ao-skill-devops
# or
poetry update ao-skill-devops
```

#### Docker

```bash
docker pull launchappdev/ao-skill-devops:vVERSION
```

---

### Upgrade Guide

#### From v[X.Y] to v[X.Y]

1. **Backup your configuration**
   ```bash
   # Backup your pack.toml
   cp pack.toml pack.toml.backup
   ```

2. **Update dependencies**
   ```bash
   npm update @launchapp-dev/ao-skill-devops
   ```

3. **Review breaking changes**
   - [Specific breaking change and migration]

4. **Test your configurations**
   ```bash
   ao devops validate --all
   ```

5. **Report issues**
   - [Link to issue tracker]

---

### Coming Next

Preview of what's coming in future releases.

- [Planned feature]
- [Planned enhancement]

---

## Previous Releases

- [v0.1.0](./CHANGELOG/v0.1.0.md) - Initial release
- [v0.0.9](./CHANGELOG/v0.0.9.md) - Beta preview

---

## Contact & Support

- **GitHub Issues**: [Bug reports and feature requests](https://github.com/launchapp-dev/ao-skill-devops/issues)
- **GitHub Discussions**: [Questions and community support](https://github.com/launchapp-dev/ao-skill-devops/discussions)
- **Documentation**: [Latest docs](../README.md)

---

*Generated with [release-drafter](https://github.com/release-drafter/release-drafter)*
