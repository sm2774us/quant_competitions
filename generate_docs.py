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
    for company_path in Path(".").iterdir():
        if company_path.is_dir() and company_path.name not in ignore_dirs and not company_path.name.startswith("."):
            company_name = company_path.name.replace("_", " ").title()
            competitions = []
            
            # For each company, look for competitions
            for comp_path in company_path.iterdir():
                if comp_path.is_dir() and not comp_path.name.startswith("."):
                    comp_name = comp_path.name.replace("_", " ").title().replace("-", " ")
                    
                    # Generate a markdown file for this competition if not exists or update it
                    doc_filename = f"{company_path.name}_{comp_path.name}.md"
                    doc_path = projects_dir / doc_filename
                    
                    # Content generation
                    with open(doc_path, "w") as f:
                        f.write(f"# {comp_name} ({company_name})

")
                        
                        # Try to pull in competition README if it exists
                        readme_path = comp_path / "README.md"
                        if readme_path.exists():
                            f.write("## 📋 Overview
")
                            f.write(readme_path.read_text())
                            f.write("

")
                        
                        # Try to pull in SOLUTIONS.md
                        solutions_path = comp_path / "SOLUTIONS.md"
                        if solutions_path.exists():
                            f.write("## 🚀 Solutions
")
                            f.write(solutions_path.read_text())
                            f.write("

")

                        # Languages
                        f.write("## 💻 Implementations
")
                        for lang in ["python", "cpp", "rust"]:
                            lang_path = comp_path / lang
                            if lang_path.exists():
                                f.write(f"### {lang.title()}
")
                                lang_readme = lang_path / "README.md"
                                if lang_readme.exists():
                                    # Include first few paragraphs or a link
                                    f.write(lang_readme.read_text())
                                    f.write("

")
                                else:
                                    f.write(f"Implementation available in `{company_path.name}/{comp_path.name}/{lang}`.

")

                    competitions.append({comp_name: f"projects/{doc_filename}"})
            
            if competitions:
                nav_structure.append({company_name: competitions})

    # Read existing mkdocs.yml and update nav
    mkdocs_path = Path("mkdocs.yml")
    lines = []
    with open(mkdocs_path, "r") as f:
        for line in f:
            if "nav:" in line:
                break
            lines.append(line)
    
    # Append new nav
    lines.append("nav:
")
    lines.append("  - Home: index.md
")
    lines.append("  - Projects:
")
    for company_nav in nav_structure:
        for company, comps in company_nav.items():
            lines.append(f"    - {company}:
")
            for comp_dict in comps:
                for name, path in comp_dict.items():
                    lines.append(f"      - {name}: {path}
")
    lines.append("  - Technical Specification: technical_spec.md
")

    with open(mkdocs_path, "w") as f:
        f.writelines(lines)

if __name__ == "__main__":
    generate_docs()
