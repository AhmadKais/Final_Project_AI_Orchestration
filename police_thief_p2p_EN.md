# Distributed Cops-and-Robbers over a Peer-to-Peer Network

> Full English translation of the course final-project rules book (`police_thief_p2p.pdf`, 160 pages). Translated in 20-page chunks by parallel agents; `<!-- page N -->` comments trace back to source PDF pages.

<!-- page i -->

# Distributed Cops-and-Robbers over a Peer-to-Peer Network

### Rules and Guidelines Book for the Final Project — 2026, Department of Computer Science, University of Haifa

**Dr. Yoram Reuven Segal**

All rights reserved © - Dr. Yoram Reuven Segal

2026

Book version 3.0.0 | Example code version 3.0.0

<!-- page ii -->

## Abstract

This book is the complete rules and guidelines guide for the final project in the course "Orchestration of AI Agents" in the Department of Computer Science at the University of Haifa. The project sets students the development task that is the course's culmination: building two symmetric autonomous entities — a Cop and a Robber — competing against each other in a pursuit race on a board of a given size (for example, 10×10), with no central server to arbitrate between them. Neither of the two sees the true state of the world: each agent symmetrically builds a belief about its opponent's location from a decaying scent map and a verbal hint that may be false. The system is formally modeled as a Decentralized Partially Observable Markov Decision Process (Dec-POMDP), and operates over a Peer-to-Peer network in which each agent is simultaneously a server and a client atop the Model Context Protocol, using the FastMCP library.

The book covers the full breadth of the project's development: modeling the problem under uncertainty; the P2P architecture atop FastMCP; the board mechanics, barriers, and scoring system; the stigmergy-based scent-trail mechanism; the cryptographic Commit-Reveal protocol that guarantees integrity without a referee, including automatic disqualification for forgery; the strategy module based on heuristics and language models (with reinforcement learning as only one option among others); the user interface and the replay simulator; and the league structure, computational fairness, and reporting automation atop the Gmail API — including submission across two GitHub repositories (Cop and Robber) and a signed JSON report. The book includes operational appendices, as well as an example code repository — a basic, open, and public simulation implementation, described in Appendix D; a complete mapping of the mandatory rules (Appendix E); and the mandatory parameter table (Appendix F), which is the sole source of truth for quantitative values. Each chapter is tied to principles taught throughout the course, converting them from theory into a live system operating under real network conditions.

<!-- page iii -->

## A Personal Word — Before the Race Begins

I am addressing you, the students who have reached this point in the course: it is no accident that the final project is not just another classroom exercise, but a race. Over a full semester you built the infrastructure — you understood how a neural network learns, how a Transformer listens, how a single agent delegates tasks to sub-agents, and how two agents converse with each other over an MCP server. Now the moment has come to connect all the pieces into a single autonomous entity that goes out into the world and competes against another entity that you do not control.

This race differs from everything you have done so far in one essential respect: there is no referee. There is no central server that keeps the truth, arbitrates disputes, and protects you from cheating. Instead, the truth is built from the bottom up — by two opponents who do not trust each other, yet are obligated to prove their integrity through mathematics. This is exactly the challenge that real-world distributed artificial-intelligence systems face: coordination without a ruler, trust without a central authority, and intelligent decision-making under a fog of information.

### Why Strict Rules Are Precisely in Your Favor

The rules in this book are iron rules, and that is deliberate. A precise cryptographic protocol, a mandatory JSON structure, and hard time limits are not meant to make things difficult for you — they exist to enable fair play between teams that do not know each other. The sharper the specification, the greater your freedom to innovate within the framework — in strategy, in deception, and in architecture. Discipline in the details is what unleashes creativity at large.

I invite you to read this book not as a list of requirements, but as a roadmap to a system you will be proud of. Read slowly, build according to the development priority order defined in the final chapter, and test every stage before moving on to the next. True victory is not merely in capturing the Robber — it lies in your ability to build a system that withstands real network conditions, proves its own integrity, and adapts to uncertainty. This is a skill that will stay with you far beyond the course.

Dr. Yoram Reuven Segal

<!-- page iv -->

## Clarification: What Is Mandatory and What Is Merely Illustrative

### Read This Before Anything Else — The Foundational Principle

The default is that no rule is mandatory unless it is explicitly stated to be a mandatory rule. All illustrations, examples, code snippets, and scenarios in this book illustrate how the game is conducted — they do not constitute the rules of the game and are not binding on participants, unless it is explicitly noted alongside them that they are part of the rules of the game and bind the parties. Where it is not stated that a rule is mandatory — the rule is not mandatory, and each side may agree with its opponent on different behavior, or act as it sees fit within the bounds of the law.

The sole source of obligation is the mandatory parameter table at the end of the book (Appendix F). The values defined there are mandatory minimums: they may be raised by agreement, but may not be lowered.

The mandatory parameter table is accompanied throughout the book by one technical convention, which is worth becoming familiar with now.

### Key: Code Names for Quantitative Values

Throughout the book, every quantitative value appears as a Hebrew code-name enclosed in square brackets — for example, [board size], [barrier quota], or [scent decay rate]. The meaning of this convention is simple: the actual numeric value is not set in the body text but solely in the mandatory parameter table at the end of the book (Appendix F). This way, a single value can be changed in one place without the book contradicting itself, and each side knows exactly what the mandatory threshold is and what is merely an illustrative example.

<!-- page v -->

## General Guidelines for the Book and Its Structure

### Academic Freedom in Case of Contradiction

This book was written to the best of its ability to be consistent, but you may find a contradiction in it — two places that appear to dictate different behavior. In such a case, you have the academic freedom to choose one of the options and proceed accordingly, provided that you explicitly state this in your report: where you identified the contradiction, what you chose, and why. A reasoned and documented choice will not be held against you. That said, the sole mandatory source of truth for quantitative values remains the mandatory parameter table in the book's final appendix.

**Structure of the Book.** The book consists of 11 chapters and six appendices. The chapters cover the theory, the P2P architecture, the cryptography, the strategy module, the interface, and the league. The appendices are: the Gmail API and OAuth setup guide (Appendix A); the unified configuration file (Appendix B); the GitHub submission requirements (Appendix C); an example code repository — a basic, open, and public simulation implementation intended for learning purposes only (Appendix D); a mapping of all mandatory rules — do, don't, and recommendations (Appendix E); and finally the mandatory parameter table (Appendix F), the final appendix and the sole mandatory source for numeric values.

**Keywords:** Dec-POMDP · distributed multi-agent system · symmetry between agents · Peer-to-Peer network (P2P) · Model Context Protocol · FastMCP · tunneling (ngrok) · dynamic pheromones and scent trails · collective swarm memory · Commit · Reveal · SHA-256 · Zero-Knowledge · Bayesian belief map · Manhattan distance · prompt engineering and LLM strategy · reinforcement learning (optional tool) · state machine · Orchestrator · Gatekeeper · Watchdog · Token Bucket · OAuth 2.0 · Gmail API · computational fairness · replay simulator

<!-- page vi -->

## Table of Contents

- A Personal Word — Before the Race Begins ..... iii
- Clarification: What Is Mandatory and What Is Merely Illustrative ..... iv
- General Guidelines for the Book and Its Structure ..... v

**1. Theoretical Framework and Problem Modeling** ..... 1
  - 1.1 Chapter Objectives ..... 1
  - 1.2 From Single Agent to Orchestration ..... 2
  - 1.3 The Formalism: Dec-POMDP ..... 4
  - 1.4 Uncertainty as a Resource ..... 6
  - 1.5 Chapter Summary ..... 7

**2. Distributed Network Architecture (P2P) and the FastMCP Infrastructure** ..... 8
  - 2.1 Chapter Objectives ..... 8
  - 2.2 The Paradigm Shift to Full Decentralization ..... 9
  - 2.3 The MCP Protocol and LLM Integration ..... 9
  - 2.4 Tunneling and Environment Separation ..... 13
  - 2.5 Chapter Summary ..... 16

**3. The Physics Mechanics, the Board, and the Scoring System** ..... 17
  - 3.1 Chapter Objectives ..... 17

<!-- page vii -->

  - 3.2 A Discrete Space and a Shared Physical Contract ..... 18
  - 3.3 Board Dimensions and Start Points ..... 18
  - 3.4 Movement, Barriers and Spatial Engineering ..... 21
  - 3.5 Win Conditions and Scoring ..... 22
  - 3.6 Chapter Summary ..... 23

**4. Dynamic Pheromone Trails and the Swarm's Collective Memory** ..... 24
  - 4.1 Chapter Objectives ..... 24
  - 4.2 Indirect Coordination Through Environmental Modification ..... 25
  - 4.3 Emission & Decay ..... 27
  - 4.4 Scent-Map Tactics ..... 29
  - 4.5 Chapter Summary ..... 31

**5. Cryptographic Security Protocol and Zero-Knowledge** ..... 32
  - 5.1 Chapter Objectives ..... 32
  - 5.2 The Temptation to Cheat ..... 33

<!-- page viii -->

  - 5.3 Commit-Reveal over SHA-256 ..... 34
  - 5.4 Mutual Audit and Log Integrity ..... 39
  - 5.5 Step-0 and Computational Fairness ..... 39
  - 5.6 Chapter Summary ..... 40

**6. The Strategy Module and Decision-Making** ..... 41
  - 6.1 Chapter Objectives ..... 41
  - 6.2 Why a Separate Strategy Module ..... 42
  - 6.3 Reinforcement Learning as One Optional Tool ..... 43
  - 6.4 Distance Heuristics and Belief Heatmap ..... 47
  - 6.5 LLM Integration for Prompt Engineering ..... 49
  - 6.6 Chapter Summary ..... 52

**7. User Interface (GUI) and the Replay Simulator** ..... 53
  - 7.1 Chapter Objectives ..... 53
  - 7.2 Two Axes: Live Monitoring vs. Retrospective Witness ..... 54
  - 7.3 The Live GUI: Heatmap and Turn Banner ..... 54
  - 7.4 The Replay Viewer and Integrity Enforcement ..... 56
  - 7.5 The Verification Engine: A Code Sketch ..... 57
  - 7.6 Chapter Summary ..... 59

**8. Designing the Agent Architecture and Deep Reliability Mechanisms** ..... 61
  - 8.1 Chapter Objectives ..... 61
  - 8.2 Separation of Concerns as a Meta-Principle ..... 61
  - 8.3 The Orchestrator Pattern and State Machine ..... 62
  - 8.4 Reliability Patterns: Deadline Tracker and Watchdog ..... 65
  - 8.5 Chapter Summary ..... 68

**9. The League, Computational Fairness and Reporting Automation** ..... 69
  - 9.1 Chapter Objectives ..... 69
  - 9.2 The League: From Lab to Arena ..... 69
  - 9.3 Gmail API Reporting Automation ..... 71
  - 9.4 GitHub Submission: Structure, Contents, Two Repositories ..... 79

<!-- page ix -->

  - 9.5 Chapter Summary ..... 81

**10. Recommended Development Priority Order and the Development Process** ..... 83
  - 10.1 Chapter Objectives ..... 83
  - 10.2 Why Build in Layers ..... 84
  - 10.3 The Seven Development Priorities (Seven PRD Files) ..... 85
  - 10.4 Milestones and Development Discipline ..... 89
  - 10.5 Chapter Summary ..... 90

**11. Summary and Look Ahead** ..... 91
  - 11.1 Chapter Objectives ..... 91
  - 11.2 The Arc of the Book: From Modeling Uncertainty to a Live League ..... 92
  - 11.3 Systems Development, Not a Coding Task ..... 93
  - 11.4 The Four Metrics of Success ..... 94
  - 11.5 Final Pre-Submission Checklist ..... 96
  - 11.6 Looking Forward: Toward Autonomous Distributed AI ..... 99

**References** ..... 100

**Appendix A: Gmail API and OAuth 2.0 Setup Guide** ..... 104
  - 1. The Five Setup Steps ..... 104
  - 2. Token Anatomy: Access vs. Refresh ..... 106
  - 3. Implementation: Minimal Send-Only Flow in Python ..... 107
  - 4. Required Files ..... 109

**Appendix B: Unified Configuration File Format** ..... 110
  - 1. Why a Shared Constitution? A Configuration File in a Refereeless World ..... 110

<!-- page x -->

  - 2. When JSON, When TOML, and Why ..... 111
  - 3. The Signed Shared File ..... 112
  - 4. The Private Per-Peer File ..... 114

**Appendix C: GitHub Submission Requirements and Academic Report** ..... 117
  - 1. The GitHub Repository: Structure, Branches and Tagging ..... 117
  - 2. The Academic Report: README.md ..... 118
  - 3. Submission Checklist ..... 120

**Appendix D: The Example Code Repository — A Basic Simulation Implementation** ..... 122
  - 1. What the Example Shows ..... 123
  - 2. Code Layout ..... 123
  - 3. How to Run ..... 124
  - 4. How You May Use It ..... 125

**Appendix E: Mapping of the Mandatory Rules — Do, Don't, and Recommendations** ..... 126
  - 1. Network Architecture, Decentralization and Local Epistemology ..... 126
  - 2. Spatial Mechanics, Physics and Board Constraints ..... 128
  - 3. Cryptography, Log Integrity and Zero-Knowledge ..... 129
  - 4. Strategy, Language and Public Network ..... 130
  - 5. League Fairness, Administrative Procedures and Competition Integrity ..... 131
  - 6. Additions Found When Cross-Checking the Book ..... 133

**Appendix F: The Mandatory Parameter Table** ..... 135
  - 1. Status Column Definitions ..... 139
  - 2. Mandatory Rules ..... 140
  - 3. Attached Files, Repo & Addresses Variables ..... 141

<!-- page xi -->

  - 4. LLM Modes for the Verbal Game ..... 142
  - 5. Strategy Module Selection ..... 143

<!-- page xii -->

## List of Figures

1. Partial Observability in [...] ..... 5
2. Symmetric P2P Structure ..... 14
3. The Discrete Arena ..... 20
4. The Scent Field Around the Agent ..... 28
5. Scent Decay Across Turns ..... 29
6. The Commit-Reveal Sequence [caption truncated in source] ..... 36
7. The Strategy Module Within [...] [caption truncated in source] ..... 43
8. Belief Map ..... 48
9. Mock-up of the Cop's Live Interface ..... 55
10. Verification Flow in the Replay Simulator ..... 57
11. The Game-Turn State Machine ..... 63
12. The Orchestrator as Central Gate ..... 66
13. The Token Bucket Pipeline [caption truncated in source] ..... 74

<!-- page xiii -->

14. Token Bucket Level Over Time ..... 75
15. Development Roadmap Spanning [...] [caption truncated in source] ..... 88

<!-- page xiv -->

## List of Tables

1. Division of Responsibility Among Agent Components and the Integration of Each Component ..... 11
2. Scoring Table: Win Conditions and Point Allocation ..... 22
3. Mapping of the Seven Stages (Seven PRD Files) to the Book's Chapters ..... 87
4. The Project's Success Metrics and Submission Criterion ..... 94
5. Files Required for the OAuth Infrastructure, Their Source and Sensitivity ..... 109
6. Submission Checklist ..... 120
7. Network Architecture, Decentralization and Local Epistemology ..... 126
8. Spatial Mechanics, Physics and Board Constraints ..... 128
9. Cryptography, Log Integrity and Zero-Knowledge ..... 129
10. Strategy, Language and Public Network ..... 130
11. League Fairness, Administrative Procedures and Competition Integrity ..... 131
12. Additions Found When Cross-Checking the Book ..... 133
13. Board Parameters, Coordinate System and Starting Positions ..... 136

<!-- page xv -->

14. Game Arena Parameters and Verbal Hints ..... 136
15. Movement and Barrier Parameters ..... 137
16. Dynamic Pheromone Parameters ..... 137
17. Scoring Parameters (Win, Survival, and Draw) ..... 138
18. Network and League Parameters ..... 138
19. Network, Rate-Limiter and Protection Parameters (the Gatekeeper Pattern) ..... 139
20. Variables for Attached Files, Code Repository and Instructor Addresses ..... 141
21. Language Model Modes for the Verbal Game (Private Choice per Peer) ..... 142
22. Strategy Module Selection Keys (Private Choice per Peer) ..... 143

<!-- page xvi -->

*(This page is intentionally blank in the source.)*

<!-- page 1 -->

# 1. Theoretical Framework and Problem Modeling

## 1.1 Chapter Objectives

By the end of this chapter you will know: why a distributed Cop–Robber race is not a single-agent planning problem but a multi-agent system orchestration problem; how to model a competitive environment under uncertainty using the Dec-POMDP formalism; and what the practical significance is of each component of the mathematical ordered tuple, from the state to the discount factor.

<!-- page 2 -->

## 1.2 From Single Agent to Orchestration

The field of Distributed Artificial Intelligence deals with a challenge in which multiple autonomous entities act in a shared space, where each entity has only partial information about the state of the world and about the intentions of its counterpart. What is the essential difference between training a single agent in a static environment and the project before you? In a static environment, the world patiently waits for the agent's decision. Here, by contrast, the world itself is a thinking adversary — the Robber plans, deceives, and changes the face of the board while the Cop tries to infer where it is.

The project therefore moves you from a focus on algorithms to a focus on systems. It is not enough for an agent to know how to choose a good move; it must orchestrate communication, lock in signatures, manage turns, and recover from failures (the orchestration and reliability architecture is laid out in Chapter 8) — all of this against a side that you neither trust nor control. This is the step up that the course has been leading toward: from lectures on a single agent and sub-agents, through the conversation between two agents over MCP, and on toward a full autonomous confrontation.

<!-- page 3 -->

### 1.2.1 A Sharp Distinction: Prompt Chaining vs. Multi-Agent Orchestration

To prevent architectural confusion, it is important to draw a sharp distinction between two practices that are easily mistaken for one another. Prompt Chaining is the routing of one model's output as input to the next model, in a fixed, predetermined linear sequence. Prompt chaining is not an orchestration mechanism: it has no dynamic division of labor, no bidirectional context-sharing, and no shared state management — it is merely a one-directional pipe. Multi-Agent Orchestration, by contrast, is the decentralized management of the division of labor, context-sharing, and maintenance of system state among agents operating in parallel — and this is exactly the model the project adopts. It is highly recommended to review a comprehensive survey of current orchestration frameworks and protocols [1].

> **Highly Recommended: Three Typical Failure Modes in the Absence of Orchestration**
>
> In the absence of a genuine orchestration layer, multi-agent systems tend toward three critical failure modes — it is highly recommended to know them in order to avoid them:
>
> 1. **Task Duplication** — two or more agents perform the same work, wasting computation and token budget on a duplicate result.
> 2. **Contradictory Outputs** — agents reach conflicting conclusions with no arbitration mechanism, leaving the system without a coherent decision.
> 3. **Convergence Failure and Infinite Loops** — the system does not converge on a solution but instead enters a mutual-response loop that never terminates.

<!-- page 4 -->

## 1.3 The Formalism: Dec-POMDP

The environment is formally modeled as a decentralized, partially observable game, known in the research literature as a **Dec-POMDP** (Decentralized Partially Observable Markov Decision Process) [2], [3]. This model extends the classical POMDP [4] to the case of multiple decentralized decision-makers, and provides a framework for decision-making under critical uncertainty. The problem is defined by the following mathematical ordered tuple:

> **The Ordered Tuple Defining the Game Space**
>
> ⟨n, S, {Ai}, P, R, {Ωi}, O, γ⟩

To translate this formal formulation into a precise working model, we will explicitly define each of its components.

> **Ordered Tuple (tuple)**
>
> An ordered tuple is an ordered collection of eight components, in which each component has a fixed role and position; here it fully defines the game space, from the number of agents to the discount factor.

The variables defining the game space are analyzed as follows:

- **n** - the number of agents. Here n = 2 (Cop and Robber). Practical meaning: every decision is weighed against a single, rational opponent, not against random nature.
- **S** - the state space: the complete picture of the world. It contains the exact coordinates of each agent on the grid, the layout of the static barriers, and the scent-trail grid that changes dynamically at every step. Practical meaning: the state is multi-dimensional, so an exhaustive scan of it (brute force) is not feasible — a fact that will drive the choice of algorithms in Chapter 6.
- **{Ai}** - the action space: what each agent is permitted to do. Composed of physical movement actions, construction actions (placing barriers), and communicative actions (passing hints in natural language, which may be false). Practical meaning: the action space involves both physics and psychology together.


<!-- page 5 -->

**P** — the transition function: how the world changes as a result of actions. P(s′ | s, a1, a2) defines the probability of reaching a new state given the jointly-taken actions.
Practical meaning: since there is no central server, both sides must agree on the same transition function — it is encoded in the shared configuration file.

**R** — the reward function: what pays off and what is penalized. It provides the algorithmic incentive for learning. Practical meaning: it is translated directly from the scoring table in Chapter 3.

**O, {Ωi}** — the observation space: what each agent actually perceives. The core of the uncertainty. No agent sees its opponent: both the Cop and the Robber each feed on the decaying scent trails of the opponent and on the opponent's verbal statements. Practical meaning: this is where each side's need for a probabilistic belief map (Belief) of the opponent's location is born.

**γ** — the discount factor (Discount Factor): how much the future matters relative to the present. γ ∈ [0, 1] sets the weight of a future reward versus an immediate one. Practical meaning: a high γ encourages strategic patience (for example, building a barrier trap over the course of many turns).

*[Figure: a two-panel diagram. Left panel, "True world state S (no central observer)," shows the true positions of the Robber (T) and the Cop (C) on the board together with the barriers. Right panel, "Cop observation Ωi (scent + hint)," shows the same scene as perceived by the Cop: a probability gradient legend running from 0.1 to 0.9 labeled "P(thief here)," together with a speech-bubble hint reading "I moved north."]*

**Figure 1:** The true world state S (left) is not accessible to any agent; each agent constructs its own observation Ωi (right) of the opponent's location, from a decaying scent map and a verbal hint — which may be false. The setup is symmetric: the Cop and the Robber are equally hidden from each other.

<!-- page 6 -->

**What the figure shows:** On the left, the full ground-truth state is shown — the positions of both agents and the barriers. On the right, the same scene is shown as one of the agents (here, the Cop) experiences it: not a sharp point, but a probability cloud. **How to interpret:** the lighter the shade, the higher the probability that the opponent occupies that cell. **Symmetry:** the picture is identical, mirrored, for the Robber, who builds, in exactly the same way, a probability cloud of the Cop's location — the whole setup is bilateral. **"What if" analysis:** if the verbal hint ("I moved north") contradicts the scent map, the receiving agent must lower its confidence coefficient and update its map — a topic taken up in Chapter 6.

## 1.4 Uncertainty as a Resource, Not Just an Obstacle

It is easy to perceive partial observation merely as a limitation. But note the deeper insight: the same uncertainty that hampers the Cop is also the Robber's weapon — and vice versa, since the setup is symmetric. The ability to send a false verbal hint, to manipulate the opponent, or to disappear behind a barrier — all of these are active exploitation of the observation function O. It is important to emphasize: the only channel of deception is the verbal hint. The scent, by contrast, is a natural phenomenon not subject to control — an agent cannot plant a misleading scent trail in a location where it is not present; all it can do is strengthen the scent in the cell where it itself is located, by staying there or returning to it, and this is a cost rather than an advantage, since it helps the opponent locate it. The project thus teaches you to think of information not as a fixed given but as a battlefield: whoever controls the flow of information controls the race.

> **Course Connection**
>
> The formalism here is not merely abstract. The Dec-POMDP ties together three threads from the course: the idea of agents and sub-agents in orchestrated work (Lecture L05), the conversation between two agents over MCP calling external tools (Lecture L09), and the distributed conception in which there is no central control and no agent sees the full picture (Lecture L11). The following chapters will break down each component of the ordered tuple into an actual code system.

<!-- page 7 -->

## 1.5 Chapter Summary

We modeled the race as a Dec-POMDP: two agents, a multi-dimensional state space, physical and communicative actions, and partial observation that lies at the heart of the uncertainty. We understood that the transition from a single agent to systemic orchestration is the main challenge, and that uncertainty is simultaneously an obstacle and a resource. In the next chapter we will dive into the infrastructure that allows the two agents to communicate without a referee — the P2P architecture over FastMCP.

<!-- page 8 -->

