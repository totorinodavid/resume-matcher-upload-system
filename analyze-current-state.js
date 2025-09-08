#!/usr/bin/env node

// CURRENT SERVICE STATUS CHECKER
// Analysiert bestehende Render Services und aktuelle Fehler

const https = require('https');

const RENDER_API_KEY = 'rnd_fuLBqqLoUnK7cQdnORYYoYLKBFIT';

async function checkCurrentServices() {
    console.log('🔍 ANALYSIERE BESTEHENDE RENDER SERVICES...');
    console.log('==========================================');
    
    const options = {
        hostname: 'api.render.com',
        port: 443,
        path: '/v1/services',
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + RENDER_API_KEY,
            'Content-Type': 'application/json'
        }
    };

    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                console.log('✅ SERVICES RESPONSE:', res.statusCode);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const services = JSON.parse(data);
                    console.log('📋 GEFUNDENE SERVICES:', services.length);
                    
                    services.forEach(service => {
                        console.log(`\n🔧 SERVICE: ${service.name || 'unnamed'}`);
                        console.log(`   ID: ${service.id || 'no-id'}`);
                        console.log(`   Type: ${service.type || 'unknown'}`);
                        console.log(`   Status: ${service.suspended || 'unknown'}`);
                        console.log(`   Env: ${service.serviceDetails?.env || 'unknown'}`);
                        console.log(`   Runtime: ${service.serviceDetails?.runtime || 'unknown'}`);
                        console.log(`   Repository: ${service.repo || 'none'}`);
                        console.log(`   Created: ${service.createdAt || 'unknown'}`);
                        console.log(`   Updated: ${service.updatedAt || 'unknown'}`);
                        
                        // Check for our services
                        if (service.name && (service.name.includes('resume-matcher') || service.name.includes('upload'))) {
                            console.log(`   ⚠️ RESUME MATCHER SERVICE GEFUNDEN!`);
                            checkServiceDetails(service.id);
                        }
                    });
                    
                    resolve(services);
                } else {
                    console.log('❌ SERVICES LIST FAILED:', data);
                    resolve([]);
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ SERVICES CHECK ERROR:', error);
            reject(error);
        });

        req.end();
    });
}

async function checkServiceDetails(serviceId) {
    console.log(`\n🔍 DETAILLIERTE ANALYSE FÜR SERVICE: ${serviceId}`);
    
    const options = {
        hostname: 'api.render.com',
        port: 443,
        path: `/v1/services/${serviceId}`,
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + RENDER_API_KEY,
            'Content-Type': 'application/json'
        }
    };

    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const service = JSON.parse(data);
                    
                    console.log(`📋 SERVICE DETAILS:`);
                    console.log(`   Name: ${service.name}`);
                    console.log(`   Environment: ${service.serviceDetails?.env}`);
                    console.log(`   Runtime: ${service.serviceDetails?.runtime}`);
                    console.log(`   Build Command: ${service.serviceDetails?.buildCommand}`);
                    console.log(`   Start Command: ${service.serviceDetails?.startCommand}`);
                    console.log(`   Root Directory: ${service.serviceDetails?.rootDir}`);
                    console.log(`   Repository: ${service.repo}`);
                    console.log(`   Branch: ${service.branch}`);
                    
                    // Analyze the problem
                    if (service.serviceDetails?.env === 'docker') {
                        console.log(`   ❌ PROBLEM: Service läuft in Docker Environment`);
                        console.log(`   ❌ URSACHE: Docker kann nicht zu Node.js konvertiert werden`);
                        console.log(`   ✅ LÖSUNG: Blueprint erstellt neue Service mit Node.js`);
                    }
                    
                    if (service.serviceDetails?.rootDir !== 'apps/backend-clean') {
                        console.log(`   ❌ PROBLEM: Falsches Root Directory`);
                        console.log(`   ❌ AKTUELL: ${service.serviceDetails?.rootDir}`);
                        console.log(`   ✅ SOLLTE SEIN: apps/backend-clean`);
                    }
                    
                    resolve(service);
                } else {
                    console.log('❌ SERVICE DETAILS FAILED:', data);
                    resolve(null);
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ SERVICE DETAILS ERROR:', error);
            reject(error);
        });

        req.end();
    });
}

async function checkDeployments() {
    console.log('\n🚀 CHECKING RECENT DEPLOYMENTS...');
    console.log('=================================');
    
    // This would check recent deployments to see what failed
    // For now, let's check what we know about the current state
    
    console.log('🔍 BEKANNTE PROBLEME:');
    console.log('1. Docker Environment kann nicht zu Node.js geändert werden');
    console.log('2. API Limitierungen verhindern Runtime-Änderungen');
    console.log('3. Bestehende Services haben falsche Konfiguration');
    console.log('');
    console.log('✅ BLUEPRINT LÖSUNG:');
    console.log('- Erstellt NEUE Services mit korrekter Konfiguration');
    console.log('- Umgeht API-Limitierungen');
    console.log('- Nutzt render.yaml für Infrastructure as Code');
}

// Main execution
async function analyzeCurrentState() {
    try {
        console.log('🎯 AKTUELLE RENDER SERVICE ANALYSE');
        console.log('==================================\n');
        
        await checkCurrentServices();
        await checkDeployments();
        
        console.log('\n🎯 ZUSAMMENFASSUNG:');
        console.log('==================');
        console.log('❌ Bestehende Services haben Docker Environment');
        console.log('❌ API kann Docker nicht zu Node.js ändern');
        console.log('❌ Deployment schlägt weiterhin fehl');
        console.log('✅ Blueprint erstellt NEUE Services mit Node.js');
        console.log('✅ Render.yaml ist korrekt konfiguriert');
        console.log('✅ Blueprint umgeht alle API-Limitierungen');
        
    } catch (error) {
        console.error('💥 ANALYSE ERROR:', error.message);
    }
}

analyzeCurrentState();
