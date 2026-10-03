#!/usr/bin/env python3
"""Build script for Node.js AgentGuard Plugin releases in ./release/javascript/node/plugin."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
NODE_PLUGIN_DIR = ROOT_DIR / "packages" / "node-plugin"
RELEASE_NODE_DIR = ROOT_DIR / "release" / "javascript" / "node" / "plugin"


def clean_release_dir():
    print("[AgentGuard Node Build] Cleaning release directory...")
    if RELEASE_NODE_DIR.exists():
        shutil.rmtree(RELEASE_NODE_DIR)
    RELEASE_NODE_DIR.mkdir(parents=True, exist_ok=True)


def build_node_package():
    print(f"[AgentGuard Node Build] Copying Node plugin package to {RELEASE_NODE_DIR}...")
    # Copy plugin files
    for item in ["package.json", "README.md", "API_REFERENCE.md"]:
        shutil.copy2(NODE_PLUGIN_DIR / item, RELEASE_NODE_DIR / item)

    shutil.copytree(NODE_PLUGIN_DIR / "src", RELEASE_NODE_DIR / "src", dirs_exist_ok=True)
    shutil.copytree(NODE_PLUGIN_DIR / "test", RELEASE_NODE_DIR / "test", dirs_exist_ok=True)

    # Create dist folder
    dist_dir = RELEASE_NODE_DIR / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(NODE_PLUGIN_DIR / "src", dist_dir, dirs_exist_ok=True)

    # Copy full documentation set into release docs/
    rel_docs_dir = RELEASE_NODE_DIR / "docs"
    if (ROOT_DIR / "docs").exists():
        shutil.copytree(ROOT_DIR / "docs", rel_docs_dir, dirs_exist_ok=True)

    for doc_file in ["README.md", "README.TECHNICAL.md", "AGENTS.md", "LICENSE"]:
        if (ROOT_DIR / doc_file).exists():
            shutil.copy2(ROOT_DIR / doc_file, rel_docs_dir / doc_file)

    # Run npm pack to build .tgz release artifact
    print("[AgentGuard Node Build] Packing npm tarball...")
    subprocess.run(["npm", "pack"], cwd=RELEASE_NODE_DIR, check=True)


def run_node_tests():
    print("[AgentGuard Node Build] Running Node plugin test suite in release directory...")
    cmd = ["node", "--experimental-strip-types", "--test", "test/*.test.ts"]
    subprocess.run(cmd, cwd=RELEASE_NODE_DIR, check=True)


def main():
    clean_release_dir()
    build_node_package()
    run_node_tests()

    print(f"\n[AgentGuard Node Build Success] Artifacts created in {RELEASE_NODE_DIR}:")
    for f in sorted(RELEASE_NODE_DIR.rglob("*")):
        if f.is_file():
            size_kb = f.stat().st_size / 1024
            rel_name = f.relative_to(RELEASE_NODE_DIR)
            print(f"  - {rel_name} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
