/**
 * Octomind Services Index (Barrel File)
 *
 * This file provides easy access to the core biomimetic and compliance services
 * extracted from octomind.zip (May 2026).
 *
 * Usage:
 *   const { ShivaLimbOrchestrator, CoalitionEngine } = require('./octomind/services');
 *
 * Note: Not all 170+ services are re-exported here to keep the index manageable.
 *       You can still require any service directly, e.g.:
 *       const MarchChecker = require('./octomind/services/march-checker-config');
 */

module.exports = {
  // === Core Biomimetic Orchestration ===
  ShivaLimbOrchestrator: require('./shiva-limb-orchestrator'),
  OctopusNeuralLayer: require('./octopus-neural-layer'),
  SelfHealingRouter: require('./self-healing-router'),
  CrisprAgentEditor: require('./crispr-agent-editor'),
  CephalopodRecoder: require('./cephalopod-recoder'),

  // === Coalition Market Auction ===
  CoalitionEngine: require('./coalition-engine'),
  CoalitionClearing: require('./coalition-clearing'),
  CoalitionPerformance: require('./coalition-performance'),

  // === Compliance & Governance ===
  ControlHarmonization: require('./control-harmonization'),
  CompliancePolygraph: require('./compliance-polygraph'),
  ComplianceDashboard: require('./compliance-dashboard'),
  FederatedComplianceNetwork: require('./federated-compliance-network'),
  RegulatoryPolicyGraph: require('./regulatory-policy-graph'),

  // === Quality & Safety ===
  QualityGates: require('./quality-gates'),
  MarchCheckerConfig: require('./march-checker-config'),
  ConstitutionalFilter: require('./constitutional-filter'),

  // === Intent & Memory ===
  IntentEngine: require('./intent-engine'),
  MemoryConsolidationService: require('./memory-consolidation-service'),

  // Add more key services here as needed
};
