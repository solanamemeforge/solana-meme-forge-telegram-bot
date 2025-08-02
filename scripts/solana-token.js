const {Connection, Keypair, PublicKey, Transaction, SystemProgram, sendAndConfirmTransaction} = require('@solana/web3.js');
const { updateTransactionBlockhash } = require('./update-blockhash.js');
const {createInitializeMintInstruction, getMinimumBalanceForRentExemptMint, createAssociatedTokenAccountInstruction,
  getAssociatedTokenAddress, createMintToInstruction, MINT_SIZE, TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID} = require('@solana/spl-token');
const {createCreateMetadataAccountV3Instruction, PROGRAM_ID} = require('@metaplex-foundation/mpl-token-metadata');
const fs = require('fs');
const {mnemonicToSeedSync} = require('bip39');
const {derivePath} = require('ed25519-hd-key');
const bs58 = require('bs58');
const config = require('./config.js');
const { revokeAllAuthorities } = require('./revoke-authorities.js');
const { revokeMintAuthority } = require('./revoke-mint-authority.js');
const { revokeFreezeAuthority } = require('./revoke-freeze-authority.js');
const { revokeUpdateAuthority } = require('./revoke-update-authority.js');
const { uploadToIPFS } = require('./ipfs-utils.js');
const {
  isAccountAlreadyExistsError,
  getExplorerLinks,
  sleep,
  sendTokensToUser,
  logTokenCreationType,
  shouldRetryWithDatabase,
  shouldRetryWithRandom,
  handleDatabaseKeyDeletion,
  logDatabaseRetryAttempt,
  logFinalResults,
  logRevokeResults
} = require('./token-utils.js');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');
const { walletManager } = require('../database/db-wallet-manager.js');
const { customAddressManager } = require('../database/db-wallet-manager.js');

let dbPrivateKey = null;

const argv = yargs(hideBin(process.argv))
  .option('params', {
    describe: 'JSON string with parameters to override config settings',
    type: 'string',
  })
  .argv;

let runtimeConfig = { ...config };
if (argv.params) {
  try {
    const params = JSON.parse(argv.params);
    runtimeConfig = { ...config, ...params };
    console.log('Parameters overridden:', params);
  } catch (error) {
    console.error('Error parsing parameters:', error);
  }
}

if (runtimeConfig.TEST_MODE) {
  console.log('Running in test mode, using test parameters');
  runtimeConfig = { ...runtimeConfig, ...runtimeConfig.TEST_PARAMS };
}

function loadWallet() {
  const walletData = JSON.parse(fs.readFileSync(runtimeConfig.WALLET_PATH, 'utf-8'));
  if (runtimeConfig.WALLET_TYPE === 'privateKey')
    return Keypair.fromSecretKey(Buffer.from(walletData.privateKey, 'hex'));
  if (runtimeConfig.WALLET_TYPE === 'mnemonic') {
    const seed = mnemonicToSeedSync(walletData.mnemonic);
    return Keypair.fromSeed(derivePath("m/44'/501'/0'/0'", seed.toString('hex')).key);
  }
  throw new Error('Unknown wallet type in config');
}

function loadWalletPublicKey() {
  const walletData = JSON.parse(fs.readFileSync(runtimeConfig.WALLET_PATH, 'utf-8'));
  return new PublicKey(walletData.publicKey);
}

async function createMintKeypair(forceRandom = false) {
  // Implementation hidden - custom mint generation logic
  console.log('Creating mint keypair...');

  // This is a placeholder - actual implementation varies based on configuration
  const keypair = Keypair.generate();
  console.log(`Generated mint address: ${keypair.publicKey.toBase58()}`);
  return keypair;
}

const getConnection = () => new Connection(runtimeConfig.NETWORK_URL, {
  commitment: 'confirmed',
  confirmTransactionInitialTimeout: 60000
});

async function sendTransactionWithRetry(connection, transaction, signers, maxRetries = 2) {
  let lastError;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      await updateTransactionBlockhash(transaction, connection, {
        feePayer: signers[0].publicKey,
        commitment: 'finalized'
      });

      console.log(`Sending transaction attempt ${attempt + 1}/${maxRetries}...`);

      const signature = await sendAndConfirmTransaction(
        connection, transaction, signers,
        { commitment: 'confirmed', preflightCommitment: 'processed', maxRetries: 5 }
      );

      console.log(`Transaction successfully executed: ${signature}`);
      return signature;
    } catch (error) {
      console.warn(`Error on attempt ${attempt + 1}: ${error.message}`);
      lastError = error;

      if (error.message.includes('expired') || error.message.includes('blockhash') ||
          error.message.includes('block height exceeded')) {
        await sleep(2000);
        continue;
      } else {
        throw error;
      }
    }
  }

  throw lastError;
}

function updateTokenInfo(tokenInfo, updates) {
  Object.assign(tokenInfo, updates);
  fs.writeFileSync(runtimeConfig.TOKEN_INFO_PATH, JSON.stringify(tokenInfo, null, 2));
  return tokenInfo;
}

async function createMemeCoin(retryWithRandom = false, dbRetryCount = 0) {
  try {
    console.log('Creating token...');

    const wallet = loadWallet();
    const connection = getConnection();

    // Check balance
    const balance = await connection.getBalance(wallet.publicKey);
    if (balance < 10000000) throw new Error('Insufficient SOL');

    // Create mint keypair
    const tokenMintKeypair = await createMintKeypair(retryWithRandom);
    const tokenMintPubkey = tokenMintKeypair.publicKey;

    // Implementation details hidden for security
    // This would contain the actual token creation logic

    console.log('Token creation process completed');

    // Placeholder token info
    const tokenInfo = {
      name: runtimeConfig.TOKEN_NAME,
      symbol: runtimeConfig.TOKEN_SYMBOL,
      tokenMint: tokenMintPubkey.toString(),
      // Other fields would be populated by actual implementation
    };

    return tokenInfo;
  } catch (error) {
    console.error('Error creating token:', error);
    throw error;
  }
}

async function setupMetadata() {
  try {
    console.log('Setting up token metadata...');

    // Implementation details hidden
    // This would contain metadata setup logic

    return 'metadata-signature-placeholder';
  } catch (error) {
    console.error('Error setting up metadata:', error);
    throw error;
  }
}

async function runFullProcess() {
  try {
    console.log('=== STARTING TOKEN CREATION PROCESS ===');

    // Step 1: Create token
    const tokenInfo = await createMemeCoin();

    // Step 2: Upload to IPFS
    const metadataUrl = await uploadToIPFS(runtimeConfig);

    // Step 3: Set metadata
    const metadataSignature = await setupMetadata();

    // Step 4: Send tokens to user (if specified)
    // Implementation hidden

    // Step 5: Revoke authorities
    // Implementation hidden

    console.log('Token creation process completed');
    return tokenInfo;
  } catch (error) {
    console.error('Error in token creation process:', error);
    throw error;
  }
}

module.exports = {
  getConnection,
  loadWallet,
  loadWalletPublicKey,
  sleep,
  updateTokenInfo,
  sendTransactionWithRetry
};

if (require.main === module) {
  runFullProcess();
}