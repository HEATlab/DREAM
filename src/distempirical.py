import random
import numpy as np
from scipy.stats import norm

# These variables should never be imported from this file.
_samples = {}
_invcdfs = {}

def collect_data(rundir):
    pass

def empirical_sample(distribution_name: str, state=None) -> float:
    """ Gets a sample from a specified distribution.

    Return:
        Returns a float from the distribution.
    """
    if state is None:
        return np.random.choice(_samples[distribution_name])
    else:
        return state.choice(_samples[distribution_name])


# TODO: Change from capping at 0 to resampling if less than 0.
def normal_sample(mu: float, sigma: float, state=None, use_neg=False) -> float:
    """ Retrieve a sample from a normal distribution

    Args:
        mu: mean of the normal distribution
        sigma: standard deviation of the normal distribution

    Keyword Args:
        state: Numpy RandomState object to use for the sampling. Default is set
               to None, meaning that we're using the global state.
        use_neg: If we want to use negative values, set this to True. Default
                 is False
    Return:
        Returns a random sample (float).
    """
    if state is None:
        if not use_neg:
            return max(0.0, np.random.normal(mu, sigma))
        else:
            return np.random.normal(mu, sigma)
    else:
        if not use_neg:
            return max(0.0, state.random.normal(mu, sigma))
        else:
            return state.random.normal(mu, sigma)

def normal_invcdf(mu, sigma, value) -> float:
    """ Retrieve the inverse Cumulative Density Function (CDF) of a normal
        distribution.
    Args:
        mu: mean of the normal distribution
        sigma: standard deviation of the normal distribution
        value: percentile value to look up.
    """
    return norm.ppf(value, loc=mu, scale=sigma)
