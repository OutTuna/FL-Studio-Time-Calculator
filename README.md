# FL-Studio-Time-Calculator
FL Studio keeps track of how many active hours you spend on each project, but not your total time in the program. With this application, you can finally see your total hours without having to open up all your files and adding everything together! Idle time is still not accounted for, so the time this program displays to you only shows your active working hours. You may also select dates for the program to search between, say, if you wanted to see how many hours you spent on FL in a given month (or whatever time frame you like)!

![alt text](https://i.imgur.com/OZkqrj4.png)

This program was created out of the primal, human urge to keep track of and gawk at the amount of time we all spend on FL Studio. For better or for worse, we will never stop producing!

This program does not modify your save files in any way, its only allowed to read file contents.

Support us at https://ko-fi.com/flhourcounterguys

## Local ZIP support

Import a folder to scan it and its subfolders for `.flp` and `.zip` files
(case-insensitive). Every FLP inside a ZIP appears in the list/tree with its
hours and creation date. Samples are not extracted and source files are not
modified. Archives with no FLP or unreadable archives produce an import warning;
projects that cannot be parsed appear in red with an error tooltip and do not
contribute to totals. Individual FLPs larger than 256 MiB are rejected.

Multiple versions of a project are counted separately, including copies in both
ZIP and FLP form. Autosave/overwritten files are skipped, as in the original app.
Nested ZIPs are not scanned. Time is FL Studio's recorded active project time,
not audio duration or time inferred from file dates.

Run locally with Python 3.11 or newer:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python __main__.py
```

Run checks: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -s tests`.

## Windows EXE builds

GitHub Actions builds a Windows x64 EXE on every push to `main` and every pull
request targeting `main`. You can also start it manually from **Actions → Build and Release
Windows EXE → Run workflow**. Tests must pass before the EXE is built.

Successful builds of `main` automatically publish a new GitHub Release with the
EXE attached and mark it as Latest. Download `FL-Studio-Time-Calculator.exe`
from [the latest release](https://github.com/OutTuna/FL-Studio-Time-Calculator/releases/latest)
and launch it. Python does not need to be installed on the Windows computer.
Previous releases remain available. Pull request builds only upload artifacts
and do not publish releases. Artifacts are retained for 30 days.

Project statistics use a metadata-only reader. It supports the extended events
observed in FL Studio 25.2.4, 25.2.5, and 26.1 and skips plugin, playlist, and text payloads without
decoding them. Unsupported or missing time metadata still produces an error.

Legacy FLP event framing is retained for FL 19, 20, 21, 24, and 25.1,
with regression checks including FL 20.6 (2019-era projects). FL Studio 19
version strings are also covered. These checks use generated FLP fixtures;
real older projects still need validation. Recorded time must exist in the FLP;
file dates and sample duration are not used to invent missing work hours.
