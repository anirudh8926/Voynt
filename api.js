// Simple global API client for Voynt frontend.
// Usage: include this file with a <script src="api.js"></script> tag
// and access methods via window.VoyntAPI.

const API_BASE = 'http://localhost:8000';

const VoyntAPI = {
  /**
   * Submit the user's profile and goal for analysis.
   * @param {Object} payload - AnalyzeRequest-compatible JSON body.
   * @returns {Promise<Object>} - Resolves with { session_id, status }.
   */
  analyzeProfile(payload) {
    return fetch(API_BASE + '/api/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    }).then((res) => {
      if (!res.ok) {
        return res.text().then((text) => {
          throw new Error(text || 'Failed to analyze profile');
        });
      }
      return res.json();
    });
  },

  /**
   * Poll session status every 2000ms until complete or failed.
   * @param {string} sessionId
   * @param {Function} onComplete - called with the final status payload when complete.
   * @param {Function} onFailed - called with an Error if status becomes failed or polling fails.
   * @returns {number} - interval id from setInterval (for manual clearing if desired).
   */
  pollStatus(sessionId, onComplete, onFailed) {
    const intervalMs = 2000;

    const intervalId = setInterval(() => {
      fetch(API_BASE + '/api/status/' + encodeURIComponent(sessionId))
        .then((res) => {
          if (!res.ok) {
            return res.text().then((text) => {
              throw new Error(text || 'Status check failed');
            });
          }
          return res.json();
        })
        .then((data) => {
          if (!data || !data.status) {
            return;
          }

          if (data.status === 'complete') {
            clearInterval(intervalId);
            if (typeof onComplete === 'function') {
              onComplete(data);
            }
          } else if (data.status === 'failed') {
            clearInterval(intervalId);
            if (typeof onFailed === 'function') {
              onFailed(new Error('Pipeline failed for session ' + sessionId));
            }
          }
        })
        .catch((err) => {
          clearInterval(intervalId);
          if (typeof onFailed === 'function') {
            onFailed(err);
          }
        });
    }, intervalMs);

    return intervalId;
  },

  /**
   * Fetch full pipeline results for a session.
   * @param {string} sessionId
   * @returns {Promise<Object>} - Resolves with ResultsResponse payload.
   */
  getResults(sessionId) {
    return fetch(API_BASE + '/api/results/' + encodeURIComponent(sessionId)).then(
      (res) => {
        if (!res.ok) {
          return res.text().then((text) => {
            throw new Error(text || 'Failed to fetch results');
          });
        }
        return res.json();
      }
    );
  },

  /**
   * Run sandbox recalculation for manual card/ spend overrides.
   * @param {string} sessionId
   * @param {Object} spendOverrides - { card_id: { category: amount_inr } }
   * @param {Array<string>} selectedCards - list of card ids
   * @returns {Promise<Object>} - Resolves with SandboxResponse payload.
   */
  runSandbox(sessionId, spendOverrides, selectedCards) {
    const payload = {
      session_id: sessionId,
      selected_cards: selectedCards || [],
      spend_overrides: spendOverrides || {},
    };

    return fetch(API_BASE + '/api/sandbox', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    }).then((res) => {
      if (!res.ok) {
        return res.text().then((text) => {
          throw new Error(text || 'Failed to run sandbox');
        });
      }
      return res.json();
    });
  },
};

// Expose globally
window.VoyntAPI = VoyntAPI;

