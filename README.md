# Distributed-Password-Cracking-Worker-Hashcat-Redis-
Implements a distributed password cracking system using Redis as a job queue. A coordinator splits a wordlist into chunks and pushes them to Redis; workers run Hashcat on each chunk and return cracked passwords.
