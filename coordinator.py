#!/usr/bin/env python3
"""
Project 22 – Distributed Password Cracking Coordinator
Splits wordlist into chunks and pushes to Redis queue.
"""

import os
import sys
import json
import redis

# ---------- CONFIG ----------
REDIS_HOST = "localhost"
REDIS_PORT = 6379
QUEUE_NAME = "hashcat_jobs"
RESULTS_QUEUE = "hashcat_results"
CHUNK_SIZE = 1000  # lines per job

def split_wordlist(wordlist_path):
    if not os.path.exists(wordlist_path):
        print(f"[!] Wordlist not found: {wordlist_path}")
        sys.exit(1)

    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.delete(QUEUE_NAME)

    chunk_num = 0
    with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
        chunk = []
        for line in f:
            chunk.append(line.strip())
            if len(chunk) >= CHUNK_SIZE:
                job = {"chunk_id": chunk_num, "words": chunk}
                r.rpush(QUEUE_NAME, json.dumps(job))  # <-- FIXED: use JSON
                chunk_num += 1
                chunk = []
        if chunk:
            job = {"chunk_id": chunk_num, "words": chunk}
            r.rpush(QUEUE_NAME, json.dumps(job))

    print(f"[+] Pushed {chunk_num + 1} chunks to Redis queue '{QUEUE_NAME}'.")

def push_hashes(hash_file):
    if not os.path.exists(hash_file):
        print(f"[!] Hash file not found: {hash_file}")
        sys.exit(1)

    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.delete("hash_list")
    with open(hash_file, 'r') as f:
        for line in f:
            h = line.strip()
            if h:
                r.rpush("hash_list", h)
    print(f"[+] Pushed hashes to Redis.")

def main():
    if len(sys.argv) < 3:
        print("Usage: python coordinator.py <wordlist> <hashes_file>")
        print("Example: python coordinator.py /usr/share/wordlists/rockyou.txt hashes.txt")
        sys.exit(1)

    wordlist = sys.argv[1]
    hashes = sys.argv[2]

    push_hashes(hashes)
    split_wordlist(wordlist)
    print("[*] Coordinator ready. Start workers with: python worker.py")

if __name__ == "__main__":
    main()