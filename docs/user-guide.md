# User Guide

## Product Scope

Arr Helper UI has two related tools:

- Sonarr UI Helper: a Windows desktop app for browsing and managing Sonarr series, seasons, and episodes.
- Media Quality Checker: a source-install CLI for checking Sonarr/Radarr files for required English audio and subtitle streams.

The first portable Windows package starts the Sonarr UI Helper. The media checker is available when running from a source or development install.

## Install and First Run

1. Install Python 3.13 or use the portable release package when available.
2. Install FFmpeg so `ffmpeg.exe` and `ffprobe.exe` are available in `PATH`.
3. For a source install, run:

```bat
python scripts\windows\setup_env.py
```

4. Start the GUI:

```bat
pyw scripts\windows\run_app_gui.pyw
```

Use `python scripts\windows\run_app.py` when you want a console window for diagnostics.

## Configure Sonarr and Radarr

The app needs API access to Sonarr, and the media checker can also use Radarr.

Prepare:

- Sonarr base URL, including `http://` or `https://`
- Sonarr API key from Sonarr settings
- optional Radarr base URL and API key
- a working FFmpeg/ffprobe installation

Keep destructive checker runs in dry-run mode until the reported actions look correct.

## Daily Sonarr UI Workflow

1. Start the GUI.
2. Confirm the configured Sonarr instance loads.
3. Review the series, season, and episode tree.
4. Use metadata columns to spot missing or suspicious media details.
5. Toggle monitored state only after confirming the selected row.
6. Use manual search for one series, season, or episode at a time.
7. Use delete actions carefully; prefer reviewing the selected path before removal.

## Media Quality Checker Workflow

Run the checker from a source/development install:

```bat
python -m arr_helper.media_checker.app
```

or, after installing the package:

```bat
media-quality-checker
```

Recommended first pass:

1. Set `dry_run = true`.
2. Run the checker and review the report.
3. Fix API URLs, keys, language requirements, and paths until the report is sane.
4. Enable `interactive = true` if you want to review alternatives before actions are taken.
5. Only set `dry_run = false` after you trust the configuration.

## Common Tasks

### Add a Show

Use the add-show workflow from the GUI, then confirm the root folder and quality profile before sending the request to Sonarr.

### Run Manual Search

Select a series, season, or episode and start manual search. Filter by title, quality, or indexer, then double-click the chosen release.

### Open a Local Path

Use the open-path action on a selected row to inspect the local file or folder in Windows Explorer before taking destructive action.

### Schedule the Checker

After validating dry-run output, schedule the CLI with Windows Task Scheduler. Keep logs enabled and review the first unattended runs.

## Settings and Data

User configuration is stored through the app settings system. Cache files store ffprobe metadata and checker decisions so repeated runs are faster and previously accepted files are not reprocessed unnecessarily.

When troubleshooting, clear only the specific cache that matches the problem. Avoid deleting all state until you have exported or noted the current configuration.

## Safety Notes

- The media checker can delete files when `dry_run = false`.
- Sonarr search actions can trigger downloads.
- GUI delete actions can remove files from disk.
- Review paths and selected rows before using delete or unmonitor actions.
- Keep a backup or recovery path for libraries you are still validating.

## Troubleshooting Checklist

- If Sonarr does not load, verify URL, API key, and network reachability.
- If media metadata is blank, verify `ffprobe.exe` is installed and visible in `PATH`.
- If checker decisions look wrong, return to `dry_run = true` and review language rules.
- If manual search has no results, test the same query in Sonarr and confirm indexers are working.
- If settings appear stale, restart the app after saving configuration.

## Getting Help

When filing an issue, include:

- app version
- Windows version
- whether you used the portable package or source install
- sanitized Sonarr/Radarr URL shape, without API keys
- the exact workflow that failed
- relevant logs or console output
