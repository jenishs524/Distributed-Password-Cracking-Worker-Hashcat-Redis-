#!/usr/bin/env python3
"""
Project 22 – Distributed Password Cracking Worker
Pulls wordlist chunks from Redis, runs Hashcat, and saves results.
"""

import os
import sys
import json
import tempfile
import subprocess
import redis
import time

# ---------- CONFIG ----------
REDIS_HOST = "localhost"
REDIS_PORT = 6379
QUEUE_NAME = "hashcat_jobs"
HASHLIST_KEY = "hash_list"
RESULTS_QUEUE = "hashcat_results"
HASHCAT_PATH = "hashcat"

def crack_chunk(chunk_data, hashes):
    """Run Hashcat on a chunk and return cracked hashes."""
    if not hashes:
        return []

    # Write hashes to a temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as hf:
        hf.write("\n".join(hashes))
        hash_file = hf.name

    # Write wordlist chunk to a temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as wf:
        wf.write("\n".join(chunk_data["words"]))
        word_file = wf.name

    # Output file for cracked results
    output_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt').name

    # Run Hashcat to crack (mode 0 = MD5)
    cmd_crack = [
        HASHCAT_PATH,
        "-m", "0",
        "-a", "0",
        hash_file,
        word_file,
        "-o", output_file
    ]

    try:
        # Run Hashcat cracking
        subprocess.run(cmd_crack, capture_output=True, text=True, timeout=120, check=False)
        # Now read the output file
        cracked = []
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if ':' in line:
                        h, pwd = line.split(':', 1)
                        cracked.append({"hash": h, "password": pwd})
        return cracked
    except Exception as e:
        print(f"[!] Hashcat error: {e}")
        return []
    finally:
        # Clean up temp files
        for f in [hash_file, word_file, output_file]:
            try:
                os.unlink(f)
            except:
                pass

def main():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    worker_id = os.getpid()

    print(f"[*] Worker {worker_id} starting...")

    while True:
        job = r.lpop(QUEUE_NAME)
        if not job:
            print(f"[*] Worker {worker_id}: No jobs left. Exiting.")
            break

        try:
            chunk_data = json.loads(job)
            print(f"[*] Worker {worker_id}: Processing chunk {chunk_data['chunk_id']}...")
        except:
            print(f"[!] Worker {worker_id}: Invalid job data.")
            continue

        hashes = r.lrange(HASHLIST_KEY, 0, -1)
        if not hashes:
            print(f"[!] Worker {worker_id}: No hashes found.")
            continue

        results = crack_chunk(chunk_data, hashes)

        for rsl in results:
            r.rpush(RESULTS_QUEUE, f"{rsl['hash']}:{rsl['password']}")
            print(f"[+] Worker {worker_id}: Cracked {rsl['hash']} -> {rsl['password']}")

    print(f"[*] Worker {worker_id} finished.")

if __name__ == "__main__":
    main()