It looks like the previous attempt at a "Dark Mode" style resulted in a common rendering issue: the white text didn't render correctly against the dark backgrounds (remaining black/gray), or the "striped" pattern appeared, making it unreadable. **You are absolutely right—that is not presentable.**

For professional presentations, the "bulletproof" philosophy is **High-Fidelity Light Mode**. This mimics the crisp, high-contrast look of engineering blueprints or LucidChart/Visio exports. It guarantees that **black text on light backgrounds** will always be readable, regardless of the projector or screen quality.

Here is the **corrected, presentation-ready version**. I have added a `%%{init: ...}%%` configuration block to the top of each diagram. This forces the renderer to use specific high-contrast variables, overriding any default theme weirdness.

***

### **New Color Philosophy: "Engineering Blueprint"**
*   **Background:** Clean White/Paper (Maximum contrast)
*   **Nodes:** Very pale pastels (Subtle coding)
*   **Borders:** Thick, Dark, Saturated (The "Punch")
*   **Text:** Jet Black (Readability)

***

## 1. Use Case Diagram (High-Fidelity)

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#e0f2fe',
      'primaryTextColor': '#000000',
      'primaryBorderColor': '#0284c7',
      'lineColor': '#334155',
      'secondaryColor': '#dcfce7',
      'tertiaryColor': '#f3e8ff'
    }
  }
}%%
graph TB
    subgraph Actors
        User["👤 Web User"]
        APIConsumer["🤖 API Consumer"]
        Admin["👨‍💼 Admin"]
    end
    
    subgraph "ScraPy System"
        UC1["Submit Scrape Job"]
        UC2["View Job Results"]
        UC3["Download Results<br/>(JSON/CSV)"]
        UC4["View Job History"]
        UC5["Save Job to Database"]
        UC6["Generate API Key"]
        UC7["Configure Webhooks"]
        UC8["Submit Job via API"]
        UC9["Monitor Job Status"]
        UC10["Receive Webhook Notification"]
    end
    
    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC7
    
    APIConsumer --> UC8
    APIConsumer --> UC9
    APIConsumer --> UC10
    
    Admin --> UC6
    Admin --> UC7
    
    UC1 -.extends.-> UC2
    UC2 -.extends.-> UC3
    UC8 -.extends.-> UC9

    %% High-Contrast Styling
    classDef actor fill:#dbeafe,stroke:#1e40af,stroke-width:3px,color:#000,font-weight:bold
    classDef system fill:#ffffff,stroke:#475569,stroke-width:2px,color:#000

    class User,APIConsumer,Admin actor
    class UC1,UC2,UC3,UC4,UC5,UC6,UC7,UC8,UC9,UC10 system
```
**Copy to mermaid.live** ☝️

***

## 2. Data Flow Diagram (High-Fidelity)

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#ffffff',
      'primaryTextColor': '#000000',
      'primaryBorderColor': '#000000',
      'lineColor': '#000000'
    }
  }
}%%
flowchart LR
    User["👤 User<br/>(Browser)"]
    API["🤖 API Consumer"]
    
    subgraph ScraPy["ScraPy Platform"]
        Frontend["Next.js Frontend"]
        Backend["FastAPI Backend"]
        Worker["ARQ Worker"]
        DB[(PostgreSQL)]
        Cache[(Redis)]
    end
    
    Target["🌐 Target Website"]
    Webhook["📨 Webhook Endpoint"]
    
    User ==>|"1. Submit Job"| Frontend
    Frontend ==>|"2. API Request"| Backend
    Backend ==>|"3. Enqueue"| Cache
    Cache ==>|"4. Process"| Worker
    Worker ==>|"5. Scrape"| Target
    Target -.->|"6. HTML Response"| Worker
    Worker ==>|"7. Store Results"| DB
    Worker -.->|"8. Update Status"| Cache
    Backend -.->|"9. Fetch Results"| DB
    Backend -.->|"10. Return Data"| Frontend
    Frontend ==>|"11. Display"| User
    
    API ==>|"API Request"| Backend
    Backend -.->|"Results"| API
    
    Worker ==>|"Job Complete"| Webhook

    %% LucidChart-style Palette
    style User fill:#d1fae5,stroke:#047857,stroke-width:3px,color:#000
    style API fill:#d1fae5,stroke:#047857,stroke-width:3px,color:#000
    style Frontend fill:#e0f2fe,stroke:#0369a1,stroke-width:2px,color:#000
    style Backend fill:#e0f2fe,stroke:#0369a1,stroke-width:2px,color:#000
    style Worker fill:#ffedd5,stroke:#c2410c,stroke-width:2px,color:#000
    style DB fill:#f3e8ff,stroke:#7e22ce,stroke-width:2px,color:#000
    style Cache fill:#f3e8ff,stroke:#7e22ce,stroke-width:2px,color:#000
    style Target fill:#f1f5f9,stroke:#334155,stroke-width:2px,stroke-dasharray: 5 5,color:#000
```
**Copy to mermaid.live** ☝️

