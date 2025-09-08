/**
 * MCP NODEJS SERVICE CREATOR - CORRECTED SCHEMA
 * Problem: Previous JSON schema was invalid for Render API
 * Solution: Use correct field names and structure based on existing service
 */

const https = require('https');

const API_KEY = 'rnd_fuLBqqLoUnK7cQdnORYYoYLKBFIT';
const REPO_URL = 'https://github.com/davidosemwegie/Resume-Matcher';

// Corrected Node.js service configuration
const nodeServiceConfig = {
    type: 'web_service',
    name: 'resume-matcher-nodejs-clean',
    repo: REPO_URL,
    branch: 'main',
    rootDir: './apps/backend-clean',  // Corrected path format
    env: 'node',
    plan: 'free',
    region: 'oregon',
    autoDeploy: true,
    buildCommand: 'npm install && npm run build',  // Include build step
    startCommand: 'npm start',
    healthCheckPath: '/health',
    environmentVariables: [  // Corrected field name
        {
            key: 'NODE_ENV',
            value: 'production'
        },
        {
            key: 'PORT', 
            value: '3000'
        }
    ]
};

function makeRequest(method, path, data = null) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'api.render.com',
            port: 443,
            path: path,
            method: method,
            headers: {
                'Authorization': `Bearer ${API_KEY}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };

        if (data) {
            const jsonData = JSON.stringify(data);
            options.headers['Content-Length'] = Buffer.byteLength(jsonData);
        }

        const req = https.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => {
                try {
                    const result = JSON.parse(body);
                    resolve({ status: res.statusCode, data: result });
                } catch (e) {
                    resolve({ status: res.statusCode, data: body });
                }
            });
        });

        req.on('error', reject);
        
        if (data) {
            req.write(JSON.stringify(data));
        }
        req.end();
    });
}

async function checkExistingService() {
    console.log('🔍 Checking existing service structure...');
    
    try {
        const result = await makeRequest('GET', '/v1/services/srv-d2k72b8gjchc73ditfig');
        
        if (result.status === 200) {
            console.log('📋 Existing service structure:');
            console.log('- Type:', result.data.type);
            console.log('- Env:', result.data.env);
            console.log('- Runtime:', result.data.runtime);
            console.log('- RootDir:', result.data.rootDir);
            console.log('- BuildCommand:', result.data.buildCommand);
            console.log('- StartCommand:', result.data.startCommand);
            console.log('- EnvironmentVariables length:', result.data.environmentVariables?.length || 0);
            
            return result.data;
        }
    } catch (error) {
        console.log('⚠️ Could not fetch existing service:', error.message);
    }
    
    return null;
}

async function createNodeJsService() {
    console.log('🚀 MCP NODEJS SERVICE CREATOR - CORRECTED');
    console.log('==========================================');
    
    // First check existing service structure
    await checkExistingService();
    
    try {
        console.log('\n📋 Creating new Node.js service...');
        console.log('Service config:', JSON.stringify(nodeServiceConfig, null, 2));
        
        const result = await makeRequest('POST', '/v1/services', nodeServiceConfig);
        
        console.log('\n📊 CREATE SERVICE RESULT:');
        console.log('Status:', result.status);
        console.log('Response:', JSON.stringify(result.data, null, 2));
        
        if (result.status === 201 && result.data.id) {
            const serviceId = result.data.id;
            console.log('\n✅ SUCCESS: New Node.js service created!');
            console.log('🆔 Service ID:', serviceId);
            console.log('🌍 Service URL:', result.data.url || 'URL will be available after deployment');
            console.log('⚡ Runtime:', result.data.env);
            console.log('📁 Root Dir:', result.data.rootDir);
            console.log('🔧 Build Cmd:', result.data.buildCommand);
            console.log('▶️ Start Cmd:', result.data.startCommand);
            
            // Monitor deployment
            console.log('\n🔍 Monitoring deployment...');
            await monitorDeployment(serviceId);
            
        } else {
            console.log('\n❌ FAILED to create service');
            console.log('Status:', result.status);
            
            if (result.data.message) {
                console.log('Error Message:', result.data.message);
            }
            
            if (result.data.errors) {
                console.log('Validation Errors:');
                result.data.errors.forEach((error, index) => {
                    console.log(`  ${index + 1}. ${error}`);
                });
            }
        }
        
    } catch (error) {
        console.error('💥 ERROR:', error.message);
    }
}

async function monitorDeployment(serviceId) {
    let attempts = 0;
    const maxAttempts = 20; // 3+ minutes
    
    while (attempts < maxAttempts) {
        try {
            const result = await makeRequest('GET', `/v1/services/${serviceId}/deploys`);
            
            if (result.status === 200 && result.data.length > 0) {
                const latestDeploy = result.data[0];
                console.log(`\n📡 Deploy Status (${attempts + 1}/${maxAttempts}):`);
                console.log('Status:', latestDeploy.status);
                console.log('Created:', latestDeploy.createdAt);
                
                if (latestDeploy.status === 'live') {
                    console.log('\n🎉 DEPLOYMENT SUCCESSFUL!');
                    console.log('✅ Service is now live and running with Node.js runtime');
                    
                    // Get final service details
                    const serviceResult = await makeRequest('GET', `/v1/services/${serviceId}`);
                    if (serviceResult.status === 200) {
                        console.log('\n🌐 FINAL SERVICE INFO:');
                        console.log('URL:', serviceResult.data.url);
                        console.log('Runtime:', serviceResult.data.env);
                        console.log('Type:', serviceResult.data.type);
                        console.log('Status:', serviceResult.data.status || 'unknown');
                    }
                    break;
                }
                
                if (latestDeploy.status === 'build_failed' || latestDeploy.status === 'deploy_failed') {
                    console.log('\n💥 DEPLOYMENT FAILED!');
                    console.log('Status:', latestDeploy.status);
                    
                    // Get build logs
                    console.log('\n📋 Fetching build logs...');
                    const logsResult = await makeRequest('GET', `/v1/services/${serviceId}/deploys/${latestDeploy.id}/logs`);
                    if (logsResult.status === 200) {
                        console.log('Build logs:', logsResult.data);
                    }
                    break;
                }
                
                if (latestDeploy.status === 'build_in_progress' || latestDeploy.status === 'in_progress') {
                    console.log('⏳ Still building/deploying...');
                }
                
            } else {
                console.log('📭 No deploys found yet...');
            }
            
        } catch (error) {
            console.log('⚠️ Monitor error:', error.message);
        }
        
        attempts++;
        if (attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 10000)); // Wait 10 seconds
        }
    }
    
    if (attempts >= maxAttempts) {
        console.log('\n⏰ TIMEOUT: Monitoring stopped');
        console.log('Service creation completed but deployment monitoring timed out');
    }
}

// Execute
createNodeJsService();
