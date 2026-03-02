import os
import shutil
from pathlib import Path

def generate_docs():
    docs_dir = Path("docs")
    projects_dir = docs_dir / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)

    # Companies to skip or root folders to ignore
    ignore_dirs = {".github", "docs", "bazel-", ".git", "technical_specification", "node_modules"}

    nav_structure = []
    
    # Discovery loop
    # We look for folders in the root that are NOT in ignore_dirs
    for company_path in sorted(Path(".").iterdir()):
        if company_path.is_dir() and company_path.name not in ignore_dirs and not company_path.name.startswith("."):
            company_name = company_path.name.replace("_", " ").title()
            competitions = []
            
            # For each company, look for competitions
            for comp_path in sorted(company_path.iterdir()):
                if comp_path.is_dir() and not comp_path.name.startswith("."):
                    comp_name = comp_path.name.replace("_", " ").title().replace("-", " ")
                    
                    # Generate a markdown file for this competition
                    doc_filename = f"{company_path.name}_{comp_path.name}.md"
                    doc_path = projects_dir / doc_filename
                    
                    # Content generation
                    with open(doc_path, "w", encoding="utf-8") as f:
                        f.write(f"# {comp_name} ({company_name})\n\n")
                        
                        readme_path = comp_path / "README.md"
                        if readme_path.exists():
                            f.write("## 📋 Overview\n\n")
                            f.write(readme_path.read_text(encoding="utf-8"))
                            f.write("\n\n")
                        
                        solutions_path = comp_path / "SOLUTIONS.md"
                        if solutions_path.exists():
                            f.write("## 🚀 Solutions\n\n")
                            f.write(solutions_path.read_text(encoding="utf-8"))
                            f.write("\n\n")

                        f.write("## 💻 Implementations\n\n")
                        for lang in ["python", "cpp", "rust"]:
                            lang_path = comp_path / lang
                            if lang_path.exists():
                                f.write(f"### {lang.title()}\n\n")
                                lang_readme = lang_path / "README.md"
                                if lang_readme.exists():
                                    f.write(lang_readme.read_text(encoding="utf-8"))
                                    f.write("\n\n")
                                else:
                                    f.write(f"Implementation available in `{company_path.name}/{comp_path.name}/{lang}`.\n\n")

                    competitions.append({comp_name: f"projects/{doc_filename}"})
            
            if competitions:
                nav_structure.append({company_name: competitions})

    # Read existing mkdocs.yml and update nav
    mkdocs_path = Path("mkdocs.yml")
    lines = []
    if mkdocs_path.exists():
        with open(mkdocs_path, "r", encoding="utf-8") as f:
            for line in f:
                if "nav:" in line:
                    break
                lines.append(line)
    
    # Append new nav
    lines.append("nav:\n")
    lines.append("  - Home: index.md\n")
    lines.append("  - Projects:\n")
    for company_nav in nav_structure:
        for company, comps in company_nav.items():
            lines.append(f"    - {company}:\n")
            for comp_dict in comps:
                for name, path in comp_dict.items():
                    lines.append(f"      - {name}: {path}\n")
    lines.append("  - Technical Specification: technical_spec.md\n")

    with open(mkdocs_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

if __name__ == "__main__":
    generate_docs()
