#!/usr/bin/env python3

import os
import pathlib
import base64
import getpass
import logging
import cryptography

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


# ============================================================
# PROJECT DIRECTORIES
# ============================================================

# Directory where this Python script is located
BASE_DIRECTORY = os.path.dirname(
    os.path.abspath(__file__)
)

# ONLY this directory is allowed to contain files that
# the simulator can encrypt/decrypt.
# >>> CHANGED: now points to ~/Desktop/ransomeware_test
LAB_DIRECTORY = os.path.expanduser(
    "~/Pictures/Formal"
)

# Log file
LOG_FILE = os.path.join(
    BASE_DIRECTORY,
    "activity.log"
)

# Ransom note
RANSOM_NOTE = os.path.join(
    LAB_DIRECTORY,
    "RANSOMWARE_SIMULATION.txt"
)

# Salt file
SALT_FILE = os.path.join(
    BASE_DIRECTORY,
    "lab.salt"
)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ============================================================
# SAFETY CHECK
# ============================================================

def safety_check(path):
    """
    Make sure the simulator can only access files
    inside the dedicated lab directory.
    """

    target = os.path.abspath(path)
    lab = os.path.abspath(LAB_DIRECTORY)

    # Target must be inside LAB_DIRECTORY
    if not target.startswith(lab + os.sep):
        raise PermissionError(
            "\n[BLOCKED] Safety check failed!\n"
            "The target is outside the allowed laboratory directory.\n"
            f"Allowed directory: {lab}\n"
        )


# ============================================================
# KEY DERIVATION
# ============================================================

def generate_salt():
    """
    Generate a random 16-byte salt.
    """

    return os.urandom(16)


def derive_key(password, salt):
    """
    Derive a Fernet-compatible encryption key
    from the password and salt using Scrypt.
    """

    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1
    )

    derived_key = kdf.derive(
        password.encode()
    )

    return base64.urlsafe_b64encode(
        derived_key
    )


# ============================================================
# ENCRYPTION
# ============================================================

def encrypt_file(filename, key):
    """
    Encrypt one file inside the lab directory.
    """

    safety_check(filename)

    # Do not encrypt the ransom note
    if os.path.abspath(filename) == os.path.abspath(RANSOM_NOTE):
        return

    # Do not encrypt an already locked file
    if filename.endswith(".locked"):
        return

    encrypted_filename = filename + ".locked"

    print(f"[*] Encrypting: {filename}")

    with open(filename, "rb") as file:
        file_data = file.read()

    fernet = Fernet(key)

    encrypted_data = fernet.encrypt(
        file_data
    )

    # Write encrypted copy
    with open(encrypted_filename, "wb") as file:
        file.write(encrypted_data)

    # Remove original file
    os.remove(filename)

    logging.info(
        "ENCRYPTED: %s -> %s",
        filename,
        encrypted_filename
    )

    print(
        f"[+] Encrypted: "
        f"{os.path.basename(filename)}"
    )


# ============================================================
# DECRYPTION
# ============================================================

def decrypt_file(filename, key):
    """
    Decrypt one .locked file inside the lab directory.
    """

    safety_check(filename)

    if not filename.endswith(".locked"):
        return

    print(f"[*] Decrypting: {filename}")

    with open(filename, "rb") as file:
        encrypted_data = file.read()

    fernet = Fernet(key)

    try:

        decrypted_data = fernet.decrypt(
            encrypted_data
        )

    except cryptography.fernet.InvalidToken:

        print(
            f"[!] Incorrect password/key: "
            f"{os.path.basename(filename)}"
        )

        logging.warning(
            "FAILED DECRYPTION: %s",
            filename
        )

        return

    # Remove .locked
    original_filename = filename[:-7]

    safety_check(original_filename)

    with open(original_filename, "wb") as file:
        file.write(decrypted_data)

    os.remove(filename)

    logging.info(
        "DECRYPTED: %s -> %s",
        filename,
        original_filename
    )

    print(
        f"[+] Restored: "
        f"{os.path.basename(original_filename)}"
    )


