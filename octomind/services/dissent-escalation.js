/**
 * DissentEscalation
 *
 * Handles dissent and escalation in multi-agent decisions.
 */

class DissentEscalation {
  escalate(dissentEvent) {
    return { escalated: true, reason: dissentEvent.reason };
  }
}

module.exports = DissentEscalation;
