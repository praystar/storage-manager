# Contributing to Storage Manager

Thank you for your interest in contributing to **Storage Manager**.  
This project focuses on proactive disk space management to prevent system instability, especially on Linux-based systems. Contributions of all kinds are welcome, including code, documentation, testing, and feature ideas.

---

## How to Contribute

1. **Fork the repository**  
   Use the GitHub *Fork* button to create your own copy of the repository.

2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/project-name.git
   cd project-name



3. **Create a feature branch**
Always work on a new branch.

git checkout -b feature/short-description


Examples:

feature/live-download-counter

fix/disk-space-calculation

docs/setup-guide

4. **Make your changes**

Follow the existing code structure and style

Keep changes focused and readable

Write clear and descriptive commit messages

5.**Test thoroughly**
Before submitting, ensure:

Disk space calculations are accurate

Low-disk scenarios behave correctly

No existing features are broken

6.**Submit a pull request**

Push your branch to your fork

Open a pull request against the main branch

Clearly describe:

What problem you solved

How you tested it

Any known limitations


## Areas for Contribution

### Core Features
- Multiple download queue support
- Live download counter showing active downloads
- Real-time disk usage updates during downloads
- Predictive warnings for queued downloads
- Emergency blocking when disk space becomes critical

### Cross-Platform Compatibility
- Windows support (NTFS behavior)
- macOS support (APFS behavior)
- Platform-specific disk reservation handling

### Configuration and Settings
- Configurable safe disk buffer
- Per-partition disk monitoring
- Notification and warning preferences
- Import and export of settings

### System Awareness
- Filesystem detection (ext4, btrfs, xfs, NTFS, APFS)
- OS-reserved space detection
- Partition-level monitoring instead of only root

### Monitoring and Health
- Server and service health monitoring
- Disk I/O pressure detection
- Background service status indicator

### Error Handling and Stability
- Clear error messages for permission issues
- Graceful handling when disk statistics are unavailable
- Recovery handling after disk cleanup

### Testing
- Unit tests for disk calculation logic
- Integration tests for native messaging
- Edge-case testing for nearly full disks

### Documentation
- Installation and setup guide
- Architecture overview
- FAQ explaining:
  - GB vs GiB
  - Linux reserved disk space
  - Causes of system instability on low disk

### UI and UX Improvements
- Disk usage visualization
- Color-coded danger indicators
- Clear and human-readable warnings
- Accessibility improvements

### Security and Privacy
- Minimal permission usage
- Secure native messaging communication
- No collection of personal file data

---

## Coding Guidelines

- Follow consistent naming and formatting
- Avoid hard-coded paths and magic numbers
- Prefer clarity over clever implementations
- Comment complex or non-obvious logic

---

## Reporting Bugs and Feature Requests

Please use GitHub Issues and include:
- Operating system and filesystem type
- Steps to reproduce the issue
- Expected and actual behavior
- Logs or screenshots if available

---

## Code of Conduct

All contributors are expected to be respectful and constructive.
Harassment, discrimination, or hostile behavior will not be tolerated.

---

## Final Note

Even small contributions such as documentation fixes, improved warnings,
or better logs are valuable. If you are unsure where to start,
feel free to open an issue for guidance.
