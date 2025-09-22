# JIRA Integration System Architecture Diagrams

This document contains Mermaid diagrams showing the architecture and data flow of the JIRA integration system.

## System Overview Architecture

```mermaid
architecture-beta
    group jira_integration(cloud)[JIRA Integration System]
    
    service sync_engine(server)[Sync Engine] in jira_integration
    service task_generator(disk)[Task Generator] in jira_integration  
    service diagram_builder(database)[Diagram Builder] in jira_integration
    service markdown_renderer(server)[Markdown Renderer] in jira_integration
    
    group external_systems(internet)[External Systems]
    service jira_api(cloud)[JIRA Cloud API] in external_systems
    service local_files(disk)[Local Files] in external_systems
    
    group validation_layer(server)[Validation Layer]
    service quality_enforcer(database)[Quality Enforcer] in validation_layer
    service naming_validator(server)[Naming Validator] in validation_layer
    
    sync_engine:R --> L:jira_api
    sync_engine:B --> T:task_generator
    task_generator:R --> L:diagram_builder  
    diagram_builder:B --> T:markdown_renderer
    markdown_renderer:R --> L:local_files
    sync_engine:L --> R:quality_enforcer
    quality_enforcer:B --> T:naming_validator
```

## Component Architecture

```mermaid
flowchart TB
    subgraph "JIRA Integration System"
        direction TB
        
        subgraph "Core Components"
            direction LR
            JTS[JiraTaskSync<br/>Main Engine]
            FetchModule[Fetch Module<br/>API Integration]
            GenModule[Content Generator<br/>Markdown Builder]
            WriteModule[File Writer<br/>Output Manager]
        end
        
        subgraph "Data Processing"
            direction LR
            Parser[Issue Parser<br/>Data Normalization]
            Hierarchy[Hierarchy Builder<br/>Parent-Child Relations]
            Timeline[Timeline Generator<br/>Mermaid Diagrams]
            Mindmap[Mindmap Generator<br/>Visual Hierarchy]
        end
        
        subgraph "Quality Layer"
            direction LR
            Validator[Content Validator<br/>Standards Check]
            Logger[Logging System<br/>Debug & Audit]
            Config[Configuration<br/>Settings Management]
        end
    end
    
    subgraph "External Systems"
        direction TB
        JIRA[(JIRA Cloud API<br/>PT Project)]
        Files[(Local Files<br/>TASKS.md)]
        Scripts[(Validation Scripts<br/>Quality Gates)]
    end
    
    %% Main data flow
    JTS --> FetchModule
    FetchModule --> JIRA
    JIRA --> Parser
    Parser --> Hierarchy
    Hierarchy --> Timeline
    Hierarchy --> Mindmap
    Timeline --> GenModule
    Mindmap --> GenModule
    GenModule --> WriteModule
    WriteModule --> Files
    
    %% Quality flow
    JTS --> Validator
    Validator --> Scripts
    Logger --> Config
    
    %% Cross-cutting concerns
    JTS -.-> Logger
    FetchModule -.-> Logger
    GenModule -.-> Logger
    WriteModule -.-> Logger
    
    %% Styling
    classDef core fill:#e1f5fe
    classDef external fill:#c8e6c9
    classDef quality fill:#fff3e0
    
    class JTS,FetchModule,GenModule,WriteModule core
    class JIRA,Files,Scripts external
    class Validator,Logger,Config quality
```

## Data Flow Architecture

```mermaid
flowchart TD
    A[Command Line<br/>Execution] --> B{Configuration<br/>Load}
    B --> C[Initialize<br/>JiraTaskSync]
    C --> D[Fetch JIRA Issues<br/>API Call]
    
    D --> E{Data<br/>Validation}
    E -->|Valid| F[Parse Issues<br/>Normalize Format]
    E -->|Invalid| G[Error Log<br/>& Exit]
    
    F --> H[Build Hierarchy<br/>Parent-Child Links]
    H --> I[Generate Timeline<br/>Mermaid Code]
    H --> J[Generate Mindmap<br/>Mermaid Code]
    
    I --> K[Content Assembly<br/>Markdown Builder]
    J --> K
    
    K --> L{Dry Run<br/>Mode?}
    L -->|Yes| M[Preview Output<br/>Console Display]
    L -->|No| N[Write File<br/>TASKS.md]
    
    N --> O[Validation<br/>Quality Check]
    O --> P[Success<br/>Confirmation]
    
    M --> Q[Process Complete]
    P --> Q
    G --> Q
    
    %% Logging throughout
    C -.-> R[Logging System]
    D -.-> R
    F -.-> R
    K -.-> R
    N -.-> R
    
    style A fill:#e3f2fd
    style Q fill:#c8e6c9
    style G fill:#ffebee
    style R fill:#fff3e0
```

## Class Hierarchy

