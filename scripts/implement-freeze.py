#!/usr/bin/env python3
"""
Credits System Frontend Freeze Implementation
Updates frontend components to respect CREDITS_WRITE_FREEZE flag
Usage: python scripts/implement-freeze.py [--verify-only]
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class FrontendFreezeImplementer:
    def __init__(self, frontend_dir: str = "apps/frontend"):
        self.frontend_dir = Path(frontend_dir)
        self.changes_made = []
        
    def find_credit_components(self) -> List[Path]:
        """Find components related to credit purchasing"""
        credit_patterns = [
            "**/credit*",
            "**/payment*", 
            "**/stripe*",
            "**/billing*",
            "**/purchase*"
        ]
        
        found_files = []
        for pattern in credit_patterns:
            found_files.extend(self.frontend_dir.glob(pattern))
        
        # Filter for TypeScript/React files
        tsx_files = [f for f in found_files if f.suffix in ['.ts', '.tsx', '.js', '.jsx']]
        
        logger.info(f"Found {len(tsx_files)} credit-related component files")
        return tsx_files
    
    def check_freeze_implementation(self, file_path: Path) -> Dict:
        """Check if file already implements freeze logic"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            has_freeze_check = 'CREDITS_WRITE_FREEZE' in content
            has_env_import = 'process.env' in content
            has_disabled_state = 'disabled' in content.lower()
            
            return {
                'has_freeze_check': has_freeze_check,
                'has_env_import': has_env_import,
                'has_disabled_state': has_disabled_state,
                'needs_update': not has_freeze_check
            }
            
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return {'error': str(e)}
    
    def add_freeze_logic(self, file_path: Path) -> bool:
        """Add freeze logic to a component file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Skip if already has freeze logic
            if 'CREDITS_WRITE_FREEZE' in content:
                logger.info(f"Freeze logic already present in {file_path.name}")
                return False
            
            # Common patterns to look for
            patterns_to_update = [
                ('onClick={handlePurchase}', 'onClick={isFrozen ? undefined : handlePurchase}'),
                ('disabled={loading}', 'disabled={loading || isFrozen}'),
                ('disabled={!isValid}', 'disabled={!isValid || isFrozen}'),
                ('<Button', '<Button disabled={isFrozen}'),
                ('type="submit"', 'type="submit" disabled={isFrozen}')
            ]
            
            # Add freeze check at top of component
            freeze_check = """
  // Credits system freeze check
  const isFrozen = process.env.NEXT_PUBLIC_CREDITS_WRITE_FREEZE === '1';
  
  // Show freeze message if system is frozen
  if (isFrozen) {
    return (
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex">
          <div className="flex-shrink-0">
            ⚠️
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              Credits System Temporarily Unavailable
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              We're updating our credits system. Credit purchases are temporarily disabled.
              Please check back soon.
            </div>
          </div>
        </div>
      </div>
    );
  }
