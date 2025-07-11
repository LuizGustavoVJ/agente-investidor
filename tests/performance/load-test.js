import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
export let errorRate = new Rate('errors');

// Test configuration
export let options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up to 10 users
    { duration: '5m', target: 10 }, // Stay at 10 users
    { duration: '2m', target: 20 }, // Ramp up to 20 users
    { duration: '5m', target: 20 }, // Stay at 20 users
    { duration: '2m', target: 0 },  // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must complete below 500ms
    http_req_failed: ['rate<0.1'],    // Error rate must be below 10%
    errors: ['rate<0.1'],             // Custom error rate must be below 10%
  },
};

const BASE_URL = 'http://localhost';

// Test data
const testUsers = [
  { email: 'test1@example.com', password: 'password123' },
  { email: 'test2@example.com', password: 'password123' },
  { email: 'test3@example.com', password: 'password123' },
];

const stockSymbols = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA'];
const methodologies = ['value_investing', 'dividend_investing', 'growth_investing'];

export function setup() {
  // Setup test data if needed
  console.log('Setting up performance test...');
  
  // Health check
  let healthResponse = http.get(`${BASE_URL}/health`);
  check(healthResponse, {
    'health check status is 200': (r) => r.status === 200,
  });
  
  return { baseUrl: BASE_URL };
}

export default function(data) {
  let user = testUsers[Math.floor(Math.random() * testUsers.length)];
  let stockSymbol = stockSymbols[Math.floor(Math.random() * stockSymbols.length)];
  let methodology = methodologies[Math.floor(Math.random() * methodologies.length)];
  
  // Test 1: Health Check
  let healthResponse = http.get(`${BASE_URL}/health`);
  check(healthResponse, {
    'health check status is 200': (r) => r.status === 200,
  }) || errorRate.add(1);
  
  sleep(1);
  
  // Test 2: User Registration
  let registerPayload = JSON.stringify({
    email: `perf_test_${__VU}_${__ITER}@example.com`,
    password: 'password123',
    full_name: `Performance Test User ${__VU}`,
  });
  
  let registerResponse = http.post(`${BASE_URL}/api/v1/auth/register`, registerPayload, {
    headers: { 'Content-Type': 'application/json' },
  });
  
  check(registerResponse, {
    'registration status is 201': (r) => r.status === 201,
    'registration response has token': (r) => r.json('access_token') !== undefined,
  }) || errorRate.add(1);
  
  let token = registerResponse.json('access_token');
  let authHeaders = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  };
  
  sleep(1);
  
  // Test 3: Stock Data Retrieval
  let stockResponse = http.get(`${BASE_URL}/api/v1/data/stock/${stockSymbol}`, {
    headers: authHeaders,
  });
  
  check(stockResponse, {
    'stock data status is 200': (r) => r.status === 200,
    'stock data has price': (r) => r.json('current_price') !== undefined,
  }) || errorRate.add(1);
  
  sleep(1);
  
  // Test 4: Methodology Analysis
  let methodologyPayload = JSON.stringify({
    stock_symbol: stockSymbol,
    methodology: methodology,
    parameters: {
      min_market_cap: 1000000000,
      max_pe_ratio: 15,
      min_dividend_yield: 0.03,
    },
  });
  
  let methodologyResponse = http.post(`${BASE_URL}/api/v1/methodology/analyze`, methodologyPayload, {
    headers: authHeaders,
  });
  
  check(methodologyResponse, {
    'methodology analysis status is 200': (r) => r.status === 200,
    'methodology analysis has score': (r) => r.json('score') !== undefined,
  }) || errorRate.add(1);
  
  sleep(1);
  
  // Test 5: Financial Analysis
  let analysisPayload = JSON.stringify({
    stock_symbol: stockSymbol,
    analysis_type: 'comprehensive',
    include_ratios: true,
    include_valuation: true,
  });
  
  let analysisResponse = http.post(`${BASE_URL}/api/v1/analysis/analyze`, analysisPayload, {
    headers: authHeaders,
  });
  
  check(analysisResponse, {
    'financial analysis status is 200': (r) => r.status === 200,
    'financial analysis has ratios': (r) => r.json('financial_ratios') !== undefined,
  }) || errorRate.add(1);
  
  sleep(1);
  
  // Test 6: User Profile
  let profileResponse = http.get(`${BASE_URL}/api/v1/auth/profile`, {
    headers: authHeaders,
  });
  
  check(profileResponse, {
    'profile status is 200': (r) => r.status === 200,
    'profile has email': (r) => r.json('email') !== undefined,
  }) || errorRate.add(1);
  
  sleep(1);
  
  // Test 7: Cache Performance (multiple requests for same data)
  for (let i = 0; i < 3; i++) {
    let cachedStockResponse = http.get(`${BASE_URL}/api/v1/data/stock/${stockSymbol}`, {
      headers: authHeaders,
    });
    
    check(cachedStockResponse, {
      'cached stock data status is 200': (r) => r.status === 200,
      'cached response time < 100ms': (r) => r.timings.duration < 100,
    }) || errorRate.add(1);
    
    sleep(0.5);
  }
  
  // Test 8: Concurrent Analysis Requests
  let requests = [];
  for (let i = 0; i < 3; i++) {
    requests.push(['GET', `${BASE_URL}/api/v1/methodology/list`, null, { headers: authHeaders }]);
  }
  
  let batchResponses = http.batch(requests);
  batchResponses.forEach((response, index) => {
    check(response, {
      [`batch request ${index} status is 200`]: (r) => r.status === 200,
    }) || errorRate.add(1);
  });
  
  sleep(2);
}

export function teardown(data) {
  console.log('Performance test completed');
  
  // Cleanup if needed
  let healthResponse = http.get(`${data.baseUrl}/health`);
  check(healthResponse, {
    'final health check status is 200': (r) => r.status === 200,
  });
}

