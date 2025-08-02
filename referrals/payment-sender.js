const { Connection, Keypair, PublicKey, Transaction, SystemProgram, sendAndConfirmTransaction, LAMPORTS_PER_SOL } = require('@solana/web3.js');
const { updateTransactionBlockhash } = require('../scripts/update-blockhash.js');
const fs = require('fs');
const { mnemonicToSeedSync } = require('bip39');
const { derivePath } = require('ed25519-hd-key');
const config = require('../scripts/config.js');

function loadWallet() {
    const walletData = JSON.parse(fs.readFileSync(config.WALLET_PATH, 'utf-8'));
    if (config.WALLET_TYPE === 'privateKey') {
        return Keypair.fromSecretKey(Buffer.from(walletData.privateKey, 'hex'));
    }
    if (config.WALLET_TYPE === 'mnemonic') {
        const seed = mnemonicToSeedSync(walletData.mnemonic);
        return Keypair.fromSeed(derivePath("m/44'/501'/0'/0'", seed.toString('hex')).key);
    }
    throw new Error('Unknown wallet type in config');
}

const getConnection = () => new Connection(config.NETWORK_URL, {
    commitment: 'confirmed',
    confirmTransactionInitialTimeout: 60000
});

async function sendReferralPayment(referrerWalletAddress, amountSol, paymentDetails = {}) {
    try {
        const senderWallet = loadWallet();
        const connection = getConnection();

        const balance = await connection.getBalance(senderWallet.publicKey);
        const balanceSol = balance / LAMPORTS_PER_SOL;

        const amountLamports = Math.floor(amountSol * LAMPORTS_PER_SOL);
        const minRequiredBalance = amountLamports + 5000;

        if (balance < minRequiredBalance) {
            const errorMsg = `Insufficient SOL. Required: ${minRequiredBalance / LAMPORTS_PER_SOL} SOL, available: ${balanceSol} SOL`;
            return { success: false, error: errorMsg };
        }

        let recipientPubkey;
        try {
            recipientPubkey = new PublicKey(referrerWalletAddress);
        } catch (error) {
            const errorMsg = `Invalid recipient address: ${referrerWalletAddress}`;
            return { success: false, error: errorMsg };
        }

        const transaction = new Transaction().add(
            SystemProgram.transfer({
                fromPubkey: senderWallet.publicKey,
                toPubkey: recipientPubkey,
                lamports: amountLamports,
            })
        );

        await updateTransactionBlockhash(transaction, connection, {
            feePayer: senderWallet.publicKey,
            commitment: 'finalized'
        });

        const signature = await sendAndConfirmTransaction(
            connection,
            transaction,
            [senderWallet],
            {
                commitment: 'confirmed',
                preflightCommitment: 'processed',
                maxRetries: 5
            }
        );

        return {
            success: true,
            txHash: signature,
            amount: amountSol,
            recipient: referrerWalletAddress,
            paymentDetails: paymentDetails
        };

    } catch (error) {
        let errorMessage = error.message;

        if (error.message.includes('insufficient funds')) {
            errorMessage = 'Insufficient funds in wallet';
        } else if (error.message.includes('blockhash')) {
            errorMessage = 'Error getting current network blockhash';
        } else if (error.message.includes('timeout')) {
            errorMessage = 'Transaction timeout';
        }

        return {
            success: false,
            error: errorMessage,
            originalError: error.message
        };
    }
}

async function sendReferralPaymentFromArgs() {
    const args = process.argv.slice(2);

    if (args.length < 2) {
        process.stderr.write('Usage: node payment-sender.js <wallet_address> <amount_sol> [payment_details_json]\n');
        process.exit(1);
    }

    const walletAddress = args[0];
    const amountSol = parseFloat(args[1]);
    let paymentDetails = {};

    try {
        if (args[2]) {
            paymentDetails = JSON.parse(args[2]);
        }
    } catch (e) {
        paymentDetails = { note: args[2] || 'referral_payout' };
    }

    if (isNaN(amountSol) || amountSol <= 0) {
        process.stderr.write('Error: amount_sol must be a positive number\n');
        process.exit(1);
    }

    try {
        const result = await sendReferralPayment(walletAddress, amountSol, paymentDetails);
        console.log(JSON.stringify(result));

        if (result.success) {
            process.exit(0);
        } else {
            process.exit(1);
        }
    } catch (error) {
        console.log(JSON.stringify({ success: false, error: error.message }));
        process.exit(1);
    }
}

module.exports = {
    sendReferralPayment
};

if (require.main === module) {
    sendReferralPaymentFromArgs();
}