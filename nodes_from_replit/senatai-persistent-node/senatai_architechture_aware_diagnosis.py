#!/usr/bin/env python3
"""
Senatai Architecture-Aware Diagnostic
Respects the dual-database design pattern
"""

import glob
import re
from pathlib import Path

class SenataiArchitectureDoctor:
    def __init__(self, senatai_path="~/senatai"):
        self.senatai_path = Path(senatai_path).expanduser()
        
        # Define which files belong to which node type
        self.sovereign_node_patterns = [
            "**/sovereign_node/**/*.py",
            "**/usb_node/**/*.py", 
            "**/offline/**/*.py",
            "**/sqlite/**/*.py"
        ]
        
        self.persistent_node_patterns = [
            "**/persistent_node/**/*.py",
            "**/web_server/**/*.py",
            "**/website/**/*.py", 
            "**/postgres/**/*.py",
            "app.py"  # Main Flask app
        ]
        
    def classify_files(self):
        """Classify files by their node architecture"""
        python_files = glob.glob(str(self.senatai_path / "**" / "*.py"), recursive=True)
        
        sovereign_files = []
        persistent_files = []
        unknown_files = []
        
        for py_file in python_files:
            relative_path = Path(py_file).relative_to(self.senatai_path)
            
            # Check if file matches known patterns
            if any(Path(py_file).match(pattern) for pattern in self.sovereign_node_patterns):
                sovereign_files.append(py_file)
            elif any(Path(py_file).match(pattern) for pattern in self.persistent_node_patterns):
                persistent_files.append(py_file)
            else:
                unknown_files.append(py_file)
        
        return sovereign_files, persistent_files, unknown_files
    
    def analyze_sql_compatibility(self):
        """Analyze SQL compatibility based on architecture"""
        sovereign_files, persistent_files, unknown_files = self.classify_files()
        
        print("🏛️  SENATAI ARCHITECTURE ANALYSIS")
        print("=" * 50)
        
        print(f"🗳️  Sovereign Node Files (SQLite): {len(sovereign_files)}")
        for f in sovereign_files:
            print(f"   ✓ {Path(f).relative_to(self.senatai_path)}")
            
        print(f"🌐 Persistent Node Files (PostgreSQL): {len(persistent_files)}")  
        for f in persistent_files:
            print(f"   ✓ {Path(f).relative_to(self.senatai_path)}")
            
        print(f"❓ Unknown/Shared Files: {len(unknown_files)}")
        for f in unknown_files:
            print(f"   ? {Path(f).relative_to(self.senatai_path)}")
        
        # Check for SQL syntax issues
        self.check_sql_syntax_issues(sovereign_files, persistent_files, unknown_files)
    
    def check_sql_syntax_issues(self, sovereign_files, persistent_files, unknown_files):
        """Check SQL syntax based on expected database type"""
        print("\n🔍 SQL SYNTAX COMPATIBILITY CHECK")
        print("=" * 50)
        
        # Sovereign nodes should use ? placeholders
        print("Checking Sovereign Nodes (should use SQLite ? syntax):")
        for file_path in sovereign_files:
            self.check_file_syntax(file_path, expected_db="sqlite")
        
        # Persistent nodes should use %s placeholders  
        print("\nChecking Persistent Nodes (should use PostgreSQL %s syntax):")
        for file_path in persistent_files:
            self.check_file_syntax(file_path, expected_db="postgresql")
            
        # Unknown files need manual review
        print("\nChecking Unknown/Shared Files (need manual review):")
        for file_path in unknown_files:
            self.check_file_syntax(file_path, expected_db="unknown")
    
    def check_file_syntax(self, file_path, expected_db):
        """Check a file's SQL syntax compatibility"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        issues = []
        
        for i, line in enumerate(lines, 1):
            if 'cursor.execute' in line or 'cursor.fetch' in line:
                has_sqlite_syntax = '?' in line
                has_postgres_syntax = '%s' in line
                
                if expected_db == "sqlite" and has_postgres_syntax:
                    issues.append(f"Line {i}: Uses PostgreSQL %s but should use SQLite ?")
                elif expected_db == "postgresql" and has_sqlite_syntax:
                    issues.append(f"Line {i}: Uses SQLite ? but should use PostgreSQL %s")
                elif expected_db == "unknown" and (has_sqlite_syntax or has_postgres_syntax):
                    issues.append(f"Line {i}: Uses SQL - needs architecture assignment")
        
        relative_path = Path(file_path).relative_to(self.senatai_path)
        if issues:
            print(f"  ❌ {relative_path}:")
            for issue in issues[:3]:  # Show first 3 issues
                print(f"     {issue}")
            if len(issues) > 3:
                print(f"     ... and {len(issues) - 3} more issues")
        else:
            print(f"  ✅ {relative_path}: Compatible with {expected_db}")

# Quick architecture assessment
def quick_architecture_check():
    """Run a quick architecture assessment"""
    doctor = SenataiArchitectureDoctor()
    doctor.analyze_sql_compatibility()

if __name__ == "__main__":
    quick_architecture_check()
