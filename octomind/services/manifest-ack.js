/**
 * ManifestAck
 *
 * Acknowledges and signs context manifests.
 */

class ManifestAck {
  acknowledge(manifest) {
    return { acknowledged: true };
  }
}

module.exports = ManifestAck;
