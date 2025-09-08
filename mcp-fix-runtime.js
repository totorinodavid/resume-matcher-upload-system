// MCP Service Runtime Fix - Node.js statt Docker
const https = require('https');

const RENDER_API_KEY = 'rnd_fuLBqqLoUnK7cQdnORYYoYLKBFIT';
const SERVICE_ID = 'srv-d2k72b8gjchc73ditfig';

async function fixServiceRuntime() {
    console.log('🔧 FIXING SERVICE RUNTIME TO NODE.JS...');
    
    const updateData = JSON.stringify({
        type: 'web_service',
        rootDir: 'apps/backend-clean',
        runtime: 'node',
        buildCommand: 'npm ci && npm run build',
        startCommand: 'npm start',
        envVars: [
            { key: 'NODE_ENV', value: 'production' },
            { key: 'UPLOAD_DIR', value: '/opt/render/project/src/uploads' }
        ],
        // Remove Docker-specific config
        dockerCommand: null,
        dockerfilePath: null,
        dockerContext: null,
        preDeployCommand: null
    });

    const options = {
        hostname: 'api.render.com',
        port: 443,
        path: '/v1/services/' + SERVICE_ID,
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
                console.log('✅ RUNTIME FIX RESPONSE:', res.statusCode);
                console.log('📡 DATA:', data);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    console.log('🎉 SERVICE RUNTIME FIXED TO NODE.JS!');
                    // Trigger new deploy
                    await triggerNewDeploy();
                    resolve(JSON.parse(data));
                } else {
                    reject(new Error(`Runtime fix failed: ${res.statusCode} - ${data}`));
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ RUNTIME FIX ERROR:', error);
            reject(error);
        });

        req.write(updateData);
        req.end();
    });
}

async function triggerNewDeploy() {
    console.log('🚀 TRIGGERING NEW DEPLOY WITH NODE.JS RUNTIME...');
    
    const postData = JSON.stringify({
        clearCache: "clear"
    });

    const options = {
        hostname: 'api.render.com',
        port: 443,
        path: '/v1/services/' + SERVICE_ID + '/deploys',
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
                console.log('✅ NEW DEPLOYMENT RESPONSE:', res.statusCode);
                console.log('📡 DATA:', data);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const result = JSON.parse(data);
                    console.log('🎉 NEW DEPLOYMENT TRIGGERED!');
                    console.log('📋 NEW DEPLOY ID:', result.id);
                    console.log('⚡ STATUS:', result.status);
                    resolve(result);
                } else {
                    reject(new Error(`New deployment failed: ${res.statusCode} - ${data}`));
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ NEW DEPLOYMENT ERROR:', error);
            reject(error);
        });

        req.write(postData);
        req.end();
    });
}

// Execute runtime fix
fixServiceRuntime()
    .then(result => {
        console.log('🎉 MCP RUNTIME FIX COMPLETED!');
        console.log('🌐 SERVICE WILL BE AVAILABLE AT: https://resume-matcher-backend-j06k.onrender.com');
    })
    .catch(error => {
        console.error('💥 MCP RUNTIME FIX FAILED:', error.message);
        process.exit(1);
    });
