
---

# ESG RAG Agent

具備 Routing、Retrieval Quality Control 與 Structured Memory 的可控檢索系統

---

## 專案簡介

本專案實作一個應用於 ESG / 財務長文件的問答系統，
基於 Retrieval-Augmented Generation（RAG）架構，進一步設計：

* Query Routing（檢索決策控制）
* Retrieval Quality Control（RQC，檢索品質門控）
* Structured Memory（結構化記憶）
* Retrieval / Memory 解耦設計

本系統的目標不是單純提升模型能力，而是透過系統設計，使整體流程具備：

* 可控性（Controllable）
* 可驗證性（Verifiable）

---

## 設計思維（Design Rationale）

在 ESG 與財務文件場景中，存在以下三個核心問題：

### 1. 語意落差（Query vs Document Gap）

* 使用者問題偏抽象
* 文件內容為正式且具體的專業描述

導致查詢難以對應至實際文件段落。

---

### 2. 單次檢索不足（Shallow Retrieval）

* 檢索結果多為概述性描述
* 缺乏可直接支撐回答的細節

---

### 3. 多輪對話失效（Conversation Failure）

* Follow-up query 缺少主詞
* Retrieval 與 Memory 混用造成語意污染

---

## 核心設計

系統將問題拆解為三個層次，並分別處理：

---

### 1. Query Alignment：HyDE

為縮小使用者查詢與文件語言的差距，引入 HyDE（Hypothetical Document Expansion）：

* 生成符合 ESG 報告語境的假設語句
* 提升語意覆蓋範圍
* 改善檢索命中率

此機制主要解決語意對齊問題，但仍可能產生概述性結果，因此需搭配後續控制機制。

---

### 2. Retrieval Quality Control（RQC）

RQC 為一個閉環檢索控制機制：

```
Retrieve → Evaluate → Refine → Retrieve
```

核心功能：

* 判斷檢索結果是否具備可回答性
* 若資訊不足，觸發 query refinement 或 HyDE
* 僅在資訊充分時允許生成

此設計將檢索流程由單次查詢轉為可控流程，提升回答穩定性。

---

### 3. Query Routing（決策外部化）

系統透過 Router 判斷查詢類型：

* Retrieval：需要文件內容
* Memory：延續對話
* General：一般知識

設計目的：

* 避免所有查詢進入 retrieval
* 降低 latency 與成本
* 避免 LLM 做高風險決策

---

## Memory 設計

---

### Memory 汙染問題

若將 retrieval 結果直接寫入 memory，會導致：

* 長文本重複累積（token 膨脹）
* 語意混雜（query drift）
* 注意力分散，影響回答品質

---

### Retrieval 與 Memory 解耦

本系統採用以下設計：

* Retrieval content：每輪注入 system prompt
* Memory：僅儲存對話資訊

效果：

* 避免 memory 汙染
* 保持檢索上下文乾淨
* 控制 token 成長
* 提升多輪穩定性

---

### Structured Memory（處理追問）

為解決 follow-up query 缺少主詞的問題：

例如：

* 第一輪：Apple 的 ESG 表現如何？
* 第二輪：那它的碳排呢？

系統設計：

* 使用獨立 dict 儲存結構化資訊（如 company）
* Router 判斷 query 是否缺主詞
* 若缺，從 structured memory 補齊

效果：

* 正確理解追問問題
* 提升 retrieval query 完整性
* 避免語意斷裂

---

## System Architecture

```
                        ┌──────────────────────┐
                        │      User Query      │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │   Query Router (LLM) │
                        └──────────┬───────────┘
                                   │
        ┌──────────────────────────────────────────────────┐
        │                                                  │
        ▼                                                  ▼
┌────────────────┐                              ┌──────────────────────────┐
│   Retrieval    │                              │   Non-Retrieval Path     │
│   Required     │                              │ (Memory / General)       │
└──────┬─────────┘                              └──────────┬───────────────┘
       │                                                   ▼
       ▼                                        ┌──────────────────────┐
┌──────────────────────────────┐                │     Final Answer     │
│   Retrieval Pipeline         │                └──────────────────────┘
└──────────────┬───────────────┘    
               │                    
               ▼                    
      ┌──────────────────────────┐  
      │ Retrieval Quality Control│  
      │           (RQC)          │  
      └────────────┬─────────────┘  
                   │
         ┌─────────┴─────────┐
         │                   │
         ▼                   ▼
   ┌──────────────┐   ┌───────────────┐
   │     PASS     │   │    RETRY      │
   │ (sufficient) │   │ (insufficient)│
   └──────┬───────┘   └──────┬────────┘
          │                  │
          │                  ▼
          │        ┌──────────────────┐
          │        │   HyDE Module    │
          │        │ (Query Expansion)│
          │        └────────┬─────────┘
          │                 │
          └──────────┬──────┘
                     ▼
        ┌────────────────────────────────┐
        │          Agent Layer           │
        │                                │
        │  - LLM (Controlled Generation) │
        │  - Tool Calling                │
        │                                │
        │  + Memory (generation only)    │
        └──────────┬─────────────────────┘
                   │
                   ▼
           ┌──────────────────────┐
           │     Final Answer     │
           └──────────────────────┘
```

---

## 系統能力（System Capabilities）

### 受控生成（Controlled Generation）

* 僅在 retrieval 資訊充足時生成
* 資訊不足時拒答，避免 hallucination

---

### 多輪檢索（Multi-round Retrieval）

* 自動判斷是否需要 retry
* 動態調整 query（HyDE / keyword）

---

### 對話理解（Conversation-aware）

* 支援 follow-up 問題
* 自動補齊缺失資訊

---

### 工具擴展（Tool Integration）

* calculator（數值計算）
* 可擴展至 API / database

---

## 設計總結

本系統的核心不在於使用哪些模型，

而在於：

* 將檢索決策從 LLM 中抽離
* 將流程轉為可控系統

具體體現在：

* Router：控制是否檢索
* RQC：控制檢索品質
* Memory：僅負責對話理解

最終提升：

* 穩定性（Stability）
* 可控性（Controllability）
* 可驗證性（Verifiability）

---

## 延伸設計（Extensions）

### QA-based Query Optimization（External Module）

在另一個獨立實作中，設計了一個 QA-based Query Optimization 模組，用於優化查詢策略。

核心概念：

* 將 User Query 與既有 QA 集合進行 semantic matching
* 若相似度高 → 使用 QA 進行 query rewrite
* 若相似度低 → fallback 至 HyDE + multi-round retrieval

設計價值：

* 降低 HyDE 使用（降低成本與 latency）
* 提升 query 與文件語言一致性
* 區分 head queries 與 long-tail queries

此模組目前未整合進本 repo，可於另一專案查看。



---

## 環境安裝（Setup）

```bash
python -m venv .venv
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

---

## 環境變數

```env
GOOGLE_API_KEY=your_api_key
```

---

## 建立向量資料庫

```bash
python scripts/build_vectorstore.py
```

---

## 啟動系統

```bash
python main.py
```

---
