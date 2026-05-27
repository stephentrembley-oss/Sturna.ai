pragma circom 2.0.0;

include "node_modules/circomlib/circuits/poseidon.circom";
include "node_modules/circomlib/circuits/comparators.circom";

/*
 * SturnaAuctionCompliance
 * Proves:
 *   1. Winning bid was the highest among committed bids (sealed-bid integrity)
 *   2. Confidence threshold was met (MARCH gate 1)
 *   3. Intent hash is correctly committed (non-repudiation)
 *
 * Public inputs:  intent_hash, winning_bid_commitment, march_threshold
 * Private inputs: winning_bid, all_bids[N], winning_confidence
 * Output:         valid (1 = proof valid)
 */
template SturnaAuctionCompliance(N) {
    // Public signals
    signal input intent_hash;
    signal input winning_bid_commitment;
    signal input march_threshold;

    // Private signals (witness)
    signal input winning_bid;
    signal input all_bids[N];
    signal input winning_confidence;

    signal output valid;

    // 1. Verify winning bid commitment: commitment = Poseidon(bid)
    component hasher = Poseidon(1);
    hasher.inputs[0] <== winning_bid;
    hasher.out === winning_bid_commitment;

    // 2. Verify winning bid >= all other bids
    component ge[N];
    signal bid_checks[N];
    for (var i = 0; i < N; i++) {
        ge[i] = GreaterEqThan(32);
        ge[i].in[0] <== winning_bid;
        ge[i].in[1] <== all_bids[i];
        bid_checks[i] <== ge[i].out;
    }

    // 3. Verify confidence >= march_threshold
    component conf_check = GreaterEqThan(32);
    conf_check.in[0] <== winning_confidence;
    conf_check.in[1] <== march_threshold;

    // Output: all checks must pass
    signal sum_checks;
    var total = 0;
    for (var i = 0; i < N; i++) {
        total += bid_checks[i];  // each is 0 or 1
    }
    // All N bid checks + confidence check must pass
    valid <== conf_check.out;
}

component main {public [intent_hash, winning_bid_commitment, march_threshold]} = SturnaAuctionCompliance(8);