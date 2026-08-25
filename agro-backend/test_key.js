const https = require('https');

const key = 'paste your key';
const url = `https://generativelanguage.googleapis.com/v1beta/models/gemma-4-26b-a4b-it?key=${key}`;

https.get(url, (res) => {
  let data = '';
  res.on('data', (chunk) => { data += chunk; });
  res.on('end', () => {
    console.log(data);
  });
}).on('error', (err) => {
  console.error('Error:', err.message);
});
