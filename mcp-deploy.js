// MCP Direct Deployment Script für Resume Matcher Clean Backend
const https = require('https');

const RENDER_API_KEY = 'rnd_fuLBqqLoUnK7cQdnORYYoYLKBFIT';

async function listServicesAndDeploy() {
    console.log('🔍 LISTING SERVICES TO FIND CORRECT ID...');
    
    // First, list all services to find the correct one
    const listOptions = {
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
        const req = https.request(listOptions, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', async () => {
                console.log('📋 SERVICES RESPONSE:', res.statusCode);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const services = JSON.parse(data);
                    console.log('🔍 FOUND SERVICES:', services.length);
                    console.log('📋 ALL SERVICES:', JSON.stringify(services, null, 2));
                    
                    // Find resume-matcher service
                    const targetService = services.find(service => 
                        service.service && (
                            (service.service.name && service.service.name.includes('resume-matcher')) || 
                            (service.service.repo && service.service.repo.includes('resume-matcher-upload-system'))
                        )
                    );
                    
                    if (targetService) {
                        console.log('✅ FOUND TARGET SERVICE:', targetService.service.name, targetService.service.id);
                        console.log('🔍 CURRENT ROOT DIR:', targetService.service.rootDir);
                        
                        // Check if it's pointing to the wrong directory
                        if (targetService.service.rootDir === 'apps/backend') {
                            console.log('🔧 UPDATING SERVICE TO USE CLEAN BACKEND...');
                            await updateServiceConfig(targetService.service.id);
                        } else {
                            await triggerDeploy(targetService.service.id);
                        }
                        resolve(targetService.service);
                    } else {
                        // Just trigger deploy on first service as fallback
                        if (services.length > 0 && services[0].service) {
                            console.log('🔄 USING FIRST SERVICE AS FALLBACK:', services[0].service.name);
                            await triggerDeploy(services[0].service.id);
                            resolve(services[0].service);
                        } else {
                            console.log('❌ NO SERVICES FOUND');
                            resolve(null);
                        }
                    }
                } else {
                    reject(new Error(`Failed to list services: ${res.statusCode} - ${data}`));
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ LIST SERVICES ERROR:', error);
            reject(error);
        });

        req.end();
    });
}

async function triggerDeploy(serviceId) {
    console.log('🚀 TRIGGERING DEPLOY FOR SERVICE:', serviceId);
    
    const postData = JSON.stringify({
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
            'Content-Length': Buffer.byteLength(postData)
        }
    };

    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                console.log('✅ DEPLOYMENT RESPONSE:', res.statusCode);
                console.log('📡 DATA:', data);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const result = JSON.parse(data);
                    console.log('🎉 DEPLOYMENT TRIGGERED SUCCESSFULLY!');
                    console.log('📋 DEPLOY ID:', result.id);
                    console.log('⚡ STATUS:', result.status);
                    resolve(result);
                } else {
                    reject(new Error(`Deployment failed: ${res.statusCode} - ${data}`));
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ DEPLOYMENT ERROR:', error);
            reject(error);
        });

        req.write(postData);
        req.end();
    });
}

async function updateServiceConfig(serviceId) {
    console.log('🔧 UPDATING SERVICE CONFIG FOR:', serviceId);
    
    const updateData = JSON.stringify({
        rootDir: 'apps/backend-clean',
        buildCommand: 'npm ci && npm run build',
        startCommand: 'npm start',
        runtime: 'node',
        envVars: [
            { key: 'NODE_ENV', value: 'production' },
            { key: 'UPLOAD_DIR', value: '/opt/render/project/src/uploads' }
        ]
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
                console.log('✅ UPDATE SERVICE RESPONSE:', res.statusCode);
                console.log('📡 DATA:', data);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    console.log('🎉 SERVICE UPDATED SUCCESSFULLY!');
                    // Now trigger deploy
                    await triggerDeploy(serviceId);
                    resolve(JSON.parse(data));
                } else {
                    reject(new Error(`Service update failed: ${res.statusCode} - ${data}`));
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ UPDATE SERVICE ERROR:', error);
            reject(error);
        });

        req.write(updateData);
        req.end();
    });
}

async function getUserInfo() {
    console.log('👤 GETTING USER INFO...');
    
    const options = {
        hostname: 'api.render.com',
        port: 443,
        path: '/v1/owners',
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
                console.log('👤 USER INFO RESPONSE:', res.statusCode);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const owners = JSON.parse(data);
                    console.log('👤 FOUND OWNERS:', owners.length);
                    resolve(owners[0]); // Use first owner
                } else {
                    reject(new Error(`Failed to get user info: ${res.statusCode} - ${data}`));
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ GET USER INFO ERROR:', error);
            reject(error);
        });

        req.end();
    });
}

async function createNewService() {
    console.log('🆕 CREATING NEW SERVICE...');
    
    // Get user info first
    const owner = await getUserInfo();
    console.log('👤 USING OWNER:', owner.id, owner.name);
    
    const serviceData = JSON.stringify({
        type: 'web_service',
        name: 'resume-matcher-auto',
        ownerId: owner.id,
        repo: 'https://github.com/totorinodavid/resume-matcher-upload-system',
        branch: 'security-hardening-neon',
        rootDir: 'apps/backend-clean',
        buildCommand: 'npm ci && npm run build',
        startCommand: 'npm start',
        envVars: [
            { key: 'NODE_ENV', value: 'production' },
            { key: 'UPLOAD_DIR', value: '/opt/render/project/src/uploads' }
        ]
    });

    const options = {
        hostname: 'api.render.com',
        port: 443,
        path: '/v1/services',
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + RENDER_API_KEY,
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(serviceData)
        }
    };

    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                console.log('✅ CREATE SERVICE RESPONSE:', res.statusCode);
                console.log('📡 DATA:', data);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const result = JSON.parse(data);
                    console.log('🎉 SERVICE CREATED SUCCESSFULLY!');
                    console.log('📋 SERVICE ID:', result.id);
                    console.log('🌐 SERVICE URL:', result.serviceDetails?.url);
                    resolve(result);
                } else {
                    reject(new Error(`Service creation failed: ${res.statusCode} - ${data}`));
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ CREATE SERVICE ERROR:', error);
            reject(error);
        });

        req.write(serviceData);
        req.end();
    });
}

// Execute deployment
listServicesAndDeploy()
    .then(result => {
        console.log('🎉 MCP DEPLOYMENT COMPLETED!');
        if (result) {
            console.log('📋 SERVICE:', result.name);
            console.log('🌐 URL: https://' + result.name + '.onrender.com');
        }
    })
    .catch(error => {
        console.error('💥 MCP DEPLOYMENT FAILED:', error.message);
        process.exit(1);
    });
