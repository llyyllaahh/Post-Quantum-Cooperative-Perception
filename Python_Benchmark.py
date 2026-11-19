"""Benchmark ECDSA-P256 and ML-DSA-44 signing and signature verification.

Each operation is warmed up and then timed 10,000 times by default. Key
generation and test-message setup happen outside the timed sections.
"""
import gc
import math
import statistics
import time
import oqs
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec


def benchmark(fn, iters=10000, warmup=1000):
    """Time a zero-argument function and return median and p99 in microseconds."""
    if iters <= 0:
        raise ValueError("iters must be greater than zero")
    if warmup < 0:
        raise ValueError("warmup cannot be negative")

    for _ in range(warmup): #warming up the function to avoid cold start effects
        fn()

    times = [0] * iters 
    gc.collect()
    gc_was_enabled = gc.isenabled()
    gc.disable()

    try:
        for i in range(iters):
            start = time.perf_counter_ns()
            fn()
            end = time.perf_counter_ns()
            times[i] = end - start
    finally:
        if gc_was_enabled:
            gc.enable()

    times.sort()
    median = statistics.median(times)
    p99 = times[math.ceil(0.99 * iters) - 1]

    return {
        "median_us": median / 1000,
        "p99_us": p99 / 1000,
    }

def ecdsa_p256(message):
    """Sign a message with ECDSA-P256 and verify the signature."""
    alg = ec.ECDSA(hashes.SHA256())
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    signature = private_key.sign(message, alg)
    # Check the setup before timing so failed verification is never reported
    # as a successful benchmark.
    public_key.verify(signature, message, alg)

    return {
        "sign": lambda: private_key.sign(message, alg),
        "verify": lambda: public_key.verify(signature, message, alg),
    }

def oqs_sig_ops(algorithm, message, iters, warmup):
    """Benchmark signing and verification for an OQS signature algorithm."""
    if algorithm not in oqs.get_enabled_sig_mechanisms():
        raise ValueError(f"{algorithm} is not enabled in the installed liboqs")

    with oqs.Signature(algorithm) as signer, oqs.Signature(algorithm) as verifier:
        public_key = signer.generate_keypair()
        signature = signer.sign(message)
        if not verifier.verify(message, signature, public_key):
            raise RuntimeError(f"{algorithm} signature verification failed")

        return {
            "sign": benchmark(lambda: signer.sign(message), iters, warmup),
            "verify": benchmark(
                lambda: verifier.verify(message, signature, public_key),
                iters,
                warmup,
            ),
        }
def oqs_kem_ops(algorithm, iters, warmup):
    """Benchmark key generation, encapuslation, and decapsulation for an OQS KEM algorithm."""
    if algorithm not in oqs.get_enabled_kem_mechanisms():
        raise ValueError(f"{algorithm} is not enabled in the installed liboqs")

    with oqs.KeyEncapsulation(algorithm) as keygen_kem, \
     oqs.KeyEncapsulation(algorithm) as kem:
        public_key = kem.generate_keypair()
        ciphertext, ss_enc = kem.encap_secret(public_key)
        if kem.decap_secret(ciphertext) != ss_enc:
            raise RuntimeError(f"{algorithm} KEM decapsulation failed")

        return {
            "keygen": benchmark(lambda: keygen_kem.generate_keypair(), iters, warmup),
            "encapsulate": benchmark(lambda: kem.encap_secret(public_key), iters, warmup),
            "decapsulate": benchmark(lambda: kem.decap_secret(ciphertext), iters, warmup),
        }

def run_benchmarks(message=b"Post-quantum signature benchmark", iters=10000, warmup=1000):
    classical_ops = ecdsa_p256(message)
    return {
        "ECDSA-P256": {
            operation: benchmark(fn, iters, warmup)
            for operation, fn in classical_ops.items()
        },
        "ML-DSA-44": oqs_sig_ops("ML-DSA-44", message, iters, warmup),
        "ML-DSA-65": oqs_sig_ops("ML-DSA-65", message, iters, warmup),
        "Falcon-512": oqs_sig_ops("Falcon-512", message, iters, warmup),
        "ML-KEM-768": oqs_kem_ops("ML-KEM-768", iters, warmup),
    }
def print_table(results): #Printing as a table for readability
    header = f"{'Scheme':<12} {'Operation':<12} {'Median (us)':<12} {'P99 (us)':<12}"
    print(header)
    print("-" * len(header))
    for scheme, ops in results.items():
        for ops, stats in ops.items():
            print(f"{scheme:<12} {ops:<12} {stats['median_us']:<12.2f} {stats['p99_us']:<12.2f}")
if __name__ == "__main__":
    print_table(run_benchmarks())

