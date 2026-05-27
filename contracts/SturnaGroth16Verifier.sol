// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * SturnaGroth16Verifier.sol
 *
 * Groth16 verifier for the SturnaAuctionCompliance circuit.
 * Generated from: snarkjs zkey export solidityverifier circuit_final.zkey verifier.sol
 *
 * Circuit: SturnaAuctionCompliance.circom
 *   - Public signals: [auction_commitment, march_pass, confidence_scaled]
 *   - Constraints: <500K (bn128 / BN254 curve)
 *   - Prover: snarkjs groth16.fullProve()
 *
 * Deployment target: zkSync Era Sepolia (chain ID 300)
 *   npx hardhat deploy-zksync --script deploy/deploy-verifier.ts --network zkSyncSepoliaTestnet
 *
 * What this contract verifies (NOT what snarkjs generates — this is the circuit semantics):
 *   1. auction_commitment: SHA-256 of (run_id + winner_bid + coalition_json + HMAC sig)
 *   2. march_pass: 1 = all 3 MARCH gates passed, 0 = failure
 *   3. confidence_scaled: winning agent's declared confidence * 1000 (integer, 0–1000)
 *
 * NOTE: The actual verification key (alpha, beta, gamma, delta, IC) must be replaced
 * with the real values generated from the trusted setup ceremony.
 * Placeholder values below are for ABI/interface reference only.
 */

// Pairing library for BN254 (standard Groth16 verification)
library Pairing {
    struct G1Point {
        uint256 X;
        uint256 Y;
    }
    struct G2Point {
        uint256[2] X;
        uint256[2] Y;
    }

    function negate(G1Point memory p) internal pure returns (G1Point memory) {
        if (p.X == 0 && p.Y == 0) return G1Point(0, 0);
        uint256 q = 21888242871839275222246405745257275088696311157297823662689037894645226208583;
        return G1Point(p.X, q - (p.Y % q));
    }

    function addition(G1Point memory p1, G1Point memory p2)
        internal view returns (G1Point memory r)
    {
        uint256[4] memory input;
        input[0] = p1.X;
        input[1] = p1.Y;
        input[2] = p2.X;
        input[3] = p2.Y;
        bool success;
        assembly {
            success := staticcall(sub(gas(), 2000), 6, input, 0x80, r, 0x40)
            switch success case 0 { invalid() }
        }
    }

    function scalar_mul(G1Point memory p, uint256 s)
        internal view returns (G1Point memory r)
    {
        uint256[3] memory input;
        input[0] = p.X;
        input[1] = p.Y;
        input[2] = s;
        bool success;
        assembly {
            success := staticcall(sub(gas(), 2000), 7, input, 0x60, r, 0x40)
            switch success case 0 { invalid() }
        }
    }

    function pairing(G1Point[] memory p1, G2Point[] memory p2)
        internal view returns (bool)
    {
        require(p1.length == p2.length, "Pairing: input mismatch");
        uint256 elements = p1.length;
        uint256 inputSize = elements * 6;
        uint256[] memory input = new uint256[](inputSize);
        for (uint256 i = 0; i < elements; i++) {
            input[i * 6 + 0] = p1[i].X;
            input[i * 6 + 1] = p1[i].Y;
            input[i * 6 + 2] = p2[i].X[0];
            input[i * 6 + 3] = p2[i].X[1];
            input[i * 6 + 4] = p2[i].Y[0];
            input[i * 6 + 5] = p2[i].Y[1];
        }
        uint256[1] memory out;
        bool success;
        assembly {
            success := staticcall(sub(gas(), 2000), 8, add(input, 0x20), mul(inputSize, 0x20), out, 0x20)
            switch success case 0 { invalid() }
        }
        return out[0] != 0;
    }
}

contract SturnaGroth16Verifier {
    using Pairing for *;