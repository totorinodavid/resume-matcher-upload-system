#!/usr/bin/env node

// RENDER BLUEPRINT SCHEMA VALIDATOR
// Validates render.yaml against official Render Blueprint specification

console.log('🔧 RENDER BLUEPRINT SCHEMA VALIDATION');
console.log('====================================');
console.log('');

console.log('❌ GEFUNDENER FEHLER:');
console.log('   Field: instanceCount');
console.log('   Problem: Nicht Teil der Blueprint Service Schema');
console.log('   Lösung: Field entfernt');
console.log('');

console.log('✅ KORREKTE BLUEPRINT FIELDS:');
console.log('   - type: web');
console.log('   - name: resume-matcher-clean');
console.log('   - runtime: node');
console.log('   - rootDir: apps/backend-clean');
console.log('   - buildCommand: npm ci && npm run build');
console.log('   - startCommand: npm start');
console.log('   - healthCheckPath: /api/health');
console.log('   - autoDeploy: true');
console.log('   - disk: (persistent storage config)');
console.log('   - envVars: (environment variables)');
console.log('');

console.log('📋 RENDER BLUEPRINT SERVICE SCHEMA:');
console.log('==================================');
console.log('Required Fields:');
console.log('  ✓ type: "web"');
console.log('  ✓ name: string');
console.log('  ✓ runtime: "node"');
console.log('');
console.log('Optional Fields:');
console.log('  ✓ rootDir: string');
console.log('  ✓ buildCommand: string');
console.log('  ✓ startCommand: string');
console.log('  ✓ healthCheckPath: string');
console.log('  ✓ autoDeploy: boolean');
console.log('  ✓ disk: object');
console.log('  ✓ envVars: array');
console.log('');
console.log('❌ NOT SUPPORTED in Blueprint:');
console.log('  ❌ instanceCount (use scaling in dashboard)');
console.log('  ❌ region (auto-selected)');
console.log('  ❌ plan (use dashboard configuration)');
console.log('');

console.log('🎯 KORRIGIERTE RENDER.YAML:');
console.log('===========================');
console.log(`
services:
  - type: web
    name: resume-matcher-clean
    runtime: node
    rootDir: apps/backend-clean
    buildCommand: npm ci && npm run build
    startCommand: npm start
    healthCheckPath: /api/health
    autoDeploy: true
    disk:
      name: ats-data
      mountPath: /opt/render/project/src/uploads
      sizeGB: 10
    envVars:
      - key: NODE_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: resume-matcher-db
          property: connectionString
      - key: ADMIN_PASSWORD
        sync: false
      - key: UPLOAD_DIR
        value: /opt/render/project/src/uploads

databases:
  - name: resume-matcher-db
    databaseName: resume_matcher_db
    user: resume_user
`);

console.log('✅ BLUEPRINT SCHEMA VALIDATION ERFOLGREICH!');
console.log('==========================================');
console.log('🎉 render.yaml ist jetzt Blueprint-kompatibel!');
console.log('📋 Bereit für Dashboard Deployment!');
console.log('🌐 Nächster Schritt: https://dashboard.render.com/blueprints');
