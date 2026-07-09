📁 Distributed Password Cracking Worker (Hashcat + Redis)

Description
Implements a distributed password cracking system using Redis as a job queue. A coordinator splits a wordlist into chunks and pushes them to Redis; workers run Hashcat on each chunk and return cracked passwords.

Key Features

    Coordinator splits wordlist and pushes jobs.

    Workers pull jobs, run Hashcat, and store results.

    Scales horizontally – add more workers.

    Results are stored in Redis.

Technologies

    Redis, Hashcat, Python redis library.

Prerequisites

    Redis server, Hashcat installed.

    Python 3.

Installation
bash

sudo apt install redis-server hashcat
pip install redis

Usage

    Start Redis: sudo systemctl start redis-server.

    Prepare a small wordlist and hashes file.

    Run coordinator:
    bash

python coordinator.py wordlist.txt hashes.txt

Run workers (one or more):
bash

python worker.py

Check results:
bash

redis-cli lrange hashcat_results 0 -1

Sample Output
Worker:
text

[*] Worker 12345: Processing chunk 0...
[+] Worker 12345: Cracked 5f4dcc3b5aa765d61d8327deb882cf99 -> password
