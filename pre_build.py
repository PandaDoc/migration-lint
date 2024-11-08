import subprocess


SQUAWK_VERSION = "1.1.2"


if __name__ == "__main__":
    subprocess.run(["mkdir", "-p", "migration_lint/bin"])
    subprocess.run(
        [
            "curl",
            "-L",
            f"https://github.com/sbdchd/squawk/releases/download/v{SQUAWK_VERSION}/squawk-darwin-arm64",
            "-o",
            "migration_lint/bin/squawk-darwin-arm64",
        ]
    )
    subprocess.run(
        [
            "curl",
            "-L",
            f"https://github.com/sbdchd/squawk/releases/download/v{SQUAWK_VERSION}/squawk-linux-x64",
            "-o",
            "migration_lint/bin/squawk-linux-x86",
        ]
    )
    subprocess.run(["chmod", "+x", "migration_lint/bin/squawk-darwin-arm64"])
    subprocess.run(["chmod", "+x", "migration_lint/bin/squawk-linux-x86"])