***

## 3. Detailed Flowchart (The Masterpiece)

This version uses specific **shape styles** and **thick borders** to guide the eye.

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#fff',
      'edgeLabelBackground': '#fff',
      'tertiaryColor': '#f8fafc'
    }
  }
}%%
flowchart TD
    Start([User Submits Scrape Job]) --> Auth{Authenticated?}
    
    Auth -->|No| Return401[Return 401<br/>Unauthorized]
    Auth -->|Yes| ValidateInput[Validate Input<br/>URL, Mode, Selectors]
    
    ValidateInput --> InputValid{Valid?}
    InputValid -->|No| Return422[Return 422<br/>Validation Error]
    InputValid -->|Yes| GenerateID[Generate Job ID]
    
    GenerateID --> StoreRedis[Store Job in Redis<br/>Status: pending]
    StoreRedis --> EnqueueWorker[Enqueue to ARQ Worker]
    EnqueueWorker --> ReturnJobID[Return Job ID to Client]
    
    ReturnJobID --> WorkerPick[Worker Picks Up Job]
    WorkerPick --> InsertDB[Insert Job to PostgreSQL<br/>Status: processing]
    
    InsertDB --> CheckMode{Scraping Mode?}
    
    CheckMode -->|Guided| CheckJS1{Render JS?}
    CheckJS1 -->|Yes| DynamicScrape[Playwright Dynamic Scrape]
    CheckJS1 -->|No| StaticScrape[BeautifulSoup Static Scrape]
    
    CheckMode -->|Smart| CheckJS2{Render JS?}
    CheckJS2 -->|Yes| DynamicScrape
    CheckJS2 -->|No| StaticScrape
    
    DynamicScrape --> GotHTML[Got HTML Content]
    StaticScrape --> GotHTML
    
    GotHTML --> SmartMode{Smart Mode?}
    SmartMode -->|Yes| LLMAnalyze[Gemini AI Analyzes<br/>Extract Data]
    SmartMode -->|No| ExtractData[Extract Using Selectors]
    
    LLMAnalyze --> UpdateSuccess
    ExtractData --> UpdateSuccess[Update DB & Redis<br/>Status: completed<br/>Store Results]
    
    UpdateSuccess --> HasWebhook{Webhook<br/>Configured?}
    HasWebhook -->|Yes| SendWebhook[Send Webhook Notification]
    HasWebhook -->|No| Done
    SendWebhook --> Done
    
    GotHTML --> Error{Error?}
    Error -->|Yes| UpdateFailed[Update DB & Redis<br/>Status: failed<br/>Store Error Message]
    UpdateFailed --> Done([Job Complete])
    
    Done --> UserPoll[User Polls for Results]
    UserPoll --> DisplayResults[Display Results in UI<br/>Table/JSON View]
    DisplayResults --> Download{Download?}
    Download -->|JSON| DownloadJSON[Download JSON File]
    Download -->|CSV| DownloadCSV[Download CSV File]
    Download -->|Save to DB| SaveDB[Save to Database]
    
    %% High Visibility Styles
    style Start fill:#dcfce7,stroke:#15803d,stroke-width:4px,color:#000
    style Done fill:#f1f5f9,stroke:#334155,stroke-width:4px,color:#000
    style Return401 fill:#fee2e2,stroke:#b91c1c,stroke-width:2px,color:#000
    style Return422 fill:#fee2e2,stroke:#b91c1c,stroke-width:2px,color:#000
    style UpdateFailed fill:#fee2e2,stroke:#b91c1c,stroke-width:2px,color:#000
    
    style WorkerPick fill:#ffedd5,stroke:#c2410c,stroke-width:2px,color:#000
    style DynamicScrape fill:#dbeafe,stroke:#1e40af,stroke-width:2px,color:#000
    style StaticScrape fill:#dbeafe,stroke:#1e40af,stroke-width:2px,color:#000
    style LLMAnalyze fill:#e0e7ff,stroke:#4338ca,stroke-width:2px,color:#000
    
    style Auth fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#000
    style CheckMode fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#000
    style InputValid fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#000
