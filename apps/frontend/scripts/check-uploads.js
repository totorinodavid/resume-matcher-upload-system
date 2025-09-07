#!/usr/bin/env node

// Einfaches Node.js-Script um Uploads zu überprüfen
// Ausführen mit: node check-uploads.js

const { PrismaClient } = require('@prisma/client')
const fs = require('fs')
const path = require('path')

const prisma = new PrismaClient()

async function checkUploads() {
  try {
    console.log('🔍 Überprüfe Upload-Status...\n')
    
    // 1. Datenbank-Uploads
    const uploads = await prisma.upload.findMany({
      orderBy: { createdAt: 'desc' },
      take: 10
    })
    
    console.log(`📊 Gefundene Uploads in DB: ${uploads.length}`)
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    
    for (const upload of uploads) {
      console.log(`📄 ${upload.originalFilename}`)
      console.log(`   ID: ${upload.id}`)
      console.log(`   Typ: ${upload.kind}`)
      console.log(`   Größe: ${upload.sizeBytes ? Number(upload.sizeBytes) / 1024 / 1024 : '?'} MB`)
      console.log(`   Erstellt: ${upload.createdAt}`)
      console.log(`   Storage: ${upload.storageKey}`)
      
      // Überprüfe ob Datei existiert
      if (upload.storageKey.startsWith('disk://')) {
        const filePath = path.join(
          process.env.FILES_DIR || '/var/data',
          upload.storageKey.slice(7)
        )
        
        try {
          const stats = fs.statSync(filePath)
          console.log(`   ✅ Datei existiert (${stats.size} bytes)`)
        } catch {
          console.log(`   ❌ Datei nicht gefunden`)
        }
      }
      console.log('')
    }
    
    // 2. Statistiken
    const stats = await prisma.upload.aggregate({
      _count: true,
      _sum: { sizeBytes: true }
    })
    
    console.log('📈 Upload-Statistiken:')
    console.log(`   Gesamt: ${stats._count} Dateien`)
    console.log(`   Gesamtgröße: ${stats._sum.sizeBytes ? Number(stats._sum.sizeBytes) / 1024 / 1024 : 0} MB`)
    
    // 3. Nach Typ gruppiert
    const byKind = await prisma.upload.groupBy({
      by: ['kind'],
      _count: true,
      _sum: { sizeBytes: true }
    })
    
    console.log('\n📋 Nach Typ:')
    for (const group of byKind) {
      console.log(`   ${group.kind}: ${group._count} Dateien, ${group._sum.sizeBytes ? Number(group._sum.sizeBytes) / 1024 / 1024 : 0} MB`)
    }
    
  } catch (error) {
    console.error('❌ Fehler:', error.message)
  } finally {
    await prisma.$disconnect()
  }
}

// Nur ausführen wenn direkt aufgerufen
if (require.main === module) {
  checkUploads()
}

module.exports = { checkUploads }
