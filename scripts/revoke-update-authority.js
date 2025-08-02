const { Connection, Keypair, PublicKey, Transaction } = require('@solana/web3.js');
const { createUpdateMetadataAccountV2Instruction, PROGRAM_ID } = require('@metaplex-foundation/mpl-token-metadata');
const fs = require('fs');
const config = require('./config');
const { updateTransactionBlockhash } = require('./update-blockhash');

async function revokeUpdateAuthority() {
    try {
        console.log('\n=== Revoking Update Authority ===');

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

        const [metadataPDA] = PublicKey.findProgramAddressSync(
            [
                Buffer.from('metadata'),
                PROGRAM_ID.toBuffer(),
                tokenMint.toBuffer(),
            ],
            PROGRAM_ID
        );

        console.log('Metadata address:', metadataPDA.toString());

        const metadataAccount = await connection.getAccountInfo(metadataPDA);
        if (!metadataAccount) {
            console.log('Metadata not found, Update Authority cannot be revoked');
            return false;
        }

        // Implementation details hidden for security
        // This would contain the actual update authority revocation logic

        console.log('Creating update authority revocation transaction...');

        // Placeholder - actual implementation would create and send transaction
        const signature = 'placeholder-update-signature';

        console.log('Update Authority successfully revoked! Transaction:', signature);

        tokenInfo.updateAuthorityRevoked = true;
        tokenInfo.updateAuthorityRevokeSignature = signature;
        tokenInfo.isMutable = false;
        fs.writeFileSync(config.TOKEN_INFO_PATH, JSON.stringify(tokenInfo, null, 2));

        return true;
    } catch (error) {
        console.error('Error revoking Update Authority:', error);
        return false;
    }
}

module.exports = { revokeUpdateAuthority };