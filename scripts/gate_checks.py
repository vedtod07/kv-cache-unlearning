"""Dependency-free checks for the cache-path diagnostic (not an efficacy test)."""
import math


def assess_gate(parallel, dynamic, identity, quantized, instrumentation, atol, rtol):
    """Return failures and token-level effects; equal quantized scores are valid."""
    failures = []
    sequences = (parallel, dynamic, identity, quantized)
    if not math.isfinite(atol) or not math.isfinite(rtol) or min(atol, rtol) < 0:
        raise ValueError('Tolerances must be finite and nonnegative')
    if len(parallel) < 2 or any(len(x) != len(parallel) for x in sequences):
        return {'passed': False, 'failures': ['Need matching sequences of at least two scored tokens']}
    if any(not math.isfinite(v) for seq in sequences for v in seq):
        return {'passed': False, 'failures': ['Nonfinite token NLL']}
    def close(a, b):
        return all(abs(x-y) <= atol + rtol * abs(y) for x, y in zip(a, b))
    if not close(dynamic, parallel):
        failures.append('Ordinary sequential/parallel baseline exceeds tolerance')
    if not close(identity, dynamic):
        failures.append('Instrumented identity cache differs from ordinary sequential baseline')
    if not instrumentation:
        failures.append('No cache-layer instrumentation')
    for layer in instrumentation:
        if min(layer['writes_k'], layer['writes_v'], layer['reads_k'], layer['reads_v']) < 1:
            failures.append(f"Layer {layer['layer']}: missing K/V write or read")
        if not layer['stored_kv']:
            failures.append(f"Layer {layer['layer']}: missing quantized storage")
        if not math.isfinite(layer['max_reconstruction_error']):
            failures.append(f"Layer {layer['layer']}: nonfinite reconstruction error")
    if instrumentation and not any(x['max_reconstruction_error'] > 0 for x in instrumentation):
        failures.append('No nonzero reconstruction error observed; inspect fixture/intervention')
    differences = [q-d for q, d in zip(quantized, dynamic)]
    return {
        'passed': not failures, 'failures': failures,
        'token_nll_delta_quantized_minus_dynamic': differences,
        'mean_nll_delta': sum(differences)/len(differences),
        'max_abs_token_nll_delta': max(map(abs, differences)),
        'max_abs_dynamic_parallel_delta': max(abs(d-p) for d, p in zip(dynamic, parallel)),
        'max_abs_identity_dynamic_delta': max(abs(i-d) for i, d in zip(identity, dynamic)),
    }