# ============================================================
# FIND NORMAL FILES
# ============================================================

def find_files():
    """
    Find files inside the lab directory that can be encrypted.
    """

    files = []

    if not os.path.exists(LAB_DIRECTORY):
        return files

    for path in pathlib.Path(
        LAB_DIRECTORY
    ).rglob("*"):

        if not path.is_file():
            continue

        filename = str(path)

        # Skip ransom note
        if filename == RANSOM_NOTE:
            continue

        # Skip already encrypted files
        if filename.endswith(".locked"):
            continue

        files.append(filename)

    return files


# ============================================================
# FIND LOCKED FILES
# ============================================================

def find_locked_files():
    """
    Find .locked files inside the lab directory.
    """

    files = []

    if not os.path.exists(LAB_DIRECTORY):
        return files

    for path in pathlib.Path(
        LAB_DIRECTORY
    ).rglob("*.locked"):

        if path.is_file():
            files.append(str(path))

    return files


# ============================================================
# CREATE RANSOM NOTE
# ============================================================

def create_ransom_note():

    note = """
============================================================
          RANSOMWARE SIMULATION
          EDUCATIONAL CYBERSECURITY LAB
============================================================

THIS IS A SIMULATION ONLY.

The files inside this laboratory directory have been
encrypted as part of a controlled cybersecurity experiment.

No files outside the laboratory directory should be affected.

This simulation demonstrates:

    - File discovery
    - File encryption
    - File renaming
    - Ransomware-style notification
    - Activity logging
    - File recovery

To recover the files, run the program again and select
RECOVERY MODE using the original simulation password.

============================================================
                 END OF SIMULATION
============================================================
"""

    with open(RANSOM_NOTE, "w") as file:
        file.write(note)

    logging.info(
        "RANSOM NOTE CREATED: %s",
        RANSOM_NOTE
    )

    print(
        f"\n[+] Simulation ransom note created."
    )


# ============================================================
# ENCRYPTION SIMULATION
# ============================================================

def simulate_encryption(password):

    print("\n")
    print("=" * 60)
    print("             RANSOMWARE SIMULATION")
    print("=" * 60)

    print(
        f"\n[*] Protected directory:"
        f"\n    {LAB_DIRECTORY}\n"
    )

    # Make sure lab directory exists
    if not os.path.exists(LAB_DIRECTORY):

        print(
            "[!] Lab directory does not exist."
        )

        print(
            f"\n[*] Creating:"
            f"\n    {LAB_DIRECTORY}"
        )

        os.makedirs(
            LAB_DIRECTORY,
            exist_ok=True
        )

        print(
            "\n[!] No files are currently available."
        )

        print(
            "    Put some dummy files inside "
            "~/Desktop/ransomeware_test/ and run again."
        )

        return

    files = find_files()

    if not files:

        print(
            "[!] No files found to encrypt."
        )

        return

    # Generate a new salt
    salt = generate_salt()

    # Save salt only inside the project directory
    with open(SALT_FILE, "wb") as file:
        file.write(salt)

    logging.info(
        "NEW SIMULATION STARTED"
    )

    logging.info(
        "Files discovered: %d",
        len(files)
    )

    # Derive encryption key
    key = derive_key(
        password,
        salt
    )

    print(
        f"[*] Files discovered: {len(files)}\n"
    )

    # Encrypt each file
    for filename in files:

        try:

            encrypt_file(
                filename,
                key
            )

        except Exception as error:

            print(
                f"[!] Error encrypting "
                f"{filename}: {error}"
            )

            logging.error(
                "ERROR ENCRYPTING %s: %s",
                filename,
                error
            )

    # Create simulated ransom note
    create_ransom_note()

    print("\n" + "=" * 60)
    print("             SIMULATION COMPLETED")
    print("=" * 60)

    print(
        f"\n[+] Files processed: {len(files)}"
    )

    print(
        f"[+] Log file:"
        f"\n    {LOG_FILE}"
    )

    print(
        f"[+] Ransom note:"
        f"\n    {RANSOM_NOTE}"
    )


