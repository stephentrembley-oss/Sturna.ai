/**
 * Octomind Services Index
 *
 * Central barrel file for the biomimetic multi-agent layer.
 * 
 * Design philosophy:
 * - Small, focused, composable services
 * - Many start as structured interfaces / placeholders
 * - Emphasis on self-healing, coalition coordination, and compliance
 */

// === Core Biomimetic Orchestration ===
exports.ShivaLimbOrchestrator = require('./shiva-limb-orchestrator');
exports.OctopusNeuralLayer = require('./octopus-neural-layer');
exports.SelfHealingRouter = require('./self-healing-router');
exports.CrisprAgentEditor = require('./crispr-agent-editor');
exports.CephalopodRecoder = require('./cephalopod-recoder');

// === Coalition Market Auction System ===
exports.CoalitionEngine = require('./coalition-engine');
exports.CoalitionClearing = require('./coalition-clearing');
exports.CoalitionPerformance = require('./coalition-performance');
exports.CoalitionAdjacency = require('./coalition-adjacency');
exports.CoalitionTransfer = require('./coalition-transfer');

// === Compliance & Governance ===
exports.ControlHarmonization = require('./control-harmonization');
exports.CompliancePolygraph = require('./compliance-polygraph');
exports.ComplianceDashboard = require('./compliance-dashboard');
exports.FederatedComplianceNetwork = require('./federated-compliance-network');
exports.RegulatoryPolicyGraph = require('./regulatory-policy-graph');

// === Quality Gates & Safety ===
exports.QualityGates = require('./quality-gates');
exports.MarchCheckerConfig = require('./march-checker-config');
exports.MarchAdversarial = require('./march-adversarial');
exports.ConstitutionalFilter = require('./constitutional-filter');
exports.GSARRecovery = require('./gsar-recovery');

// === Intent, Memory & Telemetry ===
exports.IntentEngine = require('./intent-engine');
exports.IntentClassifier = require('./intent-classifier');
exports.MemoryConsolidationService = require('./memory-consolidation-service');
exports.MemoryInstrumentationService = require('./memory-instrumentation-service');
exports.MemoryAnomalyDetector = require('./memory-anomaly-detector');
exports.LiveTelemetry = require('./live-telemetry');

// === Supporting Infrastructure ===
exports.ContextManifest = require('./context-manifest');
exports.DissentEscalation = require('./dissent-escalation');
exports.CausalChain = require('./causal-chain');
exports.LeakDetector = require('./leak-detector');
exports.ManifestAck = require('./manifest-ack');
exports.ManifestValidator = require('./manifest-validator');