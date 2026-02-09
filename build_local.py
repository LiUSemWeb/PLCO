#!/usr/bin/env python3
"""
Local WIDOCO Documentation Generator with Index Page Creation
Simulates the GitHub Actions workflow for testing purposes
"""
import os
import subprocess
import sys
from pathlib import Path
from pybars import Compiler
from glob import glob
import re
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)

# Configuration
WIDOCO_VERSION = "1.4.25"
WIDOCO_JAR_PATH = f"tools/widoco-{WIDOCO_VERSION}.jar"
ONTOLOGY_DIR = "ontology"
DOCS_DIR = "docs/dev"

# WIDOCO options
WIDOCO_OPTIONS = [
    "-rewriteAll",
    "-includeImportedOntologies",
    "-webVowl",
    "-licensius"
]

def check_widoco():
    """Check if WIDOCO jar exists in tools/ folder"""
    if os.path.exists(WIDOCO_JAR_PATH):
        print(f"✓ WIDOCO jar found: {WIDOCO_JAR_PATH}")
        return True
    else:
        print(f"✗ WIDOCO jar not found: {WIDOCO_JAR_PATH}")
        print(f"  Please ensure widoco-{WIDOCO_VERSION}.jar is in the tools/ folder")
        return False

def check_java():
    """Check if Java 17+ is installed"""
    try:
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True
        )
        version_output = result.stderr  # Java outputs version to stderr
        print(f"✓ Java is installed")
        print(f"  {version_output.split(chr(10))[0]}")
        return True
    except FileNotFoundError:
        print("✗ Java is not installed or not in PATH")
        print("  Please install Java 17 or higher")
        return False

def find_ontology_files():
    """Find all ontology files in the ontology directory (modules/ and demo/)"""
    ontology_path = Path(ONTOLOGY_DIR)
    if not ontology_path.exists():
        print(f"✗ Ontology directory not found: {ONTOLOGY_DIR}")
        return []
    
    # Check for modules/ and demo/ subdirectories
    modules_path = ontology_path / "modules"
    demo_path = ontology_path / "demo"
    
    extensions = ['*.owl', '*.ttl', '*.rdf']
    ontology_files = []
    
    # Search in modules/ folder
    if modules_path.exists():
        for ext in extensions:
            ontology_files.extend(modules_path.rglob(ext))
    
    # Search in demo/ folder
    if demo_path.exists():
        for ext in extensions:
            ontology_files.extend(demo_path.rglob(ext))
    
    return sorted(ontology_files)

