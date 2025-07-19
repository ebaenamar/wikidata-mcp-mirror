const http = require('http');
const https = require('https');
const { URL } = require('url');
const EventSource = require('eventsource');
const readline = require('readline');

// Configuration
const MCP_POST_URL = 'http://localhost:8000/messages/';
const MCP_SSE_URL = 'http://localhost:8000/sse/';
const PORT = 3000;
const RECONNECT_DELAY = 5000; // 5 seconds

// Parse URL to determine HTTP or HTTPS
const postUrl = new URL(MCP_POST_URL);
const httpModule = postUrl.protocol === 'https:' ? https : http;

// Set up readline for reading from stdin
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

// Handle incoming messages from Claude Desktop (via stdio)
rl.on('line', (line) => {
  try {
    const message = JSON.parse(line);
    console.error('Received from Claude Desktop:', JSON.stringify(message, null, 2));
    
    // Forward message to MCP server via HTTP POST
    const options = {
      hostname: postUrl.hostname,
      port: postUrl.port || (postUrl.protocol === 'https:' ? 443 : 80),
      path: postUrl.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': postUrl.hostname
      }
    };
    
    console.error('Sending request to MCP server:', JSON.stringify(options, null, 2));
    
    const req = httpModule.request(options,
      (res) => {
        let data = '';
        res.on('data', (chunk) => {
          data += chunk;
          // Forward response back to Claude Desktop
          process.stdout.write(chunk);
        });
        
        res.on('end', () => {
          if (res.statusCode !== 200) {
            console.error(`HTTP error! Status: ${res.statusCode}`);
            console.error('Response:', data);
          }
        });
      }
    );
    
    req.on('error', (error) => {
      console.error('Error forwarding message to MCP server:', error);
    });
    
    req.write(JSON.stringify(message));
    req.end();
    
  } catch (error) {
    console.error('Error processing message:', error);
  }
});

// Function to create a new SSE connection
function createSSEConnection() {
  console.error('Creating new SSE connection to:', MCP_SSE_URL);
  
  const es = new EventSource(MCP_SSE_URL, {
    headers: {
      'Accept': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    }
  });

  es.on('open', () => {
    console.error('SSE Connection established');
  });

  es.on('message', (event) => {
    try {
      console.error('Received from MCP server:', event.data);
      // Forward message to Claude Desktop (via stdout)
      process.stdout.write(event.data + '\n');
    } catch (error) {
      console.error('Error processing SSE message:', error);
    }
  });

  es.on('error', (error) => {
    console.error('SSE Error:', error);
    console.error('Event details:', {
      type: error.type,
      message: error.message,
      status: error.status,
      readyState: es.readyState
    });
    
    // Close the current connection
    es.close();
    
    // Attempt to reconnect after a delay
    console.error(`Attempting to reconnect in ${RECONNECT_DELAY/1000} seconds...`);
    setTimeout(createSSEConnection, RECONNECT_DELAY);
  });

  return es;
}

// Initialize SSE connection
let es = createSSEConnection();

console.error(`MCP Gateway started. Forwarding messages to ${MCP_POST_URL}`);
console.error('Press Ctrl+C to stop.');

// Handle process termination
process.on('SIGINT', () => {
  console.error('\nShutting down MCP Gateway...');
  es.close();
  process.exit(0);
});
