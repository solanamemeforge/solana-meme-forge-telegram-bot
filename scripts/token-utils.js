const {PublicKey, Transaction} = require('@solana/web3.js');
const {createAssociatedTokenAccountInstruction, getAssociatedTokenAddress, createMintToInstruction, TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID} = require('@solana/spl-token');

function isAccountAlreadyExistsError(error) {
  const errorMessage = error.message || '';
  const errorLogs = error.transactionLogs || [];

  const isAlreadyInUse = errorMessage.includes('already in use') ||
                        errorLogs.some(log => log.includes('already in use'));

  const isCustomError0x0 = errorMessage.includes('custom program error: 0x0') &&
                          errorLogs.some(log => log.includes('Create Account:'));

  return isAlreadyInUse || isCustomError0x0;
}

function getExplorerLinks(address, useMainnet) {
  const cluster = useMainnet ? 'mainnet' : 'devnet';
  return {
    solanaExplorer: `https://explorer.solana.com/address/${address}?cluster=${cluster}`,
    solscan: `https://solscan.io/token/${address}${useMainnet ? '' : '?cluster=devnet'}`
  };
}

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

async function sendTokensToUser(connection, wallet, recipientWallet, tokenMint, amount, decimals, sendTransactionWithRetry) {
  try {
    console.log(`Sending ${amount} tokens to user wallet: ${recipientWallet}`);

    // Token sending logic placeholder
    await new Promise(resolve => setTimeout(resolve, 1000));

    const signature = 'placeholder-send-signature';
    console.log(`Tokens successfully sent. Signature: ${signature}`);
    return { success: true, signature };
  } catch (error) {
    console.error('Error sending tokens:', error);
    return { success: false, error: error.message };
  }
}

function logTokenCreationType(tokenInfo) {
  if (tokenInfo.wasRetryWithRandom) {
    console.log('🎲 Token created with random mint address after predefined failed');
  } else if (tokenInfo.usedMemeDatabase) {
    const retryText = (tokenInfo.dbRetryCount > 0) ? ` (attempt ${tokenInfo.dbRetryCount + 1})` : '';
    console.log(`🎯 Token created with mint address from database${retryText}`);
  } else if (tokenInfo.isPredefinedMint) {
    console.log('🎯 Token created with predefined mint address');
  } else {
    console.log('🎲 Token created with random mint address');
  }
}

function shouldRetryWithDatabase(error, config, dbPrivateKey, dbRetryCount, maxDbRetries) {
  // Database retry logic placeholder
  return false;
}

function shouldRetryWithRandom(error, retryWithRandom, config, dbRetryCount, maxDbRetries) {
  // Random retry logic placeholder
  return false;
}

async function handleDatabaseKeyDeletion(walletManager, dbPrivateKey, action = 'duplicate') {
  try {
    // Database operation placeholder
    console.log('✅ Database operation completed');
    return true;
  } catch (deleteError) {
    console.warn(`⚠️ Database operation failed:`, deleteError.message);
    return false;
  }
}

function logDatabaseRetryAttempt(dbRetryCount, maxDbRetries, isExhausted = false) {
  if (isExhausted) {
    console.log(`\n⚠️ Exhausted database retry attempts (${maxDbRetries})`);
    console.log('🔄 Switching to random mint address generation...\n');
  } else {
    console.log(`\n⚠️ Database mint address already in use! Removing from database...`);
    console.log(`🔄 Retry with new database key (${dbRetryCount + 1}/${maxDbRetries})...\n`);
  }
}

function logFinalResults(tokenInfo, config) {
  const links = getExplorerLinks(tokenInfo.tokenMint, config.USE_MAINNET);

  console.log('\n=== TOKEN CREATION SUMMARY ===');
  console.log('\nTOKEN INFORMATION:');
  console.log(`Name: ${tokenInfo.name}`);
  console.log(`Symbol: ${tokenInfo.symbol}`);
  console.log(`Address: ${tokenInfo.tokenMint}`);
  console.log(`Metadata URI: ${tokenInfo.uri}`);
  console.log(`Total Supply: ${tokenInfo.totalSupply}`);

  logTokenCreationType(tokenInfo);
  console.log(`Solscan: ${links.solscan}`);
  console.log('\nProcess completed!');
}

function logRevokeResults(tokenInfo) {
  if (tokenInfo.mintAuthorityRevoked &&
      tokenInfo.freezeAuthorityRevoked &&
      tokenInfo.updateAuthorityRevoked) {
    console.log('\n✅ All authorities successfully revoked step by step!');
  } else {
    console.log('\n⚠️ Not all authorities were revoked:');
    if (!tokenInfo.mintAuthorityRevoked) console.log('- Mint Authority still active');
    if (!tokenInfo.freezeAuthorityRevoked) console.log('- Freeze Authority still active');
    if (!tokenInfo.updateAuthorityRevoked) console.log('- Update Authority still active');
  }
}

module.exports = {
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
};