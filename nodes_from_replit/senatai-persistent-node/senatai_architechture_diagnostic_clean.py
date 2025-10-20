#!/usr/bin/env python3
"""
Senatai Architecture Summary Diagnostic
Clean, concise reporting for dual-database architecture
"""

import glob
import json
from pathlib import Path
from datetime import datetime

class SenataiArchitectureSummary:
    def __init__(self, senatai_path="~/senatai"):
        self.senatai_path = Path(senatai_path).expanduser()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "architecture_summary": {},
            "sql_compatibility": {},
            "action_items": []
        }
        
    def classify_files(self):
        """Classify files by architecture with simple patterns"""
        python_files = glob.glob(str(self.senatai_path / "**" / "*.py"), recursive=True)
        
        sovereign_files = []
        persistent_files = []
        unknown_files = []
        
        for py_file in python_files:
            path_str = str(py_file).lower()
            
            # Simple classification based on path patterns
            if any(pattern in path_str for pattern in ['sovereign', 'usb', 'offline', 'sqlite']):
                sovereign_files.append(py_file)
            elif any(pattern in path_str for pattern in ['persistent', 'web', 'website', 'postgres', 'app.py', 'nodes_from_replit']):
                persistent_files.append(py_file)
            else:
                unknown_files.append(py_file)
        
        return sovereign_files, persistent_files, unknown_files
    
    def analyze_architecture(self):
        """Run comprehensive analysis and generate summary"""
        print("🏛️  SENATAI ARCHITECTURE ANALYSIS")
        print("=" * 40)
        
        sovereign_files, persistent_files, unknown_files = self.classify_files()
        
        # Architecture Summary
        self.results["architecture_summary"] = {
            "sovereign_node_files": len(sovereign_files),
            "persistent_node_files": len(persistent_files),
            "unknown_shared_files": len(unknown_files),
            "total_python_files": len(sovereign_files) + len(persistent_files) + len(unknown_files)
        }
        
        # SQL Compatibility Analysis
        sql_issues = self.check_sql_compatibility(sovereign_files, persistent_files, unknown_files)
        self.results["sql_compatibility"] = sql_issues
        
        # Generate Action Items
        self.generate_action_items(sql_issues, unknown_files)
        
        return self.results
    
    def check_sql_compatibility(self, sovereign_files, persistent_files, unknown_files):
        """Check SQL syntax compatibility"""
        issues = {
            "sovereign_node_issues": 0,
            "persistent_node_issues": 0, 
            "unknown_file_issues": 0,
            "critical_issues": []
        }
        
        # Check Sovereign Nodes (should use ?)
        for file_path in sovereign_files:
            file_issues = self.check_file_syntax(file_path, "sqlite")
            issues["sovereign_node_issues"] += file_issues
            if file_issues > 0:
                issues["critical_issues"].append(f"Sovereign node using PostgreSQL syntax: {Path(file_path).name}")
        
        # Check Persistent Nodes (should use %s)
        for file_path in persistent_files:
            file_issues = self.check_file_syntax(file_path, "postgresql")
            issues["persistent_node_issues"] += file_issues
            if file_issues > 0:
                issues["critical_issues"].append(f"Persistent node using SQLite syntax: {Path(file_path).name}")
        
        # Check Unknown Files
        for file_path in unknown_files:
            file_issues = self.check_file_syntax(file_path, "unknown")
            issues["unknown_file_issues"] += file_issues
        
        return issues
    
    def check_file_syntax(self, file_path, expected_db):
        """Check a single file's SQL syntax"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except:
            return 0
            
        issues = 0
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if 'cursor.execute' in line:
                has_sqlite = '?' in line
                has_postgres = '%s' in line
                
                if expected_db == "sqlite" and has_postgres:
                    issues += 1
                elif expected_db == "postgresql" and has_sqlite:
                    issues += 1
                elif expected_db == "unknown" and (has_sqlite or has_postgres):
                    issues += 1
        
        return issues
    
    def generate_action_items(self, sql_issues, unknown_files):
        """Generate actionable recommendations"""
        actions = []
        
        # SQL Syntax Issues
        total_issues = (sql_issues["sovereign_node_issues"] + 
                       sql_issues["persistent_node_issues"] + 
                       sql_issues["unknown_file_issues"])
        
        if total_issues > 0:
            actions.append(f"Fix {total_issues} SQL syntax compatibility issues")
        
        if sql_issues["sovereign_node_issues"] > 0:
            actions.append(f"Convert {sql_issues['sovereign_node_issues']} sovereign node files to SQLite syntax")
            
        if sql_issues["persistent_node_issues"] > 0:
            actions.append(f"Convert {sql_issues['persistent_node_issues']} persistent node files to PostgreSQL syntax")
        
        # Unknown Files
        if len(unknown_files) > 0:
            actions.append(f"Classify {len(unknown_files)} unassigned files to proper architecture")
        
        # Critical Issues
        if sql_issues["critical_issues"]:
            actions.append("Address critical database syntax mismatches")
        
        self.results["action_items"] = actions
    
    def print_summary(self):
        """Print a clean, readable summary"""
        results = self.analyze_architecture()
        
        print("\n📊 ARCHITECTURE SUMMARY")
        print("=" * 40)
        
        arch = results["architecture_summary"]
        print(f"🗳️  Sovereign Node Files: {arch['sovereign_node_files']}")
        print(f"🌐 Persistent Node Files: {arch['persistent_node_files']}") 
        print(f"❓ Unclassified Files: {arch['unknown_shared_files']}")
        print(f"📁 Total Python Files: {arch['total_python_files']}")
        
        print("\n🔍 SQL COMPATIBILITY")
        print("=" * 40)
        sql = results["sql_compatibility"]
        print(f"✅ Sovereign Node Issues: {sql['sovereign_node_issues']}")
        print(f"✅ Persistent Node Issues: {sql['persistent_node_issues']}")
        print(f"✅ Unclassified File Issues: {sql['unknown_file_issues']}")
        
        if sql['critical_issues']:
            print(f"🚨 Critical Issues: {len(sql['critical_issues'])}")
            for issue in sql['critical_issues'][:3]:  # Show only first 3
                print(f"   • {issue}")
            if len(sql['critical_issues']) > 3:
                print(f"   ... and {len(sql['critical_issues']) - 3} more")
        
        print("\n🎯 RECOMMENDED ACTIONS")
        print("=" * 40)
        for i, action in enumerate(results["action_items"], 1):
            print(f"{i}. {action}")
        
        # Save detailed report
        report_file = self.senatai_path / "architecture_report.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Full report saved to: {report_file}")
        
        return results

def main():
    """Run the summary analysis"""
    analyzer = SenataiArchitectureSummary()
    results = analyzer.print_summary()
    
    # Simple health score
    total_issues = (results["sql_compatibility"]["sovereign_node_issues"] +
                   results["sql_compatibility"]["persistent_node_issues"] +
                   results["sql_compatibility"]["unknown_file_issues"])
    
    if total_issues == 0:
        print("\n🎉 Architecture is clean! No SQL syntax issues found.")
    else:
        print(f"\n⚠️  Found {total_issues} SQL syntax issues that need attention.")

if __name__ == "__main__":
    main()