```
**Copy to mermaid.live** ☝️

***

## 4. ER Diagram (Database)

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#f1f5f9',
      'primaryTextColor': '#000',
      'primaryBorderColor': '#334155',
      'lineColor': '#334155'
    }
  }
}%%
erDiagram
    JOBS ||--o{ JOB_RESULTS : contains
    JOBS {
        uuid id PK
        string url
        string mode
        string status
        json data
        timestamp created_at
    }
    
    JOB_RESULTS {
        uuid job_id FK
        json extracted_data
        timestamp scraped_at
    }
    
    API_KEYS ||--o{ JOBS : authenticates
    API_KEYS {
        uuid id PK
        string key_prefix
        string user_id
        boolean is_active
        int rate_limit
        timestamp created_at
    }
    
    WEBHOOKS ||--o{ WEBHOOK_DELIVERIES : triggers
    WEBHOOKS {
        uuid id PK
        string url
        string secret
        string user_id
    }
```
**Copy to mermaid.live** ☝️

***

## 5. Component Architecture

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#ffffff',
      'primaryTextColor': '#000000',
      'lineColor': '#000000',
      'clusterBkg': '#f8fafc',
      'clusterBorder': '#cbd5e1'
    }
  }
}%%
graph TB
    subgraph Client["Client Layer"]
        Browser["🌐 Web Browser"]
        APIClient["🤖 API Client"]
    end
    
    subgraph Frontend["Frontend Layer (Vercel)"]
        NextJS["Next.js 16"]
        AuthUI["Clerk Auth UI"]
    end
    
    subgraph Backend["Backend Layer (Railway)"]
        FastAPI["FastAPI Server"]
        ScrapeAPI["API Routes"]
        ScraperService["Scraper Service"]
    end
    
    subgraph Worker["Worker Layer"]
        ARQ["ARQ Worker"]
        Playwright["Playwright"]
    end
    
    subgraph Data["Data Layer"]
        DB[(PostgreSQL)]
        Redis[(Redis)]
    end
    
    Browser --> NextJS
    NextJS --> AuthUI
    NextJS --> ScrapeAPI
    APIClient --> ScrapeAPI
    
    ScrapeAPI --> Redis
    ScrapeAPI --> DB
    
    Redis --> ARQ
    ARQ --> ScraperService
    ScraperService --> Playwright
    ARQ --> DB
    
    %% Styling
    style Browser fill:#dcfce7,stroke:#15803d,stroke-width:2px,color:#000
    style NextJS fill:#dcfce7,stroke:#15803d,stroke-width:2px,color:#000
    style FastAPI fill:#dbeafe,stroke:#1d4ed8,stroke-width:2px,color:#000
    style ARQ fill:#ffedd5,stroke:#c2410c,stroke-width:2px,color:#000
    style DB fill:#f3e8ff,stroke:#7e22ce,stroke-width:2px,color:#000
    style Redis fill:#f3e8ff,stroke:#7e22ce,stroke-width:2px,color:#000