# ============================================================
# RECOVERY
# ============================================================

def recover_files(password):

    print("\n")
    print("=" * 60)
    print("                 RECOVERY MODE")
    print("=" * 60)

    # Check whether salt exists
    if not os.path.exists(SALT_FILE):

        print(
            "\n[!] lab.salt was not found."
        )

        print(
            "[!] The simulation key cannot be recreated."
        )

        return

    # Load salt
    with open(SALT_FILE, "rb") as file:
        salt = file.read()

    # Derive the same key
    key = derive_key(
        password,
        salt
    )

    # Find encrypted files
    files = find_locked_files()

    if not files:

        print(
            "\n[!] No .locked files were found."
        )

        return

    print(
        f"\n[*] Locked files found: "
        f"{len(files)}\n"
    )

    successful = 0

    for filename in files:

        try:

            before = os.path.exists(
                filename
            )

            decrypt_file(
                filename,
                key
            )

            # Check whether the encrypted file disappeared
            if before and not os.path.exists(filename):
                successful += 1

        except Exception as error:

            print(
                f"[!] Error decrypting "
                f"{filename}: {error}"
            )

            logging.error(
                "ERROR DECRYPTING %s: %s",
                filename,
                error
            )

    # Remove simulation ransom note
    if os.path.exists(RANSOM_NOTE):

        os.remove(
            RANSOM_NOTE
        )

        logging.info(
            "RANSOM NOTE REMOVED"
        )

    logging.info(
        "RECOVERY FINISHED"
    )

    print("\n" + "=" * 60)
    print("                RECOVERY COMPLETED")
    print("=" * 60)

    print(
        f"\n[+] Files restored: "
        f"{successful}"
    )


# ============================================================
# SHOW LAB STATUS
# ============================================================

def show_status():

    print("\n")
    print("=" * 60)
    print("                   LAB STATUS")
    print("=" * 60)

    normal_files = find_files()
    locked_files = find_locked_files()

    print(
        f"\n[*] Normal files : "
        f"{len(normal_files)}"
    )

    print(
        f"[*] Locked files : "
        f"{len(locked_files)}"
    )

    print(
        f"\n[*] Lab directory:"
        f"\n    {LAB_DIRECTORY}"
    )

    print(
        f"\n[*] Activity log:"
        f"\n    {LOG_FILE}"
    )


# ============================================================
# MAIN MENU
# ============================================================

def main():

    print("\n")
    print("=" * 60)
    print("            SAFE RANSOMWARE SIMULATOR")
    print("                 EDUCATIONAL VM LAB")
    print("=" * 60)

    print(
        "\n[!] SAFETY RESTRICTION:"
    )

    print(
        "    Only files inside:"
    )

    print(
        f"    {LAB_DIRECTORY}"
    )

    print(
        "\n    can be modified by this program."
    )

    print("\n------------------------------------------------------------")

    print(
        "\n1. Simulate ransomware encryption"
    )

    print(
        "2. Recover encrypted files"
    )

    print(
        "3. Show lab status"
    )

    print(
        "4. Exit"
    )

    print(
        "\n------------------------------------------------------------"
    )

    choice = input(
        "\nSelect option: "
    ).strip()

    # ========================================================
    # ENCRYPT
    # ========================================================

    if choice == "1":

        password = getpass.getpass(
            "\nEnter simulation password: "
        )

        if not password:

            print(
                "[!] Password cannot be empty."
            )

            return

        simulate_encryption(
            password
        )

    # ========================================================
    # DECRYPT
    # ========================================================

    elif choice == "2":

        password = getpass.getpass(
            "\nEnter recovery password: "
        )

        if not password:

            print(
                "[!] Password cannot be empty."
            )

            return

        recover_files(
            password
        )

    # ========================================================
    # STATUS
    # ========================================================

    elif choice == "3":

        show_status()

    # ========================================================
    # EXIT
    # ========================================================

    elif choice == "4":

        print(
            "\n[*] Exiting simulation."
        )

    else:

        print(
            "\n[!] Invalid option."
        )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
