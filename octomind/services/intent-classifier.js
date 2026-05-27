/**
 * IntentClassifier
 *
 * Classifies user/agent intents into categories.
 */

class IntentClassifier {
  classify(text) {
    return { category: 'general', confidence: 0.8 };
  }
}

module.exports = IntentClassifier;
