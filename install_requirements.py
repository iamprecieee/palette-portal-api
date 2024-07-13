import subprocess
import sys


def install_package(utf_version):
    """
    This helps with auto alternative package installation, and skips commented-out packages.
    Also tries installing packages without their version in case of errors.
    """
    with open("requirements.txt", "r", encoding=f"utf-{utf_version}") as file:
        for line in file:
            if not line.startswith("#"):
                if line.startswith("psycopg2"):
                    try:
                        subprocess.check_call(
                            [sys.executable, "-m", "pip", "install", "psycopg2"]
                        )
                    except subprocess.CalledProcessError:
                        subprocess.check_call(
                            [sys.executable, "-m", "pip", "install", "psycopg2-binary"]
                        )
                else:
                    try:
                        subprocess.check_call(
                            [sys.executable, "-m", "pip", "install", line.strip()]
                        )
                    except subprocess.CalledProcessError:
                        subprocess.check_call(
                            [
                                sys.executable,
                                "-m",
                                "pip",
                                "install",
                                line.strip().split("==")[0],
                            ]
                        )


try:
    # Works for requirement.txt files encoded in utf-16
    install_package(16)
except UnicodeDecodeError:
    install_package(8)
