Here is the requested addendum to the design document.

-----

### **Addendum: Technology Stack and Layering Strategy**

**1. Abstract**

This addendum provides a comparative analysis of relevant agentic frameworks and prescribes a specific, layered technology stack to implement the Autonomous Agentic System (AAS). The strategy is predicated on using the best-suited framework for each stage of the Validation-Centric Pipeline, creating a hybrid system that leverages the unique strengths of each technology.

**2. Framework Compare & Contrast Analysis**

The choice of framework is not monolithic; it is stage-dependent.

| Framework | Planning Stage (Stage 1) | Generation Stage (Stage 2) | Critique Stage (Stage 3) | Suitability for Loops |
| :--- | :--- | :--- | :--- | :--- |
| **CrewAI** | **Excellent.** Ideal for a "Project Manager" agent to decompose prompts into structured plans due to its role-based design. | **Good.** Well-suited for structured content generation (research reports). Less effective for iterative, stateful coding tasks. | **Excellent.** The definitive choice for creating a "Red Team" of diverse, specialized agents (Skeptic, QA, Auditor). | **Requires External Orchestrator.** Processes are sequential by default; loops must be managed by a parent script. |
| **AutoGen** | **Poor.** Not designed for high-level, structured planning. Its focus is on conversational problem-solving, not project decomposition. | **Excellent.** Natively designed for iterative code generation and debugging via its conversational `AssistantAgent` \<\> `UserProxyAgent` feedback loop. | **Good.** The `UserProxyAgent` can be configured to run tests, acting as a built-in critique mechanism for code. Less flexible for diverse, non-code-based critique teams. | **Natively Cyclical.** The core operational model is a conversation loop, making it ideal for the inner `Generate <-> Revise` cycle. |
| **Open-Hands** | **N/A.** Cannot perform planning. | **Specialized.** Unsuitable for initial, creative generation. Its strength is in meticulously executing a pre-defined, detailed plan (e.g., refactoring a codebase). It is a "tool" to be called by another agent, not a core generative framework. | **N/A.** | **N/A.** |
| **Single Agent (LangChain)** | **Poor.** A single agent lacks the structural capacity to decompose a complex problem into a reliable plan. | **Poor.** Prone to losing focus and producing low-quality, incomplete artifacts when tasked with a complex project. | **Limited.** Can be used to create simple, single-purpose "Tool Agents" (e.g., a citation checker), but cannot manage a complex, multi-faceted critique process. | **Requires External Orchestrator.** |

**3. Prescribed Layering and Tiering Strategy**

The AAS will be constructed as a hybrid system managed by a central **Orchestrator** (`orchestrator.py`). This script is responsible for executing the primary state machine, managing the `C(v)` score, and invoking the appropriate agentic crews/tools for each stage.

#### 3.1. Use Case 1: MVP Software Development

| Layer / Stage | Technology | Implementation Details | Critical Tools |
| :--- | :--- | :--- | :--- |
| **Layer 1: Orchestration** | Custom Python Script | `orchestrator.py` manages the primary `while` loop, tracks `C(v)` and `ΔC`, and executes the tiered intervention protocol. | `git` (for state reversion). |
| **Layer 2: Planning (Stage 1)** | `CrewAI` | A **"Software Architect" Agent** is invoked once. It consumes the user prompt and produces a `spec.yaml` file defining modules, function signatures, dependencies, and a list of required unit tests. | `pyyaml`. |
| **Layer 3: Generation & Revision (Stage 2)** | `AutoGen` | The Orchestrator initiates an `AutoGen` conversation. An **`AssistantAgent`** writes the Python code. A **`UserProxyAgent`** is configured to execute shell commands to: 1. Run a linter (`flake8`). 2. Run the test suite (`pytest`) against the tests defined in `spec.yaml`. The loop continues until all tests pass and linter errors are resolved. | `pytest`, `flake8`. |
| **Layer 4: Adversarial Critique (Stage 3)** | `CrewAI` | After the `AutoGen` loop succeeds, the Orchestrator invokes a **"QA Red Team" Crew**. This crew consists of: **"Spec Compliance Agent"** (compares final app features to the plan), **"Security Auditor Agent"** (uses static analysis tools to find vulnerabilities), and **"Maintainability Agent"** (scores code complexity and documentation). The output is the final `C(v)` score and a list of any remaining high-level flaws. | Static analysis tools (e.g., `Bandit`). |
| **Layer 5: Synthesis (Stage 4)** | `CrewAI` | If the Critique stage generates final revisions, a **"Refinement Agent"** incorporates them. A **"Documentation Agent"** generates a `README.md` based on the plan and final code. | |

#### 3.2. Use Case 2: Verifiable Research Report

| Layer / Stage | Technology | Implementation Details | Critical Tools |
| :--- | :--- | :--- | :--- |
| **Layer 1: Orchestration** | Custom Python Script | `orchestrator.py` manages the primary `while` loop, tracks `C(v)` and `ΔC`, and executes the tiered intervention protocol. | `git`. |
| **Layer 2: Planning (Stage 1)** | `CrewAI` | A **"Lead Researcher" Agent** is invoked once. It consumes the user prompt and produces a detailed `outline.json` file, defining the report structure, key sections, and primary hypotheses to be investigated. | |
| **Layer 3: Generation & Revision (Stage 2)** | `CrewAI` | A **"Drafting Crew"** is invoked. It includes a **"Search Agent"** (uses tools to query academic databases and the web) and a **"Writer Agent"** (populates the sections of `outline.json` with draft text and preliminary citations). | Web search APIs, ArXiv/Semantic Scholar APIs. |
| **Layer 4: Adversarial Critique (Stage 3)** | `CrewAI` + RAG System | This is the core validation layer, the **"Council of Skeptics" Red Team**: \<br\>1. **"Citation Validator Agent":** Checks for the existence of cited works via APIs. \<br\>2. **"Source-Reader Agent":** This agent is the system's primary defense against hallucination. It uses a **Retrieval-Augmented Generation (RAG)** system to ingest the *full text* of a cited source, then determines if the source's content truly supports the claim made in the draft. \<br\>3. **"Skeptic Agent":** Reads the draft and actively attempts to find logical fallacies or formulate counter-arguments. \<br\>The combined output determines the `C(v)` score. | **Vector Database** (Chroma, FAISS), PDF text extraction libraries (`PyMuPDF`), scientific APIs. |
| **Layer 5: Synthesis (Stage 4)** | `CrewAI` | A final **"Editor Agent"** incorporates the verified claims and revisions from the critique loop into a final, coherent report, ensuring proper formatting and bibliographic style. | |
