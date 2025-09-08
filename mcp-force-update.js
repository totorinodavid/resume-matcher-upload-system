// MCP FORCE UPDATE SERVICE TO NODE.JS - NO ALTERNATIVES
const https = require('https');

const RENDER_API_KEY = 'rnd_fuLBqqLoUnK7cQdnORYYoYLKBFIT';
const SERVICE_ID = 'srv-d2k72b8gjchc73ditfig';

async function forceUpdateToNodeJS() {
    console.log('🔧 FORCE UPDATING SERVICE TO NODE.JS...');
    
    // Complete Node.js configuration
    const updateData = JSON.stringify({
        buildCommand: 'npm ci && npm run build',
        startCommand: 'npm start',
        healthCheckPath: '/api/health',
        envVars: [
            { key: 'NODE_ENV', value: 'production' },
            { key: 'UPLOAD_DIR', value: '/opt/render/project/src/uploads' }
        ]
    });

    const options = {
        hostname: 'api.render.com',
        port: 443,
        path: `/v1/services/${SERVICE_ID}`,
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${RENDER_API_KEY}`,
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
            
            res.on('end', () => {
                console.log('✅ UPDATE RESPONSE:', res.statusCode);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const result = JSON.parse(data);
                    console.log('🎉 SERVICE UPDATED!');
                    console.log('📋 SERVICE DETAILS:', JSON.stringify(result.serviceDetails, null, 2));
                    resolve(result);
                } else {
                    console.log('❌ UPDATE FAILED:', data);
                    reject(new Error(`Update failed: ${res.statusCode} - ${data}`));
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

async function triggerDeploy() {
    console.log('🚀 TRIGGERING DEPLOY...');
    
    const postData = JSON.stringify({
        clearCache: 'clear'
    });

    const options = {
        hostname: 'api.render.com',
        port: 443,
        path: `/v1/services/${SERVICE_ID}/deploys`,
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${RENDER_API_KEY}`,
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
                console.log('✅ DEPLOY RESPONSE:', res.statusCode);
                console.log('📡 DEPLOY DATA:', data);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const result = JSON.parse(data);
                    console.log('🎉 DEPLOY TRIGGERED!');
                    console.log('📋 DEPLOY ID:', result.id);
                    console.log('⚡ STATUS:', result.status);
                    resolve(result);
                } else {
                    console.log('❌ DEPLOY FAILED:', data);
                    reject(new Error(`Deploy failed: ${res.statusCode} - ${data}`));
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ DEPLOY ERROR:', error);
            reject(error);
        });

        req.write(postData);
        req.end();
    });
}

async function executeForceUpdate() {
    try {
        await forceUpdateToNodeJS();
        await triggerDeploy();
        console.log('🎉 MCP FORCE UPDATE COMPLETED!');
    } catch (error) {
        console.error('💥 MCP FORCE UPDATE FAILED:', error.message);
        process.exit(1);
    }
}

executeForceUpdate();
