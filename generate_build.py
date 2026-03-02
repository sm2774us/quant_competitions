import os
from pathlib import Path

def generate_build_bazel():
    build_file_content = """load("@rules_shell//shell:sh_test.bzl", "sh_test")

package(default_visibility = ["//visibility:public"])

# --- Auto-generated Test Targets ---
# These targets are dynamically generated based on the monorepo's structure.
# Any new competition projects following the standard (python/cpp/rust)
# subdirectory conventions will automatically get build/test targets.

"""
    
    # Companies to skip or root folders to ignore
    ignore_dirs = {".github", "docs", "bazel-", ".git", "technical_specification", "node_modules"}

    # Base directory (monorepo root)
    root_dir = Path(".")

    # Discovery loop
    for company_path in sorted(root_dir.iterdir()):
        if company_path.is_dir() and company_path.name not in ignore_dirs and not company_path.name.startswith("."):
            for comp_path in sorted(company_path.iterdir()):
                if comp_path.is_dir() and not comp_path.name.startswith("."):
                    comp_id = f"{company_path.name}_{comp_path.name.replace('-', '_')}"
                    
                    for lang in ["python", "cpp", "rust"]:
                        lang_path = comp_path / lang
                        if lang_path.is_dir():
                            target_name = f"{comp_id}_{lang}"
                            build_file_content += f"""
sh_test(
    name = "{target_name}",
    srcs = ["run_{lang}_build.sh"],
    data = glob(["{lang_path}/**"]) + [
        "run_{lang}_build.sh",
        "discover_and_test.sh",
        "generate_build.py",
        "generate_docs.py",
    ],
    tags = ["{lang}", "auto_generated"],
    # Ensure the script is run from the project subdirectory
    chdir = "{lang_path}",
)
"""
    
    with open("BUILD.bazel", "w") as f:
        f.write(build_file_content)

if __name__ == "__main__":
    generate_build_bazel()
