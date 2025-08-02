const { revokeMintAuthority } = require('./revoke-mint-authority');
const { revokeFreezeAuthority } = require('./revoke-freeze-authority');
const { revokeUpdateAuthority } = require('./revoke-update-authority');
const fs = require('fs');
const config = require('./config');

async function revokeAllAuthorities() {
    try {
        console.log('=== REVOKING ALL TOKEN AUTHORITIES ===');

        if (!fs.existsSync(config.TOKEN_INFO_PATH)) {
            throw new Error(`File ${config.TOKEN_INFO_PATH} not found. Create token first.`);
        }

        const tokenInfo = JSON.parse(fs.readFileSync(config.TOKEN_INFO_PATH, 'utf-8'));
        if (!tokenInfo.tokenMint) {
            throw new Error('Token info does not contain tokenMint address');
        }

        console.log('\nRevoking Freeze Authority first:');
        const freezeResult = await revokeFreezeAuthority();

        const mintResult = await revokeMintAuthority();
        const updateResult = await revokeUpdateAuthority();

        console.log('\n=== AUTHORITY REVOCATION RESULTS ===');
        console.log('Mint Authority:', mintResult ? 'Revoked' : 'Not revoked');
        console.log('Freeze Authority:', freezeResult ? 'Revoked' : 'Not revoked');
        console.log('Update Authority:', updateResult ? 'Revoked' : 'Not revoked');

        const updatedTokenInfo = JSON.parse(fs.readFileSync(config.TOKEN_INFO_PATH, 'utf-8'));

        const explorerCluster = config.USE_MAINNET ? 'mainnet' : 'devnet';
        console.log('\nCheck your token in blockchain explorer:');
        console.log(`https://explorer.solana.com/address/${updatedTokenInfo.tokenMint}?cluster=${explorerCluster}`);
        console.log(`https://solscan.io/token/${updatedTokenInfo.tokenMint}${config.USE_MAINNET ? '' : '?cluster=devnet'}`);

        if (mintResult && freezeResult && updateResult) {
            console.log('\n✅ All token authorities successfully revoked!');
            console.log('Token is fully decentralized and cannot be modified!');
            return true;
        } else {
            console.log('\n⚠️ Not all authorities were revoked:');
            if (!mintResult) console.log('- Mint Authority still active');
            if (!freezeResult) console.log('- Freeze Authority still active');
            if (!updateResult) console.log('- Update Authority still active');

            console.log('\nTo retry revocation run:');
            if (!mintResult) console.log('node revoke-mint-authority.js');
            if (!freezeResult) console.log('node revoke-freeze-authority.js');
            if (!updateResult) console.log('node revoke-update-authority.js');

            return false;
        }
    } catch (error) {
        console.error('Error revoking authorities:', error);
        return false;
    }
}

module.exports = { revokeAllAuthorities };

if (require.main === module) {
    revokeAllAuthorities()
        .then(() => console.log('Authority revocation script completed'))
        .catch(err => console.error('Error in authority revocation script:', err));
}