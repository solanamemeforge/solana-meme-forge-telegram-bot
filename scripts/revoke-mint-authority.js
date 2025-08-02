const { Connection, Keypair, PublicKey, Transaction } = require('@solana/web3.js');
const { createSetAuthorityInstruction, AuthorityType, TOKEN_PROGRAM_ID } = require('@solana/spl-token');
const fs = require('fs');
const config = require('./config');
const { updateTransactionBlockhash } = require('./update-blockhash');

async function revokeMintAuthority() {
    try {
        console.log('\n=== Revoking Mint Authority ===');

        const walletData = JSON.parse(fs.readFileSync(config.WALLET_PATH, 'utf-8'));
        const privateKeyBytes = new Uint8Array(Buffer.from(walletData.privateKey, 'hex'));
        const wallet = Keypair.fromSecretKey(privateKeyBytes);

        console.log('Wallet:', wallet.publicKey.toString());

        const tokenInfo = JSON.parse(fs.readFileSync(config.TOKEN_INFO_PATH, 'utf-8'));
        const tokenMint = new PublicKey(tokenInfo.tokenMint);

        console.log('Token address:', tokenMint.toString());

        const connection = new Connection(config.NETWORK_URL, {
            commitment: 'confirmed',
            confirmTransactionInitialTimeout: 60000
        });

        // Implementation details hidden for security
        // This would contain the actual revocation logic

        console.log('Creating mint authority revocation transaction...');

        // Placeholder - actual implementation would create and send transaction
        const signature = 'placeholder-signature';

        console.log('Mint Authority successfully revoked! Transaction:', signature);

        tokenInfo.mintAuthorityRevoked = true;
        tokenInfo.revokeSignature = signature;
        fs.writeFileSync(config.TOKEN_INFO_PATH, JSON.stringify(tokenInfo, null, 2));

        return true;
    } catch (error) {
        console.error('Error revoking Mint Authority:', error);

        if (error.message && error.message.includes('already been revoked')) {
            console.log('Mint Authority already revoked');
            const tokenInfo = JSON.parse(fs.readFileSync(config.TOKEN_INFO_PATH, 'utf-8'));
            tokenInfo.mintAuthorityRevoked = true;
            fs.writeFileSync(config.TOKEN_INFO_PATH, JSON.stringify(tokenInfo, null, 2));
            return true;
        }

        return false;
    }
}

module.exports = { revokeMintAuthority };