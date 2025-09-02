#!/usr/bin/env node
/**
 * Credits System Environment Checker
 * Node.js/TypeScript CLI for validating environment variables
 * Usage: node scripts/env-checker.js [--environment=production]
 */

const fs = require('fs');
const path = require('path');

// ANSI color codes for terminal output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m'
};

class EnvironmentChecker {
    constructor() {
        this.requiredVars = [
            {
                name: 'STRIPE_SECRET_KEY',
                description: 'Stripe secret key for payment processing',
                pattern: /^sk_/,
                critical: true
            },
            {
                name: 'STRIPE_WEBHOOK_SECRET',
                description: 'Stripe webhook endpoint secret',
                pattern: /^whsec_/,
                critical: true
            },
            {
                name: 'DATABASE_URL',
                description: 'PostgreSQL database connection string',
                pattern: /^postgres(ql)?:\/\//,
                critical: true
            },
            {
                name: 'NEXTAUTH_SECRET',
                description: 'NextAuth.js secret for session encryption',
                minLength: 32,
                critical: true
            },
            {
                name: 'OPENAI_API_KEY',
                description: 'OpenAI API key for AI processing',
                pattern: /^sk-/,
                critical: false
            },
            {
                name: 'CREDITS_WRITE_FREEZE',
                description: 'Credits system write freeze flag',
                expectedValue: '1',
                critical: false
            }
        ];
        
        this.envFiles = [
            '.env',
            '.env.local',
            'apps/frontend/.env.local',
            'apps/backend/.env'
        ];
        
        this.results = {
            passed: 0,
            failed: 0,
            warnings: 0,
            critical: 0
        };
    }