def generate_documentation(ontology_file):
    """Generate documentation for a single ontology file"""
    print(f"\nProcessing: {ontology_file}")
    
    # Extract relative path from ontology/
    # Example: ontology/modules/core/0.1/core.owl -> modules/core/0.1
    relative_path = ontology_file.relative_to(ONTOLOGY_DIR)
    
    # Get directory path (e.g., modules/core/0.1 or demo/example/0.1)
    dir_path = relative_path.parent
    
    # Get filename without extension
    base_name = ontology_file.stem
    
    # Create output directory (preserves modules/ or demo/ structure)
    output_dir = Path(DOCS_DIR) / dir_path
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"  Path: {dir_path}")
    print(f"  Ontology name: {base_name}")
    print(f"  Output directory: {output_dir}")
    
    # Build WIDOCO command using tools/widoco jar
    cmd = [
        "java", "-jar", WIDOCO_JAR_PATH,
        "-ontFile", str(ontology_file),
        "-outFolder", str(output_dir)
    ] + WIDOCO_OPTIONS
    
    print(f"  Running WIDOCO...")
    try:
        # Run WIDOCO
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print(f"  ✓ Documentation generated successfully")
            
            # Rename index-en.html to index.html
            index_en = output_dir / "index-en.html"
            index_html = output_dir / "index.html"
            if index_en.exists():
                index_en.rename(index_html)
                print(f"  ✓ Renamed index-en.html to index.html")
            
            return True
        else:
            print(f"  ✗ WIDOCO failed with return code {result.returncode}")
            if result.stderr:
                print(f"  Error output: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  ✗ WIDOCO timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"  ✗ Error running WIDOCO: {e}")
        return False

def create_latest_folders():
    """Create 'latest' folders for each module (matching the workflow behavior)"""
    print("\n5. Creating 'latest' folders...")
    print("-" * 60)
    
    docs_path = Path(DOCS_DIR)
    
    # Process each category (modules/, demo/)
    for category_dir in docs_path.iterdir():
        if not category_dir.is_dir() or category_dir.name == 'dev':
            continue
        
        print(f"\nProcessing category: {category_dir.name}")
        
        # Process each module within the category
        for module_dir in category_dir.iterdir():
            if not module_dir.is_dir():
                continue
            
            # Find version directories (e.g., 0.1, 0.2, 1.0)
            version_dirs = [
                d for d in module_dir.iterdir()
                if d.is_dir() and d.name != 'latest' and d.name[0].isdigit()
            ]
            
            if not version_dirs:
                continue
            
            # Sort versions and get the latest
            version_dirs.sort(key=lambda x: [int(p) for p in x.name.split('.')])
            latest_version = version_dirs[-1]
            
            print(f"  Creating latest for {category_dir.name}/{module_dir.name}")
            print(f"    Latest version: {latest_version.name}")
            
            # Copy latest version to 'latest' folder
            latest_dir = module_dir / "latest"
            if latest_dir.exists():
                import shutil
                shutil.rmtree(latest_dir)
            
            import shutil
            shutil.copytree(latest_version, latest_dir)
            print(f"    ✓ Created: {latest_dir}")

def create_index_file():
    """Generate index.html from template"""
    print("\n6. Generating index file...")
    print("-" * 60)
    
    compiler = Compiler()
    template_file = "index.hbs"
    index_file = "docs/dev/index.html"
    
    # Updated core categories to match your ontology structure
    core = ["actorODP", "observation", "processODP", "product", "resourceODP", "location"]
    core_actor = ["actorODP"]
    core_process = ["processODP"]
    core_resource = ["resourceODP", "product"]
    core_observation = ["observation"]  # Fixed typo: obsrvation -> observation
    core_supplementary = ["location"]
    
    data = {
        "core": [],
        "other": [],
        "demo": [],
        "actor": [],
        "observation": [],
        "process": [],
        "resource": [],
        "supplementary": []
    }
    
    for type in ["modules", "demo"]:
        ontologies = {}
        
        # Updated pattern to match new structure: ontology/modules/name/version/*.ttl
        for source in glob(f"ontology/{type}/*/*/*", recursive=True):
            if not source.endswith(".ttl"):
                continue
            
            parts = re.match(f"ontology/{type}/([^/]*)/([^/]*)", source)
            name = parts.group(1)
            version = parts.group(2)
            
            if not ontologies.get(name):
                ontologies[name] = {
                    "name": name,
                    "versions": []
                }
            
            ontologies[name]["versions"].append(version)
            ontologies[name]["versions"].sort(reverse=True)
        
        # Split into core, other and demo
        for name in ontologies:
            ontology = {
                "name": name,
                "versions": ontologies[name]["versions"]
            }
            
            if type == "demo":
                data["demo"].append(ontology)
            else:
                if name in core:
                    data["core"].append(ontology)
                    
                    # Categorize core modules
                    if name in core_actor:
                        data["actor"].append(ontology)
                    if name in core_process:
                        data["process"].append(ontology)
                    if name in core_resource:
                        data["resource"].append(ontology)
                    if name in core_observation:  # Fixed typo
                        data["observation"].append(ontology)
                    if name in core_supplementary:
                        data["supplementary"].append(ontology)
                else:
                    data["other"].append(ontology)
    
    # Sort all lists by name
    for list in data.values():
        list.sort(key=lambda x: x["name"])
    
    # Generate index.html from template
    try:
        with open(template_file, "r") as f:
            template = compiler.compile(f.read())
        
        with open(index_file, "w") as f:
            f.write(template({"data": data}))
        
        print(f"✓ Index file generated: {index_file}")
        return True
    except Exception as e:
        print(f"✗ Failed to generate index file: {e}")
        return False

def main():
    """Main execution function"""
    print("=" * 60)
    print("Local WIDOCO Documentation Generator")
    print("=" * 60)
    
    # Check prerequisites
    print("\n1. Checking prerequisites...")
    if not check_java():
        sys.exit(1)
    
    # Check WIDOCO jar
    print("\n2. Checking WIDOCO jar...")
    if not check_widoco():
        sys.exit(1)
    
    # Find ontology files
    print(f"\n3. Finding ontology files in '{ONTOLOGY_DIR}/'...")
    ontology_files = find_ontology_files()
    
    if not ontology_files:
        print(f"✗ No ontology files found in '{ONTOLOGY_DIR}/'")
        print(f"  Please add .owl, .ttl, or .rdf files to:")
        print(f"    - '{ONTOLOGY_DIR}/modules/module-name/version/'")
        print(f"    - '{ONTOLOGY_DIR}/demo/demo-name/version/'")
        print(f"  Expected structure: {ONTOLOGY_DIR}/modules/core/0.1/ontology.owl")
        sys.exit(1)
    
    print(f"✓ Found {len(ontology_files)} ontology file(s):")
    for f in ontology_files:
        print(f"  - {f}")
    
    # Generate documentation
    print(f"\n4. Generating documentation...")
    print("-" * 60)
    
    success_count = 0
    fail_count = 0
    
    for ontology_file in ontology_files:
        if generate_documentation(ontology_file):
            success_count += 1
        else:
            fail_count += 1
    
    # Create latest folders
    if success_count > 0:
        create_latest_folders()
        
        # Generate index page
        if not create_index_file():
            print("⚠️  Index file generation failed")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total files processed: {len(ontology_files)}")
    print(f"✓ Successful: {success_count}")
    print(f"✗ Failed: {fail_count}")
    
    if success_count > 0:
        print(f"\n📁 Documentation generated in '{DOCS_DIR}/' directory")
        print(f"\nStructure:")
        print(f"  {DOCS_DIR}/")
        print(f"  ├── index.html          (main landing page)")
        print(f"  ├── modules/")
        print(f"  │   └── module-name/")
        print(f"  │       ├── version/")
        print(f"  │       └── latest/")
        print(f"  └── demo/")
        print(f"      └── demo-name/")
        print(f"          ├── version/")
        print(f"          └── latest/")
        print(f"\nTo view the documentation:")
        print(f"  1. Open the main index page:")
        print(f"     open {DOCS_DIR}/index.html")
        print(f"\n  2. Or browse individual modules:")
        # Find first generated index.html
        docs_path = Path(DOCS_DIR)
        index_files = [f for f in docs_path.rglob("index.html") if f != docs_path / "index.html"]
        if index_files:
            # Prioritize showing a 'latest' index if available
            latest_indexes = [f for f in index_files if 'latest' in str(f)]
            example_file = latest_indexes[0] if latest_indexes else index_files[0]
            print(f"     open {example_file}")
    
    if fail_count > 0:
        print(f"\n⚠️  Some documentation generation failed. Check the output above.")
        sys.exit(1)
    
    print("\n✓ All documentation generated successfully!")

if __name__ == "__main__":
    main()
