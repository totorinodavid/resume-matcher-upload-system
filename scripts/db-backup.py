#!/usr/bin/env python3
"""
Credits System Database Backup Utility
Python script for creating PostgreSQL backups compatible with Render and other cloud providers
Usage: python scripts/db-backup.py [--compress] [--output-dir=backups]
"""

import os
import sys
import subprocess
import argparse
import logging
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import gzip
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backup.log')
    ]
)
logger = logging.getLogger(__name__)

class DatabaseBackup:
    def __init__(self, database_url: str, output_dir: str = "backups", compress: bool = True):
        self.database_url = database_url
        self.output_dir = Path(output_dir)
        self.compress = compress
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)
        
        # Parse database URL
        self.parsed_url = urlparse(database_url)
        
    def check_pg_dump(self) -> bool:
        """Check if pg_dump is available in the system"""
        try:
            result = subprocess.run(['pg_dump', '--version'], 
                                 capture_output=True, text=True, check=True)
            logger.info(f"Found pg_dump: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("pg_dump not found. Please install PostgreSQL client tools.")
            return False
    
    def get_backup_filename(self) -> str:
        """Generate backup filename with timestamp"""
        base_name = f"resume_matcher_backup_{self.timestamp}"
        if self.compress:
            return f"{base_name}.sql.gz"
        else:
            return f"{base_name}.sql"
    
    def create_backup(self) -> tuple[bool, str]:
        """Create database backup using pg_dump"""
        if not self.check_pg_dump():
            return False, "pg_dump not available"
        
        backup_file = self.output_dir / self.get_backup_filename()
        
        try:
            logger.info(f"Creating backup: {backup_file}")
            logger.info(f"Database: {self.parsed_url.hostname}:{self.parsed_url.port}")
            
            # Build pg_dump command
            cmd = [
                'pg_dump',
                '--verbose',
                '--no-owner',
                '--no-privileges',
                '--clean',
                '--if-exists',
                self.database_url
            ]
            
            # Execute pg_dump
            with open(backup_file if not self.compress else backup_file.with_suffix('.sql'), 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                logger.error(f"pg_dump failed: {result.stderr}")
                return False, f"pg_dump error: {result.stderr}"
            
            # Compress if requested
            if self.compress:
                sql_file = backup_file.with_suffix('.sql')
                logger.info("Compressing backup...")
                with open(sql_file, 'rb') as f_in:
                    with gzip.open(backup_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove uncompressed file
                sql_file.unlink()
            
            backup_size = backup_file.stat().st_size
            logger.info(f"✅ Backup created successfully: {backup_file}")
            logger.info(f"📁 Size: {backup_size / (1024*1024):.2f} MB")
            
            return True, str(backup_file)
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            return False, str(e)
    
    def verify_backup(self, backup_file: str) -> bool:
        """Verify backup file integrity"""
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_file}")
                return False
            
            if backup_path.suffix == '.gz':
                # Test gzip file
                with gzip.open(backup_path, 'rt') as f:
                    # Read first few lines to verify it's a valid SQL dump
                    for i, line in enumerate(f):
                        if i > 10:  # Read first 10 lines
                            break
                        if 'PostgreSQL database dump' in line:
                            logger.info("✅ Backup file appears to be valid")
                            return True
            else:
                # Test plain SQL file
                with open(backup_path, 'r') as f:
                    first_lines = [f.readline() for _ in range(10)]
                    if any('PostgreSQL database dump' in line for line in first_lines):
                        logger.info("✅ Backup file appears to be valid")
                        return True
            
            logger.warning("⚠️ Backup file may be corrupted or invalid")
            return False
            
        except Exception as e:
            logger.error(f"Backup verification failed: {str(e)}")
            return False
    
    def list_backups(self) -> list:
        """List all existing backup files"""
        backups = []
        for file in self.output_dir.glob("resume_matcher_backup_*.sql*"):
            stat = file.stat()
            backups.append({
                'file': file.name,
                'path': str(file),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_mtime)
            })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups
    
    def cleanup_old_backups(self, keep_count: int = 5) -> int:
        """Remove old backup files, keeping only the specified number"""
        backups = self.list_backups()
        if len(backups) <= keep_count:
            logger.info(f"No cleanup needed. Found {len(backups)} backups (keeping {keep_count})")
            return 0
        
        to_remove = backups[keep_count:]
        removed_count = 0
        
        for backup in to_remove:
            try:
                Path(backup['path']).unlink()
                logger.info(f"🗑️ Removed old backup: {backup['file']}")
                removed_count += 1
            except Exception as e:
                logger.error(f"Failed to remove {backup['file']}: {str(e)}")
        
        logger.info(f"Cleanup complete. Removed {removed_count} old backups")
        return removed_count

def load_database_url() -> str:
    """Load DATABASE_URL from environment or .env files"""
    # First check environment variable
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        return db_url
    
    # Check .env files
    env_files = ['.env', '.env.local', 'apps/backend/.env']
    for env_file in env_files:
        if Path(env_file).exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('DATABASE_URL='):
                            return line.split('=', 1)[1].strip('"\'')
            except Exception as e:
                logger.warning(f"Could not read {env_file}: {str(e)}")
    
    return None

def main():
    parser = argparse.ArgumentParser(description='Resume Matcher Database Backup Utility')
    parser.add_argument('--compress', action='store_true', default=True,
                       help='Compress backup with gzip (default: True)')
    parser.add_argument('--no-compress', action='store_true',
                       help='Do not compress backup')
    parser.add_argument('--output-dir', default='backups',
                       help='Output directory for backups (default: backups)')
    parser.add_argument('--database-url',
                       help='Database URL (if not provided, will load from environment)')
    parser.add_argument('--list', action='store_true',
                       help='List existing backups')
    parser.add_argument('--cleanup', type=int, metavar='N',
                       help='Keep only N most recent backups, remove others')
    parser.add_argument('--verify', metavar='BACKUP_FILE',
                       help='Verify integrity of specific backup file')
    
    args = parser.parse_args()
    
    # Handle compress options
    compress = args.compress and not args.no_compress
    
    # Load database URL
    database_url = args.database_url or load_database_url()
    if not database_url:
        logger.error("❌ DATABASE_URL not found. Please set it in environment or .env file")
        sys.exit(1)
    
    # Create backup instance
    backup = DatabaseBackup(database_url, args.output_dir, compress)
    
    # Handle different actions
    if args.list:
        backups = backup.list_backups()
        if not backups:
            print("No backups found.")
        else:
            print(f"\n📁 Found {len(backups)} backups in {args.output_dir}:")
            print("-" * 70)
            for b in backups:
                size_mb = b['size'] / (1024*1024)
                print(f"{b['file']:<35} {size_mb:>8.2f} MB  {b['created']}")
        return
    
    if args.verify:
        success = backup.verify_backup(args.verify)
        sys.exit(0 if success else 1)
    
    if args.cleanup is not None:
        removed = backup.cleanup_old_backups(args.cleanup)
        print(f"Removed {removed} old backups")
        return
    
    # Create backup
    print("🚀 Resume Matcher Database Backup")
    print("=" * 35)
    
    success, result = backup.create_backup()
    
    if success:
        # Verify the backup
        if backup.verify_backup(result):
            print(f"\n✅ Backup completed successfully!")
            print(f"📄 File: {result}")
            
            # Show backup list
            backups = backup.list_backups()
            print(f"\n📚 Total backups: {len(backups)}")
            
            # Auto-cleanup if more than 10 backups
            if len(backups) > 10:
                removed = backup.cleanup_old_backups(5)
                print(f"🧹 Auto-cleanup: removed {removed} old backups")
        else:
            print(f"\n⚠️ Backup created but verification failed: {result}")
            sys.exit(1)
    else:
        print(f"\n❌ Backup failed: {result}")
        sys.exit(1)

if __name__ == '__main__':
    main()
