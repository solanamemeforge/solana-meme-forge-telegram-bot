function getConfigFromPython() {
  const fs = require('fs');
  const path = require('path');
  const configPath = path.join(__dirname, '..', 'config.py');
  const configPy = fs.readFileSync(configPath, 'utf-8');

  const debugMatch = configPy.match(/DEBUG_MODE\s*=\s*(True|False)/);
  if (!debugMatch) throw new Error('DEBUG_MODE not found in config.py');
  const DEBUG_MODE = debugMatch[1] === 'True';

  const predefinedMintMatch = configPy.match(/USE_PREDEFINED_MINT\s*=\s*(True|False)/);
  if (!predefinedMintMatch) throw new Error('USE_PREDEFINED_MINT not found in config.py');
  let USE_PREDEFINED_MINT = predefinedMintMatch[1] === 'True';

  const memeDatabaseMatch = configPy.match(/USE_MEME_MINT_DATABASE\s*=\s*(True|False)/);
  if (!memeDatabaseMatch) throw new Error('USE_MEME_MINT_DATABASE not found in config.py');
  const USE_MEME_MINT_DATABASE = memeDatabaseMatch[1] === 'True';

  if (USE_MEME_MINT_DATABASE) {
    USE_PREDEFINED_MINT = false;
  }

  const testModeMatch = configPy.match(/TEST_MODE\s*=\s*(True|False)/);
  if (!testModeMatch) throw new Error('TEST_MODE not found in config.py');
  const TEST_MODE = testModeMatch[1] === 'True';

  const privateKeyMatch = configPy.match(/PREDEFINED_MINT_PRIVATE_KEY\s*=\s*['"]([^'"]+)['"]/);
  if (!privateKeyMatch) {
    throw new Error('PREDEFINED_MINT_PRIVATE_KEY not found in config.py');
  }
  const PREDEFINED_MINT_PRIVATE_KEY = privateKeyMatch[1];

  const tokenNameMatch = configPy.match(/['"]TOKEN_NAME['"]:\s*['"]([^'"]+)['"]/);
  const tokenSymbolMatch = configPy.match(/['"]TOKEN_SYMBOL['"]:\s*['"]([^'"]+)['"]/);
  const totalSupplyMatch = configPy.match(/['"]TOTAL_SUPPLY['"]:\s*(\d+)/);
  const logoUrlMatch = configPy.match(/['"]LOGO_URL['"]:\s*['"]([^'"]+)['"]/);
  const tokenDescMatch = configPy.match(/['"]TOKEN_DESCRIPTION['"]:\s*['"]([^'"]+)['"]/);
  const userWalletMatch = configPy.match(/['"]USER_WALLET['"]:\s*['"]([^'"]+)['"]/);

  if (!tokenNameMatch || !tokenSymbolMatch || !totalSupplyMatch || !logoUrlMatch || !tokenDescMatch || !userWalletMatch) {
    throw new Error('TEST_PARAMS data not found in config.py');
  }

  const TEST_PARAMS = {
    TOKEN_NAME: tokenNameMatch[1],
    TOKEN_SYMBOL: tokenSymbolMatch[1],
    TOTAL_SUPPLY: parseInt(totalSupplyMatch[1]),
    LOGO_URL: logoUrlMatch[1],
    TOKEN_DESCRIPTION: tokenDescMatch[1],
    USER_WALLET: userWalletMatch[1]
  };

  return { DEBUG_MODE, USE_PREDEFINED_MINT, USE_MEME_MINT_DATABASE, TEST_MODE, PREDEFINED_MINT_PRIVATE_KEY, TEST_PARAMS };
}

const { DEBUG_MODE, USE_PREDEFINED_MINT, USE_MEME_MINT_DATABASE, TEST_MODE, PREDEFINED_MINT_PRIVATE_KEY, TEST_PARAMS } = getConfigFromPython();

const USE_MAINNET = !DEBUG_MODE;

// PLACEHOLDER API KEYS - Replace with your own
const HELIUS_API_KEY = 'your-helius-api-key-here';
const NETWORK_URL = USE_MAINNET
  ? `https://mainnet.helius-rpc.com/?api-key=${HELIUS_API_KEY}`
  : `https://devnet.helius-rpc.com/?api-key=${HELIUS_API_KEY}`;

const WALLET_TYPE = 'privateKey';
const WALLET_PATH = 'wallet.json';

const DECIMALS = 9;

const REVOKE_AUTHORITIES = { MINT: true, FREEZE: true, UPDATE: true };

const TOKEN_INFO_PATH = 'token-info.json';

// PLACEHOLDER IPFS KEYS - Replace with your own
const PINATA_API_KEY = 'your-pinata-api-key';
const PINATA_SECRET_KEY = 'your-pinata-secret-key';

module.exports = {
  DEBUG_MODE, USE_MAINNET, NETWORK_URL, WALLET_TYPE, WALLET_PATH,
  DECIMALS, REVOKE_AUTHORITIES, TOKEN_INFO_PATH,
  PINATA_API_KEY, PINATA_SECRET_KEY, TEST_MODE, TEST_PARAMS,
  USE_PREDEFINED_MINT, USE_MEME_MINT_DATABASE, PREDEFINED_MINT_PRIVATE_KEY
};