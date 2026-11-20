/*
 * Copyright © 2026 2Q Software Inc. All rights reserved.
 * U.S. Patent Pending — 2Q Software Inc.
 *
 * NOTICE: All information contained herein is, and remains the property of 2Q Software Inc.
 * The intellectual and technical concepts contained herein are proprietary to 2Q Software Inc.
 * Dissemination of this information or reproduction of this material is strictly forbidden
 * unless prior written permission is obtained from 2Q Software Inc.
 */

# TFS Tri-Engine Suite — AWS Marketplace Client Benchmark Harness

**TFS Tri-Engine Suite** by **2Q Software Inc.** is a multi-architecture (`linux/amd64` and `linux/arm64`), VPC-isolated container acceleration utility for NVIDIA GPU and DPU clusters on AWS.

Designed as a drop-in runtime accelerator requiring **zero application code changes**, TFS eliminates container IPC serialization overhead, expands effective GPU memory capacity, and offloads PCIe interconnect congestion across **Amazon EKS**, **Amazon ECS**, and self-managed Kubernetes clusters.

---

## Speed, Time, Cloud Cost & Data Center Energy Impact

Modern 8-GPU servers draw **8 kW to 14+ kW** continuously, and rack-scale Blackwell/Rubin deployments exceed **120 kW per rack**. When high-density GPUs stall waiting on millisecond TCP/gRPC serialization, host CPU packet parsing, or HBM capacity limits, organizations pay full cloud rates and burn full electrical power for idle silicon.


| Dimension                     | Standard Container Stack (TCP/gRPC + Unoptimized PCIe/HBM)        | With TFS Tri-Engine Suite (Drop-In Runtime)                                          |
| :---                          | :---                                                              | :---                                                                                 |
| **Control-Plane IPC Speed**   | Millisecond-scale (`ms`) serialization & network stack overhead   | **`~28 µs` deterministic IPC** (`35,000+ ops/sec`, **>95% latency reduction**)       |
| **Effective GPU Memory**      | Native physical HBM ceiling (forces multi-node over-provisioning) | **Up to `4.0x` HBM payload expansion** (fits larger workloads on fewer GPUs)         |
| **PCIe Interconnect Load**    | Host CPU bound on packet parsing & uncompressed transfers         | **Up to `72.73%` PCIe bus traffic reduction** via BlueField-3 DPU offload.           |
| **Job Completion Time**       | Extended wall-clock runtimes due to GPU stall cycles              | **Faster training & inference completion** in significantly fewer GPU-hours          |
| **User Cloud Spend (FinOps)** | Paying full hourly rates across over-provisioned GPU nodes        | **Proportional AWS compute & CapEx reduction** by extracting more work per GPU-hour  |
| **Electricity & Environment** | High kWh draw and cooling load during stalled compute cycles      | **Lower kWh electricity consumption & Scope 2/3 carbon footprint** per job completed |

- **Air-Gapped VPC Execution:** Executes 100% inside your AWS VPC with zero customer payload egress, supporting enterprise data sovereignty and sustainability reporting mandates (such as EU CSRD and Energy Efficiency Directive goals).


---

## Available AWS Marketplace Listings (7-Day Free Trial)

- **TFS Tri-Engine Suite - Enterprise (Hopper, Blackwell & Rubin Edition):** [View on AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-e6wu4saw6ejzu)
- **TFS Tri-Engine Suite - Container Acceleration for GPU and DPU (Standard Edition):** [View on AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-lpfjogdd2khby)

---

## Quickstart Verification Workflow

1. **Subscribe & Launch via AWS Marketplace:** Subscribe to either edition on AWS Marketplace (7-day free trial) and follow the private **Launch / Usage Instructions** in your AWS Marketplace Console to start the runtime container.
2. **Run the Client-Side IPC Comparison Benchmark:** Once the TFS runtime container is active on the host, run:
   `python3 benchmarks/run_ipc_comparison.py --iterations 10000 --payload-bytes 4096`

## Support & Enterprise Inquiries
- **Technical Support:** `customerservice@2qsoftware.com`
- **Enterprise Multi-Node Private Offers:** `rupen@2qsoftware.com`
