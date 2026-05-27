/**
 * Octomind Services Index
 *
 * Barrel file for convenient access to key services.
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
  CoalitionAdjacency: require('./coalition-adjacency'),
  CoalitionTransfer: require('./coalition-transfer'),

  // Compliance & Governance
  ControlHarmonization: require('./control-harmonization'),
  CompliancePolygraph: require('./compliance-polygraph'),
  ComplianceDashboard: require('./compliance-dashboard'),
  FederatedComplianceNetwork: require('./federated-compliance-network'),
  RegulatoryPolicyGraph: require('./regulatory-policy-graph'),

  // Quality & Safety
  QualityGates: require('./quality-gates'),
  MarchCheckerConfig: require('./march-checker-config'),
  MarchAdversarial: require('./march-adversarial'),
  ConstitutionalFilter: require('./constitutional-filter'),
  GSARRecovery: require('./gsar-recovery'),

  // Intent & Memory
  IntentEngine: require('./intent-engine'),
  IntentClassifier: require('./intent-classifier'),
  MemoryConsolidationService: require('./memory-consolidation-service'),
  MemoryInstrumentationService: require('./memory-instrumentation-service'),
  MemoryAnomalyDetector: require('./memory-anomaly-detector'),
};