```
**Copy to mermaid.live** ☝️

### Why this fixes the issue:
1.  **Explicit Theme Override**: The `%%{init...}%%` block forces the diagram to ignore default dark/weird themes.
2.  **Dark Borders, Light Fills**: This is the "Contrast Pop". The eye tracks the dark border, but reads the text on the clean light background.
3.  **Zero Color Clash**: Black text on white/pastel is mathematically the highest contrast ratio possible.

[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/11362919/42b9f4d3-c1b1-4b5b-905b-fbc14bbce75f/Screenshot-from-2025-11-27-17-44-52.jpg?AWSAccessKeyId=ASIA2F3EMEYEQWOCN6WT&Signature=3v%2FzrQ840%2FUoQ3fm4Z4AC9k06uI%3D&x-amz-security-token=IQoJb3JpZ2luX2VjENT%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIBGM3DGMoGk5AFiESsuY8b0DSkYTl0ZPFQ%2Ftm6mNensEAiBwPg3T%2FR6WgJ9DXQKDpS1a%2BC3RPcdD1QIobtNlk1HCrCr8BAid%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDY5OTc1MzMwOTcwNSIMXovHV%2BOJvwHjwncDKtAE1K0426VR7He7vwYEdEAYWMEZdGSIWEElNHHr%2FYgzSOu%2BOXZ0akz5AtfJcWbcS7HndPhyA7ZsOkZ0F9xK73wNNaDqGDGYZN%2BkvdOZGLe4X3FBtr0cHuUjM8KxlTrGnuq5RatDE2dLDckF8%2BvnzGYI0WfQTrG65HrfCMw6gLDQTfmW41%2F9Dtb9YY9fLWlhM2BBZqLWD0MJieCSuHLiceIZe7syJSwB7JW1Zbr3lQN7C535iWx%2FK056clz%2FwP2nwpuSn5DUpCyg5btj57h0EOR4s%2BIvvW5AqlxZFm3dksSb4EV93r4DSXgzyrMGzh1K9AYPhhW1zUqzWmbua64sVtAofEtKd1tg3zQ6OSu0amGzbs6iEJYHxCHru%2FWioCkzjJM1S8mO5fUDVi45u9U2CL9Qu1bLCpnC%2BiSJ78jP0SCYMi3PL2LSNx7hrrj1X%2B26e50sbXJ8wb2SPY5JD04haDuIWi0eTMdUDkiBbMv4nmpKpGU4SNAnUj9SlbFujcuHkS7oBp5cZvQLc1Zz5YovEx82HBIi5milxkZaEaiUtWEZ6NEoVrbpcD33XCkIPWm3RCbZlNDVB3X5qCSmcbFhRIBQf5LQ56K%2FKCFpDUkrKN9G2HBoomFJupSf5w3PlQuGMT6Kdopdp49NMnqz13c2a3SdPr4IJJP88sXkFxbUOmDmTtbOKieEgi%2BMYqAmbRnGzMZiXb%2BrX5XJNcSuotIgfJqemjVKZGGG6NT6Jvyrub5blSYD6kRHHH9gDGJY2RPEcYhxwlW2%2BoclJY2xtNY1XfliTzDj%2BKDJBjqZAVBozx3bKuvVjwSX0sPjg7D68asu6kd5sjZEd5XJuw3CGktNlMI%2F7pEJW4NTAAsF2h5aC0VSuTcbDJnQ99vfO3CQAOA4EXHBI0gZkzUkDnNLCXAqNhM1VEcO05fQarE4MbQhyZIrFsGvQgAS7d8%2Bqy8w9AeN9nTk2J2Y9aSPnT9AUSkS9ZN%2Bm355clflOaZ9gZv0vJ4ziswXMQ%3D%3D&Expires=1764246531)
[2](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/11362919/a0d8c1b6-5ca7-4892-bd32-471c2074e8bc/Screenshot-from-2025-11-27-17-46-02.jpg?AWSAccessKeyId=ASIA2F3EMEYEQWOCN6WT&Signature=z1Vt97i%2B4ilQ02eGCmSWSoPuTcI%3D&x-amz-security-token=IQoJb3JpZ2luX2VjENT%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIBGM3DGMoGk5AFiESsuY8b0DSkYTl0ZPFQ%2Ftm6mNensEAiBwPg3T%2FR6WgJ9DXQKDpS1a%2BC3RPcdD1QIobtNlk1HCrCr8BAid%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDY5OTc1MzMwOTcwNSIMXovHV%2BOJvwHjwncDKtAE1K0426VR7He7vwYEdEAYWMEZdGSIWEElNHHr%2FYgzSOu%2BOXZ0akz5AtfJcWbcS7HndPhyA7ZsOkZ0F9xK73wNNaDqGDGYZN%2BkvdOZGLe4X3FBtr0cHuUjM8KxlTrGnuq5RatDE2dLDckF8%2BvnzGYI0WfQTrG65HrfCMw6gLDQTfmW41%2F9Dtb9YY9fLWlhM2BBZqLWD0MJieCSuHLiceIZe7syJSwB7JW1Zbr3lQN7C535iWx%2FK056clz%2FwP2nwpuSn5DUpCyg5btj57h0EOR4s%2BIvvW5AqlxZFm3dksSb4EV93r4DSXgzyrMGzh1K9AYPhhW1zUqzWmbua64sVtAofEtKd1tg3zQ6OSu0amGzbs6iEJYHxCHru%2FWioCkzjJM1S8mO5fUDVi45u9U2CL9Qu1bLCpnC%2BiSJ78jP0SCYMi3PL2LSNx7hrrj1X%2B26e50sbXJ8wb2SPY5JD04haDuIWi0eTMdUDkiBbMv4nmpKpGU4SNAnUj9SlbFujcuHkS7oBp5cZvQLc1Zz5YovEx82HBIi5milxkZaEaiUtWEZ6NEoVrbpcD33XCkIPWm3RCbZlNDVB3X5qCSmcbFhRIBQf5LQ56K%2FKCFpDUkrKN9G2HBoomFJupSf5w3PlQuGMT6Kdopdp49NMnqz13c2a3SdPr4IJJP88sXkFxbUOmDmTtbOKieEgi%2BMYqAmbRnGzMZiXb%2BrX5XJNcSuotIgfJqemjVKZGGG6NT6Jvyrub5blSYD6kRHHH9gDGJY2RPEcYhxwlW2%2BoclJY2xtNY1XfliTzDj%2BKDJBjqZAVBozx3bKuvVjwSX0sPjg7D68asu6kd5sjZEd5XJuw3CGktNlMI%2F7pEJW4NTAAsF2h5aC0VSuTcbDJnQ99vfO3CQAOA4EXHBI0gZkzUkDnNLCXAqNhM1VEcO05fQarE4MbQhyZIrFsGvQgAS7d8%2Bqy8w9AeN9nTk2J2Y9aSPnT9AUSkS9ZN%2Bm355clflOaZ9gZv0vJ4ziswXMQ%3D%3D&Expires=1764246531)
[3](https://mermaid.js.org/config/configuration.html)
[4](https://daobook.github.io/mermaid/theming.html)
[5](https://stackoverflow.com/questions/49535327/change-mermaid-theme-in-markdown)
[6](https://sli.dev/custom/config-mermaid)
[7](https://www.influxdata.com/blog/getting-started-mermaidjs-diagramming-charting/)
[8](https://github.com/mermaid-js/mermaid/issues/684)
[9](https://miro.com/diagramming/what-is-mermaid/)
[10](https://mermaid.js.org/config/schema-docs/config.html)
[11](https://stackoverflow.com/questions/67431973/changing-color-of-font-in-mermaid-js-for-a-single-message)
[12](https://clickup.com/blog/mermaid-diagram-examples/)
[13](https://notepad.onghu.com/2024/making-mermaid-sequence-diagrams-prettier-part1/)
[14](https://mermaid.js.org/config/theming.html)
[15](https://www.kallemarjokorpi.fi/blog/mastering-diagramming-as-code-essential-mermaid-flowchart-tips-and-tricks-2/)
[16](https://www.freecodecamp.org/news/use-mermaid-javascript-library-to-create-flowcharts/)
[17](https://github.com/mermaid-js/mermaid/issues/2673)
[18](https://docs.mermaidchart.com/guides/presentation)
[19](https://docs.mermaidchart.com/mermaid-oss/syntax/gitgraph.html)
[20](https://docs.mermaidchart.com/mermaid-oss/syntax/classDiagram.html)
[21](https://mermaid.js.org/intro/syntax-reference.html)
[22](https://stackoverflow.com/questions/63587556/color-change-of-one-element-in-a-mermaid-sequence-diagram)