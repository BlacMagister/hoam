```
git clone https://github.com/BlacMagister/hoam
cd hoam
```

# 🚀 Blockchain Future Roadmap

Berikut roadmap pengembangan lengkap dengan timeline dan target fitur:

---

## **Phase 1: Core Blockchain Engine** *(Q3 2024)*
✅ **Milestone:**  
✔️ Implementasi Proof-of-Work dengan SHA3-256  
✔️ Sistem transaksi ECDSA (Kurva SECP256K1)  
✔️ Merkle Tree untuk verifikasi transaksi kilat  
✔️ CLI Wallet dengan fungsi sign/verify  
✔️ Unit test coverage 85%+  

---

## **Phase 2: Network & Consensus** *(Q4 2024)*
🔨 **In Progress:**  
▢ Protokol P2P menggunakan libp2p  
▢ Mekanisme gossip untuk broadcast block  
▢ Dynamic difficulty adjustment tiap 2016 block  
▢ REST API dengan rate limiting  
▢ Native binary build untuk Linux ARM/X64  

---

## **Phase 3: Scalability** *(Q1 2025)*
🔄 **Planned:**  
▢ Sharding dengan 4 shard minimum  
▢ State channels untuk off-chain transaction  
▢ Zero-Knowledge Rollups (ZK-SNARKs)  
▢ Cross-shard atomic swaps  
▢ Layer-2 payment channel network  

---

## **Phase 4: Ecosystem** *(Q2 2025)*
🌐 **Future:**  
▢ Block Explorer Web dengan React/Web3.js  
▢ Mobile Wallet (Flutter)  
▢ Decentralized Exchange (DEX) prototype  
▢ NFT Marketplace sederhana  
▢ Oracles untuk data eksternal  

---

## **Phase 5: Quantum Resistance** *(Q3 2025)*
🔒 **Security Future:**  
▢ Migrasi ke algoritma post-quantum  
▢ Hybrid signature (NTRU + ECDSA)  
▢ Quantum-secure hashing (SPHINCS+)  
▢ Key rotation mechanism  
▢ Quantum random number generator  

---

## **Technical Upgrade Path**
```mermaid
graph LR
A[PoW] --> B[PoS]
B --> C[DPoS]
C --> D[PBFT]
D --> E[Hybrid PoW/PoS]
