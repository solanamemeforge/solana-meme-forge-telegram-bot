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

        const nullAddress = new PublicKey('11111111111111111111111111111111');
        console.log('Null address for Update Authority revocation:', nullAddress.toString());

        const transaction = new Transaction().add(
            createUpdateMetadataAccountV2Instruction(
                {
                    metadata: metadataPDA,
                    updateAuthority: wallet.publicKey,
                },
                {
                    updateMetadataAccountArgsV2: {
                        data: null, // Leave data unchanged
                        updateAuthority: nullAddress, // Set to null address
                        primarySaleHappened: null,
                        isMutable: false, // Make token immutable
                    },
                }
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

        console.log('Update Authority successfully revoked! Transaction:', signature);

        tokenInfo.updateAuthorityRevoked = true;
        tokenInfo.updateAuthorityRevokeSignature = signature;
        tokenInfo.isMutable = false;
        fs.writeFileSync(config.TOKEN_INFO_PATH, JSON.stringify(tokenInfo, null, 2));

        return true;
    } catch (error) {
        console.error('Error revoking Update Authority:', error);
        if (error.logs) {
            console.error('Error logs:', error.logs);
        }
        return false;
    }
}

module.exports = { revokeUpdateAuthority };