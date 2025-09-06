// Fix Unescaped Entities in JSX
const fs = require('fs');
const path = require('path');

// Files to fix
const filesToFix = [
  './app/demo/glassmorphism/page.tsx',
  './app/docs/glassmorphism/page.tsx'
];

// Function to fix apostrophes in JSX
function fixApostrophes(content) {
  // Replace ' with &apos; inside JSX attributes and text content
  return content.replace(/'([^']*)'(?=\s*[,:])/g, "&apos;$1&apos;")
               .replace(/'s\b/g, "&apos;s");
}

// Process each file
filesToFix.forEach(file => {
  const fullPath = path.join(process.cwd(), file);
  console.log(`Processing ${fullPath}...`);
  
  let content = fs.readFileSync(fullPath, 'utf8');
  const fixedContent = fixApostrophes(content);
  
  if (content !== fixedContent) {
    fs.writeFileSync(fullPath, fixedContent, 'utf8');
    console.log(`Fixed apostrophes in ${file}`);
  } else {
    console.log(`No changes needed in ${file}`);
  }
});

console.log('All files processed');
