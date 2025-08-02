const { Connection } = require('@solana/web3.js');
const axios = require('axios');
const config = require('./config');

async function updateTransactionBlockhash(transaction, connection, options = {}) {
    try {
        const commitment = options.commitment || 'finalized';
        const logEnabled = options.log !== false;

        if (logEnabled) {
            console.log('Getting new blockhash...');
        }

        // Try using Helius API first
        try {
            const heliusUrl = config.NETWORK_URL;

            const rpcRequest = {
                jsonrpc: '2.0',
                id: 1,
                method: 'getLatestBlockhash',
                params: [{ commitment }]
            };

            const response = await axios.post(heliusUrl, rpcRequest, {
                headers: {
                    'Content-Type': 'application/json'
                },
                timeout: 10000
            });

            if (response.data && response.data.result && response.data.result.value) {
                const { blockhash, lastValidBlockHeight } = response.data.result.value;

                transaction.recentBlockhash = blockhash;
                transaction.lastValidBlockHeight = lastValidBlockHeight;

                if (options.feePayer) {
                    transaction.feePayer = options.feePayer;
                }

                if (logEnabled) {
                    console.log(`Transaction updated with blockhash: ${blockhash}`);
                }

                return transaction;
            }
        } catch (heliusError) {
            console.warn('Helius API error, falling back to standard method:', heliusError.message);
        }

        // Fallback to standard Connection method
        const { blockhash, lastValidBlockHeight } = await connection.getLatestBlockhash(commitment);

        transaction.recentBlockhash = blockhash;
        transaction.lastValidBlockHeight = lastValidBlockHeight;

        if (options.feePayer) {
            transaction.feePayer = options.feePayer;
        }

        if (logEnabled) {
            console.log(`Transaction updated with blockhash (standard method): ${blockhash}`);
        }

        return transaction;
    } catch (error) {
        console.error('Error updating blockhash:', error);
        throw error;
    }
}

module.exports = { updateTransactionBlockhash };