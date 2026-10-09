---
title: "Feature: Testbed Client (RESTConf & Nobel-Germany Mock)"
date: 2026-08-17
tags: [feature, restconf, api, testbed, mock-topology, nobel-germany, edfa, qot]
status: active
---

# Feature: Testbed Client (RESTConf & Nobel-Germany Mock)

## 1. Title and Overview
**TestbedClient** (`src/services/testbed_client.py`)
This feature provides the abstract NBI interface `TestbedClient` and two concrete implementations:
1. `MockTestbedClient`: Returns a realistic 17-node, 26-link **Nobel-Germany** optical backbone topology (standard SNDlib instance) enriched with physical fiber lengths and calibrated EDFA configurations (boosters, ILAs, preamps) for deterministic GN-model QoT evaluations.
2. `RESTConfTestbedClient`: Serves as the bridge between the Orchestrator and the physical (virtualized) SM Optics Optical Network Controller (ONC) via REST NBI with CAS SSO authentication.

## 2. Mock Topology: Nobel-Germany (17 Nodes, 26 Links)

### Network Elements (17 Core Nodes)
- **Hubs & Core Cities**: `Hannover`, `Frankfurt`, `Hamburg`, `Norden`, `Bremen`, `Berlin`, `Munich`, `Ulm`, `Nuremberg`, `Stuttgart`, `Karlsruhe`, `Mannheim`, `Essen`, `Dortmund`, `Dusseldorf`, `Cologne`, `Leipzig`.

### Physical Fiber and EDFA Placement Model
Each link defines:
- **Fiber Length ($L$)**: Realistic geographic fiber distances spanning from 37.5 km to 381.9 km.
- **Booster EDFA ($0.0\text{ km}$)**: Calibrated with gain $3.0\text{ dB}$ to offset node traversal loss while avoiding non-linear distortion on downstream spans.
- **Inline Amplifiers (ILAs)**: For links longer than $55\text{ km}$, ILAs are placed every $\approx 70\text{ km}$ ($num\_spans = \max(2, \text{round}(L / 70))$) with gain compensating fiber attenuation ($\alpha = 0.25\text{ dB/km}$) and connector losses ($2\text{ dB}$).
- **Preamplifier EDFA ($L\text{ km}$)**: Positioned at the destination node ingress, compensating the final span loss before demux.

## 3. RESTConf Client & CAS SSO Authentication
The live client communicates with the REST NBI on port `8443`:
1. Accessing protected endpoints triggers an HTTP redirect to CAS (port `8843`).
2. `_authenticate_cas` extracts the execution token from the login form and posts credentials.
3. CAS redirects back to the NBI, establishing the session cookie in the `httpx` client.

## 4. Associated Files
- **Implementation**: [src/services/testbed_client.py](file:///home/felipeab/MultiAgentON/src/services/testbed_client.py)
- **Data Structures**: [src/core/state.py](file:///home/felipeab/MultiAgentON/src/core/state.py)
- **Tests**: [tests/unit/test_testbed_client.py](file:///home/felipeab/MultiAgentON/tests/unit/test_testbed_client.py) and [tests/unit/test_onc_client.py](file:///home/felipeab/MultiAgentON/tests/unit/test_onc_client.py)

## 5. How to Test
```bash
# Unit tests (offline, mock client)
uv run pytest tests/unit/test_testbed_client.py

# Live testbed integration tests (requires VPN)
uv run pytest tests/integration/test_onc_api.py -v -m integration
```
