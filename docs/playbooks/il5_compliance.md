# IL5 Compliance Path

## Overview

Guide for achieving IL5 (Impact Level 5) authorization for production deployment.

## Demo vs Production

| Aspect | Demo | Production |
|--------|------|------------|
| Classification | Unclassified | Up to IL5 |
| Data | Synthetic | Real operational |
| Network | Internet | Isolated/GovCloud |
| LLM | Claude API | Bedrock or local |
| Embeddings | OpenAI | Local BGE |

## Key Requirements

### 1. Network Isolation

- Deploy in AWS GovCloud or Azure Government
- No external API calls from data plane
- Air-gapped options for highest security

### 2. LLM Selection

- Replace Claude API with Amazon Bedrock
- Or deploy local models (Llama, Mistral)
- Implement LLM abstraction interface

### 3. Embedding Models

- Replace OpenAI with local BGE-large-en-v1.5
- Run on dedicated GPU nodes
- No data leaves environment

### 4. Data Protection

- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Key management via HSM

### 5. Audit & Logging

- Comprehensive audit logging
- Immutable log storage
- SIEM integration

## Authorization Timeline

1. Security documentation (4-6 weeks)
2. Security assessment (2-4 weeks)
3. Remediation (varies)
4. ATO approval (2-4 weeks)
