#!/usr/bin/env node

/**
 * Asset Optimization Script
 * Converts PNG images to WebP format with quality optimization
 * Part of Resume Matcher repository size reduction initiative
 */

const imagemin = require('imagemin');
const imageminWebp = require('imagemin-webp');
const imageminPng = require('imagemin-png');
const fs = require('fs');
const path = require('path');

async function optimizeAssets() {
  const assetsDir = path.join(__dirname, '..', 'assets');
  const outputDir = path.join(__dirname, '..', 'assets', 'optimized');
  
  // Ensure output directory exists
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  console.log('🖼️  Starting asset optimization...');
  console.log(`📁 Source: ${assetsDir}`);
  console.log(`📁 Output: ${outputDir}`);
  
  try {
    // Convert PNG files to WebP with 80% quality
    const webpFiles = await imagemin([`${assetsDir}/*.png`], {
      destination: outputDir,
      plugins: [
        imageminWebp({
          quality: 80,
          method: 6, // Best compression
          lossless: false
        })
      ]
    });
    
    console.log('✅ WebP Conversion Results:');
    for (const file of webpFiles) {
      const originalPath = file.sourcePath;
      const originalSize = fs.statSync(originalPath).size;
      const newSize = file.data.length;
      const savings = ((originalSize - newSize) / originalSize * 100).toFixed(1);
      
      console.log(`   ${path.basename(originalPath)} → ${path.basename(file.destinationPath)}`);
      console.log(`   Size: ${(originalSize/1024/1024).toFixed(2)}MB → ${(newSize/1024/1024).toFixed(2)}MB (${savings}% savings)`);
    }
    
    // Calculate total savings
    const totalOriginal = webpFiles.reduce((sum, file) => 
      sum + fs.statSync(file.sourcePath).size, 0);
    const totalOptimized = webpFiles.reduce((sum, file) => 
      sum + file.data.length, 0);
    const totalSavings = ((totalOriginal - totalOptimized) / totalOriginal * 100).toFixed(1);
    
    console.log('\n📊 Optimization Summary:');
    console.log(`   Original total: ${(totalOriginal/1024/1024).toFixed(2)}MB`);
    console.log(`   Optimized total: ${(totalOptimized/1024/1024).toFixed(2)}MB`);
    console.log(`   Total savings: ${totalSavings}% (${((totalOriginal-totalOptimized)/1024/1024).toFixed(2)}MB)`);
    
    // Create usage documentation
    const usageDoc = `# Optimized Assets Usage

## Generated WebP Files
${webpFiles.map(file => `- ${path.basename(file.destinationPath)}`).join('\n')}

## Frontend Implementation
\`\`\`typescript
// Replace PNG imports with WebP versions
import optimizedImage from '/assets/optimized/${path.basename(webpFiles[0].destinationPath)}';

// Or use dynamic imports with fallback
const getOptimizedImage = (name: string) => {
  const webpPath = \`/assets/optimized/\${name.replace('.png', '.webp')}\`;
  const fallbackPath = \`/assets/\${name}\`;
  
  return {
    webp: webpPath,
    fallback: fallbackPath
  };
};
\`\`\`

## HTML Usage with Fallback
\`\`\`html
<picture>
  <source srcset="/assets/optimized/features.webp" type="image/webp">
  <img src="/assets/features.png" alt="Features" loading="lazy">
</picture>
\`\`\`
`;
    
    fs.writeFileSync(path.join(outputDir, 'README.md'), usageDoc);
    console.log('📝 Created usage documentation: assets/optimized/README.md');
    
  } catch (error) {
    console.error('❌ Optimization failed:', error);
    process.exit(1);
  }
}

// Self-check and install dependencies if needed
async function checkDependencies() {
  try {
    require('imagemin');
    require('imagemin-webp');
    return true;
  } catch (error) {
    console.log('📦 Installing optimization dependencies...');
    const { execSync } = require('child_process');
    
    try {
      execSync('npm install imagemin imagemin-webp imagemin-png --save-dev', { 
        stdio: 'inherit',
        cwd: path.join(__dirname, '..', 'apps', 'frontend')
      });
      return true;
    } catch (installError) {
      console.error('❌ Failed to install dependencies:', installError.message);
      console.log('💡 Please run manually: npm install imagemin imagemin-webp imagemin-png --save-dev');
      return false;
    }
  }
}

// Main execution
async function main() {
  console.log('🚀 Resume Matcher Asset Optimizer');
  console.log('   Reducing repository size through WebP conversion\n');
  
  const depsOk = await checkDependencies();
  if (!depsOk) {
    process.exit(1);
  }
  
  await optimizeAssets();
  
  console.log('\n✅ Asset optimization complete!');
  console.log('💡 Next steps:');
  console.log('   1. Update frontend components to use WebP files');
  console.log('   2. Add progressive enhancement with <picture> elements');
  console.log('   3. Replace PNG references in documentation');
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { optimizeAssets };
