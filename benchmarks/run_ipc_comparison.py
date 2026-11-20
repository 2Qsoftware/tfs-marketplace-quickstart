#!/usr/bin/env python3
"""
TFS Tri-Engine Suite - Open-Source Client IPC Latency Comparison Harness
Copyright (c) 2026 2Q Software Inc. (MIT License - Client Benchmark Harness)
"""
import argparse, json, os, socket, statistics, threading, time
from typing import List, Tuple

def percentile(sorted_data: List[float], pct: float) -> float:
    if not sorted_data:
        return 0.0
    k = (len(sorted_data) - 1) * (pct / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_data) - 1)
    return sorted_data[f] if f == c else sorted_data[f] * (c - k) + sorted_data[c] * (k - f)

def start_tcp_echo_baseline(host: str, port: int, stop_event: threading.Event) -> None:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(1)
    srv.settimeout(0.5)
    while not stop_event.is_set():
        try:
            conn, _ = srv.accept()
        except socket.timeout:
            continue
        with conn:
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            while not stop_event.is_set():
                data = conn.recv(65536)
                if not data:
                    break
                decoded = json.loads(data.decode("utf-8"))
                conn.sendall(json.dumps({"status": "ok", "seq": decoded["seq"]}).encode("utf-8"))
    srv.close()

def benchmark_tcp_baseline(iterations: int, payload_bytes: int) -> Tuple[List[float], float]:
    host = "127.0.0.1"
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.bind((host, 0))
    port = probe.getsockname()[1]
    probe.close()
    stop_event = threading.Event()
    t = threading.Thread(target=start_tcp_echo_baseline, args=(host, port, stop_event), daemon=True)
    t.start()
    time.sleep(0.05)
    raw_blob = "X" * max(1, payload_bytes - 64)
    latencies_us: List[float] = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.connect((host, port))
    for i in range(200):
        sock.sendall(json.dumps({"seq": i, "tensor_blob": raw_blob}).encode("utf-8"))
        sock.recv(4096)
    wall_start = time.perf_counter()
    for i in range(iterations):
        t0 = time.perf_counter_ns()
        sock.sendall(json.dumps({"seq": i, "tensor_blob": raw_blob}).encode("utf-8"))
        _ = sock.recv(4096)
        latencies_us.append((time.perf_counter_ns() - t0) / 1_000.0)
    wall_elapsed = time.perf_counter() - wall_start
    sock.close()
    stop_event.set()
    t.join(timeout=1.0)
    return latencies_us, iterations / wall_elapsed

def benchmark_tfs_unix_socket(socket_path: str, iterations: int, payload_bytes: int) -> Tuple[List[float], float]:
    if not os.path.exists(socket_path):
        raise FileNotFoundError(f"TFS IPC socket not found at {socket_path}. Ensure the TFS container is running with -v /tmp:/tmp.")
    payload = b"\x01" * payload_bytes
    latencies_us: List[float] = []
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(2.0)
    sock.connect(socket_path)
    for _ in range(200):
        sock.sendall(payload)
        try:
            sock.recv(4096)
        except socket.timeout:
            break
    wall_start = time.perf_counter()
    for _ in range(iterations):
        t0 = time.perf_counter_ns()
        sock.sendall(payload)
        try:
            _ = sock.recv(4096)
        except socket.timeout:
            pass
        latencies_us.append((time.perf_counter_ns() - t0) / 1_000.0)
    wall_elapsed = time.perf_counter() - wall_start
    sock.close()
    return latencies_us, iterations / wall_elapsed

def print_summary(label: str, latencies_us: List[float], ops_per_sec: float) -> None:
    s = sorted(latencies_us)
    print(f"\n[{label}]\n  Throughput : {ops_per_sec:,.0f} ops/sec\n  Mean       : {statistics.mean(s):,.2f} us\n  p50        : {percentile(s, 50):,.2f} us\n  p95        : {percentile(s, 95):,.2f} us\n  p99        : {percentile(s, 99):,.2f} us")

def main() -> None:
    parser = argparse.ArgumentParser(description="TFS Tri-Engine Suite IPC vs TCP Serialization Benchmark")
    parser.add_argument("--socket", default="/tmp/tfs_engine.sock")
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--payload-bytes", type=int, default=4096)
    args = parser.parse_args()
    print("=" * 68 + f"\nTFS Tri-Engine Suite — IPC Transport Benchmark (2Q Software Inc.)\nIterations: {args.iterations:,} | Payload: {args.payload_bytes:,} bytes\n" + "=" * 68)
    tcp_lat, tcp_ops = benchmark_tcp_baseline(args.iterations, args.payload_bytes)
    print_summary("Baseline: Standard TCP + JSON Container Serialization", tcp_lat, tcp_ops)
    try:
        tfs_lat, tfs_ops = benchmark_tfs_unix_socket(args.socket, args.iterations, args.payload_bytes)
        print_summary(f"TFS IPC Socket ({args.socket})", tfs_lat, tfs_ops)
        tcp_p50, tfs_p50 = percentile(sorted(tcp_lat), 50), percentile(sorted(tfs_lat), 50)
        if tfs_p50 > 0:
            print(f"\np50 Latency Reduction : {((tcp_p50 - tfs_p50) / tcp_p50) * 100.0:.2f}% ({tcp_p50 / tfs_p50:.1f}x faster)")
    except FileNotFoundError as exc:
        print(f"\n[Skipped TFS Socket Test] {exc}")

if __name__ == "__main__":
    main()
