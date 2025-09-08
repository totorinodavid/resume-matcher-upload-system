// MCP Blueprint Deployment Script - Infrastructure as Code
const https = require('https');

const RENDER_API_KEY = 'rnd_fuLBqqLoUnK7cQdnORYYoYLKBFIT';

async function createBlueprint() {
    console.log('🎯 CREATING BLUEPRINT FROM RENDER.YAML...');
    
    // First, we need to get the repository info for blueprint creation
    const owner = 'totorinodavid';
    const repo = 'resume-matcher-upload-system';
    const branch = 'security-hardening-neon';
    
    const blueprintData = JSON.stringify({
        name: 'resume-matcher-blueprint',
        repo: `https://github.com/${owner}/${repo}`,
        branch: branch,
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
                console.log('✅ BLUEPRINT CREATION RESPONSE:', res.statusCode);
                console.log('📡 DATA:', data);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const result = JSON.parse(data);
                    console.log('🎉 BLUEPRINT CREATED SUCCESSFULLY!');
                    console.log('📋 BLUEPRINT ID:', result.id);
                    console.log('📋 BLUEPRINT NAME:', result.name);
                    resolve(result);
                } else {
                    console.log('❌ BLUEPRINT CREATION FAILED:', res.statusCode, data);
                    // Try manual sync approach
                    console.log('🔄 TRYING MANUAL SYNC APPROACH...');
                    resolve(null);
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ BLUEPRINT CREATION ERROR:', error);
            reject(error);
        });

        req.write(blueprintData);
        req.end();
    });
}

async function listBlueprints() {
    console.log('📋 LISTING EXISTING BLUEPRINTS...');
    
    const options = {
        hostname: 'api.render.com',
        port: 443,
        path: '/v1/blueprints',
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
                console.log('✅ BLUEPRINTS LIST RESPONSE:', res.statusCode);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const blueprints = JSON.parse(data);
                    console.log('📋 FOUND BLUEPRINTS:', blueprints.length);
                    
                    if (blueprints.length > 0) {
                        blueprints.forEach(bp => {
                            console.log(`- ${bp.name} (${bp.id}) - ${bp.repo}`);
                        });
                        
                        // Find our blueprint
                        const ourBlueprint = blueprints.find(bp => 
                            bp.repo && bp.repo.includes('resume-matcher-upload-system')
                        );
                        
                        if (ourBlueprint) {
                            console.log('✅ FOUND OUR BLUEPRINT:', ourBlueprint.name);
                            return syncBlueprint(ourBlueprint.id);
                        }
                    }
                    
                    resolve(blueprints);
                } else {
                    console.log('❌ BLUEPRINTS LIST FAILED:', data);
                    resolve([]);
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ BLUEPRINTS LIST ERROR:', error);
            reject(error);
        });

        req.end();
    });
}

async function syncBlueprint(blueprintId) {
    console.log('🔄 SYNCING BLUEPRINT:', blueprintId);
    
    const options = {
        hostname: 'api.render.com',
        port: 443,
        path: `/v1/blueprints/${blueprintId}/sync`,
        method: 'POST',
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
                console.log('✅ BLUEPRINT SYNC RESPONSE:', res.statusCode);
                console.log('📡 DATA:', data);
                
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    const result = JSON.parse(data);
                    console.log('🎉 BLUEPRINT SYNC TRIGGERED!');
                    console.log('📋 SYNC ID:', result.id);
                    resolve(result);
                } else {
                    console.log('❌ BLUEPRINT SYNC FAILED:', res.statusCode, data);
                    resolve(null);
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ BLUEPRINT SYNC ERROR:', error);
            reject(error);
        });

        req.end();
    });
}

// Execute blueprint workflow
async function runBlueprintDeployment() {
    try {
        console.log('🚀 STARTING BLUEPRINT DEPLOYMENT...');
        
        // First check existing blueprints
        const blueprints = await listBlueprints();
        
        if (!blueprints || blueprints.length === 0) {
            // Create new blueprint
            const newBlueprint = await createBlueprint();
            
            if (newBlueprint) {
                console.log('🎉 BLUEPRINT DEPLOYMENT COMPLETED!');
                console.log('🌐 CHECK DASHBOARD: https://dashboard.render.com/blueprints');
            } else {
                console.log('❌ BLUEPRINT DEPLOYMENT FAILED');
            }
        }
        
    } catch (error) {
        console.error('💥 BLUEPRINT DEPLOYMENT ERROR:', error.message);
    }
}

runBlueprintDeployment();
