# Safe Ransomware Simulator (Educational Lab)

A deliberately limited, safety-scoped Python script that demonstrates
**file encryption, file renaming, ransom-note generation, activity logging,
and recovery** — the mechanical skeleton of ransomware — inside a single,
user-chosen directory.

This is a **teaching tool**. It is not malware. It cannot spread, cannot
persist, cannot phone home, and cannot destroy backups. See
[What this is NOT](#what-this-is-not) for the full list of deliberate
limitations.

---

## Table of contents

- [Purpose](#purpose)
- [What this is NOT](#what-this-is-not)
- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Safety model](#safety-model)
- [File layout](#file-layout)
- [Cryptography details](#cryptography-details)
- [Recovery](#recovery)
- [Known limitations](#known-limitations)
- [Lessons for defenders](#lessons-for-defenders)
- [Legal and ethical notice](#legal-and-ethical-notice)

---

## Purpose

This project exists to make the **mechanics** of ransomware-style file
encryption visible and hands-on in a controlled environment. It is intended for:

- Cybersecurity students learning how file encryption works
- Blue-teamers who want to see what encryption behavior looks like on disk
- Anyone curious about what a ransom note, a salt file, and a `.locked`
  extension actually are

The script does exactly one thing: it finds files in a directory you
specify, encrypts them with a real cipher, renames them with a `.locked`
extension, deletes the originals, drops a ransom note, and logs what it did.
Then it offers a recovery mode that reverses the process when given the
same password.

That's it. Everything that makes real ransomware dangerous is intentionally
absent.

---

## What this is NOT

This script deliberately does **not** include, and should **not** be extended
to include, any of the following:

| Real ransomware has | This script |
|---|---|
| Random per-victim keys | Password + salt (recoverable) |
| Asymmetric key wrapping (RSA/ECC) | Symmetric-only (Fernet) |
| Private key held on a C2 server | No network code at all |
| Persistence (registry, services, cron) | Runs once, exits |
| Lateral movement (SMB, RDP, WMI) | Single directory, single machine |
| Anti-VM / anti-debug / packing | Plain readable Python |
| Backup / shadow-copy destruction | Does not touch backups |
| Data exfiltration | No network code |
| C2, payment portal, extortion | A friendly text note |
| Self-propagation | Manual execution only |

If you are looking for a tool that does any of the above, **this is not it**,
and the author will not help you turn it into one. See
[Legal and ethical notice](#legal-and-ethical-notice).

---

## How it works

High-level flow:

```
┌─────────────────────────┐
│  User picks a target    │
│  directory (LAB_DIR)    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Generate random salt   │
│  Write salt to disk     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Derive key = Scrypt(   │
│    password + salt )    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  For each file found:   │
│    - read plaintext     │
│    - Fernet.encrypt()   │
│    - write .locked      │
│    - delete original    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Write ransom note      │
│  Log every action       │
└─────────────────────────┘
```

Recovery reverses it: same password + same salt → same key → decrypt each
`.locked` file → restore original name.

---

## Requirements

- Python 3.7+
- [`cryptography`](https://pypi.org/project/cryptography/) library

Install with:

```bash
pip install cryptography
```

---

## Installation

1. Save the script somewhere **outside** the folder you intend to encrypt.
   For example:

   ```bash
   mkdir -p ~/ransomware_lab
   mv ransomware.py ~/ransomware_lab/
   ```

2. Make it executable (optional):

   ```bash
   chmod +x ~/ransomware_lab/ransomware.py
   ```

3. **Do not** put the script inside the target directory. If it ends up
   there, the hardened `find_files()` will skip it, but the salt and log
   can still be at risk. Keep them separate.

---

## Configuration

Open the script and edit the paths at the top. The only one you *need* to
change is `LAB_DIRECTORY`.

```python
# Folder the script lives in (used for salt + log by default)
BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# >>> EDIT THIS: the folder whose files will be encrypted
LAB_DIRECTORY = os.path.expanduser("~/Desktop/ransomeware_test")

# Log file (kept outside the target folder)
LOG_FILE = os.path.join(BASE_DIRECTORY, "activity.log")

# Ransom note (created inside the target folder)
RANSOM_NOTE = os.path.join(LAB_DIRECTORY, "RANSOMWARE_SIMULATION.txt")

# Salt file (kept outside the target folder)
SALT_FILE = os.path.join(BASE_DIRECTORY, "lab.salt")
```

### Recommended hardening

Even though the script is scoped to `LAB_DIRECTORY`, it's worth making the
exclusions explicit so the script, salt, and log can never be encrypted
even if they end up inside the target:

```python
def find_files():
    files = []
    if not os.path.exists(LAB_DIRECTORY):
        return files

    script_path = os.path.abspath(__file__)
    salt_abs    = os.path.abspath(SALT_FILE)
    log_abs     = os.path.abspath(LOG_FILE)
    note_abs    = os.path.abspath(RANSOM_NOTE)

    for path in pathlib.Path(LAB_DIRECTORY).rglob("*"):
        if not path.is_file():
            continue

        filename = os.path.abspath(str(path))

        if filename in (script_path, salt_abs, log_abs, note_abs):
            continue
        if filename.endswith(".locked"):
            continue

        files.append(str(path))

    return files
```

### Recommended salt location

Put the salt somewhere fixed and outside the target, e.g.:

```python
SALT_FILE = os.path.expanduser("~/.ransomware_sim_salt")
```

---

## Usage

Run the script:

```bash
python3 ransomware.py
```

You'll see a menu:

```
============================================================
            SAFE RANSOMWARE SIMULATOR
                 EDUCATIONAL VM LAB
============================================================

[!] SAFETY RESTRICTION:
    Only files inside:
    /home/user/Desktop/ransomeware_test

    can be modified by this program.

------------------------------------------------------------

1. Simulate ransomware encryption
2. Recover encrypted files
3. Show lab status
4. Exit
```

### Encrypt

Choose `1`, enter a password. Every non-excluded file under
`LAB_DIRECTORY` is encrypted, renamed to `*.locked`, and the original is
deleted. A ransom note is written and every action is logged.

### Recover

Choose `2`, enter the **same password** you used to encrypt. Every
`.locked` file is decrypted, restored to its original name, and the `.locked`
copy is removed. The ransom note is deleted.

### Status

Choose `3` to see how many normal and locked files are currently in the
target directory, plus the paths to the log and lab directory.

---

## Safety model

The script's safety depends on four things:

1. **`LAB_DIRECTORY` is explicit.** Every file operation goes through
   `safety_check()`, which refuses any path not under `LAB_DIRECTORY`.
2. **The salt and log live outside the target.** If they don't, they get
   encrypted too — and without the salt, **recovery is impossible**.
3. **You have backups.** This is non-negotiable. Treat the target folder
   as expendable before you run encryption mode.
4. **You run it in a VM or a throwaway directory** the first time, and
   verify the full encrypt → recover cycle before pointing it at anything
   you care about.

### The salt is the single point of failure

The encryption key is `Scrypt(password + salt)`. If the salt is lost or
encrypted, **the files cannot be recovered** — not by you, not by the
author, not by anyone. This is by design: it's the same property that makes
real ransomware unrecoverable without the attacker's key.

Before running encryption mode, make sure the salt file is **outside**
`LAB_DIRECTORY` and **backed up**.

---

## File layout

After a typical run, you'll have:

```
~/ransomware_lab/                  # where the script lives
├── ransomware.py                  # this script
├── activity.log                   # append-only log of every action
└── lab.salt                       # salt used to derive the key

~/Desktop/ransomeware_test/        # the target folder
├── RANSOMWARE_SIMULATION.txt      # ransom note
├── document.pdf.locked            # encrypted file
├── photo.jpg.locked               # encrypted file
└── notes.txt.locked               # encrypted file
```

After recovery:

```
~/Desktop/ransomeware_test/
├── document.pdf
├── photo.jpg
└── notes.txt
```

The `.locked` files are gone, the ransom note is gone, and the log records
the decryption.

---

## Cryptography details

| Component | Choice | Notes |
|---|---|---|
| Cipher | Fernet | AES-128-CBC + HMAC-SHA256, authenticated |
| Key derivation | Scrypt | `n=2**14, r=8, p=1`, 32-byte output |
| Salt | 16 random bytes | `os.urandom(16)` |
| Key encoding | `base64.urlsafe_b64encode` | Fernet-compatible |

**Why Fernet?** It's a high-level, misuse-resistant recipe from the
`cryptography` library. It handles IV generation, padding, and
authentication for you, so the demo doesn't accidentally teach bad crypto.

**Why Scrypt?** It's a memory-hard KDF, which means brute-forcing the
password is expensive. Real ransomware usually skips the password entirely
and uses a random key wrapped with the attacker's public key — see
[What this is NOT](#what-this-is-not).

**What "authenticated" means here:** If a `.locked` file is modified or
decrypted with the wrong key, `Fernet.decrypt()` raises `InvalidToken`
instead of returning garbage. The script catches this and reports
"incorrect password/key" rather than writing corrupted output.

---

## Recovery

Recovery requires **three things**, all of which must match:

1. The `.locked` files (obviously)
2. The **same password** used at encryption time
3. The **same `lab.salt` file** written at encryption time

If any of the three is missing, recovery is impossible. If you've lost the
salt, check:

```bash
find ~ -name "lab.salt*" 2>/dev/null
```

If you find `lab.salt.locked` instead of `lab.salt`, the salt was encrypted
along with everything else — and you're in the situation described in
[The salt is the single point of failure](#the-salt-is-the-single-point-of-failure).

---

## Known limitations

These are deliberate, not bugs:

- **Single-threaded.** Encrypts one file at a time; slow on large folders.
- **Reads whole files into memory.** Will fail on very large files.
- **No resume.** If interrupted, some files will be `.locked` and some not.
- **No symlink handling.** Follows symlinks by default; can be surprising.
- **No permission handling.** Fails on files it can't read.
- **No filename encryption.** Only contents are encrypted; names are visible.
- **No compression.** Output is slightly larger than input.
- **No key rotation.** One key per run.
- **Salt is on disk in plaintext.** Required for recovery; also the weakness.

Every one of these is a difference from real ransomware, and every one is
intentional. See [What this is NOT](#what-this-is-not).

---

## Lessons for defenders

If you're using this to learn blue-team skills, watch for these behaviors
while the script runs — they're the same signals real ransomware produces:

- **Mass file rename** — many files getting a new extension in a short window
- **High-entropy writes** — new files that look random, not like documents
- **Original deletion** — files disappearing as `.locked` files appear
- **Ransom note creation** — a new file with a suspicious name in the target
- **Rapid file I/O** — a spike in reads followed by writes
- **Salt file creation** — a small binary file appearing next to the script

Real ransomware adds *more* signals on top (shadow copy deletion, C2
beaconing, credential access, lateral movement). If you want to practice
detecting those, look at:

- **Sysmon** (Windows) or **auditd** (Linux) for file and process telemetry
- **Atomic Red Team** for safe, repeatable technique tests
- **MITRE ATT&CK T1486** (Data Encrypted for Impact) for the technique map

The defender side is where the real learning is — and it's legal,
valuable, and hireable.

---

## Legal and ethical notice

This script is provided for **educational use in controlled environments
only**. By using it, you agree that:

- You will only run it against files you own or have explicit permission
  to modify.
- You will only run it inside a virtual machine or an isolated lab
  environment you control.
- You have working backups of every file in the target directory.
- You will not modify it to add persistence, propagation, exfiltration,
  C2, anti-analysis, or any other capability that would make it a real
  payload.
- You will not use it to harm, threaten, or extort anyone.

Using ransomware against systems you do not own is a serious crime in
almost every jurisdiction. "It was just a test" is not a defense.

The author provides this code **as-is**, with no warranty, and accepts no
liability for misuse, data loss, or legal consequences.

---

## Further reading

- [MITRE ATT&CK — T1486: Data Encrypted for Impact](https://attack.mitre.org/techniques/T1486/)
- [cryptography.io — Fernet documentation](https://cryptography.io/en/latest/fernet/)
- [cryptography.io — Scrypt documentation](https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/#scrypt)
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) — safe,
  repeatable technique tests for defenders
- *Ransomware: Defending Against Digital Extortion* — O'Reilly
