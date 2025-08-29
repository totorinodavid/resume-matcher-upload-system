#!/usr/bin/env python3
"""
Resume Matcher Repository Doctor
Analyzes the repository for:
- Memory-intensive files (large files, duplicates)
- Security risks and vulnerabilities
- Code quality issues
- Performance bottlenecks
- Architecture problems
"""

import os
import sys
import hashlib
import json
import re
import subprocess
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set
import mimetypes

class RepoDoctor:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.results = {
            "memory_analysis": {},
            "security_risks": {},
            "code_quality": {},
            "performance_issues": {},
            "architecture_analysis": {}
        }
        
    def analyze_file_sizes(self) -> Dict:
        """Analyze file sizes to identify memory-intensive files"""
        print("🔍 Analyzing file sizes...")
        
        large_files = []
        total_size = 0
        file_count = 0
        size_by_extension = defaultdict(int)
        size_by_directory = defaultdict(int)
        
        # Skip these directories/files
        skip_dirs = {'.git', '__pycache__', 'node_modules', '.next', 'dist', 'build', 
                    'env', 'venv', '.venv', 'logs', 'test-results', '.pytest_cache'}
        skip_files = {'.pyc', '.pyo', '.pyd', '.so', '.dylib', '.dll', '.DS_Store'}
        
        for root, dirs, files in os.walk(self.repo_path):
            # Remove skip directories from dirs list
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if any(file.endswith(ext) for ext in skip_files):
                    continue
                    
                file_path = Path(root) / file
                try:
                    size = file_path.stat().st_size
                    total_size += size
                    file_count += 1
                    
                    # Track by extension
                    ext = file_path.suffix.lower()
                    size_by_extension[ext] += size
                    
                    # Track by directory
                    rel_path = file_path.relative_to(self.repo_path)
                    top_dir = str(rel_path.parts[0]) if rel_path.parts else "root"
                    size_by_directory[top_dir] += size
                    
                    # Track large files (>1MB)
                    if size > 1024 * 1024:
                        large_files.append({
                            "path": str(rel_path),
                            "size_mb": round(size / (1024 * 1024), 2),
                            "type": ext or "no_extension"
                        })
                        
                except (OSError, PermissionError):
                    continue
        
        # Sort results
        large_files.sort(key=lambda x: x["size_mb"], reverse=True)
        
        return {
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_count": file_count,
            "large_files": large_files[:20],  # Top 20 largest files
            "size_by_extension": dict(sorted(size_by_extension.items(), 
                                           key=lambda x: x[1], reverse=True)[:10]),
            "size_by_directory": dict(sorted(size_by_directory.items(), 
                                           key=lambda x: x[1], reverse=True))
        }
    
    def find_duplicate_files(self) -> Dict:
        """Find duplicate files that waste space"""
        print("🔍 Finding duplicate files...")
        
        hashes = defaultdict(list)
        skip_dirs = {'.git', '__pycache__', 'node_modules', '.next', 'dist', 'build', 
                    'env', 'venv', '.venv', 'logs', 'test-results'}
        
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                file_path = Path(root) / file
                try:
                    if file_path.stat().st_size < 100:  # Skip very small files
                        continue
                        
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        rel_path = file_path.relative_to(self.repo_path)
                        hashes[file_hash].append({
                            "path": str(rel_path),
                            "size_mb": round(file_path.stat().st_size / (1024 * 1024), 3)
                        })
                except (OSError, PermissionError, UnicodeDecodeError):
                    continue
        
        # Find duplicates
        duplicates = {hash_val: files for hash_val, files in hashes.items() if len(files) > 1}
        
        return {
            "duplicate_groups": len(duplicates),
            "duplicates": dict(list(duplicates.items())[:10]),  # Top 10 duplicate groups
            "wasted_space_mb": sum(
                sum(file["size_mb"] for file in files[1:])  # All but first file are waste
                for files in duplicates.values()
            )
        }
    
    def analyze_security_risks(self) -> Dict:
        """Analyze for security risks and vulnerabilities"""
        print("🔍 Analyzing security risks...")
        
        risks = {
            "secrets_found": [],
            "dangerous_patterns": [],
            "insecure_dependencies": [],
            "permission_issues": []
        }
        
        # Patterns to look for
        secret_patterns = [
            (r'api[_-]?key\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})', "API Key"),
            (r'secret[_-]?key\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})', "Secret Key"),
            (r'password\s*[:=]\s*["\']([^"\']{8,})', "Password"),
            (r'token\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})', "Token"),
            (r'sk-[a-zA-Z0-9]{48}', "OpenAI API Key"),
            (r'ghp_[a-zA-Z0-9]{36}', "GitHub Token"),
        ]
        
        dangerous_patterns = [
            (r'eval\s*\(', "Dangerous eval() usage"),
            (r'exec\s*\(', "Dangerous exec() usage"),
            (r'shell=True', "Shell injection risk"),
            (r'innerHTML\s*=', "XSS risk"),
            (r'dangerouslySetInnerHTML', "React XSS risk"),
            (r'process\.env\.[A-Z_]+', "Environment variable exposure"),
        ]
        
        # Search in code files
        code_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.env', '.yaml', '.yml', '.json'}
        
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '.next', 'dist'}]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() not in code_extensions:
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        rel_path = file_path.relative_to(self.repo_path)
                        
                        # Check for secrets
                        for pattern, risk_type in secret_patterns:
                            matches = re.finditer(pattern, content, re.IGNORECASE)
                            for match in matches:
                                line_num = content[:match.start()].count('\n') + 1
                                risks["secrets_found"].append({
                                    "file": str(rel_path),
                                    "line": line_num,
                                    "type": risk_type,
                                    "preview": content[max(0, match.start()-20):match.end()+20]
                                })
                        
                        # Check for dangerous patterns
                        for pattern, risk_type in dangerous_patterns:
                            matches = re.finditer(pattern, content, re.IGNORECASE)
                            for match in matches:
                                line_num = content[:match.start()].count('\n') + 1
                                risks["dangerous_patterns"].append({
                                    "file": str(rel_path),
                                    "line": line_num,
                                    "type": risk_type,
                                    "preview": content[max(0, match.start()-20):match.end()+20]
                                })
                                
                except (OSError, PermissionError, UnicodeDecodeError):
                    continue
        
        return risks
    
    def analyze_code_quality(self) -> Dict:
        """Analyze code quality issues"""
        print("🔍 Analyzing code quality...")
        
        quality_issues = {
            "large_functions": [],
            "complex_files": [],
            "todo_comments": [],
            "code_smells": []
        }
        
        code_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx'}
        
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '.next', 'dist', '__pycache__'}]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() not in code_extensions:
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.split('\n')
                        rel_path = file_path.relative_to(self.repo_path)
                        
                        # Count lines of code
                        loc = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
                        
                        # Large files
                        if loc > 500:
                            quality_issues["complex_files"].append({
                                "file": str(rel_path),
                                "lines_of_code": loc
                            })
                        
                        # TODO comments
                        for i, line in enumerate(lines):
                            if re.search(r'(TODO|FIXME|HACK|XXX)', line, re.IGNORECASE):
                                quality_issues["todo_comments"].append({
                                    "file": str(rel_path),
                                    "line": i + 1,
                                    "comment": line.strip()
                                })
                        
                        # Code smells
                        if 'except:' in content:
                            quality_issues["code_smells"].append({
                                "file": str(rel_path),
                                "type": "Bare except clause",
                                "line": content[:content.find('except:')].count('\n') + 1
                            })
                            
                        if content.count('if __name__ == "__main__"') > 1:
                            quality_issues["code_smells"].append({
                                "file": str(rel_path),
                                "type": "Multiple main blocks"
                            })
                            
                except (OSError, PermissionError, UnicodeDecodeError):
                    continue
        
        return quality_issues
    
    def analyze_dependencies(self) -> Dict:
        """Analyze dependency files for issues"""
        print("🔍 Analyzing dependencies...")
        
        dep_analysis = {
            "python_deps": {},
            "node_deps": {},
            "outdated_patterns": [],
            "security_issues": []
        }
        
        # Check Python dependencies
        requirements_files = ['requirements.txt', 'pyproject.toml', 'Pipfile']
        for req_file in requirements_files:
            req_path = self.repo_path / req_file
            if req_path.exists():
                try:
                    with open(req_path, 'r') as f:
                        content = f.read()
                        # Look for pinned versions
                        unpinned = re.findall(r'^([a-zA-Z0-9_-]+)(?:\s*[><=]+.*)?$', content, re.MULTILINE)
                        dep_analysis["python_deps"][req_file] = {
                            "total_deps": len(re.findall(r'^[a-zA-Z]', content, re.MULTILINE)),
                            "unpinned": len(unpinned)
                        }
                except Exception:
                    pass
        
        # Check Node.js dependencies
        package_json = self.repo_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = data.get('dependencies', {})
                    dev_deps = data.get('devDependencies', {})
                    dep_analysis["node_deps"] = {
                        "dependencies": len(deps),
                        "devDependencies": len(dev_deps),
                        "caret_versions": len([v for v in deps.values() if v.startswith('^')]),
                        "tilde_versions": len([v for v in deps.values() if v.startswith('~')])
                    }
            except Exception:
                pass
        
        return dep_analysis
    
    def generate_report(self) -> str:
        """Generate a comprehensive report"""
        print("\n" + "="*80)
        print("🏥 RESUME MATCHER REPOSITORY DOCTOR REPORT")
        print("="*80)
        
        # Run all analyses
        self.results["memory_analysis"] = self.analyze_file_sizes()
        self.results["duplicates"] = self.find_duplicate_files()
        self.results["security_risks"] = self.analyze_security_risks()
        self.results["code_quality"] = self.analyze_code_quality()
        self.results["dependencies"] = self.analyze_dependencies()
        
        report = []
        
        # Memory Analysis
        report.append("\n📊 MEMORY ANALYSIS")
        report.append("-" * 40)
        mem = self.results["memory_analysis"]
        report.append(f"Total repository size: {mem['total_size_mb']} MB")
        report.append(f"Total files analyzed: {mem['file_count']}")
        
        if mem["large_files"]:
            report.append(f"\n🔥 TOP MEMORY CONSUMERS:")
            for file in mem["large_files"][:5]:
                report.append(f"  • {file['path']}: {file['size_mb']} MB ({file['type']})")
        
        report.append(f"\n📁 LARGEST DIRECTORIES:")
        for dir_name, size in list(mem["size_by_directory"].items())[:5]:
            report.append(f"  • {dir_name}: {round(size / (1024 * 1024), 2)} MB")
        
        # Duplicates
        dup = self.results["duplicates"]
        if dup["duplicate_groups"] > 0:
            report.append(f"\n🔄 DUPLICATE FILES")
            report.append("-" * 40)
            report.append(f"Duplicate groups found: {dup['duplicate_groups']}")
            report.append(f"Wasted space: {dup['wasted_space_mb']:.2f} MB")
        
        # Security Risks
        report.append(f"\n🔒 SECURITY ANALYSIS")
        report.append("-" * 40)
        sec = self.results["security_risks"]
        
        if sec["secrets_found"]:
            report.append(f"⚠️  POTENTIAL SECRETS FOUND: {len(sec['secrets_found'])}")
            for secret in sec["secrets_found"][:3]:
                report.append(f"  • {secret['type']} in {secret['file']}:{secret['line']}")
        
        if sec["dangerous_patterns"]:
            report.append(f"⚠️  DANGEROUS PATTERNS: {len(sec['dangerous_patterns'])}")
            for pattern in sec["dangerous_patterns"][:3]:
                report.append(f"  • {pattern['type']} in {pattern['file']}:{pattern['line']}")
        
        # Code Quality
        report.append(f"\n🧹 CODE QUALITY")
        report.append("-" * 40)
        qual = self.results["code_quality"]
        
        if qual["complex_files"]:
            report.append(f"📄 LARGE FILES ({len(qual['complex_files'])} files > 500 LOC):")
            for file in qual["complex_files"][:3]:
                report.append(f"  • {file['file']}: {file['lines_of_code']} lines")
        
        if qual["todo_comments"]:
            report.append(f"📝 TODO COMMENTS: {len(qual['todo_comments'])}")
            
        if qual["code_smells"]:
            report.append(f"👃 CODE SMELLS: {len(qual['code_smells'])}")
            for smell in qual["code_smells"][:3]:
                report.append(f"  • {smell['type']} in {smell['file']}")
        
        # Dependencies
        report.append(f"\n📦 DEPENDENCY ANALYSIS")
        report.append("-" * 40)
        deps = self.results["dependencies"]
        
        if deps["python_deps"]:
            report.append("🐍 Python Dependencies:")
            for file, info in deps["python_deps"].items():
                report.append(f"  • {file}: {info['total_deps']} packages")
        
        if deps["node_deps"]:
            node = deps["node_deps"]
            report.append(f"📦 Node.js Dependencies:")
            report.append(f"  • Production: {node['dependencies']} packages")
            report.append(f"  • Development: {node['devDependencies']} packages")
        
        # Recommendations
        report.append(f"\n💡 RECOMMENDATIONS")
        report.append("-" * 40)
        
        if mem["large_files"]:
            report.append("• Consider optimizing large files or moving them to external storage")
        
        if dup["wasted_space_mb"] > 5:
            report.append("• Remove duplicate files to save space")
            
        if sec["secrets_found"]:
            report.append("• ⚠️  URGENT: Review and remove potential secrets from code")
            
        if qual["complex_files"]:
            report.append("• Consider breaking down large files into smaller modules")
            
        if qual["code_smells"]:
            report.append("• Address code smells to improve maintainability")
        
        report.append(f"\n" + "="*80)
        report.append("📋 SUMMARY: Repository analyzed successfully!")
        report.append("="*80)
        
        return "\n".join(report)

def main():
    if len(sys.argv) != 2:
        print("Usage: python repo_doctor.py <repository_path>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    if not os.path.exists(repo_path):
        print(f"Error: Repository path '{repo_path}' does not exist")
        sys.exit(1)
    
    doctor = RepoDoctor(repo_path)
    report = doctor.generate_report()
    print(report)
    
    # Save report to file
    report_file = Path(repo_path) / "logs" / "repo_doctor_report.txt"
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Full report saved to: {report_file}")

if __name__ == "__main__":
    main()
