#!/usr/bin/env node

// 🚀 RENDER DIRECT UPDATE VIA API - LIVE DEPLOYMENT
const https = require('https');

const RENDER_API_KEY = 'rnd_fuLBqqLoUnK7cQdnORYYoYLKBFIT';

console.log('🚀 MAKING IT LIVE VIA RENDER API - SOFORT!');
console.log('==========================================');

// Finde Service und update Build Command direkt
async function updateServiceDirectly() {
    console.log('🔍 Finding services...');
    
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
            
            res.on('end', async () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const services = JSON.parse(data);
                    console.log('📋 FOUND SERVICES:', services.length);
                    
                    // Find resume-matcher service
                    for (const service of services) {
                        if (service.name && service.name.includes('resume-matcher')) {
                            console.log('🎯 FOUND TARGET SERVICE:', service.name);
                            console.log('📋 SERVICE ID:', service.id);
                            
                            // Update build command directly
                            await updateBuildCommand(service.id);
                            break;
                        }
                    }
                    
                    resolve(services);
                } else {
                    console.log('❌ SERVICES FETCH FAILED:', data);
                    resolve([]);
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ API ERROR:', error);
            reject(error);
        });

        req.end();
    });
}

async function updateBuildCommand(serviceId) {
    console.log('🔧 UPDATING BUILD COMMAND FOR SERVICE:', serviceId);
    
    const updateData = JSON.stringify({
        buildCommand: 'npm install && npm run build'
    });

    const options = {
        hostname: 'api.render.com',
        port: 443,
        path: '/v1/services/' + serviceId,
        method: 'PATCH',
        headers: {
            'Authorization': 'Bearer ' + RENDER_API_KEY,
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(updateData)
        }
    };

    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', async () => {
                console.log('✅ UPDATE RESPONSE:', res.statusCode);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    console.log('🎉 BUILD COMMAND UPDATED!');
                    console.log('🚀 Triggering new deploy...');
                    
                    // Trigger new deploy
                    await triggerDeploy(serviceId);
                    
                } else {
                    console.log('❌ UPDATE FAILED:', data);
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ UPDATE ERROR:', error);
            reject(error);
        });

        req.write(updateData);
        req.end();
    });
}

async function triggerDeploy(serviceId) {
    console.log('🚀 TRIGGERING LIVE DEPLOY...');
    
    const deployData = JSON.stringify({
        clearCache: "clear"
    });

    const options = {
        hostname: 'api.render.com',
        port: 443,
        path: '/v1/services/' + serviceId + '/deploys',
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + RENDER_API_KEY,
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(deployData)
        }
    };

    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                console.log('✅ DEPLOY TRIGGERED:', res.statusCode);
                console.log('📡 RESPONSE:', data);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const result = JSON.parse(data);
                    console.log('🎉 LIVE DEPLOYMENT STARTED!');
                    console.log('📋 DEPLOY ID:', result.id);
                    console.log('🌐 Service wird in 2-3 Minuten live sein!');
                    
                } else {
                    console.log('❌ DEPLOY FAILED:', data);
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ DEPLOY ERROR:', error);
            reject(error);
        });

        req.write(deployData);
        req.end();
    });
}

// EXECUTE LIVE UPDATE
updateServiceDirectly()
    .then(() => {
        console.log('🎉 LIVE DEPLOYMENT PROCESS COMPLETED!');
    })
    .catch(error => {
        console.error('💥 LIVE DEPLOYMENT FAILED:', error.message);
    });
