#!/usr/bin/env python3
"""
Senatai Comprehensive Diagnostic Tool
Scans the entire ~/senatai folder and provides system health reporting
"""

import os
import sys
import psycopg2
import sqlite3
import yaml
import json
import logging
from pathlib import Path
from datetime import datetime
import subprocess
import glob

class SenataiDiagnostic:
    def __init__(self, senatai_path="~/senatai"):
        self.senatai_path = Path(senatai_path).expanduser()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system_health": {},
            "issues": [],
            "recommendations": []
        }
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(self.senatai_path / 'diagnostic.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def log(self, message, level="INFO"):
        """Log message and store in results"""
        getattr(self.logger, level.lower())(message)
        
        if level.upper() in ["WARNING", "ERROR"]:
            self.results["issues"].append({
                "level": level.upper(),
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
    
    def check_folder_structure(self):
        """Verify essential folder structure exists"""
        self.log("Checking folder structure...")
        
        essential_folders = [
            "data",
            "scripts", 
            "config",
            "logs",
            "backups"
        ]
        
        for folder in essential_folders:
            folder_path = self.senatai_path / folder
            if folder_path.exists():
                self.results["system_health"][f"folder_{folder}"] = "OK"
                self.log(f"✓ Folder exists: {folder}")
            else:
                self.results["system_health"][f"folder_{folder}"] = "MISSING"
                self.log(f"✗ Missing folder: {folder}", "WARNING")
                self.results["recommendations"].append(f"Create missing folder: {folder}")
    
    def check_config_files(self):
        """Check for essential configuration files"""
        self.log("Checking configuration files...")
        
        config_files = [
            "config/database.yaml",
            "config/api_keys.yaml", 
            "config/settings.yaml"
        ]
        
        for config_file in config_files:
            config_path = self.senatai_path / config_file
            if config_path.exists():
                self.results["system_health"][f"config_{Path(config_file).stem}"] = "OK"
                self.log(f"✓ Config file exists: {config_file}")
                
                # Validate YAML syntax
                try:
                    with open(config_path, 'r') as f:
                        yaml.safe_load(f)
                    self.log(f"✓ Valid YAML: {config_file}")
                except yaml.YAMLError as e:
                    self.log(f"✗ Invalid YAML in {config_file}: {e}", "ERROR")
            else:
                self.results["system_health"][f"config_{Path(config_file).stem}"] = "MISSING"
                self.log(f"✗ Missing config file: {config_file}", "WARNING")
    
    def check_python_scripts(self):
        """Check Python scripts for syntax errors"""
        self.log("Checking Python scripts...")
        
        python_files = glob.glob(str(self.senatai_path / "**" / "*.py"), recursive=True)
        
        for py_file in python_files:
            try:
                with open(py_file, 'r') as f:
                    compile(f.read(), py_file, 'exec')
                self.log(f"✓ Valid Python: {Path(py_file).relative_to(self.senatai_path)}")
            except SyntaxError as e:
                self.log(f"✗ Syntax error in {py_file}: {e}", "ERROR")
    
    def check_database_connections(self):
        """Check both PostgreSQL and SQLite database connections"""
        self.log("Checking database connections...")
        
        # PostgreSQL Connection Check
        try:
            conn = psycopg2.connect(
                dbname="openparliament",
                user="dan",
                password="senatai2025",
                host="localhost"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            self.log(f"✓ PostgreSQL connected: {version[0].split(',')[0]}")
            self.results["system_health"]["postgresql"] = "OK"
            
            # Run duplicate bills check
            self.check_duplicate_bills(cursor)
            
            cursor.close()
            conn.close()
        except Exception as e:
            self.log(f"✗ PostgreSQL connection failed: {e}", "ERROR")
            self.results["system_health"]["postgresql"] = "ERROR"
    
    def check_duplicate_bills(self, cursor):
        """Check for duplicate bill handling in PostgreSQL"""
        try:
            cursor.execute("""
                SELECT original_bill_number, COUNT(*) 
                FROM legislation 
                GROUP BY original_bill_number 
                HAVING COUNT(*) > 1 
                ORDER BY COUNT(*) DESC 
                LIMIT 10;
            """)
            duplicates = cursor.fetchall()
            
            if duplicates:
                self.log(f"Duplicate bills found: {len(duplicates)} bill numbers have multiple versions")
                for bill_num, count in duplicates:
                    self.log(f"  📄 {bill_num}: {count} versions")
                
                self.results["system_health"]["duplicate_bills"] = f"{len(duplicates)} duplicates"
            else:
                self.log("No duplicate bill numbers found")
                self.results["system_health"]["duplicate_bills"] = "OK"
                
        except Exception as e:
            self.log(f"Duplicate bill check failed: {e}", "WARNING")
    
    def check_data_files(self):
        """Check data files integrity"""
        self.log("Checking data files...")
        
        data_patterns = [
            "data/*.json",
            "data/*.csv", 
            "data/*.xml",
            "data/**/*.json",
            "data/**/*.csv"
        ]
        
        data_files = []
        for pattern in data_patterns:
            data_files.extend(glob.glob(str(self.senatai_path / pattern), recursive=True))
        
        valid_files = 0
        for data_file in data_files:
            try:
                if data_file.endswith('.json'):
                    with open(data_file, 'r') as f:
                        json.load(f)
                # Add validation for other file types as needed
                valid_files += 1
                self.log(f"✓ Valid data file: {Path(data_file).relative_to(self.senatai_path)}")
            except Exception as e:
                self.log(f"✗ Invalid data file {data_file}: {e}", "WARNING")
        
        self.results["system_health"]["data_files"] = f"{valid_files}/{len(data_files)} valid"
    
    def check_system_resources(self):
        """Check system resources and permissions"""
        self.log("Checking system resources...")
        
        # Check disk space
        try:
            result = subprocess.run(['df', '-h', str(self.senatai_path)], 
                                  capture_output=True, text=True)
            self.log(f"Disk space:\n{result.stdout}")
        except Exception as e:
            self.log(f"Disk space check failed: {e}", "WARNING")
        
        # Check folder permissions
        try:
            stat_info = os.stat(self.senatai_path)
            self.log(f"Folder permissions: {oct(stat_info.st_mode)[-3:]}")
        except Exception as e:
            self.log(f"Permission check failed: {e}", "WARNING")
    
    def check_recent_activity(self):
        """Check for recent file modifications"""
        self.log("Checking recent activity...")
        
        recent_files = []
        for pattern in ["**/*.py", "**/*.yaml", "**/*.json"]:
            for file_path in glob.glob(str(self.senatai_path / pattern), recursive=True):
                file_stat = os.stat(file_path)
                mod_time = datetime.fromtimestamp(file_stat.st_mtime)
                if (datetime.now() - mod_time).days < 7:  # Last 7 days
                    recent_files.append((file_path, mod_time))
        
        recent_files.sort(key=lambda x: x[1], reverse=True)
        
        self.log(f"Recently modified files (last 7 days): {len(recent_files)}")
        for file_path, mod_time in recent_files[:5]:  # Top 5 most recent
            self.log(f"  📝 {Path(file_path).relative_to(self.senatai_path)} - {mod_time.strftime('%Y-%m-%d %H:%M')}")
    
    def generate_report(self):
        """Generate comprehensive diagnostic report"""
        report = {
            "diagnostic_report": self.results,
            "summary": {
                "total_issues": len(self.results["issues"]),
                "errors": len([i for i in self.results["issues"] if i["level"] == "ERROR"]),
                "warnings": len([i for i in self.results["issues"] if i["level"] == "WARNING"]),
                "health_score": self.calculate_health_score()
            }
        }
        
        # Save report to file
        report_file = self.senatai_path / "diagnostic_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def calculate_health_score(self):
        """Calculate overall system health score"""
        total_checks = len(self.results["system_health"])
        ok_checks = len([v for v in self.results["system_health"].values() 
                        if v == "OK" or "valid" in str(v).lower()])
        
        return round((ok_checks / total_checks) * 100) if total_checks > 0 else 0
    
    def run_comprehensive_diagnostic(self):
        """Run all diagnostic checks"""
        self.log("=" * 60)
        self.log("SENATAI COMPREHENSIVE DIAGNOSTIC")
        self.log("=" * 60)
        
        checks = [
            self.check_folder_structure,
            self.check_config_files,
            self.check_python_scripts,
            self.check_database_connections,
            self.check_data_files,
            self.check_system_resources,
            self.check_recent_activity
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                self.log(f"Check {check.__name__} failed: {e}", "ERROR")
        
        report = self.generate_report()
        
        # Print summary
        self.log("=" * 60)
        self.log("DIAGNOSTIC SUMMARY")
        self.log("=" * 60)
        self.log(f"Health Score: {report['summary']['health_score']}%")
        self.log(f"Total Issues: {report['summary']['total_issues']}")
        self.log(f"Errors: {report['summary']['errors']}")
        self.log(f"Warnings: {report['summary']['warnings']}")
        
        if report['summary']['errors'] > 0:
            self.log("❌ System needs attention - critical errors found", "ERROR")
        elif report['summary']['warnings'] > 0:
            self.log("⚠️  System operational but has warnings", "WARNING")
        else:
            self.log("✅ System is healthy")
        
        self.log(f"Full report saved to: {self.senatai_path / 'diagnostic_report.json'}")
        
        return report

def main():
    """Main execution function"""
    diagnostic = SenataiDiagnostic()
    report = diagnostic.run_comprehensive_diagnostic()
    
    # Exit with appropriate code
    if report['summary']['errors'] > 0:
        sys.exit(1)
    elif report['summary']['warnings'] > 0:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
