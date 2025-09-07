#!/usr/bin/env node
console.log('🔄 Running Prisma migrations...');

const { exec } = require('child_process');

exec('npx prisma migrate deploy', (error, stdout, stderr) => {
  if (error) {
    console.error('❌ Migration failed:', error);
    process.exit(1);
  }
  
  console.log('✅ Migrations completed:', stdout);
  if (stderr) console.log('Stderr:', stderr);
  
  console.log('🚀 Starting application...');
  process.exit(0);
});
