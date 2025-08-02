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

        const transaction = new Transaction().add(
            createSetAuthorityInstruction(
                tokenMint,
                wallet.publicKey,
                AuthorityType.MintTokens,
                null, // Set to null to revoke
                [],
                TOKEN_PROGRAM_ID
            )
        );

        await updateTransactionBlockhash(transaction, connection, {
            feePayer: wallet.publicKey
        });

        let signature = null;
        let success = false;

        for (let attempt = 0; attempt < 2; attempt++) {
            try {
                if (attempt > 0) {
                    await updateTransactionBlockhash(transaction, connection, {
                        feePayer: wallet.publicKey
                    });
                }

                signature = await connection.sendTransaction(transaction, [wallet], {
                    skipPreflight: false,
                    preflightCommitment: 'processed',
                    maxRetries: 3
                });

                console.log(`Transaction sent, awaiting confirmation: ${signature}`);

                await connection.confirmTransaction({
                    signature,
                    blockhash: transaction.recentBlockhash,
                    lastValidBlockHeight: transaction.lastValidBlockHeight
                }, 'confirmed');

                success = true;
                break;
            } catch (error) {
                console.warn(`Error on attempt ${attempt + 1}: ${error.message}`);
                if (attempt < 1 && (
                    error.message.includes('expired') ||
                    error.message.includes('blockhash') ||
                    error.message.includes('block height exceeded')
                )) {
                    console.log('Waiting before retry...');
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    continue;
                }
                throw error;
            }
        }

        if (!success) {
            throw new Error('All transaction attempts exhausted');
        }

        console.log('Mint Authority successfully revoked! Transaction:', signature);

        tokenInfo.mintAuthorityRevoked = true;
        tokenInfo.revokeSignature = signature;
        fs.writeFileSync(config.TOKEN_INFO_PATH, JSON.stringify(tokenInfo, null, 2));

        return true;
    } catch (error) {
        console.error('Error revoking Mint Authority:', error);
        if (error.logs) {
            console.error('Error logs:', error.logs);
        }

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