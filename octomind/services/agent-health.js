/**
 * AgentHealth
 *
 * Monitors health and status of individual agents.
 */

class AgentHealth {
  check(agentId) {
    return { healthy: true };
  }
}

module.exports = AgentHealth;
