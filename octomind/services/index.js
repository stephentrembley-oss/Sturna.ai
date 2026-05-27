/**
 * Octomind Services Index
 *
 * Barrel file for convenient access to key services from the biomimetic layer.
 */

module.exports = {
  // Biomimetic Core
  ShivaLimbOrchestrator: require('./shiva-limb-orchestrator'),
  OctopusNeuralLayer: require('./octopus-neural-layer'),
  SelfHealingRouter: require('./self-healing-router'),
  CrisprAgentEditor: require('./crispr-agent-editor'),
  CephalopodRecoder: require('./cephalopod-recoder'),

  // Coalition System
  CoalitionEngine: require('./coalition-engine'),
  CoalitionClearing: require('./coalition-clearing'),
  CoalitionPerformance: require('./coalition-performance'),

  // Compliance & Governance
  ControlHarmonization: require('./control-harmonization'),
  CompliancePolygraph: require('./compliance-polygraph'),
  FederatedComplianceNetwork: require('./federated-compliance-network'),
  RegulatoryPolicyGraph: require('./regulatory-policy-graph'),

  // Quality & Safety
  QualityGates: require('./quality-gates'),
  MarchCheckerConfig: require('./march-checker-config'),
  ConstitutionalFilter: require('./constitutional-filter'),

  // Intent & Memory
  IntentEngine: require('./intent-engine'),
  MemoryConsolidationService: require('./memory-consolidation-service'),
};
