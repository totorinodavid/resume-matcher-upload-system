// Comprehensive fix for unescaped entities
const fs = require('fs');
const path = require('path');

// Files to fix
const filePaths = [
  path.join(process.cwd(), 'app', 'docs', 'glassmorphism', 'page.tsx')
];

function fixFile(filePath) {
  console.log(`Processing: ${filePath}`);
  const content = fs.readFileSync(filePath, 'utf8');
  
  // Fix all single quotes within JSX attributes and content
  let fixedContent = content.replace(/([<][^>]*[>].*?)'/g, (match, p1) => {
    return p1 + '&apos;';
  });
  
  // Fix remaining apostrophes in content
  fixedContent = fixedContent.replace(/: '([^']*)'(?=[,\s}])/g, ': &apos;$1&apos;');
  fixedContent = fixedContent.replace(/'([^']*)'(?=[,\s])/g, '&apos;$1&apos;');
  
  // Write changes back to file
  if (content !== fixedContent) {
    fs.writeFileSync(filePath, fixedContent, 'utf8');
    console.log(`Fixed apostrophes in ${filePath}`);
    return true;
  }
  
  console.log(`No changes needed in ${filePath}`);
  return false;
}

// Process all files
let changesCount = 0;
filePaths.forEach(filePath => {
  if (fixFile(filePath)) {
    changesCount++;
  }
});

console.log(`Fixed ${changesCount} files.`);
