// Load environment variables from .env file
require('dotenv').config();

// Import the PinataSDK
const { PinataSDK } = require('pinata');

// Get the Pinata JWT from environment variables
const pinataJwt = process.env.PINATA_JWT;

if (!pinataJwt) {
  console.error('Pinata JWT is missing. Please make sure you have it in your .env file.');
  process.exit(1); // Exit the app if the JWT is missing
}

// Create a Pinata SDK instance
const pinata = new PinataSDK({
  pinataJwt, // Use the JWT token from the environment variable
});

// Function to list files from Pinata
async function listFiles() {
  try {
    const response = await pinata.files.list().limit(10);  // List files with limit
    console.log('Files:', response.files);
  } catch (error) {
    console.error('Error fetching files:', error);
  }
}

// Call the function to list files
listFiles();
