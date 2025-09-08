const https = require('https');

const RENDER_API_TOKEN = 'rnd_7zXTjXyqN5qKDjgvWQdL7aOA8fBs';
const SERVICE_ID = 'srv-d2k72b8gjchc73ditfig';

// Service configuration for new Node.js service
const NEW_SERVICE_CONFIG = {
  name: 'resume-matcher-backend',
  type: 'web_service',
  repo: 'https://github.com/DBLR83/Resume-Matcher',
  branch: 'main',
  rootDir: 'apps/backend-clean',
  // Node.js runtime configuration (NO Docker fields)
  env: 'node',
  buildCommand: 'npm install && npm run build',
  startCommand: 'npm start',
  plan: 'free',
  region: 'oregon',
  autoDeploy: 'yes',
  environmentVariables: [
    {
      key: 'NODE_ENV',
      value: 'production'
    },
    {
      key: 'PORT',
      value: '10000'
    }
  ]
};

function makeApiRequest(method, path, data = null) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.render.com',
      port: 443,
      path: path,
      method: method,
      headers: {
        'Authorization': `Bearer ${RENDER_API_TOKEN}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    };

    const req = https.request(options, (res) => {
      let responseData = '';
      res.on('data', (chunk) => {
        responseData += chunk;
      });

      res.on('end', () => {
        try {
          const parsed = JSON.parse(responseData);
          console.log(`✅ ${method} ${path} - Status: ${res.statusCode}`);
          if (res.statusCode < 400) {
            resolve(parsed);
          } else {
            reject(new Error(`API Error ${res.statusCode}: ${JSON.stringify(parsed)}`));
          }
        } catch (e) {
          console.log(`📄 Raw Response: ${responseData}`);
          if (res.statusCode < 400) {
            resolve(responseData);
          } else {
            reject(new Error(`HTTP ${res.statusCode}: ${responseData}`));
          }
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    if (data) {
      req.write(JSON.stringify(data));
    }
    req.end();
  });
}

async function recreateService() {
  console.log('🎯 MCP SERVICE RECREATION - PURE AUTOMATION');
  console.log('=' * 50);

  try {
    // Step 1: Delete existing service
    console.log('🗑️ Step 1: Deleting existing service...');
    console.log(`Service ID: ${SERVICE_ID}`);
    
    await makeApiRequest('DELETE', `/v1/services/${SERVICE_ID}`);
    console.log('✅ Service deleted successfully');
    
    // Wait a moment for deletion to process
    console.log('⏱️ Waiting 5 seconds for deletion to complete...');
    await new Promise(resolve => setTimeout(resolve, 5000));

    // Step 2: Create new Node.js service
    console.log('🆕 Step 2: Creating new Node.js service...');
    console.log('Configuration:');
    console.log(JSON.stringify(NEW_SERVICE_CONFIG, null, 2));
    
    const newService = await makeApiRequest('POST', '/v1/services', NEW_SERVICE_CONFIG);
    console.log('✅ New service created successfully!');
    console.log(`New Service ID: ${newService.id}`);
    console.log(`Service URL: ${newService.url}`);

    // Step 3: Monitor initial deployment
    console.log('📊 Step 3: Monitoring initial deployment...');
    const deployments = await makeApiRequest('GET', `/v1/services/${newService.id}/deploys?limit=1`);
    
    if (deployments && deployments.length > 0) {
      const latestDeploy = deployments[0];
      console.log(`🚀 Deployment ${latestDeploy.id} - Status: ${latestDeploy.status}`);
      console.log(`Created: ${latestDeploy.createdAt}`);
    }

    console.log('');
    console.log('🎉 SERVICE RECREATION COMPLETE!');
    console.log('=' * 50);
    console.log(`✅ Old Docker service deleted: ${SERVICE_ID}`);
    console.log(`✅ New Node.js service created: ${newService.id}`);
    console.log(`🔗 Service URL: ${newService.url}`);
    console.log('');
    console.log('📋 Next Steps:');
    console.log('1. Service is now using Node.js runtime (no Docker)');
    console.log('2. Building from apps/backend-clean directory');
    console.log('3. Using npm install && npm run build');
    console.log('4. Starting with npm start');
    console.log('');
    console.log('🎯 MCP AUTOMATION - TASK COMPLETED');

  } catch (error) {
    console.error('❌ Error during service recreation:');
    console.error(error.message);
    process.exit(1);
  }
}

// Execute the recreation
recreateService();