# 2 Distributed Network Architecture (P2P) and FastMCP Infrastructure

## 2.1 Chapter Goals

By the end of this chapter you will know: why full decentralization of state management (State Management) eliminates the need for a central referee and replaces it with cryptographic negotiation between peers; how the MCP protocol and the FastMCP infrastructure allow each agent to be a server and a client simultaneously; and why exposing the server to the public internet through tunneling (Tunneling), and complete separation of work environments, are not a recommendation but a necessary condition for the legitimacy of the architecture.

<!-- page 9 -->

## 2.2 The Paradigm Shift to Full Decentralization

In traditional game architectures, a game server (Game Server) sits at the center. It holds the ground truth (Ground Truth), adjudicates disputes, and updates the clients. But what happens when we remove the referee from the arena? The project before you does exactly that: it completes the paradigm shift toward full decentralization of state management. There is no longer a central authority whose word is law. Instead, the game runs over a peer-to-peer network (Peer-to-Peer, P2P for short), in which each agent holds only its own local truth. The two sides do not trust each other, and therefore every move is verified against the opponent by means of cryptographic negotiation. This is a fundamental shift from the centralized world to a distributed world, in which trust is not assumed as given but is built, step by step, out of signatures and verifications. The professional literature on distributed systems has long warned that removing a single point of control shifts the center of gravity from local computation to coordination among components — and this is exactly the challenge before you [5].

### 2.2.1 Why Not a Central Server?

A central server is a single point of failure (Single Point of Failure) and also a single point of trust: whoever holds it can, in principle, change the outcome of the game. Decentralization eliminates both weaknesses at once, but exacts a price — each agent must independently verify that the opponent has not cheated. This is where the communication protocol comes into the picture.

## 2.3 The MCP Protocol and LLM Integration

Communication between the agents relies on the Model Context Protocol (MCP) — an open standard that connects large language models (LLMs) to data sources and to external tools [6], [7]. In our implementation we will use a Python library called FastMCP [8], which simplifies building both the server and the client. The key architectural insight is one of symmetry: each agent is simultaneously a server (Server) — exposing tools (Tools), such as receiving a natural-language message — and also a client (Client) — calling the opponent's server to send data or run

<!-- page 10 -->

queries. There is no "strong" side and "weak" side here; the two peers are entirely equal in their role on the network.

> **Tool in MCP**
>
> A tool is a function that the server exposes outward, described in a structured schema so that the calling side (even a language model) can invoke it safely and remotely. In FastMCP, a function is marked as a tool by means of the `@mcp.tool` decorator (Decorator).

The MCP standard is the project's communication backbone for connecting agents to tools and to data sources; alongside it, complementary protocols are taking shape in the industry for managing the lifecycle of tasks and for secure federated communication, which are well worth becoming familiar with.

> **Highly Recommended: Complementary Communication Protocols — A2A and ACP**
>
> The MCP standard is the project's requirement for connecting agents to tools and to data, and it must not be replaced. Alongside it, it is highly recommended to become familiar with two complementary protocols:
>
> - **A2A** (Agent-to-Agent, Google) — for managing the full lifecycle of a task between agents, by passing structured states such as "submitted," "in progress," and "completed." Highly recommended for communication and for handing off tasks between the agents.
> - **ACP** (Agent Communication Protocol) — for advanced groups: federated communication in a zero-trust (Zero-Trust) configuration for multi-participant systems and for federations of swarms [9].

<!-- page 11 -->

### 2.3.1 Division of Responsibility Among Agent Components

The agent architecture breaks down into three components with distinct areas of responsibility. The local server manages resources and asynchronous communication; the client engine runs the game logic and calls the strategy model; and the language model provides the linguistic and psychological layer. The table below summarizes the division and the integration point of each component.

**Table 1: Division of responsibility among agent components and the integration point of each component**

| Component | Areas of Responsibility | Integration Point |
|---|---|---|
| Local FastMCP server | Resource management, exposing actions to the opponent, and asynchronous response processing | Use of decorators such as `@mcp.tool` to receive cryptographic signatures |
| Client Engine | Game logic, calling the strategy model, and turn scheduling | Connecting to the opponent's URL address and invoking its tools over the network |
| Language Model (LLM) | Producing natural-language hints, text decoding, and prompt engineering for the psychological game | Accessible via API: local (Ollama) or cloud (Claude, Gemini) |

An important distinction: the language model does not decide legal moves — it produces the rhetorical and deceptive layer of the game. The legal decision remains the responsibility of the client engine and cryptographic verification, and therefore a verbal hint is never trustworthy in itself. This rhetorical layer can be produced in four modes — from a free Python template (zero tokens, the default), through a local Ollama model, up to a cloud model or a CLI — as detailed in Chapter 6 and in the language-model-mode table in Appendix F.

### 2.3.2 A Minimal FastMCP Server

<!-- page 12 -->

The code below demonstrates the server skeleton: creating a FastMCP instance, exposing a single tool that receives a cryptographic signature from the opponent, and running the server. Note that the `@mcp.tool` decorator is all that is required to turn the `receive_move` function into an endpoint that the opponent can call remotely.

*Example: a minimal FastMCP server exposing a tool*

```python
from fastmcp import FastMCP

# Each agent runs its own server instance (local truth)
mcp = FastMCP("police_thief_peer")


@mcp.tool
def receive_move(signed_move: str, signature: str) -> dict:
    """Expose an action to the opponent over the network.

    The opponent (acting as a client) calls this tool to submit
    a cryptographically signed move. We verify the signature
    against the shared config before accepting the move.
    """
    is_valid = verify_signature(signed_move, signature)
    # Return an acknowledgement; never trust an unverified move
    return {"accepted": is_valid, "move": signed_move if
    is_valid else None}


if __name__ == "__main__":
    # Bind the server so a tunnel can expose it publicly
    mcp.run(transport="http", host="0.0.0.0", port=8000)
```

A complete, running implementation of the FastMCP server and client, alongside the full game loop, is available in the sample code repository in Appendix D.

<!-- page 13 -->

> **Course Connection**
>
> This architecture is the direct extension of Lecture L09 in the "Orchestration of AI Agents" course and of Exercise ex06, in which two AI agents conversed with each other over the MCP protocol and called external tools (e.g., the Gmail/Google API). There you learned that an agent can be both a server and a client, and you exercised external tool calls; here we turn the friendly conversation into a full competitive confrontation, in which every "statement" by the opponent must be verified. If in ex06 the goal was conversation-based cooperation, in this project the goal is to defeat an opponent who does not trust you — and whom you do not trust.

## 2.4 Tunneling and Environment Separation

For the agents to operate as independent entities against other groups across the internet — in the live league discussed in Chapter 9 — running the servers on `localhost` is permitted, but only during the early coding stages. In practice, each group must expose its FastMCP server to the public internet using a tunneling tool, such as ngrok [10] or Localtonet.

<!-- page 14 -->

### 2.4.1 Why Is Tunneling Needed? NAT Traversal

Most computers sit behind a firewall and behind network address translation (NAT), and are therefore not directly accessible from the internet. The tunneling tool generates a public URL address that bypasses the firewall and performs NAT traversal (NAT Traversal) — a fundamental problem in peer-to-peer communication, which protocols such as STUN are designed to solve by discovering the public address of a private host [11]. The practical result: the opponent, anywhere in the world, can connect remotely to your server through that same public address.

