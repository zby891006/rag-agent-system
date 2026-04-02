# ESG RAG Agent（具備 Routing 與 Quality Control 的檢索系統）


## 專案簡介

本專案實作一個應用於 ESG / 財務文件的問答 AI Agent，  
透過 Retrieval-Augmented Generation（RAG）架構，結合查詢路由（Routing）、檢索品質控制（RQC）做為門控機制與 HyDE 強化檢索策略。  



---
## 設計思維（Design Rationale）

本系統的設計源於 ESG 與財務文件場景的實務觀察。

在實際使用中，使用者提出的查詢通常具有以下特性：

- 語意較為模糊，缺乏精確的專業術語
- 無法有效對應到文件中的正式表述方式
- 難以直接檢索到具體且可操作的內容

此外，ESG 與財報文件具有高度專業性與結構化特徵，
使得傳統基於關鍵字或單次檢索的 RAG 方法，容易出現以下問題：

- 檢索結果偏向概述性描述（high-level statements）
- 雖涵蓋相關主題，但缺乏具體方法或細節
- 無法支撐完整且精確的回答

---

### HyDE：提升語意對齊能力

為解決使用者查詢與文件語言之間的落差，本系統引入 HyDE（Hypothetical Document Expansion）：

- 生成符合 ESG 報告語境的假設性段落
- 模擬文件中實際可能出現的敘述方式
- 提升 query 與文件語意的對齊程度

此設計可有效縮小使用者查詢與文件語言之間的語意落差，
提升檢索品質。

---

### RQC：建立檢索品質控制機制

即使透過 HyDE 改善召回率，仍可能出現資訊不足或過於概括的情況。

因此本系統設計 Retrieval Quality Controller（RQC），作為檢索流程中的品質閘門：

- 評估檢索結果是否足以支撐回答
- 若資訊不足，觸發多輪檢索（feedback loop）
- 從初始結果中抽取關鍵專有名詞，進一步強化檢索查詢

此機制將檢索流程分為：

1. **Exploration（初始檢索）**
2. **Correction（結果修正）**

以提升最終回答的可靠性與資訊完整度。

---

### Query Routing：降低不必要檢索成本

在早期設計中，所有查詢皆進入檢索流程，導致：

- 不必要的延遲（latency）
- 計算資源浪費
- 對話型問題無法有效利用記憶

因此引入 Query Routing：

- 僅當問題涉及文件內容時才啟用檢索
- 其餘情境交由語言模型直接處理

此設計可在維持回答品質的同時，降低系統成本並提升回應效率。



---

### 設計總結

本系統透過以下三個核心設計：

- HyDE（語意對齊）
- RQC（品質控制）
- Query Routing（流程控制）

在「檢索品質」、「系統穩定性」與「效率」之間取得平衡，

並使 RAG 系統更適用於高專業性文件場景。




## 系統架構

整體流程如下：

## 🧠 System Architecture

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
        │      • Calculator              │
        │      • (Extensible Tools)      │
        │                                │
        │  + Memory (generation only)    │
        └──────────┬─────────────────────┘
                   │
                   ▼
           ┌──────────────────────┐
           │     Final Answer     │
           └──────────────────────┘
```


## 系統能力（System Capabilities）

### 受控生成（Controlled Generation）
- 僅允許模型基於檢索內容進行回答
- 當資訊不足時，明確拒答以避免 hallucination
- 標準回覆：
  "Insufficient information in the retrieved documents."

---

### 對話記憶（Short-term Memory）
- 保留近期對話歷史
- 僅在生成階段使用，不參與檢索流程
- 避免 query drift（語意偏移）與檢索污染

---

### 工具擴展能力（Tool Extensibility）
- 透過 agent 架構支援工具調用
- 目前實作：
  - calculator（作為最小可行示範）
- 架構上可擴展至 API、資料庫或外部服務整合

## 環境安裝（Setup）

### 建立虛擬環境（建議）

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
```

---

### 安裝套件

```bash
pip install -r requirements.txt
```

---

### 設定環境變數

請在專案根目錄建立 `.env` 檔案：

```env
GOOGLE_API_KEY=your_api_key_here
```

---

### 建立向量資料庫（首次執行）

```bash
python scripts/build_vectorstore.py
```

---

### 啟動系統

```bash
python main.py
```
