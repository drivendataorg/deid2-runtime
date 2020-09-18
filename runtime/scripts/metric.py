import numpy as np
from scipy.spatial.distance import jensenshannon


class Deid2Metric:
    def __init__(self):
        self.threshold = 0.05
        self.misleading_presence_penalty = 0.2
        self.bias_penalty = 0.25
        self.allowable_raw_bias = 500
        self.epsilon = 1e-9

    @staticmethod
    def _normalize(arr):
        """ Turn raw counts into frequencies but handle all-zero arrays gracefully """
        if (arr > 0).any():
            return arr / arr.sum()
        return arr

    def _zero_below_threshold(self, arr):
        """ Take any entries that are below the threshold we care about and zero them out """
        return np.where(self._normalize(arr) >= self.threshold, arr, 0)

    def _score_counts(self, actual, predicted):
        """ Score one row of counts for a particular (neighborhood, year, month) """
        if (actual == predicted).all():
            return 0.0, 0.0, 0.0

        # zero out entries below the threshold
        gt = self._zero_below_threshold(actual).ravel()
        dp = self._zero_below_threshold(predicted).ravel()

        # get the base Jensen Shannon distance from the normalized values plus a tiny
        # value to avoid divide-by-zero errors
        jsd = jensenshannon(self._normalize(gt + 1e-9), self._normalize(dp + 1e-9))

        # get the overall penalty for hallucinating counts
        misleading_presence_mask = (gt == 0) & (dp > 0)
        misleading_presence_penalty = (
            misleading_presence_mask.sum() * self.misleading_presence_penalty
        )

        # get the overall penalty for bias
        bias_mask = np.abs(actual - predicted).sum() > self.allowable_raw_bias
        bias_penalty = self.bias_penalty if bias_mask.any() else 0
        return jsd, misleading_presence_penalty, bias_penalty

    def _score_all(self, actual, predicted):
        n_perms, _ = actual.shape
        scores = np.zeros(n_perms, dtype=np.float)
        for i in range(n_perms):
            scores[i] = 1 - np.sum(self._score_counts(actual[i, :], predicted[i, :]))
        return scores

    def score(self, actual, predicted, return_individual_scores=False):
        # make sure the submitted values are proper
        assert np.isfinite(predicted).all()
        assert (predicted >= 0).all()

        # get all of the individual scores
        raw_scores = self._score_all(actual, predicted)

        # clip all the scores to [0, 1]
        scores = np.clip(raw_scores, a_min=0.0, a_max=1.0)

        # take the mean and multiply by 1000
        overall_score = np.mean(scores) * 1000

        # in some uses (like visualization), it's useful to get the individual scores out too
        if return_individual_scores:
            return overall_score, scores

        return overall_score