    /**
     * Load environment variables from .env files
     */
    loadEnvFiles() {
        const envVars = {};
        
        // First load from process.env
        Object.assign(envVars, process.env);
        
        // Then load from .env files (in order of precedence)
        for (const envFile of this.envFiles) {
            const fullPath = path.resolve(envFile);
            if (fs.existsSync(fullPath)) {
                try {
                    const content = fs.readFileSync(fullPath, 'utf8');
                    const lines = content.split('\n');
                    
                    for (const line of lines) {
                        const trimmedLine = line.trim();
                        if (trimmedLine && !trimmedLine.startsWith('#')) {
                            const [key, ...valueParts] = trimmedLine.split('=');
                            if (key && valueParts.length > 0) {
                                const value = valueParts.join('=').replace(/^["']|["']$/g, '');
                                envVars[key.trim()] = value;
                            }
                        }
                    }
                    
                    console.log(`${colors.blue}📄 Loaded: ${envFile}${colors.reset}`);
                } catch (error) {
                    console.log(`${colors.yellow}⚠️  Could not read: ${envFile}${colors.reset}`);
                }
            }
        }
        
        return envVars;
    }

    /**
     * Validate a single environment variable
     */
    validateVariable(varConfig, value) {
        const result = {
            name: varConfig.name,
            value: value,
            status: 'unknown',
            message: '',
            critical: varConfig.critical
        };

        // Check if variable exists
        if (!value || value.trim() === '') {
            result.status = 'missing';
            result.message = `Missing required variable: ${varConfig.description}`;
            return result;
        }

        // Check pattern if specified
        if (varConfig.pattern && !varConfig.pattern.test(value)) {
            result.status = 'invalid';
            result.message = `Invalid format for ${varConfig.name}`;
            return result;
        }

        // Check minimum length if specified
        if (varConfig.minLength && value.length < varConfig.minLength) {
            result.status = 'invalid';
            result.message = `${varConfig.name} too short (min: ${varConfig.minLength} chars)`;
            return result;
        }

        // Check expected value if specified
        if (varConfig.expectedValue && value !== varConfig.expectedValue) {
            result.status = 'warning';
            result.message = `Expected "${varConfig.expectedValue}", got "${value}"`;
            return result;
        }

        result.status = 'valid';
        result.message = varConfig.description;
        return result;
    }

    /**
     * Mask sensitive values for display
     */
    maskValue(value, varName) {
        if (!value) return 'NOT_SET';
        
        if (varName.includes('SECRET') || varName.includes('KEY')) {
            return value.substring(0, 8) + '...***';
        }
        
        if (varName === 'DATABASE_URL') {
            return value.replace(/:\/\/.*@/, '://***:***@');
        }
        
        return value.length > 20 ? value.substring(0, 20) + '...' : value;
    }

    /**
     * Print validation results
     */
    printResults(results) {
        console.log(`\n${colors.cyan}${colors.bright}🔍 ENVIRONMENT VALIDATION RESULTS${colors.reset}`);
        console.log(`${colors.cyan}=====================================${colors.reset}\n`);

        for (const result of results) {
            const icon = result.status === 'valid' ? '✅' : 
                        result.status === 'warning' ? '⚠️' : '❌';
            
            const color = result.status === 'valid' ? colors.green :
                         result.status === 'warning' ? colors.yellow : colors.red;
            
            const maskedValue = this.maskValue(result.value, result.name);
            const criticalFlag = result.critical ? ' [CRITICAL]' : '';
            
            console.log(`${icon} ${color}${result.name}${criticalFlag}${colors.reset}`);
            console.log(`   Value: ${maskedValue}`);
            console.log(`   ${result.message}\n`);

            // Update counters
            if (result.status === 'valid') {
                this.results.passed++;
            } else if (result.status === 'warning') {
                this.results.warnings++;
            } else {
                this.results.failed++;
                if (result.critical) {
                    this.results.critical++;
                }
            }
        }
    }

    /**
     * Print summary
     */
    printSummary() {
        console.log(`${colors.magenta}${colors.bright}📊 SUMMARY${colors.reset}`);
        console.log(`${colors.magenta}==========${colors.reset}`);
        console.log(`${colors.green}✅ Passed: ${this.results.passed}${colors.reset}`);
        console.log(`${colors.yellow}⚠️  Warnings: ${this.results.warnings}${colors.reset}`);
        console.log(`${colors.red}❌ Failed: ${this.results.failed}${colors.reset}`);
        console.log(`${colors.red}🚨 Critical Issues: ${this.results.critical}${colors.reset}\n`);

        if (this.results.critical > 0) {
            console.log(`${colors.red}${colors.bright}🚨 CRITICAL ISSUES FOUND!${colors.reset}`);
            console.log(`${colors.red}Cannot proceed with deployment until resolved.${colors.reset}\n`);
            return false;
        } else if (this.results.failed > 0) {
            console.log(`${colors.yellow}⚠️  Issues found but none are critical.${colors.reset}`);
            console.log(`${colors.yellow}Review warnings before proceeding.${colors.reset}\n`);
            return true;
        } else {
            console.log(`${colors.green}${colors.bright}🎉 ALL CHECKS PASSED!${colors.reset}`);
            console.log(`${colors.green}Environment is ready for deployment.${colors.reset}\n`);
            return true;
        }
    }

    /**
     * Main validation function
     */
    async validate() {
        console.log(`${colors.cyan}${colors.bright}Resume Matcher - Environment Checker${colors.reset}`);
        console.log(`${colors.cyan}====================================${colors.reset}\n`);

        // Load environment variables
        const envVars = this.loadEnvFiles();
        
        // Validate each required variable
        const results = [];
        for (const varConfig of this.requiredVars) {
            const value = envVars[varConfig.name];
            const result = this.validateVariable(varConfig, value);
            results.push(result);
        }

        // Print results
        this.printResults(results);
        
        // Print summary and return success status
        return this.printSummary();
    }
}

// CLI execution
if (require.main === module) {
    const checker = new EnvironmentChecker();
    
    checker.validate().then(success => {
        process.exit(success ? 0 : 1);
    }).catch(error => {
        console.error(`${colors.red}Error during validation: ${error.message}${colors.reset}`);
        process.exit(1);
    });
}

module.exports = EnvironmentChecker;
