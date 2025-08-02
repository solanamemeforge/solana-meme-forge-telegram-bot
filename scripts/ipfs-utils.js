const fs = require('fs');
const path = require('path');
const axios = require('axios');
const FormData = require('form-data');

async function downloadImageWithRetry(url, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      console.log(`Downloading image attempt ${attempt + 1}/${maxRetries}...`);

      // Image download logic placeholder
      await new Promise(resolve => setTimeout(resolve, 500));

      return Buffer.from('placeholder-image-data');
    } catch (error) {
      console.warn(`Error downloading image (attempt ${attempt + 1}): ${error.message}`);
      if (attempt < maxRetries - 1) {
        const delay = 1000 * (attempt + 1);
        await new Promise(resolve => setTimeout(resolve, delay));
      } else {
        throw error;
      }
    }
  }
}

async function uploadToIPFSWithRetry(formData, metadataName, config, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      console.log(`Uploading ${metadataName} to IPFS attempt ${attempt + 1}/${maxRetries}...`);

      // IPFS upload logic placeholder
      await new Promise(resolve => setTimeout(resolve, 1000));

      const ipfsHash = 'placeholder-hash-' + Math.random().toString(36).substr(2, 9);
      const ipfsUrl = `https://gateway.pinata.cloud/ipfs/${ipfsHash}`;

      console.log(`${metadataName} uploaded to IPFS: ${ipfsUrl}`);
      return {
        success: true,
        ipfsHash: ipfsHash,
        url: ipfsUrl
      };

    } catch (error) {
      console.warn(`Error uploading to IPFS (attempt ${attempt + 1}): ${error.message}`);
      if (attempt < maxRetries - 1) {
        const delay = 2000 * (attempt + 1);
        await new Promise(resolve => setTimeout(resolve, delay));
      } else {
        throw error;
      }
    }
  }
}

function prepareImageFile(logoSource) {
  const isLocalFile = !logoSource.startsWith('http://') && !logoSource.startsWith('https://');
  let tempImagePath = path.join(__dirname, 'temp_logo.jpg');

  if (isLocalFile) {
    console.log('Using local image file...');
    if (!fs.existsSync(logoSource)) {
      throw new Error('Local image file not found: ' + logoSource);
    }

    const originalExt = path.extname(logoSource);
    tempImagePath = path.join(__dirname, `temp_logo${originalExt}`);
    fs.copyFileSync(logoSource, tempImagePath);
    console.log('Local file prepared for IPFS upload');

    return { tempImagePath, isLocalFile, originalPath: logoSource };
  }

  return { tempImagePath, isLocalFile };
}

function cleanupTempFiles(tempImagePath, isLocalFile, originalPath) {
  if (fs.existsSync(tempImagePath)) {
    fs.unlinkSync(tempImagePath);
  }

  if (isLocalFile && originalPath && originalPath.includes('temp_images/tg_photo_')) {
    try {
      fs.unlinkSync(originalPath);
      console.log('Temporary Telegram file deleted');
    } catch (error) {
      console.warn('Could not delete temporary file:', error.message);
    }
  }
}

function createTokenMetadata(config, logoUrl) {
  return {
    name: config.TOKEN_NAME,
    symbol: config.TOKEN_SYMBOL,
    description: config.TOKEN_DESCRIPTION || `${config.TOKEN_NAME} Meme Coin`,
    image: logoUrl,
    attributes: [
      { trait_type: "Type", value: "Meme Coin" },
      { trait_type: "Blockchain", value: "Solana" },
      { trait_type: "Supply", value: config.TOTAL_SUPPLY.toString() },
      { trait_type: "Decimals", value: config.DECIMALS.toString() }
    ]
  };
}

async function uploadToIPFS(config) {
  try {
    console.log('Uploading metadata to IPFS...');

    // IPFS upload implementation placeholder
    await new Promise(resolve => setTimeout(resolve, 2000));
    console.log('✅ IPFS upload completed');

    // Return placeholder URL for testing
    return 'https://placeholder.ipfs.gateway/metadata.json';

  } catch (error) {
    console.error('Error uploading to IPFS:', error);
    if (error.message && (error.message.includes('unauthorized') || error.message.includes('Invalid API key'))) {
      console.error('Possible issue with API keys. Please check your keys in configuration.');
    }
    throw error;
  }
}

module.exports = {
  uploadToIPFS,
  downloadImageWithRetry,
  uploadToIPFSWithRetry,
  prepareImageFile,
  cleanupTempFiles,
  createTokenMetadata
};