*[Figure: a diagram of two mirrored agents, Agent A and Agent B, each containing a Server component (exposing `@mcp.tool`) and a Client component. A bidirectional arrow in the middle, labeled "A calls B" / "B calls A," crosses the public internet / NAT traversal. Each agent's Server connects outward through its own Tunnel to its own public URL.]*

**Figure 2:** Symmetric P2P structure: each agent is both a server (exposing an `@mcp.tool` tool) and a client (calling the opponent's tool), and the two sides are connected through public URL addresses created by tunneling over the internet.

**What the figure shows:** two agents identical in structure, Agent A and Agent B, each of which has a server component and a client component, and each of which is exposed to the internet through a separate tunnel. **How to interpret:** the bidirectional arrow in the middle represents the public channel crossing the NAT; the curved arrows show how the client on one side calls the tool on the other side's server — full symmetry, with no central server between them. **"What if" analysis:** if one of the tunnels goes down, the opposing side will lose the ability to verify moves and will reach a "deadlock" in turn scheduling — and therefore the resilience of the tunnel is an inseparable part of the resilience of the game itself.

<!-- page 15 -->

### 2.4.2 Complete Separation of Work Environments

Beyond tunneling, the architecture requires complete separation of work environments. It is important to distinguish between two stages: during the league game itself, the two teams are already inherently separate — each runs on a different computer, in a different place — and so separation at this stage is guaranteed on its own. The separation discipline described here matters precisely at the local development stage, when one team builds both the Cop and the Robber on the same machine; there, the risk of accidental overlap (shared memory or shared variables) is real, and it can mislead development and produce behavior that will not be reproduced at all in the league. Therefore the Cop's code and the Robber's code must run in two completely separate processes, under separate configuration directories — for example, `config/thief/` versus `config/police/` (the structure of the configuration file is detailed in Appendix B; and, in accordance with this separation, the submission itself is made as two separate repositories — Cop and Robber — as detailed in Appendix C). Any attempt to share memory or read shared variables is not merely a technical bug; it is a violation of the very rules of decentralization, since it creates a "back door" through which one agent could see the local truth of its opponent.

> **Mandatory Separation Rule**
>
> The Cop's code and the Robber's code must run in two completely separate processes, under separate configuration directories (`config/thief/` versus `config/police/`). It is strictly forbidden to share memory, import a shared module holding live state, or read shared variables between the two sides. Such sharing grants one side access to the other's "local truth," breaks the architecture's zero-trust (Zero-Trust) model, and disqualifies the solution — even if the game "works" technically.

<!-- page 16 -->

## 2.5 Chapter Summary

We saw that the project completes the decentralization of state management: there is no central server, and in its place a P2P network in which each peer holds a local truth and verifies moves cryptographically. The MCP protocol, implemented via FastMCP, turns every agent into a server and a client simultaneously, while the language model adds the psychological layer. Exposing the server through tunneling solves NAT traversal, and separating processes and configuration preserves the integrity of the zero-trust model. In the next chapter we will move from the communication infrastructure to the trust layer itself — the cryptographic mechanisms that allow verifying the move of an opponent whom we do not trust.

<!-- page 17 -->

# 3 Physics Mechanics, the Board, and the Scoring System

## 3.1 Chapter Goals

By the end of this chapter you will know: how a discrete geometric space and a simple rule set define a complete confrontation arena; why increasing [board size] (relative to earlier versions sized 5 × 5) inflates the state space exponentially and thwarts exhaustive search; how the Cop's barrier-placement advantage turns it into an architect of space; and how a compact scoring table translates victory into a reward signal that a strategy — heuristic, your own dedicated algorithm, or, optionally, reinforcement learning — can maximize.

<!-- page 18 -->

## 3.2 A Discrete Space and a Shared Contract

Unlike continuous physical simulations, the game takes place in a discrete geometric space: a finite grid of cells in which every location, every move, and every blockage can be counted precisely. But where do the laws of physics come from when there is no central server to enforce them? Here lies the project's fundamental design decision: there is no external judge (no external judge). The laws of physics are enforced by the agents themselves, each in its turn, according to a mutually agreed configuration file — `config/game.json` — shared identically by both sides. This file is the game's contract: board dimensions, starting points, the barrier quota, and scoring thresholds are encoded in it as hard-coded values. Since both agents load exactly the same file, both compute the same transition function and the same decision conditions — thereby avoiding any dispute about "what is legal" before it even begins. The complete structure of the file is detailed in Appendix B.

> **The Contract Is Set by Negotiation**
>
> The game contract is not dictated from above but is set by negotiation between each pair of teams, and may therefore vary from pair to pair. A necessary condition is that the contract be mutually agreed upon by both sides. However, it must not weaken or dilute the provisions defined in this book: the agreed contract is a floor, not a ceiling. On the other hand, the teams are permitted to upgrade the rules, and it is even wise to do so — it is permitted, and even advisable, to legally exploit any loophole not defined here, for the benefit of both sides or for competitive advantage — as long as everything is legal and agreed upon between the sides.

## 3.3 Board Dimensions and Start Points

The default board is a grid of size [board size] (default 7 × 7) cells. This enlargement, relative to earlier versions that used 5 × 5, is not cosmetic: it exponentially increases the number of possible state combinations. The state space of the Dec-POMDP (see Chapter 1) grows as a product of the two agents' locations and of all possible barrier layouts; doubling the board's side

<!-- page 19 -->

multiplies the number of cells by four, and the state space by orders of magnitude. The practical result is that exhaustive search (Brute Force) of all states becomes computationally infeasible — a difficulty that is fundamental to problems in the Dec-POMDP complexity class [2] — hence the sides are forced to turn to learning and heuristics instead of enumerating all states.

**Coordinate system.** Each cell is represented as a pair (row, col). Two agreed-upon parameters determine how to read this pair: [coordinate system origin] — the corner in which cell (0,0) sits, by default the top-left corner (the vertical axis grows downward); and [axis starting index] — the number at which the counting of each axis begins, by default 0 (zero-indexed). Both parameters are subject to negotiation, but must be identical between the sides: teams that prefer 1-indexing or a different origin corner may agree to do so, but if one side counts from 0 and the other from 1, [3,3] for the one will not be [3,3] for the other, and the race will fall apart. In this book — and as the default of the reference implementation — the origin is top-left and counting starts at 0; hence the center of a 7 × 7 board is [3,3] and the corner is [0,0].

The starting points are not random but strategic, and are not fixed in advance: they are set during the negotiation stage between the two teams, and any legal layout agreed upon by the sides is permitted. The layout in which the Robber (THIEF) stands at the center of the board and the Cop (COP) is in the corner is merely one example: the Robber at the center enjoys a maximal number of escape routes in every direction, while the Cop is placed at a defined strategic distance. These positions are documented in [starting position – Robber] and [starting position – Cop] (for example, [3,3] for the Robber and [0,0] for the Cop, zero-indexed), loaded from the `config/game.json` file, and their exact values are collected in the parameter table in Appendix F. This makes it possible to change the initial balance of power, as agreed between the sides, without touching the agents' code.

<!-- page 20 -->

*[Figure: a 7 × 7 discrete arena, rows and columns indexed 0–6. The Cop (C) sits at [0,0]; the Robber (T) sits at [3,3]; barrier cells (B) appear along one edge of the grid. A legend notes: "legal move: 1 cell (up/down/left/right) or stay," illustrated by an orange marker with arrows to the four adjacent cells.]*

**Figure 3:** A board of size [board size] (in the example, 7 × 7, zero-indexed): in the example layout the Robber (T) stands at the center [3,3], the Cop (C) in the corner [0,0], and a number of barriers (B) placed by the Cop seal off cells. The orange arrow illustrates the set of legal moves — one cell in each of the four orthogonal directions, or staying in place.

**What the figure shows:** a grid of 49 cells, the two agents at their starting positions, one chain of barriers that has begun to close, and an orange star from which four arrows extend to the adjacent cells. **How to interpret:** the arrows define exactly which transitions are legal from each cell — north, south, east, west, or staying; there are no diagonals. The barriers (B) are black cells that no one can cross. **"What if" analysis:** had the board been 5 × 5, the Robber's center and the Cop's corner would have been

<!-- page 21 -->

only a few steps apart, and the chase would have been decided almost immediately; it is precisely the expansion to the current [board size] that creates the space needed for a long chase, for learning, and for maneuvering.

## 3.4 Movement, Barriers, and Spatial Engineering

On each turn an agent may perform a single move: moving one cell in one of the four orthogonal directions (up, down, left, right), or choosing to stay in place. Diagonal movement is forbidden. This simple constraint is what gives the chase its grid-like character, and links it directly to the family of "cops and robbers" problems and to the pursuit-evasion variant on graphs studied in graph-theory mathematics [12], [13]. The Cop has an asymmetric advantage in spatial engineering: on a turn in which it forgoes movement, it may place a physical barrier in any cell one step away from it — the cell it is standing on itself, or one of the four orthogonally adjacent cells. This ability turns it from a passive pursuer into an architect of the arena.

> **The Barrier Rule**
>
> On a turn in which the Cop forgoes movement, it may place a barrier in any cell one step away from it — the cell on which it stands, or one of the four orthogonally adjacent cells — and that cell becomes impassable for both players until the end of the game. A barrier is irreversible: a cell that has been blocked remains blocked. **A trapping placement:** if the Cop places a barrier on the cell on which the Robber currently stands, the Robber is captured. Similarly, a Robber that is trapped with no legal move whatsoever (all adjacent cells blocked by barriers and/or by the edges of the board) is likewise considered captured. **Duty of declaration:** the Cop must truthfully declare every barrier placement and its exact location; a barrier must not be placed covertly, and the Cop must not lie about its location. The Cop's maximum barrier quota is [barrier quota], and therefore every placement is a resource-management decision: the Cop must "squeeze" the Robber into a corner without accidentally blocking its own access routes.

[Barrier quota] is at the heart of the Cop's strategic challenge. A barrier placed greedily can trap the Cop itself behind a wall it built, or open a new escape gap for the Robber. Managing this resource — when to block, where, and how many barriers

<!-- page 22 -->

to save for the closing stage — is a strategic problem in its own right, discussed at length in Chapter 6.

> **Iron Rules: Movement and Truth Declaration**
>
> **No diagonals.** A diagonal move is not legal; an attempt to make one is rejected by the opposing agent enforcing the physics. **Duty of truth in capture.** When the Cop declares a Capture Claim, the Robber is under a cryptographic obligation to respond truthfully (the Capture protocol). An attempt to lie at this stage will inevitably be exposed at the log-audit stage and will result in absolute systemic disqualification. **Open barrier declaration.** The Cop must truthfully declare every barrier placement and its exact location; a barrier must not be placed covertly, and it is forbidden to lie about its location. A complete mapping of all binding game rules — dos, don'ts, and recommendations — is collected in Appendix E.

## 3.5 Win Conditions and Scoring

The scoring system balances two opposing tensions: the Cop's difficulty in locating a hidden player, versus the Robber's difficulty in surviving in a hostile environment that is progressively closing in. Instead of a binary victory, every end-of-game scenario awards each side a different score, thereby encoding the value of each outcome — a translation from which the reward function R of the previous chapter is derived directly.

**Table 2: The Scoring Table — Decision Conditions and Point Allocation**

| End Event | Decision Condition | Cop Score | Robber Score |
|---|---|---|---|
| Successful capture | The Cop lands on the Robber's cell and declares a Capture Claim | [capture score – Cop] | [capture score – Robber] |
| Prolonged survival | The Robber survives [survival threshold] valid steps without capture | [survival score – Cop] | [survival score – Robber] |
| Technical loss | A side crashes, exceeds the time limit, or performs a cryptographic forgery | 0 | 0 |

Note the broken symmetry in the table. Capture

<!-- page 23 -->

awards the Cop the highest reward ([capture score – Cop]), embodying its primary goal; but prolonged survival — patience over time, [survival threshold] valid steps without capture — awards the Robber its own highest reward ([survival score – Robber]). The technical loss zeroes out both sides equally, thereby incentivizing both to maintain protocol integrity rather than to win "on a technicality."

Upon a capture declaration, as noted, the Robber is under a cryptographic obligation to respond truthfully. A capture declaration is not, therefore, a matter of trust between rivals but a proof that can be verified after the fact: every response is signed and logged, and any attempt to deny the true state will be exposed at the log-audit stage and lead to disqualification. Thus scoring itself turns from a declaration in the opponent's hands into a mathematically enforceable fact.

> **Course Connection**
>
> These simple rules — a finite grid, a single orthogonal move, a known barrier quota, and an unambiguous reward signal (the scoring table) — define a distributed, finite game in which two agents coordinate their actions without a central server and without a referee. This is exactly the space discussed in the "Orchestration of AI Agents" course: in Lecture L09 we saw two agents conversing over MCP and calling external tools, and in Lecture L11 we saw a distributed swarm of agents coordinating itself without central control. The question of how to convert the scoring table into a game strategy — by means of heuristics, your own dedicated algorithm, or, as just one option, reinforcement learning — we open in Chapter 6.

## 3.6 Chapter Summary

We defined the physical arena of the chase: a discrete space of [board size] cells, in which the laws of physics are enforced by the agents themselves according to a shared configuration contract set by negotiation between the sides. We saw that the expansion from the earlier 5 × 5 grid exponentially inflates the state space and thwarts exhaustive search, that [barrier quota] turns the Cop into an architect of space under a resource-management constraint, and that an asymmetric scoring table translates every end scenario into a maximizable reward signal. In the next chapter we move from the static rules to the dynamic strategies that the agents deploy to win in this arena.

<!-- page 24 -->

# 4 Dynamic Pheromone Trails and the Swarm's Collective Memory

## 4.1 Chapter Goals

By the end of this chapter you will know how a simple biological mechanism — the dispersal of scent trails and their decay — solves, at least partially, the partial-observation problem presented in Chapter 1. You will understand what stigmergy (Stigmergy) is and why it constitutes an indirect coordination mechanism between agents; you will master the mathematical model of the emission and decay of scent intensity in each cell; and you will see how each agent leverages the historical scent map of its opponent to expose false verbal hints and to maintain a probabilistic belief map.


<!-- page 41 -->

## 4.2 Indirect Coordination through Environment Change (*Indirect Coordination*)

How do millions of ants coordinate among themselves without a central commander, without language, and without shared memory? The answer, discovered by animal-behavior researchers, lies not in the ants themselves but in the environment. Each ant leaves behind trails of pheromones, and every other ant responds to them. The environment itself becomes the shared dashboard — a mechanism known as **Stigmergy**, indirect coordination through environmental modification [14], [15]. This principle, which underlies the famous ant-colony algorithm [16], is exactly the tool we will harness here to attack uncertainty.

One of the central contributions to solving the partial-observability problem in our project is, therefore, the scent-trail mechanism — a mechanism directly inspired by ant behavior. The idea is as simple as it is powerful, and it is fully symmetric: when an agent moves on the board — the Robber and the Cop alike — it scatters virtual pheromones behind it that decay with time. No agent perceives this as deliberate communication; but its opponent, who reads the environment, turns this physical trail into a valuable source of information. The scent is natural and uncontrollable: it is emitted simply by the act of movement or of staying in place, and no one can plant a misleading trail — each side emits only its own scent, and each side reads only its opponent's scent field.

<!-- page 42 -->

### 4.2.1 What Lecture L11 Teaches: Dynamic Pheromones and Swarm Memory

The mechanism described here is exactly what is taught in Lecture L11 of the *Orchestration of AI Agents* course. Instead of central control, the swarm of agents coordinates itself through dynamic pheromone trails that encode the contextual effectiveness of each action: a successful action updates the swarm's shared representation (the *embedding*), thereby raising the probability of choosing successful paths in subsequent rounds — this is a collective memory inscribed in the environment rather than in the head of a single agent. Alongside this operates a decay/fading mechanism that prevents fixation: without it, the swarm would lock onto a local optimum, since old trails would accumulate forever and paralyze any exploration of new paths. The scent field and the decay rule we will define shortly are the direct translation of this idea into the Cop-and-Robber arena.

> **Connection to the Course**
>
> In Lecture L11 of the *Orchestration of AI Agents* course we saw a swarm of agents coordinating itself without central control, by means of dynamic pheromone trails and collective swarm memory (in the style of SwarmSys): successes update a shared representation, and a decay mechanism prevents getting stuck at a local optimum. The scent-trail mechanism in this project is the direct application of that same idea — indirect, asynchronous coordination, in which a message is sent to no one but is inscribed in the shared environment and waits there for whoever knows how to read it. Understanding this pole, alongside the direct coordination we saw in earlier lectures, is essential for anyone designing systems of autonomous agents.

<!-- page 43 -->

## 4.3 Emission & Decay Model (*Emission & Decay*)

Each time an agent moves or remains in place, a scent field of size [ scent field size ] (e.g. 5×5) is created around its location. At the emission center — the cell where the agent is located — the scent intensity is set to [ peak scent intensity ]. The farther one moves from the center, the more the intensity drops off according to a radial distribution: cells close to the center absorb high intensity, while cells at the edge of the scent field absorb only a faint residue. This produces a concentrated scent footprint, marking the agent's surroundings rather than a single isolated point. This holds for both sides alike — both the Cop and the Robber leave their own scent field.

At the end of every full turn — that is, once both the Cop and the Robber have completed their moves — all scent trails currently on the board undergo a system-wide decay process. The decay rate is [ scent decay rate ] per turn. The mathematical update of the scent intensity in cell (i, j) is given by the following formula:

**Scent-intensity update in a cell**

$$\tau_{ij}(t+1) = \max\bigl(0,\ (1-\rho)\cdot\tau_{ij}(t) + \Delta\tau_{ij}\bigr)$$

The variables making up the formula are as follows:

- **τij(t)** — the scent intensity in the cell at the current time. A continuous value in the range [0, 0.9] expressing how "fresh" the trail in cell (i, j) is. Practical meaning: this is effectively a local certainty score — a high value suggests that the agent whose field we are reading passed through here recently.
- **ρ** — the decay rate (*Decay Rate*). Here ρ = 0.10. The factor (1 − ρ) shrinks the existing scent every turn to 90% of its value. Practical meaning: this slow decay is a deliberate design choice — it leaves a historical trail long enough to be tactically useful, yet not eternal.
- **Δτij** — the new emission. The intensity added to the cell on the current turn, determined by the cell's radial proximity to the agent's emission center (and at the center itself Δτ = 0.9). If the agent is far away, Δτij = 0. Practical meaning: this is the component that connects the agent's presence to the environment — it "writes" onto the board.
- **max(0, ·)** — clipping to zero. Ensures the scent intensity is never negative.

<!-- page 44 -->

Practical meaning: a cell that has never absorbed scent, or that has fully decayed, is simply "silent" — an absence of information, not negative information.

The formula embodies a fine tension between two forces: the component (1 − ρ)·τij(t) is forgetting — the gradual erasure of the past; and the component Δτij is memory — the inscription of the present. The equilibrium between them determines how deep into the past each agent can look at its opponent's trail.

**Figure 4** *(5×5 scent-emission field, centre τ = 0.9)*: a heatmap showing scent intensity radiating outward from the center. Center value τ = 0.90; the four values at radial distance 1 are 0.62; the four diagonal-adjacent values are 0.42; the mid-edge values are 0.20; and the corner values are 0.04–0.14, decaying smoothly outward in all directions.

Figure 4: The emission field of size [ scent field size ] around the agent (Robber or Cop): at the center τ = 0.9, and the intensity decays radially with distance from the center.

What the figure shows: a 5×5 matrix of cells, where the central cell — the emitting agent's location — is colored brightest and carries the value 0.90, and the surrounding cells darken as they move farther away. How to interpret it: brightness represents the scent intensity τ; the radial falloff means the scent is not a uniform "blob" but a smooth hill whose peak sits at the center. A cell in the corner of the square receives only a negligible residue, so the Cop will assign it low certainty. "What if" analysis: had the emission been point-like (a single cell at intensity 0.9 with zeros around it), a small amount of measurement noise would have erased the entire signal; the radial distribution grants the mechanism robustness, since even if the exact cell is missed, its neighbors still indicate the direction.

<!-- page 45 -->

## 4.4 Tactical Use of the Scent Map (*Scent-Map Tactics*)

Because the scent decays slowly, it leaves behind a historical "scent trail" (*Scent Trail*) — not a snapshot, but a short film of the agent's movement over the last few turns. Each agent can sample the board and obtain its opponent's scent map. This is where the qualitative leap occurs: cross-referencing this map against that same opponent's verbal statements enables **belief modeling** (*Belief Modeling*) — the ability to maintain a probability distribution over the opponent's true location [17]. The symmetry is complete: the Cop reads the Robber's trail, and the Robber reads the Cop's trail — each side cross-references its opponent's scent map against the verbal hints that opponent provides.

The following figure illustrates why such a trail survives long enough to be useful.

**Figure 5** *(Scent intensity over turns, ρ = 0.10)*: two curves plotted against "full turns t (Cop + Thief)" on the x-axis and "scent intensity τij" on the y-axis, with a dashed reference line marking "half of peak." The curve labeled "thief leaves, single deposit, then decay (trail)" decays exponentially from the peak. The curve labeled "re-emission (thief present, turns 1–8)" stays near peak while the agent remains present, then decays once the agent departs.

Figure 5: Evolution of the scent intensity τij over turns for ρ = 0.10: a single emission followed by pure decay (the trail), versus repeated emission while the agent remains in place.

<!-- page 46 -->

What the figure shows: two curves. One ("single emission") decreases exponentially from 0.9 — this is a cell the agent passed through once and then left behind. The other ("repeated emission") stays high as long as the agent remains in the vicinity (turns 1–8), and only after it departs does it begin to decay. How to interpret it: the dashed middle line marks half of the peak intensity; one can see that the single trail crosses it only around the seventh turn — meaning the scent stays "readable" for roughly six to seven turns. "What if" analysis: had we doubled ρ to 0.20, the curve would have plunged much faster, the trail would have shortened, and the pursuing opponent would have lost the memory of the past; had we shrunk ρ to nearly zero, the board would have filled with everlasting scent and lost its ability to distinguish old from new.

> **Lie Detection: the Robber "Moved North" While the Scent Is in the Southeast**
>
> Suppose the Cop samples the board and obtains the following scent map, concentrated in the southeastern corner:
> - Southeastern cell (1, 4): τ = 0.81 (a very fresh trail).
> - Adjacent cell (1, 3): τ = 0.63.
> - All cells in the north of the board, e.g. (5, 2): τ = 0.00 — completely devoid of scent.
>
> Now the Robber's verbal statement arrives: "I moved north." Let us examine the claim quantitatively. Had the Robber actually moved north on the last turn, we would expect to find in the north a fresh trace of intensity roughly (1 − ρ)·0.9 = 0.9·0.9 ≈ 0.81. Instead we measure τ = 0.00 in the north. The gap between the expected value (≈0.81) and the measured value (0.00) is absolute: there is no scent residue whatsoever to support the claim, while the entire scent mass is concentrated at the opposite pole of the board.
>
> The Cop therefore concludes, with high confidence, that the Robber is lying. It lowers the trust coefficient it assigns to verbal statements, updates its probability matrix so that heavy weight is placed on the southeastern cells, and redirects its pursuit vector — not toward the declared north, but toward the true source of the scent. Thus the Robber's manipulation becomes a double-edged sword: the very attempt to deceive, once hidden within the environment's testimony, betrays its own location.
>
> It is important to emphasize: the scent map cannot lie — it is emitted by the very act of movement and cannot be forged. What is exposed here is a false *verbal* hint, caught precisely because the trustworthy environment contradicted it — not a "false trail" (no such thing exists). And the symmetry is complete: this same procedure is available to the Robber, who cross-references the Cop's scent trail against the hints the Cop provides — each side protects itself by verifying its opponent's words against the unforgeable evidence that opponent left in the environment.

<!-- page 47 -->

The full probability-matrix update — exactly how each agent translates its opponent's scent map and statement into a numerical belief map, and how it combines the two pieces of evidence under the Bayesian rule — will be detailed in Chapter 6, where we will build the belief mechanism (*Belief*) on the foundations laid in the current chapter; this belief map is displayed visually as a heatmap in the live interface (Chapter 7).

### 4.5 Chapter Summary

We saw how a biological principle — the stigmergy of ants — is translated into an applied mechanism that eases the partial-observability problem. We defined the emission model of size [ scent field size ] with [ peak scent intensity ] and a radial distribution, and the decay rule τij(t+1) = max(0, (1−ρ)τij(t)+Δτij) with ρ = 0.10. We emphasized that the mechanism is symmetric — both agents emit scent, and each reads its opponent's trail — and that the scent is natural and unforgeable. We showed that this slow decay produces a historical trail of about six turns, and that cross-referencing it against the opponent's verbal statements lets each agent expose false hints. In the next chapter we move from the trail each agent leaves in the environment to the channel in which it speaks explicitly — and examine how the verbal communication itself is built, and how dubious its reliability is.

> **Cryptographic Locking of the Emission-and-Decay Model Before a Series**
>
> Before a series begins, the two groups must exchange the complete emission-and-decay model between them — including a concrete numerical example (e.g., a cell at the center receives τ = 0.9, and after one turn of decay at rate ρ, one obtains 0.9·(1 − ρ)). Both sides must verify that they interpret exactly the same formula in exactly the same way, and only afterward lock in the agreement cryptographically — for example, via a SHA-256 hash of the agreed formula together with the numerical example. This way, any future deviation in the mechanism's behavior will be detected immediately. It is permitted, and even recommended, for one group to supply the other with the code of the shared scent mechanism itself, so as to ensure both sides run exactly the same behavior — leaving no room for interpretation that could compromise the fairness of the series.

<!-- page 48 -->

# 5 Cryptographic Security Protocol and Zero-Knowledge

## 5.1 Chapter Goals

By the end of this chapter you will know: why a peer-to-peer network with no objective game master suffers from a built-in temptation to cheat; how a Commit-Reveal mechanism based on hash functions (*Hash*) makes cheating practically impossible; how mutual auditing of the game logs reveals any forgery after the fact; and how a signed hardware declaration at "Step-0" ensures computational fairness between competitors with radically different machines.

<!-- page 49 -->

## 5.2 The Temptation to Cheat in a Judge-less Network (*The Temptation to Cheat*)

Imagine a game of chess with no shared physical board and no referee overseeing the rules; each player maintains a private copy of the board and reports their moves to the other. In a distributed system of this kind — a peer-to-peer (P2P) network in which the two agents speak directly to each other over a FastMCP server, with no objective game master — a built-in temptation to cheat is born. Three types of fraud threaten the integrity of the match: time travel — altering a move that has already been made; changing a move after the opponent's move has already been revealed; and disavowing a previous location or statement. As long as each side is both the player and its own record-keeper, nothing prevents it from rewriting history in its own favor.

The solution is not legal but mathematical. Instead of relying on trust, the system rests on a Commit-Reveal mechanism based on cryptographic hash functions. The underlying idea, known in the literature as "coin flipping over the telephone" [18], is this: each side is required to commit to its decision while it is still sealed and hidden, and only after the opponent has locked in its own commitment is the decision revealed. This prevents the possibility of changing a choice after the fact, since such a change would break the cryptographic signature already transmitted.

> **Connection to the Course**
>
> In the course *Orchestration of AI Agents*, in Lecture L09, you saw how two AI agents converse with each other over MCP and call external tools — two independent processes exchanging messages directly, with no central supervisory component overseeing them. This chapter adds to that same architecture of tool calls between agent and agent the integrity layer: when there is no trusted central server dictating a single truth, the need to verify the integrity of distributed communication must stem from the cryptography itself. This is the principle distinguishing a fragile distributed system from a reliable one.

<!-- page 50 -->

## 5.3 The Commit-Reveal Mechanism over SHA-256 (*Commit-Reveal over SHA-256*)

At every game step, each agent performs four mandatory cryptographic stages, in order. These stages turn every move into a binding event that cannot be denied or altered after the fact.

**Nonce — a One-Time Number**

A **Nonce** (short for *Number used once*) is a unique random string generated afresh for every commitment. Its role is twofold: first, it ensures that even if an agent repeats the exact same action, the resulting hash will differ every time. Second, it thwarts a dictionary attack (*Dictionary Attack*) — an attempt by the opponent to guess the sealed content by pre-hashing all plausible possibilities. Without the Nonce, the small move space would allow any commitment to be cracked in a fraction of a second.

### 5.3.1 Step 1 — Commit

The agent chooses its physical move and the hint it will send (including an *Intent* flag indicating whether the hint is true or false), and generates a unique Nonce. The four data components are concatenated together and encoded into a single cryptographic hash. The agent transmits, via the FastMCP server, only the signature Hcommit — not its content.

**The Cryptographic Commitment Signature**

$$H_{commit} = SHA256(State \parallel Move \parallel Intent \parallel Nonce)$$

The symbol ‖ is the concatenation operator (*Concatenation*): it glues the byte representations of the components to one another into a single continuous string, before the hash function is applied. It is not a numeric addition but a joining of byte sequences. In the reference implementation, the concatenation is performed via canonical serialization to JSON (sorted keys and fixed separators), so that both peers hash byte-identical input; the record actually signed is richer than the four fields shown here, and also includes the verbal hint, the intent classification, the step number, and the role. The formula's variables are analyzed as follows:

<!-- page 51 -->

- **Hcommit** — the commitment signature. A 256-bit string obtained from the SHA-256 function [19]. Practical meaning: this is the "fingerprint" of the move; it is sent to the opponent but reveals nothing about its content.
- **State** — the board state. The state snapshot on which the move is based, pinning the commitment to a specific game step. Practical meaning: prevents reuse of an old commitment in a new context.
- **Move** — the physical action. The chosen move (movement, placing a barrier, etc.). Practical meaning: this is the core piece meant to be locked against change.
- **Intent** — the intent flag. A value indicating whether the accompanying verbal hint is true or deceptive (a lie). Practical meaning: forces the agent to declare its honesty in advance, so it cannot later claim it lied "on purpose."
- **Nonce** — a one-time number. A cryptographically random string. Practical meaning: ensures the uniqueness of the hash and thwarts a dictionary attack, as explained in the definition above.

### 5.3.2 Steps 2–4 — Acknowledge, Reveal, Audit

After the commitment, the protocol continues through three additional stages:

- **Acknowledge.** The opponent confirms it has received the commitment and is locked onto it. This acknowledgment prevents the sender from backing out of its commitment, while also ensuring that revelation will occur only once both sides have already fixed their moves.
- **Reveal.** The agent sends the opponent the action (*Move*) and the verbal statement. The Nonce stays hidden at this stage, to prevent premature reverse-engineering of the signatures.
- **Final Audit (*Audit / Final Reveal*).** Only at the very end of the game are all the Nonce values revealed, for the purpose of a full mutual audit.

<!-- page 52 -->

**Figure 6** — Message sequence between Cop and Thief:

| Step | Cop → Thief | Thief → Cop |
|---|---|---|
| 1 | Commit: Hcommit only | Commit: Hcommit only |
| 2 | Acknowledge (locked) | Acknowledge (locked) |
| 3 | Reveal: Move + Hint (Nonce hidden) | Reveal: Move + Hint |
| 4 | Final Reveal: all Nonces (end of game) | Final Reveal: all Nonces |

Figure 6: The sequence of message exchanges between the Cop and the Robber across the four stages Commit→Acknowledge→Reveal→Audit. Note that the Nonce is revealed only at the final audit stage, at the end of the game.

What the figure shows: two vertical lifelines (Cop on the left, Thief on the right) and horizontal arrows describing the order of messages from top to bottom. First the sealed commitment passes, then the locking acknowledgment, then the mutual revelation of the moves, and finally — at the end of the game — the revelation of all the Nonces. How to interpret it: the time separation between commitment and revelation is the cryptographic heart of the mechanism; once Hcommit is sent, the move is mathematically locked even though its content is not yet known. "What if" analysis: if an agent attempts to reveal, at step 3, a move that does not match the commitment it sent at step 1, the hash recomputed at the audit stage will not match the original Hcommit — and the cheating will be unambiguously exposed.

The code below illustrates both ends of the mechanism: `commit()`, which creates the signature, and `verify()`, which reconstructs it and compares. Note the use of the `secrets` module to generate a cryptographic Nonce, rather than the too-predictable `random`.

<!-- page 53 -->

**Implementation of `commit()` and `verify()` over SHA-256**

```python
import hashlib
import json
import secrets

def commit(state: str, move: str, intent: str) -> tuple[str, str]:
    # Generate a fresh cryptographic nonce (defeats dictionary attacks)
    nonce = secrets.token_hex(16)
    # Serialize the fields as CANONICAL JSON (sorted keys, fixed separators)
    # so BOTH peers hash byte-identical input. The reference code seals a
    # richer record (hint, verdict, step, role, sub_game); the core is shown.
    payload = json.dumps({"state": state, "move": move,
                           "intent": intent, "nonce": nonce},
                          sort_keys=True, separators=(",", ":"))
    h_commit = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    # Send only h_commit now; keep nonce secret until the final audit
    return h_commit, nonce

def verify(state: str, move: str, intent: str,
           nonce: str, h_commit: str) -> bool:
    # Re-synthesize the opponent's hash from the revealed data
    payload = json.dumps({"state": state, "move": move,
                           "intent": intent, "nonce": nonce},
                          sort_keys=True, separators=(",", ":"))
    recomputed = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    # Any mismatch proves tampering occurred
```

<!-- page 54 -->

```python
    return secrets.compare_digest(recomputed, h_commit)
```

The code above illustrates a concrete commit-and-reveal mechanism; the broader theoretical idea behind it is formulated in the following box.

> **The Zero-Knowledge Framework**
>
> The Commit-Reveal mechanism embodies the spirit of a zero-knowledge proof [20]: each agent — the Cop as well as the Robber — proves that it chose a legal move and fixed it, without revealing what the move is ahead of time. At the commitment stage, the opponent receives absolute certainty that a locked decision exists — but zero knowledge of its content. Only at revelation is the content disclosed, and even then it can be verified against the original commitment. Thus commitment is separated from disclosure.

<!-- page 55 -->

## 5.4 Mutual Audit and Log Integrity (*Mutual Audit and Log Integrity*)

The reliability of the entire system rests on a post-mortem integrity check (*Post-Mortem Integrity Check*). At the end of the game, the Cop agent submits its complete log, including the Nonce revelations for all of its steps, and so does the Robber. Each side reconstructs its opponent's data via SHA-256: it takes the State, Move, Intent, and Nonce that the opponent revealed, re-hashes them, and compares the result to the signature that was declared at the commitment stage. This principle, whereby a short cryptographic fingerprint attests to the integrity of an entire block of data, also underlies hash-based signatures [21]. This verification is demonstrated visually, step by step, in the replay simulator described in Chapter 7.

> **Forgery Leads to a Technical Loss**
>
> Any mismatch between the recomputed hash and the hash declared at the commitment stage proves unambiguously that tampering (*Tampering*) occurred. There is no room here for interpretation or statistical doubt: the SHA-256 function is sensitive to every single bit, so even a tiny change to a move alters the signature entirely. The group that cheated absorbs a heavy technical loss — an absolute loss of the game, regardless of the outcome on the board. Cryptography, not human judgment, is the arbiter.

## 5.5 Step-0 and Computational Fairness (*Step-0 and Computational Fairness*)

A competition between agents raises a question of fairness: is it right for an agent running on a modest laptop to compete under the same conditions against an opponent running on a supercomputer capable of deep tree search or of running a heavy language model? Computational Fairness requires that hardware advantage alone must not decide the race — a principle that is factored into the league score (Chapter 9). Therefore, before the first move, a "Step-0" is carried out. At this step the agents collect their machine specifications: the operating system (OS), the number of CPU cores and their frequency (CPU), the memory size (RAM), the presence of a graphics accelerator and video memory (GPU/VRAM), and the name of the language model being run. Alongside the hardware specification, the Step-0 declaration also records the code version, the group name, and the game number. The entire specification is packed into a JSON string and cryptographically

<!-- page 56 -->

signed using a key supplied in advance, so that it cannot be forged after the fact. In parallel, all language-model token consumption is also monitored and cryptographically locked, in order to prevent denial of the computational resources actually consumed.

> **Mandatory: the Commit Identifier in the Agreement Declaration**
>
> Alongside the hardware specification, each side also declares, in its Step-0 declaration, the commit hash (*commit hash*) on GitHub on which the code that ran in that game is based. It is permitted to change, update, and improve the code between games — but in every game the declaration must record the exact commit identifier that was played, so that the examiner can reproduce precisely the version that competed. This identifier is also included in the JSON file sent in the final email (the `github_commit` field; see Chapter 9).

In calculating the league scores, the instructor applies a normalization formula that grants bonuses to algorithmically efficient solutions — those that achieved good results while consuming minimal resources. This reverses the incentive: it is not raw hardware power that is rewarded, but the sophistication of the algorithm. A light, fast solution running on a modest machine that beats a heavyweight opponent represents a victory of development over computational brute force.

### 5.6 Chapter Summary

We saw that in a peer-to-peer network with no referee, trust cannot be assumed — it must be proven. The Commit-Reveal mechanism over SHA-256 locks every move in a cryptographic signature before its content is revealed, thereby thwarting time travel, after-the-fact changes, and disavowal. Mutual auditing of the logs at the end of the game exposes any forgery and penalizes it with a technical loss, while Step-0 and the signed hardware declaration ensure that fairness is preserved even between machines of unequal power. The next chapter continues from the integrity layer to the strategy layer: how an agent builds a belief map and makes good decisions under the uncertainty that was faithfully preserved here.

<!-- page 57 -->

# 6 The Strategy and Decision-Making Module

## 6.1 Chapter Goals

By the end of this chapter you will know why an agent's driving logic must be independent and must never rely on a language model for spatial computation; and you will become familiar with a range of alternative, equally valid ways to implement the movement policy — Manhattan-distance heuristics combined with a Bayesian belief map, your own heuristic algorithm, and reinforcement learning as one optional possibility only. It is important to emphasize: the course did not teach reinforcement learning, and a fully strong agent can be built using heuristics alone, with no RL whatsoever. The movement decision always remains in the hands of the algorithm; the language model integrates into the process not as a navigation engine, but as a behavior analyzer and a calculated text generator for the verbal game — and even that at a token consumption level that can be tuned all the way down to zero. We will see how each side — Cop and Robber, symmetrically — builds a probabilistic belief map and updates it using Bayes' rule, and how the language model fits into the process. We will combine all of this into a single strategy module that connects to the PeerRuntime layer.

<!-- page 58 -->

## 6.2 Why a Separate Strategy Module Is Needed (*Why a Separate Strategy Module*)

The simulator infrastructure we built in previous chapters — the central orchestrator (Chapter 8) — manages the pipeline: message passing, signature locking, and turn management. But note a crucial distinction: infrastructure that knows how to pass a message does not know what to decide. An agent's driving logic must be intelligent and independent, and must not rely blindly on a language model — because language models tend to hallucinate in Cartesian spaces, and to confuse directions, distances, and coordinates. From this follows a clear development requirement: students must implement a separate strategy module, which connects to the PeerRuntime layer at a precise point — immediately after decoding the incoming hint, and before packing the outgoing Commit. Between these two points sits all of the agent's intelligence: belief update, choice of legal move, and composition of the deceptive text. This separation is not an architectural whim; it is the boundary separating a generic communication component from a thinking agent.

An example implementation of a minimal strategy module (without strategic depth, provided as a pedagogical starting point) is available in the code repository in Appendix D. In the reference implementation, the module is selected in the private configuration file, in the `[strategy]` section: the `thief_class` and `police_class` keys point to your "brain" class (written as `package.module:Class`), which inherits from `BrainBase` and overrides `_pick_move` — and, for the Cop, also the barrier choice in `_decide_move`. Leaving the section empty runs the built-in heuristic brain (see the strategy-module selection table in Appendix F and `docs/STRATEGY.md`).

<!-- page 59 -->

**Figure 7 — Strategy module inside PeerRuntime:**

```
[incoming hint + scent] → [hint decode (parse text)] → [belief update (Bayes rule)]
        → [move choice: heuristic / your algorithm / Q-policy (optional)]
        → [LLM bluff text (deception)] → [Commit pack (out)]
```

Figure 7: The decision flow within the strategy module: the incoming hint is decoded, the belief map is updated by Bayes' rule, the movement policy (heuristic, your own algorithm, or optionally Q) chooses a legal move, the language model composes the deceptive text, and everything is packed into the Commit.

What the figure shows: a chain of five stages enclosed within a dashed rectangle marking the boundary of the strategy module within the PeerRuntime — from the incoming hint (top left) to the outgoing Commit. How to interpret it: the Cartesian stage (choosing the move) and the verbal stage (the deceptive text) are clearly separated; the language model receives the movement decision as a given fact. "What if" analysis: had the language model been allowed to choose the move itself, a single Cartesian hallucination would translate directly into an illegal or suicidal move; the separation ensures that the algorithm preserves movement legality independent of the model.

## 6.3 Reinforcement Learning — One Optional Tool (*Reinforcement Learning as One Optional Tool*)

Before diving into details, let us emphasize: reinforcement learning is one of the possible ways to implement the movement policy — an optional tool only, not "what the course taught." The course did not include reinforcement learning, and many groups will build a winning agent with no RL at all, based on the two algorithmic tracks described below: pure heuristics (Manhattan distance combined with a Bayesian belief), or your own heuristic algorithm. In all three tracks, the movement decision remains in the hands of the algorithm, and the language model serves only the verbal layer. This chapter presents the three tracks as equivalent, and the choice between them is left to the group.

Since the grid is bounded to size [ board size ] (default 7×7), the state

<!-- page 60 -->

space is finite — though very large, due to the combination of player positions and barrier layout. This finiteness is the condition that allows groups who choose to do so to train the agent using classical reinforcement-learning methods, foremost among them Q-Learning [22], [23]. In this track the agent maintains a table (or network) mapping every possible state to the weights of the actions available in it, and updates these values using the Bellman equation [24].

Groups wishing to go deeper into developing advanced winning tactics are recommended (optional reading) to consult the AgentNet environment for distributed evolutionary coordination of language-model-based multi-agent systems [25] — an approach that complements the reinforcement-learning track with ideas from population-based evolution.

For groups who choose to do so, the Q-value update follows the Bellman equation:

**Q-Update per the Bellman Equation**

$$Q(s,a) \leftarrow Q(s,a) + \alpha\Bigl[r + \gamma \max_{a'} Q(s',a') - Q(s,a)\Bigr]$$

The components of the equation are analyzed as follows:

- **Q(s, a)** — the action value. The current estimate of the expected cumulative reward from performing action *a* in state *s*. Practical meaning: this is the table cell that the agent updates, and from which it will later choose its move.
- **r** — the immediate reward. The reward received right after the action, derived directly from the scoring table. Practical meaning: capture or survival translates into a concrete number that drives the learning.
- **α** — the learning rate (α ∈ (0, 1]). Determines how much weight is given to new information versus accumulated knowledge. Practical meaning: an α that is too high causes volatility and forgetting of past experience, while an α that is too low slows convergence.
- **γ** — the discount factor (γ ∈ [0, 1]). Determines the importance of future reward — long-term capture or survival — versus immediate scoring. Practical meaning: a high γ encourages strategic patience, for example building a barrier trap over many turns.
- **max_{a′} Q(s′, a′)** — the best future value. The best estimate of the reward from the next state s′. Practical meaning: this is where future knowledge "leaks" backward onto…

*[Chapter continues in the next chunk.]*


<!-- page 61 -->

...the present, and enables the agent to plan beyond the single step.

To avoid getting stuck in constant loops during the pursuit, an **Epsilon-Greedy** mechanism is incorporated: with a small probability ε the agent chooses a completely random action instead of the action with the highest Q-value. This mechanism encourages exploration (Exploration) of new escape or pursuit routes, and prevents over-exploitation (Exploitation) of a policy that has gotten stuck in a cycle.

Anyone who chose the RL track will notice that the project has a thinking adversarial side, and therefore — if you used reinforcement learning — it is actually a case of **Multi-Agent RL** [26], [27], in which the learning environment itself changes as the opponent learns and improves. That said, this is one track among several, and is not mandatory.

### 6.3.1 Two Equal Alternatives Without RL

Reinforcement learning is, as stated, only one possibility. Two additional tracks, completely equal in value, allow building a strong agent without it — and in both of them, as in RL, the movement decision remains completely algorithmic:

- **Pure heuristics (Bayes + Manhattan).** One can forgo learning entirely and rely on a deterministic decision rule: update the belief map by Bayes' rule, and then at each turn choose the legal move that minimizes the Manhattan distance to the cell of highest belief. This is a simple, transparent track that is easy to debug — and is often fully competitive against RL. This is the default policy in the reference implementation.
- **Your own heuristic algorithm.** One can design a richer movement policy that combines the belief map, the scent maps, exploitation of barriers, and forward search (e.g., minimax or expectimax against the opponent's belief) — all in deterministic, transparent code. Here too there is no training stage, and the spatial reasoning remains in your hands, not in the hands of the language model.

The three tracks — RL, heuristics, and your own algorithm — are equal-rights citizens for the movement policy; in all of them the spatial decision is algorithmic, and the language model separately serves the verbal game, as described later in the chapter. Choose the one suited to your resources and your team's style.

<!-- page 62 -->

**Example: Q update and epsilon-greedy action selection**

```python
import random

def q_update(Q, s, a, r, s_next, actions, alpha=0.1, gamma=0.95):
    # Bellman update: blend old estimate with the observed target
    best_next = max(Q[(s_next, a2)] for a2 in actions)   # max_a' Q(s',a')
    td_target = r + gamma * best_next                    # r + gamma * max Q
    td_error = td_target - Q[(s, a)]                      # temporal-difference
    Q[(s, a)] += alpha * td_error                          # move toward target
    return Q[(s, a)]

def choose_action(Q, s, actions, epsilon=0.1):
    # epsilon-greedy: explore with prob epsilon, else exploit the best Q
    if random.random() < epsilon:
        return random.choice(actions)                    # exploration
    return max(actions, key=lambda a: Q[(s, a)])          # exploitation
```

<!-- page 63 -->

## 6.4 Distance Heuristics and Belief Heatmap

Both sides are completely symmetric: neither of them sees the opponent's true location. Each side knows where it itself is, and receives the opponent's scent map (each side perceives the *other* side's scent field, not its own) and a verbal hint that may be false. Because of this, each side builds its own belief map: a matrix of size [board size] (e.g., 10×10) representing the statistical probability that the hidden opponent is located in each cell [17]. Thus the Cop builds a belief about the Robber's location from the scent map and the hints it received, and symmetrically the Robber builds a belief about the hidden Cop's location from the Cop's scent map and its own hints, and uses it to plan an escape route. On every incoming hint, the side applying it uses Bayes' rule to update the probabilities, while assigning a reliability coefficient to the text — since the text may be false. The Cop then seeks to minimize the Manhattan distance to the cell with the highest probability, while the Robber seeks to maximize it and move away from it.

**Manhattan distance on an orthogonal grid**

D = |x<sub>cop</sub> − x<sub>target</sub>| + |y<sub>cop</sub> − y<sub>target</sub>|

The components of the formula break down as follows:

- **(x<sub>cop</sub>, y<sub>cop</sub>)** — The Cop's location. The agent's known coordinates. Practical meaning: this is the only certain component in the equation.
- **(x<sub>target</sub>, y<sub>target</sub>)** — The target cell. The cell with the highest belief, arg max<sub>s</sub> b(s), from the belief map. Practical meaning: the target is not the "real" Robber but the best probabilistic guess about it.
- **D** — Manhattan distance. The sum of the absolute differences on both axes. Practical meaning: this function matches orthogonal movement on a grid, where there is no diagonal movement, and it is therefore an admissible estimate of the minimal number of steps.

<!-- page 64 -->

**Movement decision by Manhattan distance**

Suppose the Cop stands at cell (2, 2), and the belief map places the probability peak at cell (5, 5). Then D = |2−5| + |2−5| = 3 + 3 = 6. Among the legal actions, East (3, 2) gives D = 5 and North (2, 3) also gives D = 5, while West (1, 2) gives D = 7. The agent will therefore choose the eastward or northward move — both minimize D by one step — and will prefer between them by Q-value. In this way the probabilistic reasoning (target selection) and the learned reasoning (move selection) are combined.

**Figure 8 (belief heatmap diagram).** A 10×10 Bayesian belief map, b(s) = P(thief = s | hints), rendered as a color-graded grid: the y-axis (row) and x-axis (column) each run 0–9; scattered probability values are annotated on individual cells (illustrative samples visible in the source figure include values such as 0.06, 0.05, 0.04, 0.03, 0.02, 0.01, and 0.00 across the grid, forming a single concentrated hotspot); a star marks arg max<sub>s</sub> b(s); a labeled square marks the position of the side ("cop") holding the map; a color bar is labeled "posterior probability."

**Figure 8:** A Bayesian belief map of size [board size]: each cell is colored according to the probability b(s) that the hidden opponent resides there, following a Bayes update from a scent hint. Shown here is the Cop's map (belief about the Robber); the Robber holds its own symmetric map (belief about the Cop). The star marks arg max<sub>s</sub> b(s), the blue square marks the position of the side holding the map, and the dark squares are barriers with zero belief.

What is seen in the figure: a grid of size [board size] in which the concentration of probability (the lighter hue) is centered around a single cell, while the rest of the board carries a low, uniform belief; the map holder and the barriers are marked separately.

<!-- page 65 -->

Recall that both sides hold such a map — the Cop's map of the Robber, and the Robber's map of the Cop. How to interpret: the star is the target toward which minimizing the Manhattan distance is aimed (for the Cop), or from which the escape moves away (for the Robber); the distribution is not a sharp point but a cloud, reflecting the uncertainty that remains even after the update. "What if" analysis: if a new hint contradicts the previous one, the probability mass is redistributed — the peak may migrate or split into two foci, and the Cop will be forced to decide which of them to aim for first.

## 6.5 LLM Integration for Prompt Engineering

Although the spatial reasoning is handled entirely by the algorithm, the language model remains critical for the verbal game. The strategy module directs the client to use a Tool against the FastMCP server to gather data, builds a rich prompt that includes the statistics and the scent maps, and sends it to the language model to compose a calculated bluff text — or a psychological analysis of the opponent's language. In doing so, the language model functions as a Bluff Classifier and as a behavioral profiler, while the algorithm preserves movement legality. This division of labor — language to the model, space to the algorithm — is the core of the agent's design, and it rests on the attention capabilities of the Transformer architecture [28].

> **Do not rely on the language model for spatial reasoning**
>
> Never hand the language model the decision on the movement itself. Language models tend to hallucinate when computing coordinates, directions, and distances in Cartesian space, and may confidently return an illegal move, a move that collides with a barrier, or a move that moves away from the target [29]. The model's role is verbal only: composing text, classifying bluffs, and profiling. The spatial decision is reserved for the algorithm, which alone is capable of guaranteeing mathematical legality.

Despite the sweeping prohibition presented above, a single exception is defined — conditioned on the explicit agreement of both sides — that justifies separate treatment.

<!-- page 66 -->

> **Exception by mutual agreement: language-model-based tactics**
>
> The default and the recommendation remain unambiguous: the decision on the move is algorithmic, and the language model is verbal only. However, as part of the rule system open to negotiation, both sides may agree in advance — during the pre-game negotiation stage — to allow a language-model-based tactic for the move decision as well, instead of exclusive reliance on the algorithm. This permission is valid only with explicit, documented mutual consent between the teams; one side may not adopt such a tactic unilaterally. Even with such agreement, the local algorithm must still enforce move legality (and reject any illegal move the model proposes), and the risk of spatial hallucinations — as described in the warning above — remains the responsibility of the team that chose this. The reference implementation and the book's default remain algorithmic.

### 6.5.1 How the Bluff Text Is Produced — Four Operating Modes

Since the move decision is entirely algorithmic, the language model is required only for the verbal layer — and therefore the choice of how to activate it is mainly a budget question: how many tokens out of [token estimate per series] you are willing to spend on talk. The reference implementation offers four modes, selected in the private configuration file (`[trash_talk] provider`); full details are in the language-model modes table in Appendix F:

- **[template provider]** (`template`) — the default. Ready-made bluff sentences, selected in Python code — zero tokens, no network dependency. This is the recommended track: it directs full attention to the movement algorithm.
- **[Ollama provider]** (`ollama`). A local language model via Ollama (e.g., at `localhost:11434`) — zero API tokens and no rate limit.
- **[cloud provider]** (`claude_api`). A small cloud model (e.g., Haiku) via the API — real consumption counted against [token estimate per series], subject to the account's rate limit.
- **[command-line provider]** (`claude_cli`). Running `claude -p` via the Claude Code CLI — the highest cost, subject to a subscription.

<!-- page 67 -->

The `every_n_steps` parameter activates the model only once every several turns and further reduces consumption. The practical meaning: a team can play the entire series of [number of mini-games] mini-games at zero tokens (in template or Ollama mode), and compete entirely on the quality of the movement algorithm.

Location-dependent hints. The content of the hints can rely on the [game arena] — the agreed-upon realistic area in which the game "takes place" (e.g., New York, London, or Paris). When defined, hints embed real landmarks from that area ("slipping past Times Square"), thereby making the verbal game richer and more suggestive; in the absence of a definition (default `""`) generic landmarks are used. This also applies to the token-free template mode, and therefore incurs no cost. The length of each hint is capped at [word limit per hint] words (default 15) — a cutoff applied both to the template and to the language model, which also receives the limit in its system prompt. [Game arena] and [word limit per hint] are agreed-upon terms, signed like the rest of the game terms (see Appendix F).

> **Course Connection**
>
> The strategy module relies on several layers from the AI Agent Orchestration course. The move decision is algorithmic, and the language model is responsible only for the verbal layer — analyzing the opponent's language and composing bluff text — in the spirit of the agents-and-orchestration approach taught in L05. The language model's ability to analyze the opponent's language and generate bluff text relies on the foundations of deep learning (neurons, gradient, loss function) from L02 and on the attention mechanism of the Transformer from L04 [28]. Running a local language model via Ollama, as practiced in L08, allows the agent to produce the verbal layer without dependence on an external service and at zero API tokens, thereby maintaining full autonomy vis-à-vis the opponent. Reinforcement learning was not taught in the course and is only one option alongside heuristics and your own algorithm — an additional tool in the toolbox, not a cornerstone.

<!-- page 68 -->

## 6.6 Chapter Summary

We built an independent strategy module that connects to the PeerRuntime between hint decoding and Commit packaging, and we clearly separated the spatial reasoning from the verbal reasoning. We saw three equal-value tracks for the movement policy: pure heuristics (Bayesian belief map and Manhattan distance), your own heuristic algorithm, and reinforcement learning as one optional possibility (not taught in the course) — in all of them the spatial decision remains with the algorithm. We saw how each side — Cop and Robber, symmetrically — builds a belief map of the hidden opponent from the other side's scent map, and how the language model serves only the verbal game — and is never entrusted with the exact spatial computation — across four operating modes whose cost ranges from zero tokens upward. In the next chapter we move from the single decision to assembling the complete system, and see how these components work together over a full race.

<!-- page 69 -->

# 7 User Interface (GUI) and the Replay Simulator

## 7.1 Chapter Goals

By the end of this chapter you will know: why real-time monitoring (Observability) is an integral component in the development of complex P2P systems, and not external decoration; how to translate a mathematical probability table into an accessible heatmap visualization in the Cop's local interface; how the turn banner reflects the asynchronous synchronization mechanism of the race; and above all — how to build a Replay Viewer that serves as a trustworthy witness system, cryptographically verifying every past step and detecting any attempt to falsify the game log.

<!-- page 70 -->

## 7.2 Two Axes: Live Monitoring vs. Retrospective Witness

An integral part of developing a complex P2P system is the ability to monitor the agents' actions in real time and verify their legality retrospectively. These two needs — monitoring and proof — define the two tools this chapter deals with, and they do not overlap. The live interface (Live GUI) answers the question "what is happening now?", while the Replay Viewer answers the harder question: "did what happened in the past actually happen as claimed?"

The distinction is not merely technical but substantive. In a distributed environment without a central referee, the game's history is not stored with a trusted authority — it is kept in a local log file with each player. This fact opens the door to temptation: a player might try to rewrite their past in order to win retroactively. The chapter before you shows how encryption (which we relied on in Chapter 5) turns the log from a document that can be forged into an irrefutable piece of evidence.

> **Local Truth**
>
> Local truth is a design principle whereby each agent's interface displays only the information accessible to it — its own location, the scent map it senses, and the hints it has received — and never the full objective board state. There is no "bird's-eye view" showing both sides' positions simultaneously. This principle follows directly from the Dec-POMDP formalism: each agent's observation Ω<sub>i</sub> is a partial subset of the true state S, and therefore an interface that reveals the full S would violate the rules of the game.

## 7.3 The Live GUI: Heatmap and Turn Banner

Each side — Cop and Robber — runs its own software from a dedicated GUI (e.g., Tkinter or PyQt). As clarified in the definition of local truth, the interface does not expose the objective board state but only the local truth. Two central display mechanisms turn the race's abstract mathematics into controlled, accessible information for the students.

<!-- page 71 -->

### 7.3.1 Heatmap Visualization

The heatmap mechanism is completely symmetric: each of the two sides runs its own GUI, and each of them displays a dynamically changing grid showing that agent's belief map about the opponent only. At the Cop's side, cells where the probability of the Robber's presence is high — given the hints received and the Robber's scent map it senses — are colored in increasingly intense shades of red; and in parallel and identically, the Robber's window shows its belief map about the Cop's location, built from the Cop's scent map and the hints the Robber received. Neither side sees the opponent's location, only a probabilistic estimate that updates in real time. Thus, for each agent, the mathematical probability table — an abstract object — is translated into accessible, controlled visual information: the student is not required to read a matrix of numbers but to identify at a glance the focus of suspicion. This is a direct application of the belief map (Belief) built in previous chapters.

### 7.3.2 Turn Indicator

To reflect the asynchronous synchronization mechanism, the interface includes a visual turn-status banner. The banner lights up green when the opponent's MCP server has broadcast that the turn has passed to the local agent. Once the local agent has chosen its move, signed it with Commit, and broadcast it to the opponent, the banner turns gray and the interface locks from activity until the turn is received back. This banner is not merely a graphic decoration; it is a visual representation of the asynchronous state machine that prevents the player from acting out of turn.

**Cop Live GUI (Local Truth)** — diagram elements: cell `C` (Cop's own location); cell `T?` (highest-belief cell); banner state "turn received (act enabled)" → **YOUR TURN** (green); banner state "commit sent (input locked)" → **LOCKED** (gray); legend: "higher probability ⇒ deeper red."

**Figure 9:** A mock-up of the live interface: a belief grid where the intensity of red expresses the probability of the Robber's presence (T?), alongside a turn-status banner that lights up green (YOUR TURN) when the turn is received and turns gray (LOCKED) after the Commit is broadcast.

What is seen in the figure: on the left, a 3×3 grid representing the Cop's window; the cell

<!-- page 72 -->

marked darkest is labeled T? and expresses the highest probability of the Robber's presence, while the cell C marks the Cop's own location. On the right, the two banner states: green (YOUR TURN) and gray (LOCKED). How to interpret: the more intense the red hue, the higher the cumulative probability from the scent map and the hints; the green banner signals that the turn has been received from the opponent's MCP and action is possible, and the gray signals that the interface is locked after sending the Commit. "What if" analysis: if the player tries to click a move while the banner is gray, the interface ignores the input — the lock enforces the asynchronous turn and prevents a race condition in which both sides act simultaneously on the same step.

## 7.4 The Replay Viewer and Integrity Enforcement

A mandatory submission requirement is building a Replay Viewer. Its purpose is to provide a trustworthy witness system for the end of the game. The player loads the final log file (e.g., `logs/police_match.json`), and the viewing user can step forward and backward in time using control buttons. The tool's uniqueness lies not in the graphical display but in the cryptographic verification: at every step the engine runs a live verification function that takes the Nonce and the move appearing in the visible log, re-encodes them using SHA-256 [19], and compares them to the original commitment value (Commitment). If the values match, a green "Verified OK" stamp is displayed. If even the slightest change is found in the past data — an attempt to falsify the log — the viewer prints a bright red "TAMPERED" banner, and the game is immediately disqualified. This principle relies directly on the collision-resistance property of the hash function that we saw in Chapter 5: since it is impossible to find an alternative input yielding the same hash, any change to the (Nonce, move) pair is necessarily detected.

<!-- page 73 -->

**Figure 10 (flow diagram):** Read log entry (nonce, move, commit) → Recompute SHA-256(nonce, move) → equals commit? → **yes**: Verified OK / **no**: TAMPERED (disqualify).

**Figure 10:** The cryptographic verification flow in the Replay Viewer: reading a log entry, recomputing SHA-256 over the Nonce and the move, comparing to the commitment value, and branching to a green "Verified OK" stamp or a red "TAMPERED" banner that disqualifies the game.

What is seen in the figure: a chain of four stages — reading the log entry, recomputing the hash, a decision node (equals commit?), and two possible outcomes: a green box (Verified OK) or a red box (TAMPERED). How to interpret: the flow is deterministic — for the same input the same result is always obtained; the central node is the decision point at which the fate of the step is decided. "What if" analysis: if a player fraudulently altered a single move in the log but left the original commitment value unchanged, the recomputation will yield a different hash, the node will route to the "no" path, and the red banner will appear — the game is disqualified even though the change was tiny.

## 7.5 The Verification Engine: A Code Sketch

The heart of the simulator is a single step function applied to each entry. It receives a log entry, recomputes the hash over the concatenation of the Nonce and the move, compares it to the stored commitment value, and returns a status flag. The commit-reveal scheme that the engine verifies was fully defined in Chapter 5. The explanation in Hebrew is given here outside the code, since the comments within the code itself are in English only.

<!-- page 74 -->

**Example: replay verifier step**

```python
import hashlib

def verify_step(entry):
    # Recompute the commitment from the visible log fields.
    payload = f"{entry['nonce']}|{entry['move']}".encode("utf-8")
    recomputed = hashlib.sha256(payload).hexdigest()

    # Compare against the original commitment stored in the log.
    if recomputed == entry["commit"]:
        return "Verified OK"   # green stamp: reveal matches commit
    # Any mismatch means the past data was altered.
    return "TAMPERED"          # red banner: disqualify the match

def replay(log):
    # Walk every recorded step; the whole match is void on first tamper.
    for entry in log:
        if verify_step(entry) == "TAMPERED":
            return "TAMPERED"
    return "Verified OK"
```

The `verify_step` function illustrates the principle: the Nonce and the move visible in the log are re-encoded, and the comparison to the stored commit is binary — there is no "almost matching." The `replay` function walks over the entire log; a single failure suffices to disqualify the whole game. Note: the sketch simplifies the input for illustration purposes; in practice the signature covers the full set of step components — State, Intent, Move, and Nonce — as detailed in the protocol in Chapter 5.

<!-- page 75 -->

> **Submission Requirement and Disqualification**
>
> Building the Replay Viewer is a mandatory submission requirement of the project, not an optional component. Moreover, a single TAMPERED result — meaning the discovery of even the slightest change in the log's past data — disqualifies the game immediately. There is no appeal and no after-the-fact correction: the cryptographic witness system is designed precisely so that there is no room for human judgment on the question of whether the log was falsified. Screenshots of the viewer showing the Verified OK indication — alongside a screenshot of the belief map in the Live GUI — are part of the submission requirements (Appendix C); a sample implementation of the viewer and the interface is available in the code repository referenced in Appendix D.

Beyond the technical aspect of this requirement, it is worth linking it to the course's broader learning goals.

> **Course Connection**
>
> The need to monitor agents and verify their actions retrospectively is a direct expression of the Observability principle from production systems development [30]: a system that cannot be observed from within cannot be operated and cannot be trusted. The Live GUI and the Replay Viewer are two forms of monitoring a distributed system [5] — one in real time and the other retrospectively. In course terms, this chapter is a direct continuation of the lecture on AI agents and sub-agents (L05) in the AI Agent Orchestration course: there we learned about agents and sub-agents, the orchestrator, prompts and skills, as well as token consumption and context windows of agent systems. Just as an agent needs tools (agent tooling) to act, the developer needs tools to see what the agent did, to track its behavior, and to prove after the fact that it acted properly — this is exactly Observability of agent systems.

## 7.6 Chapter Summary

We saw that monitoring is not an appendix but an integral component in a P2P system: the live interface translates the belief map into an accessible heatmap and reflects the asynchronous synchronization in a turn banner, all under the local-truth principle that does not permit a bird's-eye view. The Replay Viewer, in contrast, turns the log from a forgeable document into

<!-- page 76 -->

cryptographic evidence: every step undergoes live SHA-256 verification, and every tiny change triggers the red TAMPERED banner and disqualifies the game. This closes the circle opened with the encryption in Chapter 5, and the project gains not only a mechanism of action but a mechanism of trust — the basis for a fair autonomous race between two opponents who do not trust one another.

<!-- page 77 -->

# 8 Agent Architecture Design and Deep Reliability Mechanisms

## 8.1 Chapter Goals

By the end of this chapter you will know: why an autonomous game agent is not a linear script but a distributed system requiring rigorous development according to the principle of Separation of Concerns; how the Orchestrator pattern centralizes all subsystems behind a single entry gate and subjects the course of the game to a legal state machine; and what the stability patterns — Deadline Tracker and Watchdog — that protect the agent against freezing and against peer-to-peer network disconnections are.

## 8.2 Separation of Concerns as an Overarching Principle

Why does a system that wins in simulation sometimes fail in a real game against a remote opponent? The answer usually lies not in the decision algorithm but in the system development built around it. An agent participating in a multi-participant AI-based game, as the protocols for this domain recommend, cannot mix communication management, decision-making, and logging into one piece of code. Such mixing gives birth to a fragile system in which a failure in one subsystem brings down all of them.

The development solution is division into modules with a single, clear responsibility, coordinated by one central component. The chapter before you deals with this architectural skeleton: how to build an Orchestrator that serves as a single gateway to all subsystems, and how to wrap it in a reliability layer that assumes in advance that the world — the network, the model, and the opponent — will fail at exactly the critical moment [30].

<!-- page 78 -->

## 8.3 Orchestrator Pattern and State Machine

At the heart of the architecture stands a central component serving as a Gateway — a single entry point — to all subsystems. The orchestrator is what initializes the MCP connections (Chapter 2), activates the decision module (Chapter 6), and communicates with the log managers and the cryptographic commitment mechanisms (Chapter 5). Instead of each module knowing its counterpart directly (a structure that gives birth to tangled mutual dependency), all communication passes through a single point. This pattern relies on recognized design principles in software development [31] and on gateway patterns from the world of microservices [5].

> **Orchestrator**
>
> A central software component serving as the single entry point (Single Gateway) to all of the agent's subsystems. It is responsible for initializing connections, activating the decision module, coordinating between components, and communicating with the log managers — but does not itself contain decision logic or low-level communication. Its role is to coordinate, not to execute.

The entire game is controlled by a rigorous State Machine, which ensures that only legal transitions between game stages are permitted. The waiting-for-opponent stage (`WAITING_FOR_OPPONENT`) can transition only to the move-computation stage (`COMPUTING_MOVE`), which in turn transitions to the commitment stage (`COMMITTING`), and so on. An illegal transition is rejected immediately, thereby preventing Deadlock states in which both sides wait for each other indefinitely.

> **Deadlock**
>
> A state in which two or more entities wait for a resource or message held by the other, such that neither can proceed. In a peer-to-peer system without a central referee, a deadlock can freeze an entire game with no error message at all. A state machine that blocks illegal transitions is the first line of defense against deadlock.

<!-- page 79 -->

**Figure 11 (state diagram):** `WAITING_FOR_OPPONENT` → `COMPUTING_MOVE` → `COMMITTING` → `AWAITING_REVEAL` → `VERIFYING` → (back to `WAITING_FOR_OPPONENT`); an error state `TECHNICAL_LOSS` is reachable via dashed arrows from the communication stages.

**Figure 11:** The legal state machine of a single game turn: the system cycles between waiting for the opponent, computing a move, committing, waiting for reveal, and verifying; a dashed error arrow leads from every communication stage to a technical loss.

What is seen in the figure: five valid states arranged in a cycle — `WAITING_FOR_OPPONENT`, `COMPUTING_MOVE`, `COMMITTING`, `AWAITING_REVEAL`, and `VERIFYING` — where verification returns the system to waiting for the next turn. In addition, an error state, `TECHNICAL_LOSS`, appears, reached by the dashed arrows. How to interpret: the solid arrows are the only legal transitions; any attempt to jump from one state to a state that is not a legal target for it is rejected. The dashed arrows represent an emergency exit — a transition upon failure of a communication stage. "What if" analysis: if the opponent disconnects during `AWAITING_REVEAL`, the system does not get stuck in eternal waiting but transitions in a controlled manner to `TECHNICAL_LOSS` and announces a result — exactly the behavior that a legal state machine guarantees.

The implementation of the state machine relies on a transition table specifying, for each state, which target states are legal. The following code sketches a minimal class that rejects any transition not listed in the table:

<!-- page 80 -->

**Example: a state machine with a transition table**

```python
class GamePhaseMachine:
    # Transition table: each state maps to its set of legal successors
    TRANSITIONS = {
        "WAITING_FOR_OPPONENT": {"COMPUTING_MOVE"},
        "COMPUTING_MOVE":       {"COMMITTING", "TECHNICAL_LOSS"},
        "COMMITTING":           {"AWAITING_REVEAL"},
        "AWAITING_REVEAL":      {"VERIFYING", "TECHNICAL_LOSS"},
        "VERIFYING":            {"WAITING_FOR_OPPONENT"},
        "TECHNICAL_LOSS":       set(), # terminal state
    }

    def __init__(self):
        self.state = "WAITING_FOR_OPPONENT"

    def transition(self, target):
        # Reject any transition not listed in the table
        if target not in self.TRANSITIONS[self.state]:
            raise ValueError(
                f"Illegal transition: {self.state} -> {target}")
        self.state = target
        return self.state
```

The class holds the current state, and every transition request is checked against the set of legal targets. An illegal transition immediately raises an exception instead of leaving the system in an undefined state — thus turning a logic bug into a visible error caught during development, rather than a silent deadlock during gameplay.


<!-- page 81 -->

## 8.4 Reliability Patterns: Deadline Tracker and Watchdog

Peer-to-Peer (P2P) systems are inherently exposed to disconnections and critical delays in the language model. A robust agent cannot assume that every request will be answered; it must implement active tracking patterns that distinguish between "still waiting" and "failed and action is needed" [30]. The two central patterns here are the Deadline Tracker and the Watchdog. A complementary reliability pattern — the Gatekeeper, which regulates outgoing mail — is discussed in the context of the league in Chapter 9.

### 8.4.1 Deadline Tracker

Every request sent over the FastMCP server carries a Timestamp and an Expiry Deadline. If no response arrives within the allotted time, the system performs a Retry or transmits a technical-loss message. This pattern is a concrete implementation of the Timeout pattern from the stability literature: never wait indefinitely for an external resource that is not under your control.

> **Missing a Deadline Is a Failure, Not Patience**
>
> A request whose expiry deadline has passed must be treated as a failure — not as an invitation to keep waiting. Leaving a request "hanging" without an expiry deadline is a direct recipe for deadlock: the main process gets stuck waiting, the watchdog detects the absence of a heartbeat, and the game collapses. Every request over MCP must carry an expiry deadline, and once that deadline passes the system must perform a controlled Retry or declare a technical loss and close the queue cleanly.

### 8.4.2 Watchdog

While the Deadline Tracker watches over a single request, the Watchdog watches over the entire system. It is an independent background process that monitors the main game loop. If it detects that the system has been frozen for several long minutes without emitting a Heartbeat — due to a model crash or a communication failure — it can perform a Controlled Shutdown and persist the state (State Persistence) for later recovery.

<!-- page 82 -->

```
Deadline Tracker                    MCP Connector

     Orchestrator                   Decision Module
       (Gateway)

                                     Log Manager
     Watchdog
```

**Figure 12:** The Orchestrator serves as a single gateway that branches out into five subsystems: the MCP connector, the decision module, the log manager, the deadline tracker, and the watchdog. All inter-module communication passes through it.

**What the figure shows:** a central, highlighted component — the Orchestrator — from which arrows extend to five separate modules: MCP Connector, Decision Module, Log Manager, Deadline Tracker, and Watchdog. **How to interpret it:** each arrow represents a single control channel; there are no arrows between the peripheral modules themselves, illustrating the single-gateway principle — no module knows any other module directly, only the orchestrator. **"What if" analysis:** if we wanted to replace the decision engine with a different model, it would suffice to swap out a single module while preserving the same interface toward the orchestrator; the rest of the system is unaffected — this is the power of separation of responsibility.

The following code sketches the heart of the Watchdog: a periodic heartbeat check that decides whether the main system is still alive.

<!-- page 83 -->

**Example: heartbeat check at the heart of the Watchdog**

```python
import time

def watchdog_check(last_heartbeat, timeout_sec=180):
    # last_heartbeat: epoch time of the main loop's last signal
    elapsed = time.time() - last_heartbeat
    if elapsed > timeout_sec:
        # Main loop appears frozen: persist state and shut down cleanly
        persist_state()          # save game state for later recovery
        controlled_shutdown()    # release MCP connections, close logs
        return "SHUTDOWN"
    return "ALIVE"
```

The process compares the time elapsed since the last heartbeat against a fixed threshold. As long as the main loop keeps emitting a heartbeat at a steady rate, the Watchdog returns `ALIVE` and does not intervene. But if more time than the allotted threshold has passed — a sign that the model has crashed or communication has hung — it persists the state and performs a controlled shutdown, so that recovery is later possible instead of losing the entire game.

<!-- page 84 -->

> **Connection to the Course**
>
> The idea of the orchestrator as a single entry gateway to sub-agents is not new to you. In lecture L05 of the "Orchestration of AI Agents" course, which dealt with agents and sub-agents, you saw how a super-agent (Orchestrator) delegates work to a group of sub-agents through a single gateway: it invokes Skills and Commands, and centralizes the entire flow of information between them instead of letting each component address the others directly. The Orchestrator of the game agent is exactly the same pattern, hardened for the conditions of a competitive game: the subsystems (the MCP connector, the decision module, the log manager, the deadline tracker, and the watchdog) are the "sub-agents," and delegation through a single gateway — the same separation of responsibility — is what allows each component to be swapped out, isolated, and fixed independently. Since both sides of the game are built symmetrically, each of them runs its own orchestrator and state machine following exactly the same pattern.

## 8.5 Chapter Summary

We saw that a reliable game agent is built on two pillars of development: coordination and reliability. The Orchestrator centralizes all subsystems behind a single gateway and subordinates the progress of the game to a state machine that blocks illegal transitions and prevents deadlock. The Deadline Tracker and Watchdog patterns assume in advance that the network and the model will fail, and provide retry, controlled shutdown, and state persistence instead of a silent crash. With this reliable skeleton in hand, we turn in the next chapter to the layer above it — the strategic logic that fills the decision module with content.

<!-- page 85 -->

# 9 The League, Computational Fairness, and Reporting Automation

## 9.1 Chapter Objectives

By the end of this chapter you will know: why the Cop–Robber project is not tested under closed laboratory conditions but in a dynamic academic league in which agents built by different teams compete against each other in real time; how the "diversity incentive" and "computational fairness" shape the league's scoring function; and what the Gatekeeper pattern is — the three protection mechanisms without which reporting automation over the Gmail API could collapse into flooding servers or getting the account blocked.

## 9.2 The League: From Lab to Arena

What distinguishes a programming exercise from a live system? An exercise proves itself against a single examiner known in advance; a live system must survive against opponents it has never seen. The project before you belongs to the second kind. It is not submitted under closed laboratory conditions, but is required to prove itself in a dynamic academic league — an arena in which agents from different "workshops" compete against each other in real time, with no central referee and no schedule dictated in advance.

This structure fundamentally changes the rules of the game. Success is no longer measured against a fixed test scenario, but against a changing population of opponents, each of which brings its own strategy, architecture, and failure modes. An agent that excelled against one opponent may fail decisively against another — and this is precisely the educational goal: to train robust systems, not solutions that are overfit to a single examiner.

<!-- page 86 -->

### 9.2.1 League Structure and Weighting

Every team is required to play against different opponents, and the league score is derived from the collection of these games. To prevent abuse and to encourage new challenges, the system implements a Diversity Incentive: a win against an opponent you have not yet played earns the full reward ([diversity reward]). However, the same game must not be played over and over against the same team for the purpose of accumulating score: only one counted game takes place against each opponent. Warm-up games that do not count are permitted and even recommended, for testing and calibration before the counted game. Once the counted game has ended and the two teams have agreed on its result, they send the end-of-game notification, and the encounter against that opponent is closed — no further game may be played against them for scoring purposes.

> **Game-Count Declaration**
>
> At the start of every game, each team declares to its opponent how many counted games it has already played so far, and the weighting of the diversity incentive is set according to these mutual declarations. The declaration is not a matter of trust: at the end of every legal game the two teams send the lecturer a game summary (see §9), so at any given moment the lecturer knows how many counted games each team has actually played. A false declaration discovered during the project review disqualifies the team that declared falsely.

The minimum threshold requirement for passing the project is modest but unambiguous: a valid run of at least [minimum games to pass] against different teams. On the other hand, the number of counted games is also capped from above: every team may play at most [maximum number of games per team] counted games, in order to maintain a balanced and fair league framework. Alongside the diversity incentive, the principle of Computational Fairness also operates: the system reduces the scoring advantage of anyone relying on extreme cloud resources, and rewards algorithmically efficient development that runs on limited machines. In other words, the league rewards cleverness in development, not raw computing power — since a smart algorithm on a modest machine deserves a higher score than a wasteful algorithm on a server farm.

<!-- page 87 -->

> **Tie Rule**
>
> If the cumulative score of all the mini-games between a pair of teams ends in a tie — that is, the point totals of the two teams are identical — each team receives [tie score]. This way no encounter is left without a score decision, and even an evenly matched result is translated into fair credit for both sides. The binding value of [tie score] is defined in the parameter table (Appendix F).

## 9.3 Gmail API Reporting Automation

At the end of every legal game against an opposing team, there is no longer room for human intervention in the reporting. Each of the two teams is programmed to send, on its own — each team separately — an automatic summary notification to the lecturer using the Gmail API [32]; it is not enough for only one side to send it. This automation is both a blessing and a trap: it guarantees uniform, immediate reporting, but hands over to code — which may contain a bug — the key to a live mail account. What happens when an infinite loop starts firing thousands of messages per minute?

> **Reporting Address to the Lecturer — Mandatory**
>
> At the end of every legal game, both agents automatically send the end-of-game report to the lecturer's mail address:
>
> **[agent reporting address]**
>
> This is the sole, binding address for sending reports; it must be set as the fixed destination in the mail-sending code of each of the two agents.

This point is not merely technical; it relates directly to the engineering skills the course seeks to instill, as we will clarify shortly.

<!-- page 88 -->

> **Connection to the Course**
>
> This chapter builds on lecture L09 in the "Orchestration of AI Agents" course, and specifically on exercise ex06 — a conversation between two agents over MCP, in which an agent calls an external tool through a uniform protocol. Note the essential difference in objectives: in ex06 the goal was to succeed at conversation-based communication between two agents — proving the very ability to coordinate and exchange messages. In the project before you the goal is far higher: to succeed at public communication — not local, and not over localhost — and to run a complete game with no referee at all and no central server. The reporting here is thus genuine "agent-to-agent": the Cop is not conversing with a human, but is invoking an external tool — Google's Gmail — in order to relay status to its autonomous peers and to the course servers. The critical difference is that Gmail is a quota-managed resource in the real world: one request too many, and the service provider blocks you. Therefore autonomous reporting in a public environment requires a protective layer that was not needed in ex06 — the Gatekeeper pattern set out below.

<!-- page 89 -->

### 9.3.1 The Gatekeeper Pattern and the Three Protection Mechanisms

To prevent serious failures — flooding mail servers (Spamming) or exceeding Google's quotas (Rate Limit 429) — it is recommended to implement in the communication module the Gatekeeper pattern: a reliability pattern from the same family as the Watchdog and Deadline Tracker discussed in Chapter 8, made up of three cumulative protection mechanisms.

<!-- page 90 -->

> **Terminology Clarification: Three Types of "Token"**
>
> The word "token" appears in the project in three completely different contexts, and they must not be confused:
> - **Rate-tokens (Token Bucket)** — units for regulating load in the rate-limiting component below. Not related to a language model at all.
> - **LLM tokens** — text units consumed on every call to a language model, which are measured, budgeted, and cryptographically locked in step zero (Chapter 5).
> - **OAuth tokens (Refresh Token / Access Token)** — authorization credentials against Gmail (see Appendix A).
>
> For the remainder of this chapter, "token" always denotes a rate-token — not a language-model token.

- **Quota Manager.** A counter that tracks the number of operations performed on a given day, and prevents crossing the daily safety threshold. This is the last line of defense against account blocking: if the quota is exhausted, no further request goes out.
- **Token-Bucket Rate Limiter.** An algorithm that limits the rate at which API requests are injected [33]. Every report requires a valid "rate-token" for a defined time window; the absence of a rate-token blocks the send. This prevents bursts that could trigger an immediate block from the provider. These rate-tokens must not be confused with language-model tokens.
- **DOS Detector.** Detects anomalous sending patterns that indicate a bug or an infinite loop in the agent's code. Once such a pattern is detected, the Gatekeeper completely locks access to the API and prevents the account from being suspended by the service provider — a principle known in systems development as backpressure and "circuit breaker" [30].

<!-- page 91 -->

```
Outgoing report → Quota Manager → [ok] → Token Bucket → [token] → DOS Detector → [clean] → Gmail API

                   Rejected              Blocked               LOCKED
                   (quota full)          (no token)            (anomaly)
```

**Figure 13:** An outgoing report passes through three cumulative protection gates before it reaches the Gmail API: the quota manager, the token bucket, and the DOS detector. Each gate may divert the request into a rejection or lockdown branch.

**What the figure shows:** an outgoing report (on the left) flows through three sequential gates — quota manager, token bucket, and DOS detector — until it reaches the Gmail API (on the right). From each gate a red failure branch diverges. **How to interpret it:** only a request that has passed all three gates reaches the API; failure at any gate stops the request as early as possible, per the "fail fast" principle. **"What if" analysis:** if the DOS detector identifies an infinite loop, it locks the entire pipeline (LOCKED) — sacrificing the individual report in order to save the whole account from suspension.

### 9.3.2 The Token-Bucket Rule: The Mathematical Rule

The heart of the rate limiter is a simple update rule: rate-tokens fill continuously at a fixed rate `r` up to a capacity ceiling, and are consumed one unit at a time on every report. A request is permitted only if a whole rate-token remains in the bucket. Again: these are rate-tokens for load regulation, not language-model tokens.

> **Token-Bucket Update Rule**
>
> tokens ← min(C, tokens + r · Δt),   allow ⟺ tokens ≥ 1
>
> **The variables that define the rule:**
>
> - **C — capacity.** The maximum number of tokens the bucket can hold. Practical meaning: C determines the size of the burst allowed — how many reports can be sent "all at once" after a quiet period.
> - **r — refill rate.** The number of additional tokens per unit of time.

<!-- page 92 -->

Practically: `r` is the stable average rate allowed over the long run; it must remain below Google's API quota.

- **Δt — elapsed time.** The time since the previous update. Practical meaning: the longer the time that has passed between reports, the more the bucket has filled — quiet is rewarded with future burst capacity.

Overall practical meaning: the rule separates the average rate (governed by `r`) from the momentary burst (governed by `C`). A report is accepted only when `tokens ≥ 1`; otherwise it is blocked until continuous refilling accumulates a whole token. This way the agent sends freely when traffic is low, but is gently restrained the moment it tries to breach the safety threshold.

**Token-bucket level over time (r = 0.8, C = 5)**

*[Graph: available tokens (y-axis, 0–5) vs. time t (x-axis, 0–40). A dashed capacity ceiling at 5. A labeled "burst / loop bug" region around t = 18. Green dots mark an accepted report (token spent); a red X marks a blocked report (bucket empty).]*

**Figure 14:** The token level in the bucket (r = 0.8, C = 5) over time: continuous refilling versus draining in bursts. Green dots = an approved report; red X = a report blocked when the bucket ran empty during the burst.

**What the figure shows:** the blue curve is the token level in the bucket over time. Under normal traffic the bucket fills up and allows reports (green dots), but during the marked burst (around t = 18) the request rate drains the bucket, and every additional report is blocked (red X). **How to interpret it:** the rising slope reflects the refill rate `r`; every sharp drop is a token being consumed by a report; the dashed ceiling is the capacity `C`. **"What if" analysis:** if we raise `r`, the bucket will recover faster

<!-- page 93 -->

and fewer reports will be blocked — but we risk exceeding the API quota; if we lower `C`, we will choke off legitimate bursts. The choice of `r` and `C` is, therefore, a balance between throughput and safety.

<!-- page 94 -->

**Example: Token Bucket rate limiter**

```python
import time

class TokenBucket:
    """Simple token-bucket rate limiter for outgoing API reports."""

    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = capacity          # max tokens the bucket holds
        self.refill_rate = refill_rate    # tokens added per second
        self.tokens = capacity            # start full
        self.last = time.monotonic()      # last refill timestamp

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last
        # continuous refill, clamped to capacity
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last = now

    def allow(self, cost: float = 1.0) -> bool:
        """Return True and spend a token if one is available, else block."""
        self._refill()
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False                      # caller must back off / retry later
```

<!-- page 95 -->

### 9.3.3 The Mandatory Signed Report Structure: JSON

The game report is not free text. It is packaged into a uniform, mandatory JSON structure, and sent as an attachment to the mail message. The JSON contains all the identifying details of the team, its GitHub addresses, the FastMCP server addresses, cryptographically signed hardware declarations, the game timestamp, and mutual-consent confirmations backed by SHA-256. Any attempt to send an open report that is not machine-readable (plaintext) leads to the report being rejected.

> **Mandatory: Agreement on the Result and Two Separate Reports**
>
> At the end of the game, the two teams must agree on its result, and each team must itself send the end-of-game report to the lecturer — separately and in the mandatory format. Reporting is not the responsibility of one side alone. If a report is not received from one of the sides, that side will not be credited with score for the game — even if it won on the board. Agreeing on the result and sending the two separate reports are the condition for both teams to be credited with the score due to them.

The full report is sent as an attached JSON file, and a complete example of it is included with this book as the file [results file]. In fact, four sample JSON files are attached to the book, covering the full lifecycle of the game; the variable name of each of them is defined in the variable table in Appendix F:

- **[declaration file] — pre-game declaration.** Consolidates all the constant data for the entire game (across all sub-games): the identities of the two teams and their members, the addresses of the Cop and Robber repositories, the MCP server addresses, hardware specifications, the language model, the agreed token ceiling, and the game's start and end times. Its role: to fix, with a cryptographic signature, everything that does not change during the game.
- **[configuration file] — the agreed configuration.** All the quantitative parameters of the mini-game (Appendix F), cryptographically locked and identical between the sides. Its role: to define the rules of physics and scoring that the two teams agreed on.
- **[log file] — the mini-game log.** A step-by-step record: Commit-Reveal commitments, moves, hints, and discussion fields with the language model, alongside the Nonce and the hash. Its role: to enable full cryptographic verification in the

<!-- page 96 -->

replay simulator (Chapter 7).
- **[results file] — the final results report.** A summary of all the sub-games: each team's score in each mini-game and the cumulative result, for weighting the league score by the lecturer. This is the binding report sent by email to [agent reporting address].

The four files carry a shared identifier (`game_uid`), and the name of each file is derived from the game identifier (`game_id`) — so that files from different games are never mixed up. The mandatory fields in the report include the GitHub links of both teams, the commit ID of each mini-game (Chapter 5), and the total tokens consumed.

> **Iron Rules: Rate Limit 429 and Machine-Readable Reporting**
>
> **Quota and rate.** Exceeding Google's API quota is returned as an HTTP 429 error (Too Many Requests). This error is not a transient glitch — blind persistence and immediately resending can lead to the account being suspended by the provider. The 429 must be respected, backed off from, and the next time window must be waited for.
>
> **Report format.** A report must be structured JSON, uniform and machine-readable, sent as an attached file. Any attempt to send an open report in free text (plaintext) that cannot be parsed automatically will lead to the report being rejected — and the meaning of that rejection may be the loss of that round's league points.

The security layer of the reporting also relies on controlled authorization to the API. The agent's access to Gmail does not rely on a raw password but on authorization tokens measured according to the OAuth 2.0 standard [34], which allows granting scoped permission and revoking it when needed. The full setup process for OAuth and for the Gmail API credentials is detailed in Appendix A.

<!-- page 97 -->

## 9.4 GitHub Submission: Structure, Contents, Two Repositories

Submission is done on GitHub. Every repository must be accessible to the lecturer: either it is public, or it is explicitly shared with the lecturer's address [lecturer's address]. Every team submits two separate repositories: one repository for the Cop agent and a second repository for the Robber agent, and provides two links — a link to the Cop repository and a link to the Robber repository.

<!-- page 98 -->

> **Two Repositories, Mandatory Cross-Link, and Two Links in the Submission**
>
> Every team develops two agents — Cop and Robber — in two separate GitHub repositories, accessible to the lecturer (public or shared with [lecturer's address]). The README.md file of each repository must include a link to the other repository of the same team: the Cop's README links to the Robber's repository, and vice versa. The file submitted on the LMS must contain both links (Cop and Robber), and in the end-of-game email — in the attached JSON file — all four links appear: the two links of team A and the two links of team B.

### 9.4.1 Mandatory Repository Contents

Every GitHub repository must include, at minimum: a README.md file (the academic report, see below); configuration files (`config/`); Product Requirements Document (PRD) files used to build the code; a work-plan file (PLAN); and task files (TODO). These files tell the story of the development and allow an examiner to reconstruct the working process — not just the final result. The full submission guide — branches, version tagging, and a checklist — is consolidated in Appendix C.

<!-- page 99 -->

### 9.4.2 README Contents

The heart of the documentary submission is the academic report in the README.md file at the root of each repository. The list below details the mandatory components — the absence of any one of them detracts from the submission:

> **Mandatory Contents of the Academic Report in the README**
>
> 1. **The chosen Dec-POMDP model.** A scientific description of the formalism you adopted for modeling the pursuit — the state space, the observations, and the uncertainty — as set out in Chapter 1.
> 2. **FastMCP orchestration dilemmas.** A discussion of the development considerations around orchestrating communication between the agents: queue management, handling of network failures, and the roles of the Gatekeeper and Orchestrator (Chapter 2, Chapter 8).
> 3. **The strategies implemented.** A detailed account of the decision-making mechanism you chose — heuristics (Manhattan distance, Bayesian belief map), a language-model-based (LLM) strategy, or, as an optional alternative, Q-Learning (Chapter 6).
> 4. **Learning curves (if RL was used).** If you trained an agent using reinforcement learning — learning curves as empirical evidence of policy convergence.
> 5. **Screenshots — an absolute requirement.** From the Live GUI (belief map) and from the replay application (Replay App), demonstrating Verified OK (Chapter 7).
> 6. **A link to the companion repository.** The link to the team's other GitHub repository (Cop/Robber), as required above.

## 9.5 Chapter Summary

We saw that the project is tested not in a closed lab but in a live league, in which the diversity incentive rewards facing new opponents and computational fairness rewards algorithmic cleverness over raw computing power. We broke down the reporting automation over the Gmail API and the Gatekeeper pattern — the quota manager, the token bucket, and the DOS detector — as a protective layer without which an autonomous agent could wreak havoc on a live account. We examined the mathematical rule of the token bucket and the structure of the

<!-- page 100 -->

signed, mandatory JSON. In the next chapter we will broaden the scope to the overall development considerations of the system — robustness, testing, and deployment.

# 10 Recommended Development Priority Order and Development Process

## 10.1 Chapter Objectives

This chapter is the assembly chapter, and it is entirely in the nature of a recommendation: having understood the theory, the board, the communication, and the strategy, the decisive question remains — in what order should all of this be built? By the end of the chapter you will know: why it is recommended that a complex multi-agent system be built in graduated layers rather than all at once; what the recommended seven-stage priority order is; which milestones it is recommended to complete before moving to the next stage; and why skipping the foundations in favor of jumping straight to encryption or the cloud can be a recipe for failure. This is the chapter that converts the theoretical knowledge of the entire book into a recommended, executable work plan.

## 10.2 Why Build in Layers

The great temptation for a beginning developer is to build the impressive system first — the encryption, the tunnels to the cloud, the artificial intelligence that composes lies. But a distributed system is not a tower built from the roof downward. What is the risk in placing the encryption layer on top of a communication infrastructure that has not yet been proven? When an encrypted message fails to reach its destination, we will not know whether the culprit is the cryptography, the server, or the underlying logic — the multiplication of unproven variables turns every glitch into an impossible investigation.

The principle of Incremental Delivery states that every layer is built, tested, and stabilized before the layer above it is laid upon it [5]. Every stage ends with a system that works end to end, even if narrow in scope. This way, at any given moment, the space of possible faults is narrowed down to only the last layer we added. On the other side of the same principle stands Production Readiness: a system is not considered finished when it runs on the developer's machine, but when it withstands the failures, loads, and disconnections of the real world [30]. These two principles — building incrementally and preparing for failure — are the backbone of the priority order we now set out.

> **Recommended: Layer-by-Layer Construction Using Multiple PRD Files**
>
> A recommended way to implement graduated construction is to split the software specification into several separate Product Requirements Document (PRD) files, one per layer. You start from the first PRD, generate the code from it, verify that everything works correctly — and only then add the next PRD layer. This way each layer is defined, generated, and tested separately, and the space of faults at any moment is narrowed down to the last layer you added. Writing a good PRD for the AI agent is a skill in its own right — see the recommendations file for writing and submitting software with the help of AI agents in the course introduction.

The engineering insight above gains added force when examined from the angle of the course's learning objectives.


<!-- page 101 -->

> **Connection to the Course**
>
> This chapter is the convergence point of the entire course "Orchestration of AI Agents," from L01 to L11. The staged development process is exactly the software development life cycle (SDLC) of the vibe-coding approach that opened the course (L01): define a narrow target in natural language, implement, test, and expand. The layers themselves recycle the entire learning journey — the foundations of deep learning (L02 through L04: neurons and backpropagation, sequences and RNN/LSTM, transformers and self-attention); the agents, the orchestrator, and token consumption (L05), and assembling teams of agents and tools (L06); the knowledge graphs of Graphify (L07) and running a local language model (L08); the conversation between two agents over MCP (L09) and distillation from the cloud to the local model (L10); and finally we imbue the agents with dynamic pheromone trails and collective memory (L11). The final project is not a new topic but the integration of everything you have learned: at every stage you will recognize the lecture that prepared you to build it.

## 10.3 The Seven Development Priorities — Seven PRD Files

To rein in the complexity of the project, a staged ladder of development priorities is recommended. It is recommended to implement each stage as a separate PRD file and in order, so that each stage lays a solid foundation on which the next one relies — seven stages, seven PRD files.

### 10.3.1 Stage 1: Base Logic

First, the physical core of the game is established, with no communication or intelligence whatsoever: the grid of size [board size] (default 7×7), the movement rules, [the barrier quota], and simple capture detection based on coordinate overlap. At this stage the entire system runs in a single process. Practical meaning: if two agents cannot move correctly on a local board, there is no point connecting a network between them. This is the foundation presented in Chapter 3.

<!-- page 102 -->

### 10.3.2 Stage 2: Basic FastMCP Infrastructure

Now the agents are separated into separate processes: the servers are set up and the tools are programmed to receive and send pure geometric information over Localhost[8]. The agents still speak only in numeric coordinates. Practical meaning: the goal of this stage is to prove that the pipe works — that a message sent from one agent arrives at the other — before it is loaded with complex content. This infrastructure was built in Chapter 2.

### 10.3.3 Stage 3: "Blind" Strategy Module

With a working communication pipe, an initial version of the strategy module is wired up — a simple decision-making tool that operates in a world of complete and accurate information. The implementation choice is yours: a direct heuristic (Manhattan distance, Bayesian belief), a policy based on a language model (LLM) mapped directly to a move, or — optionally — the Bellman equation/Q-Learning to find the shortest path[22] for groups that choose to do so. The module is "blind" in the sense that there is not yet scent, natural language, or deception. Practical meaning: this isolates the correctness of the decision-making core from the noise of uncertainty, which will only be added in the next stage. These foundations were discussed in Chapter 6.

### 10.3.4 Stage 4: Language and Scent Integration

This is the step-up stage. Rigid coordinates are replaced by free-language reporting; the dynamic pheromone equations and their decay are implemented; and, at the same time, the language model (LLM) is embedded for inference and for constructing lies. Practical meaning: this is where the uncertainty that is the heart of the project is born — combining scent dynamics (Chapter 4) with strategic inference (Chapter 6). This is the most sensitive stage, and therefore it comes only after the infrastructure and logic have been proven.

### 10.3.5 Stage 5: Cloud Exposure and Tunneling

Moving from Localhost to public addresses using ngrok or Localtonet, and connecting agents from remote computers[10]. Practical meaning: from this point on the system is no longer a simulation on a single machine but a genuine distributed system, with all the latency and disconnection challenges that entails. This is an extension of the same MCP infrastructure from Chapter 2, now over the network.

<!-- page 103 -->

### 10.3.6 Stage 6: Security and Cryptography

Only once remote communication works is it wrapped in the Commit-Reveal mechanisms; the Nonce generator is written, and hardware attestations (Step-0) are integrated. Practical meaning: encryption adds a layer of trust on top of communication already proven operationally reliable — an ordering that prevents confusion between a network fault and a cryptographic fault. These mechanisms were detailed in Chapter 5.

### 10.3.7 Stage 7: Reporting and Visualization Shell

Finally, the outer shell is built: connecting the Gmail API via OAuth 2.0 (detailed in Appendix A), completing the GUI, and polishing the Replay App. Practical meaning: this is the experience and documentation layer, built last because it consumes all the layers beneath it. These topics rely on the league and interface chapters, Chapters 9 and 7.

**Table 3: Mapping the Seven Stages (Seven PRD Files) to the Book's Chapters**

| Stage | What Is Built | Relevant Chapter |
|---|---|---|
| 1 | Grid [board size], movement rules, [barrier quota], capture detection | Chapter 3 |
| 2 | FastMCP servers and geometric tools over Localhost | Chapter 2 |
| 3 | Initial strategy module: heuristics, LLM policy, or Bellman/Q-Learning (optional) | Chapter 6 |
| 4 | Natural language, scent and decay equations, LLM integration for deception | Chapter 4, Chapter 6 |
| 5 | Transition to public addresses and tunneling (Localtonet/ngrok) | Chapter 2 |
| 6 | Commit-Reveal, Nonce generator, hardware attestations (Step-0) | Chapter 5 |
| 7 | Gmail API over OAuth 2.0, GUI, Replay application | Chapter 9, Chapter 7, Appendix A |

<!-- page 104 -->

**Incremental build: each stage runs end-to-end before the next is added**

1. Base Logic
2. MCP Infra
3. Strategy
4. Language + Scent
5. Cloud + Tunnel
6. Security
7. Reporting Shell

**Figure 15:** The development roadmap as ascending stairs: each stage rests on the one before it, and only after it runs end-to-end is the next stage added.

What the figure shows: seven numbered boxes descending like stairs from upper-left to lower-right, with a cumulative construction arrow connecting each stage to the next. How to interpret it: the staircase structure emphasizes that there are no jumps — each step rests on the one beneath it, just as every code layer rests on the stability of the one before it. The caption at the top reminds us that moving between steps is conditional on the current stage running end-to-end. "What if" analysis: if a step is omitted — for example jumping from Stage 2 directly to Stage 6 — the steps above it are left hanging in the air: the Commit-Reveal mechanism would be built on top of communication that has not been proven, and every fault would turn into an unsolvable, multi-variable investigation. A local example implementation of stages 1–4 and 6–7 is available in the code repository in Appendix D.

<!-- page 105 -->

## 10.4 Milestones and Development Discipline

The power of the recommended priority order lies in consistent implementation. For each stage it is recommended to define a discrete milestone: a binary criterion that should be satisfied before moving forward. A milestone is not "the code was written" but "the behavior was observed end-to-end" — precisely the spirit of production-readiness[30]. A list of all mandatory rules — do's, don'ts, and recommendations — is consolidated as a single categorical mapping in Appendix E.

### Milestone Checklist

Make sure every item works and has been observed before moving on to the next stage:

- **Stage 1:** two agents move legally on the [board size] grid; a move beyond the [barrier quota] is rejected; coordinate overlap triggers a capture.
- **Stage 2:** a geometric message sent from Agent A over Localhost is received and correctly decoded by Agent B.
- **Stage 3:** given a known target location, the agent computes and executes the shortest path without manual intervention.
- **Stage 4:** free-language reporting is translated into inference; the scent map is updated and decays at every step; the LLM produces a hint (true or false).
- **Stage 5:** an agent on a remote computer connects via ngrok and plays a full round against the local agent.
- **Stage 6:** a move is committed via Commit and then revealed via Reveal with a valid Nonce; Step-0 verifies hardware.
- **Stage 7:** a game summary is sent via Gmail; the GUI displays the state; the Replay App replays a recorded round.

Before moving on to the next exercise, it is worth noting an important recommendation regarding the correct learning pace.

<!-- page 106 -->

> **Recommended: Don't Skip Ahead**
>
> It is recommended not to approach cryptography or the cloud before the base logic and the MCP infrastructure over Localhost work end-to-end. Skipping the foundations may not save time but rather double it: a fault in an upper layer will hide behind instability in the layer beneath it, and you will lose hours investigating a source that does not exist. It is recommended to build the stairs from the bottom up.

## 10.5 Chapter Summary

We laid out the recommended seven-stage development priority order — from base logic, through MCP infrastructure, blind strategy, language and scent, cloud, security, up to the reporting shell — and recommended implementing each stage as a separate PRD file, as a direct application of the principles of incremental delivery and production-readiness. We saw that each stage corresponds to a chapter in the book and a lecture in the course, and that discrete milestones and a recommended discipline of staged construction are what turn a plan into a product. With this roadmap in hand, the theoretical knowledge of the entire book becomes an executable build process — and that, ultimately, is the real test of development.

<!-- page 107 -->

# 11 Summary and Look Ahead

## 11.1 Chapter Objectives

By the end of this chapter you will understand why the project before you is not merely a programming assignment but an exercise in developing complex systems under real network conditions; you will identify the four metrics that determine a team's success — coordination, adaptation, integrity, and architecture — and you will know how the skills you have acquired are reflected in distributed AI systems in industry. This chapter does not add a new mechanism; it ties together the threads of the entire book into a single picture.

<!-- page 108 -->

## 11.2 The Arc of the Book: From Modeling Uncertainty to a Live League

When we opened the book, we framed the race as a Dec-POMDP: two distributed agents, a multi-dimensional state space, and partial observation that is the heart of the uncertainty (Chapter 1)[2]. This distinction was the starting point for everything that followed, since the moment we accepted that there is no central server and no external referee, we were forced to build the rules of the game, trust, and decision-making from the ground up.

What, then, is the path we traveled? It is not a list of topics but a developmental narrative with an internal logic. From the abstract modeling of uncertainty we moved to the infrastructure that allows two strangers to communicate without an intermediary — the P2P architecture over FastMCP (Chapter 2). But communication between untrusting rivals requires a mechanism to prevent cheating: so we dove into the cryptography of Commit-Reveal and integrity proofs (Chapter 5)[20], which turn a verbal promise into a binding mathematical contract. At the same time, we learned how an agent can act intelligently precisely when it cannot see its rival: through scent trails inspired by stigmergy (Chapter 4)[14], which convert distributed spatial memory into computable probability.

On top of this infrastructure we placed the decision-making brain. The belief map and selection algorithms (Chapter 6) taught the agent to weigh immediate reward against strategic patience, and to translate a decaying scent field into a move. Then — once the engine was working — we assembled the development shell around it: the Gatekeeper and Orchestrator patterns (Chapter 8, Chapter 10), which ensure that resilient code does not crash under malicious input, and the Live GUI and Replay tools (Chapter 7), which turn an opaque run into a transparent, auditable game. Finally, we stepped out of the lab into the world: the live league, games against other teams, and reporting results via the Gmail API (Chapter 9). Each layer rests on the one before it; remove one, and the entire tower sways.

<!-- page 109 -->

## 11.3 The Project as Systems Development, Not a Coding Exercise

What is the essential difference between a programming exercise and systems development? A programming exercise is tested in a sterile environment, where the input is predictable and there is no adversary. A system, by contrast, is measured in a noisy world: communication lines drop, a rival sends a malformed message, a local clock drifts, and a public URL disconnects mid-turn. This project forces you to deal with all of these at once, simultaneously.

This is the insight to carry forward from here: the quality of your code is measured not when everything works, but when something goes wrong. An agent that beats a friendly partner but crashes against a hostile rival has not truly solved the problem — it has only solved the easy version of it. This distinction is what separates someone who wrote a program from someone who developed a system.

<!-- page 110 -->

## 11.4 The Four Metrics of Success

When we examine how a team performs in the real world of distributed AI systems, success converges into four metrics. They are not independent of one another — they are four facets of the same developmental capability — but each is examined in a different chapter and is expressed in a tangible code component.

**Table 4: The Project's Success Metrics and the Submission Criterion**

| Metric | Expression in the Project | Chapter |
|---|---|---|
| Coordination | Queue management, P2P protocol over FastMCP, and synchronization of two agents without a central referee | Chapter 2 |
| Adaptation | Both agents symmetrically contend with uncertainty: each side builds a belief about its rival's location from the rival's decaying scent map and from a verbal hint, and updates a probabilistic belief map | Chapter 4, Chapter 6 |
| Integrity | Preventing cheating using Commit-Reveal and SHA-256, and a complete Audit pass | Chapter 5 |
| Architecture | Adherence to the Gatekeeper and Orchestrator patterns and fault-resilient code | Chapter 8, Chapter 10 |
| Submission Criterion | The entire project — code, structure, and submission — is evaluated according to the recommendations file for writing and submitting software with the help of AI agents, from the course introduction | Course Introduction |

How to read the table: each row is a question the real world will ask of your system. Does it know how to coordinate with a party outside its control? Does it adapt when information is partial? Does it stay honest when cheating would pay off? And does its architecture hold up under load and failure? A team that answers yes to all four is not merely running an agent — it is operating a system.

<!-- page 111 -->

> **Beyond the Course**
>
> The four metrics are not unique to the Cop–Robber race; they are the common currency of every distributed AI system in industry, and they connect directly to three pillars of the Orchestration of AI Agents course. Distributed coordination is precisely the challenge of two agents conversing over MCP and calling external tools (Lecture L09), and of mass-producing teams of agents and tools with frameworks such as LangChain, LangGraph, and CrewAI (Lecture L06)[5]. Adaptation under uncertainty drew its inspiration from the distributed agent swarm of Lecture L11: dynamic scent trails and collective swarm memory, in which successes update a shared representation and a decay mechanism prevents fixation — all without a supervising controller. Cryptographic integrity is the foundation of supply-chain security, model signing, and distributed commerce. And resilient architecture — the Gatekeeper and Orchestrator patterns — is precisely what separates a demo that works once from a production service that runs for months. The skills you acquired here are not an academic exercise; they are the toolkit of a developer of distributed AI systems.

<!-- page 112 -->

## 11.5 Final Pre-Submission Checklist

Before you submit the project, stop and make sure that every layer you built throughout the book actually functions end-to-end. The following checklist maps every requirement to the chapter in which it was taught, and to the accompanying appendices.

<!-- page 113 -->

### Final Pre-Submission Checklist

Go through every item and make sure it is actually checked off, not merely intended:

- **Base logic works:** the game engine runs a complete race without crashing, and the scoring rules (Chapter 3) are enforced correctly.
- **FastMCP over a public URL:** the two agents communicate over the P2P protocol (Chapter 2) through an accessible address, not only on localhost.
- **Commit-Reveal and a passing audit:** the commit-and-reveal mechanism (Chapter 5) is active, and the Audit completes successfully without detecting any forgery.
- **Scent map and belief map:** the stigmergy trails (Chapter 4) and the belief map (Chapter 6) are computed and actually influence decisions.
- **Live GUI and Replay App with Verified OK:** the viewing tools (Chapter 7) display the game in real time and in replay, with a valid verification stamp.
- **Gmail API reporting as JSON — from both sides:** at the end of the game both teams agree on the result, and each team sends its own completion report in structured JSON format via the Gmail API (Chapter 9); if a side did not send a report, that side will not be credited with a score. For permission configuration, see Appendix A.
- **GitHub repository with a Git Tag and an academic README:** the code is tagged with a version and accompanied by an organized README; for the submission procedure, see Appendix C.
- **At least [minimum games to pass] games against different teams:** you have completed at least [minimum games to pass] races against different rivals in the live league (Chapter 9); for the shared configuration file, see Appendix B, and for the binding values, see the central parameters table in Appendix F.

Having reviewed the principles of the summary, we will now consolidate the practical submission requirements into an organized checklist.

<!-- page 114 -->

### Submission Checklist: Moodle, GitHub, and PDF Report

a. Part of the assignment is knowing how to define and specify to the agent the appropriate instructions for generating the requested code. Make sure a folder containing the markdown files (the PRD files) is attached to GitHub, and that the root of the GitHub repository is readable (README.md). Make sure the code and the entire project comply with all the guidelines in the course introduction — in the file "Recommendations for Writing and Submitting Software with the Help of AI Agents"; the assignment will be evaluated according to the principles in that file.

b. Submission is done via Moodle according to the standing guidelines. The software code must be submitted on GitHub and shared with the instructor.

c. Each member of the team submits the assignment separately on Moodle.

d. The submitting team must be given a unique eight-character identifier code, with no spaces.

e. Moodle includes a Word file containing a template for creating the PDF file to be submitted. Fields must not be changed, and elements must not be moved within the template — you should only fill in the details, save as PDF, and submit.

f. A self-assessment grade must be given for code quality only — not for the league game result. A self-assessment grade based on the game result would distort the criterion for measuring code quality.

A list of all mandatory rules — do's, don'ts, and recommendations — is consolidated as a single categorical mapping in Appendix E.

<!-- page 115 -->

## 11.6 Looking Forward: Toward Autonomous Distributed AI

The race you built is a scaled-down model of a question that will accompany the field of artificial intelligence over the coming decade: how do you get many autonomous entities — who do not trust one another, do not see the full picture, and are not subject to a central controller — to act together coherently, honestly, and resiliently? This is not a theoretical question. It lies at the very heart of the distributed, multi-agent AI systems whose potential research has only just begun to explore; reinforcement learning (Multi-Agent RL) is just one of the optional tools that certain teams may choose alongside LLM-based strategies and heuristics[26].

If you learned one thing here that stays with you, let it be this: a good distributed system is not a collection of clever agents, but an architecture that enables mediocre agents to work together with trust, adaptation, and resilience. This capability — to coordinate, to adapt, to preserve integrity, and to build correctly — you carry with you out of this book. The world of autonomous, distributed artificial intelligence has only just opened before you; you now have the tools to build within it, not merely to use it. Go and build.

<!-- page 116 -->

# References

1. LLM-Based Multi-Agent Orchestration: A Survey of Frameworks, Communication Protocols, and Emerging Patterns, arXiv preprint, 2025.
2. D. S. Bernstein, R. Givan, N. Immerman, and S. Zilberstein, "The complexity of decentralized control of Markov decision processes," *Mathematics of Operations Research*, vol. 27, no. 4, 819–840, 2002. doi: 10.1287/moor.27.4.819.297
3. F. A. Oliehoek and C. Amato, *A Concise Introduction to Decentralized POMDPs* (SpringerBriefs in Intelligent Systems). Springer, 2016. doi: 10.1007/978-3-319-28929-8
4. L. P. Kaelbling, M. L. Littman, and A. R. Cassandra, "Planning and acting in partially observable stochastic domains," *Artificial Intelligence*, vol. 101, no. 1–2, 99–134, 1998. doi: 10.1016/S0004-3702(98)00023-X
5. S. Newman, *Building Microservices: Designing Fine-Grained Systems*, 2nd ed. O'Reilly Media, 2021.
6. Anthropic. "Introducing the Model Context Protocol," Accessed: Jul. 9, 2026. [Online]. Available: https://www.anthropic.com/news/model-context-protocol
7. Model Context Protocol. "Model context protocol specification," Accessed: Jul. 9, 2026. [Online]. Available: https://modelcontextprotocol.io/specification

<!-- page 117 -->

8. J. Lowin. "FastMCP: The fast, Pythonic way to build MCP servers and clients," Accessed: Jul. 9, 2026. [Online]. Available: https://gofastmcp.com/
9. Krishnan, *Beyond Context Sharing: A Unified Agent Communication Protocol (ACP)*, arXiv preprint, 2025.
10. ngrok. "ngrok documentation: Secure tunnels to localhost," Accessed: Jul. 9, 2026. [Online]. Available: https://ngrok.com/docs
11. J. Rosenberg, R. Mahy, P. Matthews, and D. Wing, "Session traversal utilities for NAT (STUN)," Internet Engineering Task Force, RFC 5389, 2008. doi: 10.17487/RFC5389
12. R. Nowakowski and P. Winkler, "Vertex-to-vertex pursuit in a graph," *Discrete Mathematics*, vol. 43, no. 2–3, 235–239, 1983. doi: 10.1016/0012-365X(83)90160-7
13. T. D. Parsons, "Pursuit-evasion in a graph," *Theory and Applications of Graphs*, Lecture Notes in Mathematics, vol. 642, 426–441, 1978. doi: 10.1007/BFb0070400
14. G. Theraulaz and E. Bonabeau, "A brief history of stigmergy," *Artificial Life*, vol. 5, no. 2, 97–116, 1999. doi: 10.1162/106454699568700
15. E. Bonabeau, M. Dorigo, and G. Theraulaz, *Swarm Intelligence: From Natural to Artificial Systems*. Oxford University Press, 1999.
16. M. Dorigo, V. Maniezzo, and A. Colorni, "Ant system: Optimization by a colony of cooperating agents," *IEEE Transactions on Systems, Man, and Cybernetics, Part B*, vol. 26, no. 1, 29–41, 1996. doi: 10.1109/3477.484436
17. S. Thrun, W. Burgard, and D. Fox, *Probabilistic Robotics*. MIT Press, 2005.
18. M. Blum, "Coin flipping by telephone: A protocol for solving impossible problems," in *Proceedings of the 24th IEEE Computer Society International Conference (COMPCON)*, 1983, 133–137.

<!-- page 118 -->

19. National Institute of Standards and Technology, "Secure hash standard (SHS)," NIST, Federal Information Processing Standards Publication FIPS PUB 180-4, 2015. doi: 10.6028/NIST.FIPS.180-4
20. S. Goldwasser, S. Micali, and C. Rackoff, "The knowledge complexity of interactive proof systems," *SIAM Journal on Computing*, vol. 18, no. 1, 186–208, 1989. doi: 10.1137/0218012
21. R. C. Merkle, "A digital signature based on a conventional encryption function," *Advances in Cryptology — CRYPTO '87*, Lecture Notes in Computer Science, vol. 293, 369–378, 1987. doi: 10.1007/3-540-48184-2_32
22. C. J. C. H. Watkins and P. Dayan, "Q-learning," *Machine Learning*, vol. 8, no. 3–4, 279–292, 1992. doi: 10.1007/BF00992698
23. R. S. Sutton and A. G. Barto, *Reinforcement Learning: An Introduction*, 2nd ed. MIT Press, 2018.
24. R. Bellman, "A Markovian decision process," *Journal of Mathematics and Mechanics*, vol. 6, no. 5, 679–684, 1957.
25. *AgentNet: Decentralized Evolutionary Coordination for LLM-Based Multi-Agent Systems*, arXiv preprint, 2025.
26. L. Buşoniu, R. Babuška, and B. De Schutter, "A comprehensive survey of multiagent reinforcement learning," *IEEE Transactions on Systems, Man, and Cybernetics, Part C*, vol. 38, no. 2, 156–172, 2008. doi: 10.1109/TSMCC.2007.913919
27. R. Lowe, Y. Wu, A. Tamar, J. Harb, P. Abbeel, and I. Mordatch, "Multi-agent actor-critic for mixed cooperative-competitive environments," in *Advances in Neural Information Processing Systems (NeurIPS)*, 2017.
28. A. Vaswani et al., "Attention is all you need," *Advances in Neural Information Processing Systems (NeurIPS)*, 2017.
29. Z. Ji et al., "Survey of hallucination in natural language generation," *ACM Computing Surveys*, vol. 55, no. 12, 1–38, 2023. doi: 10.1145/3571730

<!-- page 119 -->

30. M. T. Nygard, *Release It! Design and Deploy Production-Ready Software*, 2nd ed. Pragmatic Bookshelf, 2018.
31. E. Gamma, R. Helm, R. Johnson, and J. Vlissides, *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley, 1994.
32. Google. "Gmail API: Usage limits and sending email," Accessed: Jul. 9, 2026. [Online]. Available: https://developers.google.com/gmail/api/reference/quota
33. A. S. Tanenbaum and D. J. Wetherall, *Computer Networks*, 5th ed. Pearson, 2011.
34. D. Hardt, "The OAuth 2.0 authorization framework," Internet Engineering Task Force, RFC 6749, 2012. doi: 10.17487/RFC6749

<!-- page 120 -->

# Appendix A: Guide to Setting Up Gmail API and OAuth 2.0

The project's automated reporting infrastructure — in which an agent sends status reports to itself, to the instructor, or to the team at the end of each run — relies on the ability to send email programmatically via the Gmail API. However, a modern, secure approach does not use the user's regular password: instead, it relies on a secure token issued under the OAuth 2.0 standard[34]. This standard separates the user's identity from the authorization they grant to the application, thereby allowing the agent to act on your behalf without your personal secret ever being exposed in the code. This appendix guides you, step by step, from setting up the project in the cloud to the first authorization flow that grants the agent full autonomy[32].

## 1 The Five Setup Steps

The complete process consists of five ordered steps. Follow them in order; skipping a step (especially configuring the consent screen) will cause the authorization flow to fail at a later, more confusing stage.

### 1.1 Step A: Opening a Project and Enabling the Service — Cloud Console

Go to the Google Cloud Console and create a new project (or select an existing one). Within the project, go to the API library and explicitly enable the Gmail API service. This activation is what signals to Google's infrastructure that your project is permitted to call the mail endpoints.


<!-- page 121 -->

### Step B: Defining the OAuth Consent Screen (1.2)

Define the OAuth Consent Screen — the screen in which Google informs the user which permissions the application is requesting. Choose External mode (for users outside the organization) or Internal (within an organization that has Google Workspace), and add the students' email addresses to the group of authorized Test Users. While the application is in Testing mode, only users on this list will be permitted to complete the authorization flow.

### Step C: Restricting Permissions to the Necessary Minimum — Scope Restriction (1.3)

Define the permission scope (Scope) to the absolute minimum required: `https://www.googleapis.com/auth/gmail.send`. This scope permits only sending mail — nothing more. Never grant read permission to a project that doesn't need it. This is a fundamental information-security principle: the less a token is capable of, the smaller the damage if it leaks.

### Step D: Creating Access Credentials — Create Credentials (1.4)

On the Credentials page, create an `OAuth Client ID` of type `Desktop Application`. Download the `credentials.json` file to the project's local working directory. It is absolutely mandatory to add this file to `.gitignore` before pushing code to GitHub, in order to prevent secret exposure (in a public repository — to the entire world; and in a private repository shared with the instructor — to them as well). Forgetting this step is one of the most common and dangerous mistakes in cloud-based projects.

<!-- page 122 -->

### Step E: The First Authorization Flow (1.5)

On the first run of the code, Google's official libraries will open a browser window and ask you to approve the authorization. Once approved, the file `token.json` is automatically created, containing a short-lived Access Token alongside a long-lived Refresh Token. Thanks to the Refresh Token, the agent will be able to send reports completely autonomously — for many months, with no further manual intervention.

> **Critical: Never Push Secrets to the Repository**
>
> Both files — `credentials.json` (the application's secret identifier) and `token.json` (the signed tokens) — are secrets. Pushing them to GitHub is equivalent to publishing the key to your mailbox in public. Add the two lines `credentials.json` and `token.json` to the `.gitignore` file before the first commit. Remember: once a secret has been pushed to even a single commit in the history, deleting it from the current code is not enough — you must rotate the credentials in the console.

## 2. Token Anatomy: Access Token vs. Refresh Token

To understand why the infrastructure works without passwords, one must distinguish between the two types of tokens defined by the OAuth 2.0 standard [34].

### Access Token vs. Refresh Token

- **Access Token** — a short-lived token (typically expiring within about an hour) that is attached to every actual API request and authorizes it. Its quick expiration narrows the risk window if it leaks.
- **Refresh Token** — a long-lived token that is not sent to the mail API itself, but is used to obtain a new Access Token when the previous one expires. It is this token that grants the agent long-term autonomy: as long as the Refresh Token remains valid, no repeated human intervention is required.

The distinction between the two token types is not merely theoretical — it is what makes it possible to actually implement a central security principle, one that deserves to be highlighted in its own right.

<!-- page 123 -->

> **The Principle of Least Privilege**
>
> Note that we requested only the `gmail.send` scope, and not a broader scope such as `gmail.modify` or `mail.google.com`. This is a direct application of the principle of least privilege: grant a component exactly the permissions it needs for its task — and no more. The reporting agent only needs to send; therefore there is no reason for it to be able to read or delete mail. Restricting the scope turns a stolen token from a powerful weapon into an almost harmless, limited tool.

## 3. Implementation: A Minimal Send-Only Flow in Python

The code below illustrates the complete flow: loading the token from `token.json` (or creating it the first time), building the Gmail service, assembling and encoding a MIME message, and finally sending it. Note that the requested scope is restricted to `gmail.send` only, as required by the principle of least privilege.

<!-- page 124 -->

**Sending a Report via the Gmail API with OAuth 2.0**

```python
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Least-privilege scope: send only, no read/modify access
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def get_service():
    # Reuse token.json if it exists; otherwise run the consent flow once
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("gmail", "v1", credentials=creds)

def send_report(service, to_addr, subject, body):
    message = MIMEText(body)          # build a plain-text MIME message
    message["to"] = to_addr
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return service.users().messages().send(
        userId="me", body={"raw": raw}).execute()

if __name__ == "__main__":
    svc = get_service()
    send_report(svc, "grader@example.com", "Run report", "Episode finished.")
```

In practice, on the first run you replace the call that loads an existing token with the authorization flow `InstalledAppFlow.from_client_secrets_file(...)`, which generates `token.json`; after that, all subsequent runs load the existing token and refresh it automatically.

<!-- page 125 -->

## 4. Summary of Required Files

Only two files are required for the infrastructure, and both are secret and both must be included in `.gitignore`. The table below summarizes their role and origin.

**Table 5: The Files Required for the OAuth Infrastructure, Their Origin and Sensitivity**

| File | Source | Content | Add to `.gitignore`? |
|---|---|---|---|
| `credentials.json` | Downloaded from the console | Application's secret identifier | Yes — mandatory |
| `token.json` | Created on first run | Access and refresh tokens | Yes — mandatory |

<!-- page 126 -->

# Appendix B: A Unified Format for the Configuration File

## 1. Why a Shared Constitution? A Configuration File in a World Without a Referee

In a P2P-style distributed game, where the two agents confront each other directly with no central server acting as referee, a fundamental question arises: who determines the physics of the game? When a central server exists, it alone enforces the grid size, the maximum number of moves, and the scent decay rate, and both players are subject to its ruling. But in the absence of a referee, each side runs its own copy of the game logic — and if the two copies do not agree on exactly the same values, the match splits into two contradictory realities that cannot be reconciled.

The practical solution is to turn all the agreed-upon game conditions into a single, readable, and transparent source of truth, centralized in the file `config/game.json` — the signed constitution of the game. This file is not merely a collection of constants; it is the constitution that both sides agree to before the curtain rises, and it is loaded byte-for-byte identically on both ends and locked with a cryptographic signature. Alongside it, each peer holds a private file — `config/game.toml` — containing only its local settings (network port, strategy module selection, language-model mode for the verbal trash-talk game, email destination, and team identity), which are not subject to negotiation and need not be identical between the two sides. When the shared JSON file exists, its values override (overlay) the values of the same keys in the private TOML file, so that both agents enforce exactly the same physics: the same board, the same boundaries, the same decay rate. Thus, even though there is no third party to adjudicate, both sides compute the same result from the same rules.

<!-- page 127 -->

A further advantage is readability and configurability. Separating the parameters from the code makes it possible to change the conditions of the match — a larger grid, a stricter time limit, a wider scent field — without touching a single line of logic code. The values shown here are the book's agreed-upon defaults, and each of them can be re-tuned per match, as long as both sides load the same JSON file. A complete example of the configuration in JSON format is attached to the book as the file [configuration file] (see the variable table in Appendix F).

## 2. When JSON, When TOML — and Why

The project uses two configuration formats, each with a distinct role. The distinction is simple: everything that both sides must agree on is written in JSON; everything that is private and local to a single peer is written in TOML.

**JSON** — for shared, signed, and exchanged data. Written in this format are: (a) the agreed-upon game conditions — `config/game.json`; (b) the four standard files — the declaration, the configuration, the log, and the results report (Chapter 9); and (c) the rate-limiter configuration — `rate_limits.json`. JSON was chosen because it is an unambiguous, cross-language standard, supports canonical serialization (sorted keys) and therefore consistent hashing (`config_sha256`), and is suitable for byte-for-byte identity, cryptographic signing, and exchange between machines and between teams who may have written their code in different languages. Anything the opponent sees, verifies, or depends on must be here.

**TOML** — for private, local configuration only. Written in this format is exclusively the private file for each peer — `config/game.toml`: the network port, the opponent's address, the strategy module selection, the language-model mode, the LLM settings, the email, and the team identity. TOML was chosen because it is hand-edited by each team, is especially readable, and supports comments — a decisive advantage, since the `[strategy]` and `[trash_talk]` sections include code explanations that guide the student. This file does not cross the network and is not signed, and therefore does not need a canonical or hashable form. No value relevant to the opponent is found in it; if any value becomes shared, its place moves to JSON.

<!-- page 128 -->

> **The Decision Test:** Ask "Must the opponent agree to this value, or rely on it?" — If yes, it belongs in the shared JSON; if not, it stays in the private TOML.

## 3. The Signed Shared File

Below is the shared constitution file `config/game.json` with its sections: the board and agents (`board_and_agents`), movement and barriers (`movement_and_barriers`), scoring (`scoring`), pheromones (`pheromones`), network and league (`network_and_league`), and the rate-limiter gatekeeper (`rate_limiter_gatekeeper`). Both peers load a byte-for-byte identical copy, and the pre-match signature exchange refuses to play on any mismatch. The values here are the book's binding defaults (see the binding table in Appendix F).

<!-- page 129 -->

**The File `config/game.json` (The Signed Shared Conditions)**

```json
{
  "schema_version": "1.2",
  "agreed_between": ["group-a", "group-b"],
  "board_and_agents": {
    "grid_size": 7,
    "num_agents": 2,
    "thief_start": [3, 3],
    "cop_start": [0, 0],
    "axis_origin_corner": "top-left",
    "axis_start_index": 0
  },
  "world": {
    "map_area": "New York",
    "hint_max_words": 15
  },
  "movement_and_barriers": {
    "move_set": ["N", "S", "E", "W", "STAY"],
    "max_barriers": 14,
    "max_moves": 35,
    "survival_threshold": 35
  },
  "scoring": {
    "capture_cop": 20, "capture_thief": 5,
    "survival_cop": 5, "survival_thief": 10,
    "tie_score": 2, "technical_loss": 0
  },
  "pheromones": {
    "pheromone_center_intensity": 0.9,
    "pheromone_decay": 0.10,
    "pheromone_grid_size": 5
  },
  "network_and_league": {
    "response_timeout_sec": 30, "watchdog_timeout_sec": 60,
    "num_games": 1, "diversity_reward": 10,
    "min_games_to_pass": 2, "max_games_per_team": 10,
    "token_budget_per_series": 200000
```

<!-- page 130 -->

```json
  },
  "rate_limiter_gatekeeper": {
    "requests_per_minute": 30, "concurrent_requests": 2,
    "retry_backoff_sec": 5, "max_retries": 3, "queue_depth": 100
  }
}
```

Key fields correspond one-to-one to the binding parameter table: `grid_size` = [board size], `max_barriers` = [barrier quota], `scoring.capture_cop` = [capture score – Cop], and so on. The value of each field may change through negotiation (only in the stricter direction for parameters of "minimum" type), but the field names are fixed and binding. The `num_games` field is sent with a default value of `1` (a single sample match); the full league series requires [number of matches] matches.

## 4. The Private Per-Peer File

Alongside the shared JSON, each peer maintains its own `config/game.toml` — private, local, and not subject to negotiation. It contains the team identity, the network port and the opponent's address, the strategy module selection (`[strategy]`), the language-model mode for the verbal trash-talk game (`[trash_talk]`), the language-model settings (`[llm]`), the email destination, and the graphical settings. Below is an abbreviated skeleton:

<!-- page 131 -->

**The File `config/game.toml` (Private per Peer — Selected Excerpt)**

```toml
version = "1.10"

[game]
group_name = "My-Team"
group_id   = "my-team"
sub_game_number = 1
members = ["id-1001", "id-1002"]
repos = { cop = "https://github.com/you/repo", thief = "https://github.com/you/repo" }

[network]
my_port      = 8802                            # MY MCP server port
opponent_url = "http://127.0.0.1:8801/mcp"     # the only thing I know about the opponent
turn_timeout_seconds = 180

# [strategy] -- optional: point at YOUR brain subclass (else the shipped heuristic runs)
# thief_class = "my_team.strategy:MyThiefBrain"
# police_class = "my_team.strategy:MyPoliceBrain"

# [trash_talk] -- optional: HOW the banter is produced. The MOVE is always pure Python.
# provider = "template"   # template(0 tokens, default) | ollama | claude_api | claude_cli

[llm]
model = "claude-opus-4-8[1m]"     # MY choice; the opponent may differ
step_deadline_seconds = 30        # hard cap on LLM thinking per step

[email]
recipient = "rmisegal+uoh26finalgame@gmail.com"
mode = "draft"
```

<!-- page 132 -->

When `config/game.json` exists, the game-condition values within it override any corresponding key in the TOML — so the private file can never "weaken" a signed condition. The complete, binding dictionary of every parameter — its name, meaning, and value — is centralized in the binding parameter table in Appendix F.

<!-- page 133 -->

# Appendix C: GitHub Submission Requirements and Academic Report

This appendix defines the formal threshold requirements for submitting the project. It is important to internalize from the outset: the submission is not a single source file attached to an email, but a complete development artifact — a code repository accessible to the instructor (public, or private and shared with them), documented, and tagged — that tells the story of the system you built. The manner of submission is measured with the same rigor as the code itself, because in the real world of distributed artificial-intelligence systems, reproducibility and process transparency are an inseparable part of the deliverable.

## 1. The GitHub Repository: Structure, Branches, and Tagging

The submission infrastructure is a well-organized GitHub repository, accessible to the instructor — either public, or explicitly shared with the instructor's address [instructor's address]. The accessibility requirement is not a technical whim but a professional stance: good professional code is written to be read, examined, and reproduced by others. Development proceeds via branches — every significant capability is developed in a dedicated branch and merged into the main branch only after it has stabilized — in accordance with development practices for distributed systems and microservices [5].

The final submission version is not marked by the vague "latest branch state," but is fixed by means of a documented Git tag (Annotated Git Tag). The tag freezes a certain, unchallengeable point in time in the repository's history, and allows the grader to reproduce exactly the code that was submitted — and not a later version that may have been written after the deadline.

<!-- page 134 -->

**Tagging the Submission Version**

```bash
# Create an annotated, documented tag for the submission commit.
# The -a flag makes it an annotated tag (stored as a full object),
# and -m attaches the mandatory documentation message.
git tag -a v1.0-submission -m "Final submission: Police-Thief P2P, group N"

# Push the tag to the remote the grader can access
# (public, or private shared with the lecturer).
git push origin v1.0-submission

# (Optional) verify the tag was created and points to the right commit.
git show v1.0-submission
```

The tag `v1.0-submission` turns the selected commit into a stable reference point. Note that this is a shell command snippet, in which the comments are in English only — as is customary throughout all the operational instructions in this book.

## 2. The Academic Report: README.md

The heart of the documentation submission is an extended academic report written in the `README.md` file at the root of the repository. This is not merely an installation-instructions file, but a scientific document that explains the design decisions, justifies them, and presents the empirical evidence for their success.

> **The Content of the README Is Defined in Chapter 9**
>
> The mandatory content of the academic report — its five components, alongside the requirement for two repositories (Cop and Robber) and the cross-link between them — is fully defined in Chapter 9 ("Submission on GitHub: Structure, Content, and Two Repositories"). Make sure all the components are present in the `README.md` file of each of the two repositories.

<!-- page 135 -->

The requirement for screenshots is not merely formal: the belief map proves that the agent is indeed conducting probabilistic inference under partial observability, and the `Verified OK` indicator proves that the integrity of the match was preserved — that the encrypted chain of moves was checked and verified, similar to cryptographic proof mechanisms that establish trust without needing a trusted central party [20].

> **Never Upload Secrets to the Repository**
>
> If the repository is public, every file uploaded to it is visible to the entire world; and even if it is private and shared only with the instructor — it is still absolutely forbidden to upload credentials and access tokens — including the OAuth `credentials.json` and `token.json` (see Appendix A) and any configuration key or secret (see Configuration Appendix B). The root of the repository must include a `.gitignore` file that explicitly excludes these files, so that they are not accidentally included in a commit. A secret that has been leaked once is considered permanently exposed — even if it is deleted in a later commit, it remains in the Git history.

<!-- page 136 -->

## 3. Submission Checklist

The table below centralizes the threshold conditions. Make sure each item meets the required status before creating the submission tag.

**Table 6: Submission Checklist**

| Item | Required Status |
|---|---|
| Two GitHub repositories (Cop, Robber) accessible to the instructor | Public, or private and shared with the instructor |
| Cross-link between the repositories + two links in the submission | Present |
| Documented Git tag for the submission version — `v1.0-submission` | Pushed |
| Report components in `README.md` (Chapter 9) | Complete in both repositories |
| Screenshots of the belief map (GUI) | Attached |
| `Replay` screenshot with `Verified OK` | Attached |
| At least two matches against different teams | 2 or more |
| End-of-match email — each team separately | Both sides sent |
| No secrets uploaded to the repository (`.gitignore`) | Verified |

<!-- page 137 -->

> **Systems Development, Not Just Programming**
>
> Remember the message that runs through the entire book: the project before you is not a mere programming assignment, but an exercise in complex systems development under real network conditions. Success is measured by four central metrics — coordination between the agents; adaptation to uncertainty by means of stigmergy-based scent trails [14]; ensuring integrity through advanced hashing mechanisms [20]; and adherence to correct code architecture (the Gatekeeper and Orchestrator patterns) [5]. These four metrics — not the elegance of any single algorithm — are what will determine each team's success and its ability to cope in the real world of distributed artificial-intelligence systems. A complete summary of these metrics is provided in Chapter 11.

<!-- page 138 -->

# Appendix D: The Sample Code Repository — A Basic Simulation Implementation

Alongside the book of rules and guidelines, a sample code repository is provided — a basic, public implementation of the Cop and Robber game, shared among the students in the course. The repository is available on GitHub:

**[sample code repository]**

The full address of the repository appears in the variable table in Appendix F. This appendix describes version 3.0.0 of the repository's code (the same version also appears on the book's title page). There is a deep, bidirectional version link between the code and the book: the code version is read from the repository's version file and is updated here automatically on every recompilation of the book, and the book version (3.0.0) is updated in the repository's README file on every commit.

> **What This Repository Is — and, More Importantly, What It Is Not**
>
> This repository is intended for learning purposes only. It demonstrates the basic game flow and the simple graphical interface, with no strategy at all — the agents move minimally in order to show how the system is assembled and runs end to end. Do not start the project from this repository, because it does not meet the full project specification: it was written as a minimal example, not as a submission solution. You are permitted to use parts of the code or modify it, and it is recommended that you use it to learn how a particular component was implemented or to clarify a point that was not understood from the book — but your own solution must independently meet the full requirements (see the binding parameter table in the final appendix).

<!-- page 139 -->

## 1. What the Example Shows

The repository runs two independent peers — Cop and Robber — each in a separate process, with its own configuration file and its own FastMCP server, exactly like two students playing against each other from two machines. It demonstrates: movement on the board, placing barriers, the scent-trail mechanism and the belief map, a Commit-Reveal protocol based on SHA-256 with full auditing at the end of the match, a token-consumption gauge, and a JSON report sent as a Gmail draft. The strategic logic — smart move selection — was intentionally left minimal, and it is the core that you are meant to develop.

## 2. Code Layout

According to the repository's `README.md` file, the architecture is built in layers:

- **Interface** (Tkinter GUI/CLI) — a live window and a Replay application.
- **SimulationSdk** - the single business entry point.
- **PeerRuntime** - one independent peer: negotiation → turn loop → audit.
- **domain** - board, scent, belief, state, rules, cryptography, negotiation, protocol, and the decision "brain."
- **infra** - language-model providers for the verbal trash-talk game (free template by default, local Ollama, or cloud CLI/API), the MCP transport to the opponent's server, and the email sender.
- **shared** - the configuration manager, the rate limiter, system info, and versioning.

Every Python file is short (up to about 150 lines of code), development is accompanied by tests (pytest), and all configuration is external — `config/police/` versus `config/thief/`, in full separation. The student's two extension points are clearly separated in the private configuration file: the `[strategy]` section (`police_class`/`thief_class`) points to your own "brain" class that inherits from `BrainBase` and overrides `_pick_move` (and, for the Cop, also `_decide_move`) — this is where the grade is earned; and the `[trash_talk]` section chooses how the taunting text is produced (default `template` — zero tokens). The move is always computed in Python; the language model touches only the verbal layer.

<!-- page 140 -->

## 3. How to Run

**Running Both Peers in Two Terminals**

```bash
uv sync

# Terminal 1
uv run python -m police_thief peer --role police
# Terminal 2
uv run python -m police_thief peer --role thief

# Replay a saved match:
uv run python -m police_thief replay --log logs/police_match.json
```

After you have run both peers and watched the match unfold in real time, it's worth knowing an efficient way to study the code structure itself in depth.

> **Tip: Turn the Repository into a "Chatbot" About the Code Using NotebookLM**
>
> A convenient way to learn the code is to convert all the repository's files to text format (`.txt`), load them into NotebookLM, and then ask questions about the code as if you had a dedicated conversational agent for the simulation: "Where is the belief map calculated?", "How is the Commit-Reveal protocol enforced?" and so on. This way you can quickly understand a particular component without reading the entire repository manually.

Beyond understanding the code itself, a substantial part of the submission is an organized documentation of the performance and insights; the template below is intended for that purpose.


<!-- page 141 -->

> **Highly recommended: Research and Performance Analysis Report — a template for your own planning**
>
> In the `docs/` folder of the reference repository, a research and performance analysis report is attached (`RESEARCH-REPORT-Performance-Analysis.md`). Based on the code itself, the report analyzes the agent's resource consumption: how many language-model calls are required in a full series, how they stack up against the rate limits (RPM and message windows) of the various providers — Ollama, Gemini, ChatGPT, Claude, and Grok — in their free versions and paid subscriptions, and how the fallback mechanism ensures that every game finishes even when a provider is blocked. Read it to plan and forecast your own project: choose the game strategy and the language model suited to your budget and infrastructure, and understand in advance where a bottleneck is expected. And more importantly — use it as a template: repeat the same analysis on your own plan, strategy, and infrastructure, so that your decisions rest on numbers rather than guesswork.

## 4 Terms of Use / How You May Use It

You may use parts of the code, learn from it, and modify it for the purposes of the project. However, remember two principles: (1) the repository is a learning starting point, not a submission skeleton — your solution is graded against the full specification; (2) the repository's license is an educational-use license (see the `LICENSE` file). Wherever the repository deviates from the book, the book and the mandatory parameter table take precedence.

<!-- page 142 -->

# Appendix E: Mapping of Mandatory Rules — Do's, Don'ts, and Recommendations

The study of distributed artificial-intelligence systems, in particular those operating under a model of decentralized partially observable Markov decisions (Dec-POMDP), requires a deep understanding of the regulatory rules. This appendix consolidates the list of mandatory system rules scattered throughout the book into a single categorized checklist, divided into five topic groups plus a group of additions. Non-compliance with these rules carries a clear systemic consequence — from disqualification, through technical loss, to loss of scoring. The binding quantitative values themselves are consolidated in the mandatory parameter table in Appendix F. Each group is presented as a three-column table — number, action (mandatory/prohibited/recommended), and instruction. To avoid gendered phrasing, all instructions are formulated in the third-person plural.

## 1 Network Architecture, Decentralization, and Local Epistemology

**Table 7: Network Architecture, Decentralization, and Local Epistemology**

| No. | Action | Instruction |
|---|---|---|
| 1 | Mandatory | Run the Cop's and the Robber's code in two completely separate processes. Sanction: total failure and breaking of the Zero-Trust model. |

*(continued on next page)*

<!-- page 143 -->

**Table 7: Network Architecture, Decentralization, and Local Epistemology** *(continued from previous page)*

| No. | Action | Instruction |
|---|---|---|
| 2 | Prohibited | Do not share memory or variables between the sides, under any circumstances. Sanction: immediate disqualification of the solution for information leakage. |
| 3 | Mandatory | Define the orchestrator component as the single entry point to the subsystems. Sanction: technical instability and loss. |
| 4 | Mandatory | Manage game states using a standard state machine. Sanction: technical loss resulting from a system deadlock. |
| 5 | Mandatory | Reject any attempt at an illegal state transition in the state machine. Sanction: a logic error leading to loss. |
| 6 | Mandatory | Implement a deadline-tracking mechanism to prevent freezing while waiting for the opponent. Sanction: system paralysis and loss on time (Timeout). |
| 7 | Mandatory | Run a watchdog to monitor process crashes and enable controlled data extraction. Sanction: game crash and loss of official documentation. |
| 8 | Mandatory | Display only the local truth in the live user interface. Sanction: disqualification of system legality due to an information breach. |
| 9 | Prohibited | Do not display the full, objective board state in the live interface. Sanction: disqualification of the project for illegal advantage. |

*(continued on next page)*

<!-- page 144 -->

**Table 7: Network Architecture, Decentralization, and Local Epistemology** *(continued from previous page)*

| No. | Action | Instruction |
|---|---|---|
| 10 | Mandatory | Use a tunneling tool to expose the local server to the public internet. Sanction: inability to compete in the league against opponents. |

## 2 Spatial Mechanics, Physics, and Board Constraints

**Table 8: Spatial Mechanics, Physics, and Board Constraints**

| No. | Action | Instruction |
|---|---|---|
| 11 | Mandatory | Ensure that the configuration file is completely identical, byte-for-byte, on both sides. Sanction: disqualification of the game for breaking symmetry. |
| 12 | Mandatory | Raise minimum values in the parameter table only by mutual agreement, and never lower them. Sanction: exceeding a threshold condition, leading to disqualification of the scoring. |
| 13 | Mandatory | Move only in orthogonal directions. Sanction: an illegal move and technical loss. |
| 14 | Prohibited | Do not make diagonal moves. Sanction: rejection of the move by the opponent, and loss. |
| 15 | Mandatory | Openly declare every barrier placement. Sanction: falsifying the board and automatic loss upon audit. |
| 16 | Prohibited | Do not lie about the location of a placed barrier. Sanction: grounds for severe disqualification. |

<!-- page 145 -->

## 3 Cryptography, Log Integrity, and Zero-Knowledge

**Table 9: Cryptography, Log Integrity, and Zero-Knowledge**

| No. | Action | Instruction |
|---|---|---|
| 17 | Mandatory | Use a Commit-Reveal protocol based on SHA-256. Sanction: the absence of the mechanism renders the solution illegal. |
| 18 | Mandatory | Keep the one-time number (Nonce) completely secret until the end of the game. Sanction: disqualification of the protection due to dictionary-attack risk. |
| 19 | Mandatory | Technically disqualify a game upon any hash mismatch discovered at the audit stage. Sanction: the iron rule dictating a score of 0 for the falsifying team. |
| 20 | Mandatory | Build a viewer application to reconstruct and verify the game log. Sanction: a threshold condition for audit approval and project submission. |
| 21 | Mandatory | Declare only the truth when capturing a Robber. Sanction: immediate disqualification for denying reality. |
| 22 | Prohibited | Do not falsely declare a capture; a false declaration entails immediate disqualification. Sanction: a score of zero and technical loss with no right of appeal. |
| 23 | Mandatory | Cryptographically lock the scent-emission model before the game begins. Sanction: deviation in the decay formula voids the game. |
| 24 | Mandatory | Perform a cryptographic hardware declaration before the game begins. Sanction: forfeiture of eligibility for the computational-fairness bonus. |

<!-- page 146 -->

## 4 Strategy, Language, and Public Network

**Table 10: Strategy, Language, and Public Network**

| No. | Action | Instruction |
|---|---|---|
| 25 | Recommended | Do not hand the language model the decision on the movement itself; use it only for text processing and generating a behavioral profile. Note: there is no mandatory sanction, but blind reliance may lead to hallucinations, illegal moves, and technical loss. |
| 26 | Mandatory | Conduct communication only in free-form natural language. Sanction: preserving the nature of the psychological challenge. |
| 27 | Prohibited | Do not use a protocol of direct numeric coordinates. Sanction: disqualification of the game's character as defined in the rulebook. |
| 28 | Mandatory | Implement a token-bucket-based rate limiter for sending reports to Gmail. Sanction: preventing a 429 block that would silence the team's reporting. |
| 29 | Mandatory | Define a denial-of-service (DOS) detector for rigorous protection of network resources. Sanction: interface lockout to prevent blocking of the reporting account. |
| 30 | Mandatory | Use send-only permission for the Gmail interface. Sanction: a security violation that would result in disqualification in code review. |

<!-- page 147 -->

## 5 League Fairness, Administrative Procedures, and Competition Integrity

**Table 11: League Fairness, Administrative Procedures, and Competition Integrity**

| No. | Action | Instruction |
|---|---|---|
| 31 | Mandatory | Play a minimum required number of games against different teams in the league. Sanction: failure to meet the minimum forfeits a passing grade. |
| 32 | Mandatory | Report game results automatically via the Gmail interface. Sanction: absence of a report disqualifies the points from that game. |
| 33 | Mandatory | Format the game report as a standard JSON data structure. Sanction: code cannot process free text, and the report will be rejected. |
| 34 | Prohibited | Do not send an end-of-game report as free text; only as an attached JSON file. Sanction: a report that is not JSON will be refused in processing and will result in a score of zero. |
| 35 | Mandatory | Agree with the opponent on the result, with each team sending a separate end-of-game report; failure of one team to report, or a contradictory report, disqualifies the game and gives both teams a score of 0. Sanction: the primary enforcement mechanism preventing reporting fraud. |
| 36 | Mandatory | Perform a comprehensive mutual log audit at the end of every game. Sanction: a necessary condition prior to agreeing on the shared JSON result. |
| 37 | Mandatory | Declare precisely the number of games actually played at the start of every game. Sanction: a threshold condition for computing the true competition factor. |

*(continued on next page)*

<!-- page 148 -->

**Table 11: League Fairness, Administrative Procedures, and Competition Integrity** *(continued from previous page)*

| No. | Action | Instruction |
|---|---|---|
| 38 | Prohibited | Do not falsely declare the number of games played; a false declaration disqualifies the project. Sanction: absolute disqualification for a disciplinary and integrity violation. |
| 39 | Prohibited | Never push secrets or credentials to the repository — even if it is private and shared only with the instructor. Sanction: a severe security failure and project failure. |
| 40 | Mandatory | Add credential and secret files to the `.gitignore` file. Sanction: mandatory protection against leakage of Gmail API credential details. |
| 41 | Mandatory | Tag the submitted version in the repository with a documented Git tag. Sanction: an administrative condition enabling the instructor to check the final version. |
| 42 | Mandatory | Write and attach a comprehensive academic report as a readme file in the repository (description of the model, deliberations, strategy, images, and RL curves). Sanction: without the report, the project is not academically complete. |
| 43 | Mandatory | Download the submission form from Moodle, fill it in, and save it as PDF; do not alter or move fields. Sanction: a bureaucratic condition for grading. |
| 44 | Mandatory | Submit the assignment on Moodle separately for each team member. Sanction: a project without an individual submission will not earn the student a grade. |
| 45 | Mandatory | Enter a unique, eight-character team identification code with no spaces. Sanction: an organizational failure that would prevent automatic assignment of reports to the team. |

<!-- page 149 -->

## 6 Additions Found When Cross-Checking the Book

The following rules appear in the body of the book but were missing from the original mapping; they are presented here to complete the picture, alongside a reference to their source.

**Table 12: Additions Found When Cross-Checking the Book**

| No. | Action | Instruction |
|---|---|---|
| 46 | Mandatory | A barrier placed on the cell where the Robber is standing at that moment counts as a capture (the Cop wins). Source: Chapter 3. |
| 47 | Mandatory | A Robber left with no legal move whatsoever is likewise considered captured. Source: Chapter 3. |
| 48 | Mandatory | Score every end-of-game scenario according to the scoring table (capture 5/20, survival 10/5, technical loss 0/0). Source: Chapter 3 and the parameter table. |
| 49 | Mandatory | Submit two separate GitHub repositories — Cop and Robber — with a cross-link in the README, two links in the Moodle submission, and four links in the JSON of both teams. Source: Chapter 9. |
| 50 | Mandatory | Include in every repository, at minimum: README, configuration files (`config/`), PRD files, a PLAN file, and TODO files. Source: Chapter 9. |
| 51 | Mandatory | Send the automated end-of-game reports to the instructor's address [Agent Reports Address]. Source: Chapter 9. |
| 52 | Mandatory | Only one counted game is held against each opponent (no repeats for accumulating score); uncounted warm-up games are permitted. Source: Chapter 9. |

*(continued on next page)*

<!-- page 150 -->

**Table 12: Additions Found When Cross-Checking the Book** *(continued from previous page)*

| No. | Action | Instruction |
|---|---|---|
| 53 | Mandatory | Record in the step-zero declaration the commit hash that was played; it is permitted to change code between games, but every game must update the commit hash. Source: Chapter 5. |
| 54 | Mandatory | Report in the end-of-game JSON file the total number of tokens consumed in the game (and in the series). Source: Chapter 5, Chapter 9. |
| 55 | Mandatory | Give a self-assessment score for code quality only — not for the league game result. Source: Chapter 11. |

<!-- page 151 -->

# Appendix F: The Mandatory Parameter Table

This appendix is the single source of truth for every quantitative value in the project. Throughout the entire book, numeric values do not appear as a "hard" number in the body text, but rather as an intuitive Hebrew code-name enclosed in square brackets — for example, [Board Size]. The actual value is determined solely here, in the tables below.

## How to Read the Table

The values shown in the "Example Value" column are the mandatory minimum: they may be raised by mutual agreement between the two competing teams, but may never be lowered below this threshold. A parameter marked "Fixed" cannot be changed at all; a parameter marked "Negotiable" is determined entirely at the negotiation stage between the parties, and the value shown is merely an example.

<!-- page 152 -->

**Table 13: Board, Coordinate-System, and Starting-Position Parameters**

| No. | Parameter Name | Meaning | Example Value | Status |
|---|---|---|---|---|
| 1 | [Board Size] | Side length of the square game grid | 7×7 | Minimum |
| 2 | [Number of Agents] | Number of players in the race | 2 | Fixed |
| 3 | [Coordinate System Origin] | The corner in which cell (0,0) sits | Top-left corner | Negotiable |
| 4 | [Axis Start Index] | The number at which the count of every axis begins | 0 | Negotiable |
| 5 | [Starting Position – Robber] | The Robber's starting cell | Center (3,3) | Negotiable |
| 6 | [Starting Position – Cop] | The Cop's starting cell | Corner (0,0) | Negotiable |

**Table 14: Game Arena and Verbal Hint Parameters**

| No. | Parameter Name | Meaning | Example Value | Status |
|---|---|---|---|---|
| 1 | [Game Arena] | The realistic region in which the game takes place — feeds real landmarks into the verbal hints. Empty ("") = generic landmarks | New York | Negotiable |
| 2 | [Word Limit per Hint] | Maximum number of words in every verbal hint sent over the network — applies to both template mode and the language model (as stated to it in the system prompt) | 15 | Negotiable |

<!-- page 153 -->

**Table 15: Movement and Barrier Parameters**

| No. | Parameter Name | Meaning | Example Value | Status |
|---|---|---|---|---|
| 1 | [Movement Set] | A single orthogonal move (one of 4 directions) or standing still; no diagonals | — | Fixed |
| 2 | [Barrier Quota] | Maximum number of barriers the Cop is allowed to place | 14 | Minimum |
| 3 | [Step Ceiling] | Maximum number of moves in a single game | 35 | Minimum |
| 4 | [Survival Threshold] | Steps the Robber must survive to win | 35 | Minimum |

**Table 16: Dynamic Pheromone Parameters**

| No. | Parameter Name | Meaning | Example Value | Status |
|---|---|---|---|---|
| 1 | [Scent Intensity at Source] | Pheromone intensity in the emitting cell | 0.9 | Fixed |
| 2 | [Scent Decay Rate] | Decay rate per turn | 0.10 | Fixed |
| 3 | [Scent Field Size] | Side length of the emission window around the agent | 5×5 | Fixed |

<!-- page 154 -->

**Table 17: Scoring Parameters (Win, Survival, and Tie)**

| No. | Parameter Name | Meaning | Example Value | Status |
|---|---|---|---|---|
| 1 | [Capture Score – Cop] | Score for the Cop on a successful capture | 20 | Fixed |
| 2 | [Capture Score – Robber] | Score for the Robber on a capture | 5 | Fixed |
| 3 | [Survival Score – Cop] | Score for the Cop when the Robber survives | 5 | Fixed |
| 4 | [Survival Score – Robber] | Score for the Robber on successful survival | 10 | Fixed |
| 5 | [Tie Score] | Score for each side when the cumulative score of all games against an opponent ends in a tie | 2 | Fixed |

**Table 18: Network and League Parameters**

| No. | Parameter Name | Meaning | Example Value | Status |
|---|---|---|---|---|
| 1 | [Number of Games] | Games in a series against one opponent | 6 | Fixed |
| 2 | [Diversity Bonus] | Score for a win against a new opponent | 10 | Fixed |
| 3 | [Minimum Games to Pass] | Minimum number of games each team must play to receive a passing grade for the project | 2 | Fixed |
| 4 | [Token Estimate per Series] | Total language-model tokens each team is allowed to consume; actual consumption is reported by email | ~200000 | Negotiable |
| 5 | [Maximum Games per Team] | Maximum number of games each team is allowed to play | 10 | Fixed |

<!-- page 155 -->

**Table 19: Network, Rate-Limiting, and Protection Parameters (the Gatekeeper Pattern)**

| No. | Parameter Name | Meaning | Example Value | Status |
|---|---|---|---|---|
| 1 | [Requests per Minute] | Maximum rate of outgoing API requests | 30 | Minimum |
| 2 | [Concurrent Requests] | Maximum number of concurrent requests | 2 | Minimum |
| 3 | [Retry Delay] | Wait time before a retry attempt after an error | 5 sec | Minimum |
| 4 | [Retry Attempts] | Number of attempts before failure | 3 | Minimum |
| 5 | [Queue Depth] | Size of the request queue under load | 100 | Minimum |
| 6 | [Response Time Limit] | Timeout for every network request | 30 sec | Negotiable |
| 7 | [Watchdog Threshold] | Freeze time until Watchdog intervention | 60 sec | Negotiable |

## 1 Status Definitions

The "Status" column in the tables above takes one of three values, whose binding meaning is defined as follows:

- **Minimum.** The parties may negotiate the value, but only in the direction that makes the game harder (usually increasing the value) — never relaxing it below the example value. In the absence of an explicit agreement between the parties, the code must ensure that the example value is the default used by the team.
- **Fixed.** A mandatory value that cannot be changed at all. Deviation from this value disqualifies the team.
- **Negotiable.** The parties may agree on any value whatsoever. In the absence of an explicit agreement between the parties, the code must ensure that the example value is the default used by the team.

<!-- page 156 -->

## 2 Mandatory Rules

1. Every team must define all of the above values in the configuration file. The teams must ensure that these values are identical between both teams, and lock them cryptographically.
2. In every new game, a team may change the settings, as long as they match the agreement with the opposing team.
3. Every configuration file must be given a different name according to the game, so as to allow easy reconstruction of each game's configuration.
4. Each game's configuration file must be attached to the GitHub repository.
5. Each team may change the code between games; therefore, for every game, an email must be sent to the instructor stating the GitHub commit number used in that game.

<!-- page 157 -->

## 3 Attached Files, Repo & Addresses

This book comes with four example JSON files — the pre-game declaration, the agreed configuration, the game log, and the results report — illustrating the full usage format; an explanation of each file's content and role appears in Chapter 9. The table below defines a variable name for each file, as well as the example code repository and the instructor's two email addresses, and these are the names used by the book throughout. This table is a reference table only — it is not part of the agreed configuration file and is not subject to negotiation. File names are derived from the game ID (`game_id`) and the game number (`<NN>`), so that files from different games are never mixed up.

**Table 20: Attached File Variables, Code Repository, and Instructor Addresses**

| Variable Name | Role and Content | Value |
|---|---|---|
| [Declaration File] | Pre-game declaration: all the fixed data of the game — teams, members, repositories, hardware, model, tokens, and times | `declaration_<game_id>.json` |
| [Configuration File] | The agreed configuration: the game's cryptographically locked parameters | `config_<game_id>_g<NN>.json` |
| [Log File] | The game log for cryptographic verification in the replay simulator | `log_<game_id>_g<NN>.json` |
| [Results File] | The final results report for the instructor's league score computation | `result_<game_id>.json` |
| [Example Code Repository] | The reference implementation of the game, on GitHub | `https://github.com/rmisegal/Game-P2P-Cop-Chase` |
| [Instructor Address] | General mail and sharing of GitHub repositories | `rmisegal@gmail.com` |
| [Agent Reports Address] | Destination for the JSON reports the agent sends automatically | `rmisegal+uoh26finalgame@gmail.com` |

<!-- page 158 -->

## 4 LLM Modes for the Verbal Game

This table documents the four operating modes of the language model, all of which relate only to the decoy text — the move decision is always algorithmic, in Python code (see Chapter 6). The mode is selected in the private configuration file (`[trash_talk_provider]`), and it determines how much of the [Token Estimate per Series] the team will spend on talk. This table is a reference table only — the choice is private to each peer, is not part of the agreed configuration file, and is not subject to negotiation.

**Table 21: LLM Modes for the Verbal Game (private choice per peer)**

| Mode | Where It Runs and Token Cost | Rate Limit | Account and Installation |
|---|---|---|---|
| [Template Provider] (`template`) | In-process; sentences prepared in advance in code — zero tokens. Default | — | None; not online, and free |
| [Ollama Provider] (`ollama`) | Local model at `localhost:11434` — zero API tokens | None | Ollama installation and model pull |
| [Cloud Provider] (`claude_api`) | Small cloud model (Haiku) via the API — real consumption, counted against [Token Estimate per Series] | Per the account | Anthropic API key (paid account) |
| [CLI Provider] (`claude_cli`) | `claude -p` via the Claude Code CLI — the highest cost | Per the subscription | Login to Claude CLI (subscription) |

The `every_n_steps` parameter activates the model only once every several turns, further reducing consumption. In `template` and `ollama` modes, the entire series of [Number of Games] games can be played at zero tokens, and the whole competition then shifts to the quality of the movement algorithm.

<!-- page 159 -->

## 5 Strategy Module Selection

The movement policy — the core of scoring — is selected in the private configuration file (`[strategy]`). Leaving the field empty runs the built-in heuristic brain of the reference implementation; to run your own strategy, point one of the keys to a class that inherits from `BrainBase` and overrides `_pick_move` (and, for the Cop, also the barrier choice in `_decide_move`). This table is a reference table only — the choice is private to each peer and is not subject to negotiation. Full details in `docs/STRATEGY.md` and in Appendix D.

**Table 22: Strategy Module Selection Keys (private choice per peer)**

| Key (`[strategy]`) | Role | How to Override |
|---|---|---|
| `thief_class` | Your Robber brain, written as `package.module:Class` | Inherit from `ThiefBrain` and override `_pick_move` |
| `police_class` | Your Cop brain | Same as above; in the Cop's `_decide_move`, the barrier choice is also selected |

<!-- page 160 -->

# End of the Book

You have reached the end of the rules and guidelines book for the final project.

**Good luck!**


