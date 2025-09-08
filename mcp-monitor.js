// MCP Build Status Monitor für Resume Matcher
const https = require('https');

const RENDER_API_KEY = 'rnd_fuLBqqLoUnK7cQdnORYYoYLKBFIT';
const SERVICE_ID = 'srv-d2k72b8gjchc73ditfig';
const DEPLOY_ID = 'dep-d2uf8ker433s73e8g66g'; // NEW DEPLOY ID

async function checkDeployStatus() {
    console.log('🔍 CHECKING DEPLOY STATUS...');
    
    const options = {
        hostname: 'api.render.com',
        port: 443,
        path: '/v1/services/' + SERVICE_ID + '/deploys/' + DEPLOY_ID,
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
                console.log('📋 DEPLOY STATUS RESPONSE:', res.statusCode);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const deploy = JSON.parse(data);
                    console.log('🎯 DEPLOY STATUS:', deploy.status);
                    console.log('📅 STARTED AT:', deploy.startedAt);
                    console.log('📅 UPDATED AT:', deploy.updatedAt);
                    console.log('💬 COMMIT:', deploy.commit.message);
                    
                    if (deploy.finishedAt) {
                        console.log('✅ FINISHED AT:', deploy.finishedAt);
                    }
                    
                    resolve(deploy);
                } else {
                    reject(new Error(`Deploy status check failed: ${res.statusCode} - ${data}`));
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ DEPLOY STATUS ERROR:', error);
            reject(error);
        });

        req.end();
    });
}

async function getServiceLogs() {
    console.log('📜 GETTING SERVICE LOGS...');
    
    const options = {
        hostname: 'api.render.com',
        port: 443,
        path: '/v1/services/' + SERVICE_ID + '/logs?startTime=2025-09-07T02:50:00Z&endTime=2025-09-07T03:00:00Z',
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
                console.log('📋 SERVICE LOGS RESPONSE:', res.statusCode);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const logs = JSON.parse(data);
                    console.log('📜 BUILD LOGS:');
                    console.log('==========================================');
                    
                    if (logs && logs.length > 0) {
                        logs.slice(-30).forEach(log => {
                            console.log(`[${log.timestamp}] ${log.message}`);
                        });
                    } else {
                        console.log('Raw logs data:', data);
                    }
                    
                    console.log('==========================================');
                    resolve(logs);
                } else {
                    console.log('❌ LOGS ERROR RESPONSE:', data);
                    resolve(null);
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ LOGS ERROR:', error);
            reject(error);
        });

        req.end();
    });
}

async function monitorBuild() {
    console.log('🚀 STARTING BUILD MONITOR...');
    
    try {
        const deploy = await checkDeployStatus();
        
        if (deploy.status === 'build_in_progress') {
            console.log('⏳ BUILD STILL IN PROGRESS...');
            await getServiceLogs();
        } else if (deploy.status === 'live') {
            console.log('🎉 BUILD COMPLETED SUCCESSFULLY!');
            console.log('🌐 SERVICE URL: https://resume-matcher-backend-j06k.onrender.com');
        } else if (deploy.status === 'build_failed') {
            console.log('❌ BUILD FAILED!');
            await getServiceLogs();
        } else {
            console.log('📊 CURRENT STATUS:', deploy.status);
            await getServiceLogs();
        }
        
    } catch (error) {
        console.error('💥 MONITOR ERROR:', error.message);
    }
}

// Execute monitoring
monitorBuild();
