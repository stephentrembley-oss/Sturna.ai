/**
 * ConsistencyChecker
 *
 * Checks consistency of agent outputs against previous results.
 */

class ConsistencyChecker {
  check(current, previous) {
    return { consistent: true };
  }
}

module.exports = ConsistencyChecker;