"""
            
            # Find where to insert freeze check (after imports, before component)
            lines = content.split('\n')
            insert_line = 0
            
            # Find last import or first function/const declaration
            for i, line in enumerate(lines):
                if (line.strip().startswith('import ') or 
                    line.strip().startswith('const ') or 
                    line.strip().startswith('function ') or
                    line.strip().startswith('export ')):
                    insert_line = i + 1
            
            # Insert freeze check
            lines.insert(insert_line, freeze_check)
            updated_content = '\n'.join(lines)
            
            # Apply pattern updates
            for old_pattern, new_pattern in patterns_to_update:
                if old_pattern in updated_content:
                    updated_content = updated_content.replace(old_pattern, new_pattern)
                    logger.info(f"Updated pattern: {old_pattern} -> {new_pattern}")
            
            # Write back to file
            file_path.write_text(updated_content, encoding='utf-8')
            self.changes_made.append(str(file_path))
            logger.info(f"✅ Added freeze logic to {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating {file_path}: {e}")
            return False
    
    def update_env_example(self) -> bool:
        """Update .env.example to include freeze flag"""
        env_example = self.frontend_dir / '.env.example'
        if not env_example.exists():
            env_example = Path('.env.example')
        
        if env_example.exists():
            try:
                content = env_example.read_text()
                if 'CREDITS_WRITE_FREEZE' not in content:
                    content += '\n# Credits system freeze flag (1 = frozen, 0 = active)\nNEXT_PUBLIC_CREDITS_WRITE_FREEZE=0\n'
                    env_example.write_text(content)
                    logger.info("✅ Updated .env.example with freeze flag")
                    return True
            except Exception as e:
                logger.error(f"Error updating .env.example: {e}")
        
        return False
    
    def create_freeze_hook(self) -> bool:
        """Create a custom hook for freeze detection"""
        hooks_dir = self.frontend_dir / 'lib' / 'hooks'
        hooks_dir.mkdir(parents=True, exist_ok=True)
        
        hook_file = hooks_dir / 'useCreditsFreeze.ts'
        
        hook_content = '''import { useMemo } from 'react';

/**
 * Custom hook to check if credits system is frozen
 * @returns {object} Object containing freeze status and message
 */
export function useCreditsFreeze() {
  const isFrozen = useMemo(() => {
    return process.env.NEXT_PUBLIC_CREDITS_WRITE_FREEZE === '1';
  }, []);

  const freezeMessage = useMemo(() => {
    if (!isFrozen) return null;
    
    return {
      title: 'Credits System Temporarily Unavailable',
      description: 'We\\'re updating our credits system. Credit purchases are temporarily disabled. Please check back soon.',
      type: 'warning' as const
    };
  }, [isFrozen]);

  return {
    isFrozen,
    freezeMessage,
    isActive: !isFrozen
  };
}

/**
 * HOC to wrap components with freeze check
 */
export function withFreeze<T extends object>(
  Component: React.ComponentType<T>,
  fallbackComponent?: React.ComponentType
) {
  return function WrappedComponent(props: T) {
    const { isFrozen, freezeMessage } = useCreditsFreeze();
    
    if (isFrozen) {
      if (fallbackComponent) {
        const FallbackComponent = fallbackComponent;
        return <FallbackComponent />;
      }
      
      return (
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex">
            <div className="flex-shrink-0">
              ⚠️
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">
                {freezeMessage?.title}
              </h3>
              <div className="mt-2 text-sm text-yellow-700">
                {freezeMessage?.description}
              </div>
            </div>
          </div>
        </div>
      );
    }
    
    return <Component {...props} />;
  };
}
'''
        
        try:
            hook_file.write_text(hook_content)
            logger.info(f"✅ Created freeze hook: {hook_file}")
            self.changes_made.append(str(hook_file))
            return True
        except Exception as e:
            logger.error(f"Error creating freeze hook: {e}")
            return False
    
    def verify_implementation(self) -> Dict:
        """Verify that freeze implementation is working"""
        results = {
            'components_checked': 0,
            'components_with_freeze': 0,
            'missing_freeze': [],
            'errors': []
        }
        
        credit_files = self.find_credit_components()
        
        for file_path in credit_files:
            results['components_checked'] += 1
            check_result = self.check_freeze_implementation(file_path)
            
            if 'error' in check_result:
                results['errors'].append(f"{file_path}: {check_result['error']}")
            elif check_result.get('has_freeze_check'):
                results['components_with_freeze'] += 1
            else:
                results['missing_freeze'].append(str(file_path))
        
        return results
    
    def run(self, verify_only: bool = False) -> bool:
        """Run the freeze implementation process"""
        logger.info("🚀 Credits Frontend Freeze Implementation")
        logger.info("=" * 45)
        
        if verify_only:
            logger.info("Running verification only...")
            results = self.verify_implementation()
            
            logger.info(f"📊 Verification Results:")
            logger.info(f"Components checked: {results['components_checked']}")
            logger.info(f"Components with freeze: {results['components_with_freeze']}")
            
            if results['missing_freeze']:
                logger.warning(f"❌ Missing freeze logic in {len(results['missing_freeze'])} files:")
                for file in results['missing_freeze']:
                    logger.warning(f"  - {file}")
            
            if results['errors']:
                logger.error("❌ Errors encountered:")
                for error in results['errors']:
                    logger.error(f"  - {error}")
            
            success_rate = results['components_with_freeze'] / max(results['components_checked'], 1) * 100
            logger.info(f"Success rate: {success_rate:.1f}%")
            
            return success_rate > 80
        
        else:
            logger.info("Implementing freeze logic...")
            
            # 1. Create freeze hook
            self.create_freeze_hook()
            
            # 2. Update .env.example
            self.update_env_example()
            
            # 3. Find and update credit components
            credit_files = self.find_credit_components()
            updated_count = 0
            
            for file_path in credit_files:
                if self.add_freeze_logic(file_path):
                    updated_count += 1
            
            logger.info(f"\n📊 Implementation Results:")
            logger.info(f"Files found: {len(credit_files)}")
            logger.info(f"Files updated: {updated_count}")
            logger.info(f"Files modified: {len(self.changes_made)}")
            
            if self.changes_made:
                logger.info("\n📝 Modified files:")
                for file in self.changes_made:
                    logger.info(f"  - {file}")
            
            # 4. Final verification
            logger.info("\n🔍 Running verification...")
            results = self.verify_implementation()
            success_rate = results['components_with_freeze'] / max(results['components_checked'], 1) * 100
            
            if success_rate > 80:
                logger.info(f"✅ Implementation successful! ({success_rate:.1f}% coverage)")
                return True
            else:
                logger.warning(f"⚠️ Implementation incomplete ({success_rate:.1f}% coverage)")
                return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Implement credits freeze in frontend')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify existing implementation, do not modify files')
    parser.add_argument('--frontend-dir', default='apps/frontend',
                       help='Frontend directory path (default: apps/frontend)')
    
    args = parser.parse_args()
    
    # Check if frontend directory exists
    frontend_path = Path(args.frontend_dir)
    if not frontend_path.exists():
        logger.error(f"Frontend directory not found: {frontend_path}")
        logger.info("Available directories:")
        for item in Path('.').iterdir():
            if item.is_dir():
                logger.info(f"  - {item}")
        sys.exit(1)
    
    implementer = FrontendFreezeImplementer(args.frontend_dir)
    success = implementer.run(verify_only=args.verify_only)
    
    if success:
        if not args.verify_only:
            logger.info("\n🎉 Freeze implementation complete!")
            logger.info("Next steps:")
            logger.info("1. Test credit purchase pages")
            logger.info("2. Verify freeze message displays correctly")
            logger.info("3. Set NEXT_PUBLIC_CREDITS_WRITE_FREEZE=1 in production")
        sys.exit(0)
    else:
        logger.error("\n❌ Implementation failed or incomplete")
        sys.exit(1)

if __name__ == '__main__':
    main()
