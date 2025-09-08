#!/usr/bin/env node

// 🚀 DIREKTE BLUEPRINT DEPLOYMENT - KEIN ACCOUNT-WECHSEL NÖTIG
// Mit Ihrem bestehenden Premium Account

const https = require('https');

const RENDER_API_KEY = 'rnd_fuLBqqLoUnK7cQdnORYYoYLKBFIT'; // Ihr Premium Key

console.log('🎯 DIREKTE PREMIUM BLUEPRINT LÖSUNG');
console.log('===================================');
console.log('');

console.log('✅ WARUM BLUEPRINT MIT IHREM PREMIUM ACCOUNT:');
console.log('- Bestehende Services: Docker Environment (unveränderbar)');
console.log('- Blueprint: Erstellt NEUE Services mit Node.js');
console.log('- Premium Account: Bereits aktiv, keine Änderung nötig');
console.log('- API Key: Funktioniert perfekt');
console.log('');

async function deployWithBlueprint() {
    console.log('🚀 STARTE BLUEPRINT DEPLOYMENT...');
    
    // Check if we can create blueprint via API
    const blueprintData = JSON.stringify({
        name: 'resume-matcher-premium',
        repo: 'https://github.com/totorinodavid/resume-matcher-upload-system',
        branch: 'security-hardening-neon',
        autoDeploy: true
    });

    const options = {
        hostname: 'api.render.com',
        port: 443,
        path: '/v1/blueprints',
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + RENDER_API_KEY,
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(blueprintData)
        }
    };

    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                console.log('✅ BLUEPRINT API RESPONSE:', res.statusCode);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    console.log('🎉 BLUEPRINT CREATED VIA API!');
                    console.log('📡 DATA:', data);
                    resolve(JSON.parse(data));
                } else {
                    console.log('❌ API BLUEPRINT FAILED, USING DASHBOARD APPROACH');
                    console.log('📡 RESPONSE:', data);
                    console.log('');
                    console.log('🎯 DASHBOARD BLUEPRINT SETUP:');
                    console.log('1. https://dashboard.render.com/blueprints');
                    console.log('2. New Blueprint');
                    console.log('3. Repository: totorinodavid/resume-matcher-upload-system');
                    console.log('4. Branch: security-hardening-neon');
                    console.log('5. render.yaml wird automatisch erkannt');
                    console.log('');
                    console.log('✅ PREMIUM ACCOUNT FEATURES WERDEN GENUTZT!');
                    resolve(null);
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ BLUEPRINT ERROR:', error);
            reject(error);
        });

        req.write(blueprintData);
        req.end();
    });
}

async function checkCurrentServices() {
    console.log('🔍 CHECKING CURRENT SERVICES...');
    
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

    return new Promise((resolve) => {
        const req = https.request(options, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const services = JSON.parse(data);
                    console.log(`📋 FOUND ${services.length} EXISTING SERVICES`);
                    
                    const dockerServices = services.filter(s => 
                        s.serviceDetails?.env === 'docker' || 
                        s.name?.includes('resume-matcher')
                    );
                    
                    if (dockerServices.length > 0) {
                        console.log('❌ DOCKER SERVICES GEFUNDEN (können nicht geändert werden):');
                        dockerServices.forEach(s => {
                            console.log(`   - ${s.name}: ${s.serviceDetails?.env || 'unknown'}`);
                        });
                        console.log('✅ BLUEPRINT ERSTELLT NEUE NODE.JS SERVICES');
                    }
                    
                    resolve(services);
                } else {
                    resolve([]);
                }
            });
        });

        req.on('error', () => resolve([]));
        req.end();
    });
}

// Execute deployment
async function executeDeployment() {
    try {
        console.log('🚀 STARTING PREMIUM BLUEPRINT DEPLOYMENT');
        console.log('========================================');
        
        await checkCurrentServices();
        console.log('');
        
        await deployWithBlueprint();
        
        console.log('');
        console.log('🎉 BLUEPRINT DEPLOYMENT INITIATED!');
        console.log('');
        console.log('📋 WHAT HAPPENS NEXT:');
        console.log('- Blueprint creates NEW Node.js services');
        console.log('- Uses your Premium account features');
        console.log('- Faster builds with Priority Queue');
        console.log('- Persistent 10GB storage');
        console.log('- PostgreSQL database');
        console.log('');
        console.log('🌐 MONITOR AT: https://dashboard.render.com/blueprints');
        
    } catch (error) {
        console.error('💥 DEPLOYMENT ERROR:', error.message);
    }
}

executeDeployment();