```mermaid
classDiagram
    class JiraTaskSync {
        -cloud_id: str
        -project_key: str
        -verbose: bool
        -dry_run: bool
        -logger: Logger
        -tasks_file: Path
        +__init__(cloud_id, project_key, verbose, dry_run)
        +setup_logging()
        +log(message, level)
        +fetch_jira_issues() List~Dict~
        +generate_tasks_content(issues) str
        +write_tasks_file(content) bool
        +sync_tasks() bool
        -_get_status_icon(status) str
    }
    
    class IssueProcessor {
        +normalize_issue(raw_issue) Dict
        +validate_issue(issue) bool
        +build_hierarchy(issues) Dict
        +sort_by_priority(issues) List~Dict~
    }
    
    class DiagramGenerator {
        +generate_timeline(issues) List~str~
        +generate_mindmap(issues) List~str~
        +generate_statistics(issues) List~str~
        +validate_mermaid_syntax(code) bool
    }
    
    class ContentBuilder {
        +build_header() List~str~
        +build_epic_section(epic, children) List~str~
        +build_task_section(task) List~str~
        +build_footer(metadata) List~str~
        +assemble_content(sections) str
    }
    
    class FileManager {
        +ensure_directory(path) bool
        +write_markdown(content, path) bool
        +backup_existing(path) bool
        +validate_output(path) bool
    }
    
    class ConfigManager {
        +load_config(path) Dict
        +get_cloud_id() str
        +get_project_key() str
        +get_output_path() Path
    }
    
    JiraTaskSync --> IssueProcessor
    JiraTaskSync --> DiagramGenerator
    JiraTaskSync --> ContentBuilder
    JiraTaskSync --> FileManager
    JiraTaskSync --> ConfigManager
    
    IssueProcessor --> DiagramGenerator
    DiagramGenerator --> ContentBuilder
    ContentBuilder --> FileManager
```

## Sequence Diagram - Sync Process

```mermaid
sequenceDiagram
    participant CLI as Command Line
    participant JTS as JiraTaskSync
    participant JIRA as JIRA Cloud API
    participant Parser as Issue Parser
    participant Gen as Content Generator
    participant File as File System
    participant Log as Logger
    
    CLI->>+JTS: Initialize with config
    JTS->>+Log: Setup logging
    Log-->>-JTS: Ready
    
    CLI->>+JTS: sync_tasks()
    JTS->>+Log: Start sync process
    
    JTS->>+JIRA: fetch_jira_issues()
    Note over JIRA: Currently uses embedded<br/>real JIRA data
    JIRA-->>-JTS: List of issues
    
    JTS->>+Parser: Process raw issues
    Parser->>Parser: Normalize format
    Parser->>Parser: Validate structure
    Parser-->>-JTS: Formatted issues
    
    JTS->>+Gen: generate_tasks_content(issues)
    Gen->>Gen: Build hierarchy
    Gen->>Gen: Generate diagrams
    Gen->>Gen: Create statistics
    Gen->>Gen: Assemble markdown
    Gen-->>-JTS: Complete content
    
    alt Dry Run Mode
        JTS->>+Log: Display preview
        Log-->>-JTS: Preview shown
    else Normal Mode
        JTS->>+File: write_tasks_file(content)
        File->>File: Ensure directory exists
        File->>File: Write TASKS.md
        File-->>-JTS: Write successful
    end
    
    JTS->>+Log: Sync completed
    Log-->>-JTS: Logged
    JTS-->>-CLI: Success/Failure status
```

## State Diagram - Issue Processing

```mermaid
stateDiagram-v2
    [*] --> Loading
    Loading --> Validating: Issues fetched
    Loading --> Error: Fetch failed
    
    Validating --> Processing: Valid format
    Validating --> Error: Invalid data
    
    Processing --> Parsing: Structure OK
    Processing --> Error: Processing failed
    
    Parsing --> Hierarchy: Issues parsed
    Parsing --> Error: Parse error
    
    Hierarchy --> Generating: Hierarchy built
    Hierarchy --> Error: Hierarchy failed
    
    Generating --> Assembling: Diagrams created
    Generating --> Error: Generation failed
    
    Assembling --> DryRunCheck: Content ready
    Assembling --> Error: Assembly failed
    
    DryRunCheck --> Preview: Dry run mode
    DryRunCheck --> Writing: Normal mode
    
    Preview --> Complete: Preview shown
    Writing --> Validating_Output: File written
    Writing --> Error: Write failed
    
    Validating_Output --> Complete: Validation passed
    Validating_Output --> Warning: Validation issues
    
    Warning --> Complete: Continue anyway
    Error --> [*]: Process failed
    Complete --> [*]: Process successful
```

## Integration Points

```mermaid
flowchart LR
    subgraph "Development Environment"
        direction TB
        IDE[VS Code<br/>Development]
        Git[Git<br/>Version Control]
        Scripts[Validation<br/>Scripts]
    end
    
    subgraph "JIRA Integration"
        direction TB
        API[JIRA REST API<br/>or MCP Tools]
        Sync[Sync Engine<br/>sync_jira_tasks_fixed.py]
        Tasks[TASKS.md<br/>Local Mirror]
    end
    
    subgraph "Quality System"
        direction TB
        PreCommit[Pre-commit<br/>Hooks]
        CICD[GitHub Actions<br/>CI/CD Pipeline]
        Validation[Quality<br/>Validation]
    end
    
    subgraph "Documentation"
        direction TB
        Docs[API Docs<br/>Developer Guides]
        Reports[Status Reports<br/>Progress Tracking]
        Diagrams[Mermaid<br/>Diagrams]
    end
    
    %% Integration flows
    IDE --> Git
    Git --> PreCommit
    PreCommit --> Scripts
    Scripts --> Validation
    
    API --> Sync
    Sync --> Tasks
    Tasks --> Git
    
    Sync --> Reports
    Reports --> Docs
    Docs --> Diagrams
    
    CICD --> Validation
    CICD --> Docs
    
    %% Styling
    classDef dev fill:#e1f5fe
    classDef jira fill:#c8e6c9
    classDef quality fill:#fff3e0
    classDef docs fill:#f3e5f5
    
    class IDE,Git,Scripts dev
    class API,Sync,Tasks jira
    class PreCommit,CICD,Validation quality
    class Docs,Reports,Diagrams docs
```
