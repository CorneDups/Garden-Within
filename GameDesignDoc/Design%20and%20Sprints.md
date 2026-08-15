# Inner Garden — Design and Sprints

## 1. Purpose of This Document

This document defines the current design and development pathway for **Inner Garden**: a persistent AI-guided exploration game in which the player enters a symbolic inner world, plants experiences as seeds, explores dynamically generated caves, discovers meaning through interactive fantasy, and returns to a persistent garden where those discoveries become trees, fruits, symbols, and memories.

The document serves two purposes:

1. **Game and systems design reference**
2. **Development roadmap divided into testable one-hour AI-assisted sprints**

The central development principle is:

> Build vertically. Every sprint should leave behind a runnable, testable version that moves the system closer to the complete Inner Garden loop.

The core game loop is:

**Ache / Calling → Seed → Cave → Discovery → Water → Tree → Fruit → Persistent Memory → Next Journey**

---

# Part I — Core Game Design

## 2. High-Level Concept

Inner Garden is a persistent symbolic autobiographical game world driven by an LLM-mediated narrative engine.

The player brings a real-life concern, ache, calling, tension, or unresolved question into the Garden. The system helps transform this concern into a symbolic **Seed**.

The player plants the Seed in fertile ground and is guided toward a **Cave**.

Inside the Cave, the LLM acts as a Dungeon Master and facilitator, creating a dreamlike fantasy experience structured around:

- the player's stated concern;
- the player's current profile;
- an evolving Enneagram hypothesis;
- previous discoveries;
- symbols already present in the Garden;
- the player's stated boundaries;
- critical questions that may be worth exploring.

The purpose of the Cave is not for the AI to diagnose or define the player.

The AI creates the environment, consequences, questions, symbolic encounters, and narrative tension.

The player creates the meaning.

At the conclusion of the Cave, the player returns to the Garden carrying a jar of water accumulated through meaningful engagement. The water is poured onto the Seed.

The Seed becomes a Tree.

The Tree bears one Fruit.

The Fruit is experienced through all senses and eventually named by the player.

The name of the Fruit becomes a symbolic representation of the discovery or "medicine" uncovered through the journey.

Over time, the Garden becomes a persistent spatial representation of the player's inner journey.

---

## 3. Core Architectural Principle

The most important distinction in the architecture is:

> **The LLM does not own the truth about the player.**

The system must distinguish between:

### 3.1 World Truth

What is true inside the fantasy.

Example:

> A chained wolf is standing inside the cavern.

### 3.2 AI Interpretation

What the AI thinks something might represent.

Example:

> The wolf may represent anger that has been restrained.

### 3.3 Player Truth

What the player says is true about themselves.

Example:

> "Yes. I suppress anger because I am afraid of becoming cruel."

Player Truth has the highest authority.

AI interpretations remain hypotheses until the player accepts, modifies, or rejects them.

---

## 4. Three Major Systems

Inner Garden consists of three interacting systems.

### 4.1 The Persistent Inner Garden

The symbolic world that remembers the player's history.

It contains:

- terrain;
- water;
- structures;
- caves;
- seeds;
- trees;
- fruits;
- animals;
- furniture;
- symbols;
- discoveries;
- unlocked areas.

### 4.2 The Cave Engine

A temporary interactive narrative space.

It:

- creates a bounded adventure;
- controls Hero's Journey progression;
- runs the Dungeon Master conversation;
- tracks the Spirit Guide;
- tracks symbolic water;
- saves turns and discoveries;
- supports pause and resume.

### 4.3 The Memory and Meaning Engine

The system that translates conversation into persistent context.

It stores:

- raw conversation;
- episodic summaries;
- semantic memories;
- user-confirmed discoveries;
- AI hypotheses;
- symbolic objects;
- previous Cave outcomes.

---

# 5. High-Level Software Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                        │
│                                                             │
│   Login → Garden → Plant Seed → Cave → Return → Tree/Fruit │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND / GAME API                       │
│                                                             │
│  Authentication                                             │
│  Game State Engine                                          │
│  Cave Orchestrator                                          │
│  Memory Manager                                             │
│  Prompt Builder                                             │
│  Media Prompt Manager                                       │
│  Safety / Consent Layer                                     │
└───────┬─────────────────────┬────────────────────┬──────────┘
        │                     │                    │
        ▼                     ▼                    ▼
┌──────────────┐      ┌──────────────┐    ┌─────────────────┐
│ PostgreSQL   │      │    LLM API   │    │ Media APIs      │
│              │      │              │    │                 │
│ Users        │      │ Cave Design  │    │ Image generation│
│ Profiles     │      │ Dungeon      │    │ Music generation│
│ Garden State │      │ Master       │    │                 │
│ Memories     │      │ Memory       │    └─────────────────┘
│ Cave State   │      │ Extraction   │
│ Seeds        │      │ Interpretation│
│ Trees/Fruit  │      │              │
└──────────────┘      └──────────────┘
```

For the first implementation, one PostgreSQL database is sufficient.

Do not begin with distributed databases or microservices.

---

# 6. Recommended Initial Technology Stack

A suitable prototype stack is:

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy or equivalent ORM
- LLM API integration

## Database

- PostgreSQL
- Supabase may be used as a managed PostgreSQL/auth/storage platform if desired

## Frontend

- HTML
- CSS
- JavaScript

A complex frontend framework is unnecessary for the first prototype.

## Optional Later Services

- image generation API;
- music generation API;
- embedding/vector retrieval;
- object storage;
- analytics;
- monitoring.

---

# 7. Authentication and Identity

The player begins by creating or logging into a private account.

Passwords must never be stored directly.

Example user structure:

```text
users
--------------------------------
user_id
username
password_hash
created_at
last_login
onboarding_complete
consent_version
```

Authentication data should remain logically separate from psychological and gameplay data.

---

# 8. First-Time Onboarding

On first login only, the player receives seven open-ended questions.

Questions 1–6 are designed to help establish an initial Enneagram hypothesis.

Question 7 is the opening Seed question:

> **What has recently happened that bothered you or felt like a calling for you to explore? Give as much detail as you feel comfortable with.**

All answers are stored.

Example:

```text
onboarding_answers
--------------------------------
answer_id
user_id
question_number
question_text
answer_text
created_at
```

---

# 9. Enneagram Hypothesis

The first six onboarding answers are sent to the LLM.

The result is not stored as established psychological truth.

It is stored as an evolving hypothesis.

Example:

```json
{
  "primary_type": 4,
  "wing": 5,
  "confidence": 0.58,
  "type_probabilities": {
    "1": 0.04,
    "2": 0.07,
    "3": 0.05,
    "4": 0.42,
    "5": 0.25,
    "6": 0.08,
    "7": 0.03,
    "8": 0.02,
    "9": 0.04
  }
}
```

The hypothesis may evolve as more information becomes available.

---

# 10. Player Profile

The Player Profile contains compressed context useful to future journeys.

Possible fields:

```text
player_profile
--------------------------------
profile_id
user_id

enneagram_primary_hypothesis
enneagram_wing_hypothesis
enneagram_confidence

values_json
recurring_fears_json
recurring_desires_json
recurring_conflicts_json
important_relationships_json
identity_statements_json
important_symbols_json

preferred_narrative_style
boundaries_json

profile_summary
updated_at
```

---

# 11. Epistemic Status

All meaningful information about the player should carry an epistemic status.

Suggested values:

```text
USER_STATED
USER_CONFIRMED
AI_HYPOTHESIS
AI_INFERENCE
NARRATIVE_SYMBOL
```

Example:

> "I always feel like I need to prove I am useful."

Stored as:

```text
USER_STATED
```

Possible AI interpretation:

> Worth may be associated with usefulness.

Stored as:

```text
AI_HYPOTHESIS
```

The two must never be treated as equivalent facts.

---

# 12. The Seed

The Seed transforms a real experience into an explorable symbolic object.

Example structure:

```text
seeds
--------------------------------
seed_id
user_id
created_at

origin_text
origin_summary

core_tension
possible_longing
possible_fear
exploration_question

visual_description

status
planted_location
source
```

Possible state sequence:

```text
CREATED
   ↓
PROPOSED
   ↓
ACCEPTED
   ↓
PLANTED
   ↓
TRANSFORMED
```

The system should present the interpretation before planting.

Possible player controls:

- Plant it
- Modify it
- Try another interpretation
- Not this

The player authorizes what becomes canonical.

---

# 13. Garden Ontology

The Garden Ontology defines what *could* exist.

Example categories:

```text
GROUND
WATER
TREE
PLANT
ANIMAL
STRUCTURE
FURNITURE
CAVE
PATH
SYMBOL
```

Example subtypes:

```text
GROUND
    rock
    sand
    barren_soil
    fertile_soil
    grass

WATER
    stream
    spring
    pond
    rain
    well

TREE
    seed
    sapling
    mature_tree

STRUCTURE
    house
    bridge
    gate
    cave
    wall

FURNITURE
    bench
    swing
    table
```

Suggested table:

```text
garden_element_catalog
--------------------------------
element_type
subtype
possible_states_json
symbolic_properties_json
visual_description_template
```

---

# 14. Player Garden State

The ontology defines what could exist.

The Garden State defines what currently exists for one player.

Example:

```text
gardens
--------------------------------
garden_id
user_id
garden_version
current_season
time_of_day
weather_state
```

Individual elements:

```text
garden_elements
--------------------------------
instance_id
garden_id
user_id

element_type
element_subtype

x
y

state_json
symbolic_meaning
created_from_event
discovered_at
```

Initial garden may contain:

- house;
- stream;
- open ground;
- fertile soil;
- path;
- distant cave edge.

---

# 15. Trees and Fruits

Trees are permanent transformations of completed Seeds.

```text
trees
--------------------------------
tree_id
user_id
seed_id
cave_id

species_description
growth_stage
location

symbolic_meaning
created_at
```

Fruits belong to Trees.

```text
fruits
--------------------------------
fruit_id
tree_id
cave_id

appearance
smell
texture
taste
sound
felt_experience

suggested_name
player_given_name
meaning

created_at
```

The provenance should remain traceable:

```text
Tree
 ↓
Fruit
 ↓
Cave
 ↓
Seed
 ↓
Original Experience
```

---

# 16. Cave Structure

Each Cave follows a compressed Hero's Journey.

Suggested stages:

```text
1. CALLING
2. THRESHOLD
3. DESCENT
4. ENCOUNTER
5. CHOICE
6. REVELATION
7. RETURN
8. INTEGRATION
9. COMPLETED
```

Narratively:

```text
Garden
   ↓
Seed planted
   ↓
Spirit Guide appears
   ↓
Journey toward Cave
   ↓
Cross threshold
   ↓
Fantasy metaphor established
   ↓
Resistance encountered
   ↓
Meaningful choice
   ↓
Current strategy becomes insufficient
   ↓
Deeper question emerges
   ↓
Discovery
   ↓
Return
   ↓
Water poured
   ↓
Tree
   ↓
Fruit
   ↓
Fruit named
```

---

# 17. Cave Designer and Dungeon Master

The Cave should not be improvised without structure.

Two LLM roles are useful.

## 17.1 Cave Designer

Creates the blueprint before play begins.

Input:

```text
Player Profile
+
Enneagram Hypothesis
+
Current Seed
+
Relevant Memories
+
Current Garden
+
Player Boundaries
```

Possible output:

```json
{
  "theme": "Integrity without external validation",
  "central_question": "Who are you when your motives are misunderstood?",
  "spirit_animal": "stag",
  "world_metaphor": "A hall where every mirror shows a different accusation",
  "threshold": "A stone door requiring the player to leave their shield outside",
  "central_conflict": "...",
  "critical_choice": "...",
  "possible_discovery": "...",
  "return_symbol": "clear water",
  "tone": "somber but safe"
}
```

## 17.2 Dungeon Master

Runs the moment-to-moment Cave experience inside the blueprint.

---

# 18. Cave State

Example table:

```text
caves
--------------------------------
cave_id
user_id
seed_id

status
theme
central_question
spirit_animal

blueprint_json

current_stage
current_scene
turn_number
water_level

started_at
completed_at

final_discovery_id
```

Status examples:

```text
LOCKED
AVAILABLE
ENTERED
ACTIVE
PAUSED
COMPLETED
INTEGRATED
ABANDONED
```

---

# 19. Dungeon Master Turn Loop

Each turn follows:

```text
PLAYER INPUT
      ↓
LOAD CAVE STATE
      ↓
RETRIEVE RELEVANT MEMORY
      ↓
BUILD CONTEXT PACKET
      ↓
CALL LLM
      ↓
STRUCTURED OUTPUT
      ↓
BACKEND VALIDATION
      ↓
SAVE TURN
      ↓
UPDATE GAME STATE
      ↓
DISPLAY NARRATIVE
```

Example LLM response:

```json
{
  "narrative": "The wolf watches you quietly from behind the iron bars...",
  "state_update": {
    "suggested_stage": "ENCOUNTER",
    "water_increment": 1,
    "memory_candidates": [],
    "possible_insight": null
  }
}
```

The user sees only the narrative.

The backend receives and validates the structured state update.

---

# 20. Database Safety Principle

The LLM must never write directly to the database.

Correct pattern:

```text
LLM
 ↓
Proposed structured state changes
 ↓
Backend validation
 ↓
Database
```

Incorrect pattern:

```text
LLM → SQL
```

---

# 21. The Spirit Guide

Each Cave contains a Spirit in animal form.

Example:

```text
guide
--------------------------------
guide_id
cave_id

animal_form
name
temperament
symbolic_role
speech_style
```

The Spirit Guide may:

- ask;
- observe;
- reflect;
- challenge gently;
- point toward symbolic details;
- accompany the player.

The Guide should not:

- diagnose;
- proclaim hidden truth;
- define the player;
- impersonate divine authority;
- imply omniscient access to the player's mind.

Preferred style:

> "What do you notice?"

rather than:

> "I know what your soul is hiding."

---

# 22. Water Jar Mechanic

The jar represents meaningful engagement with the journey.

Water should not be a reward for suffering.

Therefore avoid logic such as:

```text
crying = +50
reflection = +5
```

Instead water may increase through:

```text
Meaningful choice
Self-reflection
Emotional honesty
Recognizing contradiction
Naming a fear
Naming a desire
Changing perspective
Setting a boundary
Rejecting an AI interpretation
Acknowledging grief
Choosing differently
```

Even:

> "No, that interpretation is wrong."

can represent progress because the user has clarified something true.

---

# 23. Cave Completion

At the end of the Cave, extract:

```text
What happened?
What choice mattered?
What did the player explicitly discover?
What interpretation did they reject?
What remains unresolved?
What symbol emerged?
What changed?
```

The AI may offer a possible interpretation.

The player should then be asked to describe the discovery in their own words.

That becomes a canonical:

```text
USER_CONFIRMED
```

discovery.

---

# 24. Return, Tree, and Fruit Ritual

At the end:

```text
Cave
 ↓
Return to Garden
 ↓
Jar of Water
 ↓
Water poured onto Seed
 ↓
Seed transforms
 ↓
Tree
 ↓
One Fruit
 ↓
Sensory description
 ↓
Player names Fruit
```

Example:

```text
Seed:
Fear of being misunderstood

Cave:
Hall of Accusing Mirrors

Discovery:
"I cannot control how everyone perceives me."

Tree:
White cedar

Fruit:
Warm golden pear

Fruit name:
Integrity
```

The Fruit becomes a durable symbolic memory.

---

# 25. Memory Architecture

Use four major layers.

## 25.1 Raw Memory

Actual conversation turns.

```text
cave_turns
--------------------------------
turn_id
cave_id
speaker
content
timestamp
```

## 25.2 Episodic Memory

A compressed description of what happened.

Example:

> The player encountered a chained wolf and chose to unlock it rather than destroy it.

## 25.3 Semantic Memory

Persistent themes that appear meaningful.

Example:

> Being falsely judged appears particularly painful.

Such content remains:

```text
AI_HYPOTHESIS
```

until confirmed.

## 25.4 Symbolic Memory

Objects that now exist in the Garden.

Examples:

- silver key;
- stag;
- broken shield;
- Tree of Integrity;
- Fruit called "Known."

---

# 26. Memory Table

Possible implementation:

```text
memories
--------------------------------
memory_id
user_id
content
memory_type
epistemic_status
confidence
source_cave
source_turn
created_at
```

Suggested types:

```text
EVENT
THEME
IDENTITY
RELATIONSHIP
VALUE
FEAR
DESIRE
SYMBOL
DISCOVERY
```

---

# 27. Context Retrieval

Do not send the LLM the player's entire history.

Build a compact Context Packet.

Example:

```text
Current Seed
+
Current Cave
+
Player Profile Summary
+
Recent Conversation Context
+
5–10 Relevant Memories
+
Relevant Garden Symbols
+
Recent Discoveries
+
Player Boundaries
```

Example JSON:

```json
{
  "player": {
    "enneagram_hypothesis": "4w5",
    "confidence": 0.58,
    "values": [],
    "boundaries": []
  },

  "current_seed": {},

  "garden": {
    "important_elements": []
  },

  "relevant_memories": [],

  "current_cave": {},

  "instruction": {
    "role": "facilitator",
    "never_define_user_identity_for_them": true,
    "ask_before_interpreting": true
  }
}
```

---

# 28. Player Boundaries and Consent

Introduce persistent boundaries.

Possible fields:

```text
player_boundaries
--------------------------------
user_id

topics_to_avoid
religious_language_preference
violence_tolerance
horror_tolerance
relationship_topics
sexual_content_boundary
death_and_grief_boundary
preferred_intensity
```

The system must honor these boundaries when generating Cave material.

---

# 29. Cave Exit and Control Mechanisms

Every Cave must support:

```text
PAUSE
LEAVE CAVE
RETURN TO GARDEN
LOWER INTENSITY
SKIP SCENE
SPEAK PLAINLY
```

**Speak Plainly** is particularly important.

It temporarily stops the metaphor and asks the AI to explain what the scene may be exploring.

Example:

> "I think this scene may be exploring what happens when you feel misunderstood. Does that resonate?"

The player can then:

- accept;
- modify;
- reject;
- resume the fantasy.

---

# 30. Media Prompt Architecture

Media prompts can be stored separately and linked to important entities.

```text
media_prompts
--------------------------------
prompt_id
entity_type
entity_id

media_type
prompt_text

generation_status
output_url

created_at
```

Media types:

```text
IMAGE
SONG
AMBIENCE
```

Entities may include:

- Cave;
- Spirit Guide;
- Tree;
- Fruit;
- Garden;
- major symbolic object.

---

# 31. Core Database Relationship Map

```text
USER
 │
 ├──── AUTH
 │
 ├──── PLAYER_PROFILE
 │       │
 │       └── ENNEAGRAM_HYPOTHESES
 │
 ├──── ONBOARDING_ANSWERS
 │
 ├──── PLAYER_BOUNDARIES
 │
 ├──── SEEDS
 │       │
 │       └──── CAVES
 │               │
 │               ├──── CAVE_TURNS
 │               ├──── GUIDE
 │               ├──── DISCOVERIES
 │               └──── MEMORIES
 │
 └──── GARDEN
          │
          ├──── GARDEN_ELEMENTS
          ├──── TREES
          │       │
          │       └──── FRUITS
          │
          ├──── SYMBOLS
          └──── UNLOCKED_CAVES

MEDIA_PROMPTS
      │
      └──── linked to major entities
```

---

# 32. Initial API Structure

## Authentication

```text
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
```

## Onboarding

```text
GET  /api/onboarding/questions
POST /api/onboarding/answers
POST /api/onboarding/complete
```

## Garden

```text
GET /api/garden
GET /api/garden/elements
GET /api/garden/history
```

## Seeds

```text
GET  /api/seeds
POST /api/seeds
POST /api/seeds/{id}/plant
```

## Caves

```text
POST /api/caves/create
POST /api/caves/{id}/enter
GET  /api/caves/{id}
POST /api/caves/{id}/turn
POST /api/caves/{id}/pause
POST /api/caves/{id}/complete
```

## Memory

```text
GET  /api/memories/relevant
POST /api/memories/confirm
POST /api/memories/reject
```

## Media

```text
POST /api/media/image-prompt
POST /api/media/song-prompt
```

---

# 33. Game Loops

## Short Loop

```text
Narrative
→ Choice
→ Consequence
→ Reflection
→ Narrative
```

Timescale: minutes.

## Main Journey Loop

```text
Ache
→ Seed
→ Cave
→ Discovery
→ Water
→ Tree
→ Fruit
→ New inner state
```

Timescale: one session or several sessions.

## Long-Term Reinforcing Loop

```text
More Caves
      ↓
More Discoveries
      ↓
Richer Garden
      ↓
Better Persistent Memory
      ↓
More Personally Meaningful Caves
      ↓
More Discoveries
```

This is the primary reinforcing loop of the game's long-term experience.

The richer the Garden becomes, the richer future journeys can become.

---

# Part II — Development Sprints

## 34. Development Philosophy

Development should proceed vertically.

Do not build an extensive database, AI framework, media pipeline, and graphics system independently and hope they eventually connect.

Every sprint should produce something runnable.

Each sprint has:

```text
INPUT
→ BUILD
→ TEST
→ WORKING VERSION
```

Suggested versioning:

```text
v0.01
v0.02
v0.03
...
v1.0
```

The previous playable version should remain functional after every sprint.

---

# Phase A — Foundation

## Sprint 1 — Runnable Inner Garden Shell

### Objective

Create the smallest runnable application.

### Build

```text
/frontend
    index.html
    garden.html
    cave.html
    css/
    js/

/backend
    main.py
    requirements.txt

/database
    schema.sql

.env.example
README.md
```

Backend:

```text
GET /
GET /api/health
```

Frontend displays:

```text
INNER GARDEN

[Enter]
```

### Test

1. Start backend.
2. Open frontend.
3. Click **Enter**.
4. Garden page loads.
5. `/api/health` returns `{"status":"ok"}`.

### Deliverable

**v0.01 — Inner Garden exists as a runnable application.**

---

## Sprint 2 — Persistent Database Connection

### Objective

Prove that the application can remember users between restarts.

### Build

Initial tables:

```text
users
player_profiles
game_sessions
```

Endpoints:

```text
POST /api/users
GET  /api/users/{id}
```

### Test

1. Create a test player.
2. Stop backend.
3. Restart backend.
4. Retrieve player.

### Deliverable

**v0.02 — Inner Garden remembers that someone exists.**

---

## Sprint 3 — Authentication

### Objective

Create private persistent Gardens.

### Build

```text
Register
Login
Logout
```

Use proper password hashing.

### Test

1. Register Alice.
2. Wrong password must fail.
3. Correct password opens Garden.
4. Logout.
5. Protected API becomes inaccessible.
6. Login again and retrieve same account.

### Deliverable

**v0.03 — Secure persistent users exist.**

---

# Phase B — Player Understanding

## Sprint 4 — Seven-Question Onboarding

### Objective

Capture the player's first meaningful information.

### Build

Questions 1–6:

- open-ended;
- designed to help form an initial Enneagram hypothesis.

Question 7:

> What has recently happened that bothered you or felt like a calling for you to explore? Give as much detail as you feel comfortable with.

Save all answers.

### Test

1. Register new player.
2. Complete onboarding.
3. Refresh.
4. Answers remain.
5. Existing player is not asked again.

### Deliverable

**v0.04 — Inner Garden knows the player's opening story.**

---

## Sprint 5 — Enneagram Hypothesis Engine

### Objective

Create the first structured LLM interpretation.

### Build

Questions 1–6 → LLM → structured JSON.

Required fields:

```text
primary_type
wing
confidence
type_probabilities
reasoning_summary
uncertainties
```

Store as:

```text
AI_HYPOTHESIS
```

### Test

Use three deliberately different mock personalities.

Verify:

- valid JSON;
- type between 1 and 9;
- wing is valid;
- confidence is bounded;
- result persists.

### Deliverable

**v0.05 — Initial personality hypothesis works.**

---

## Sprint 6 — Player Profile

### Objective

Create a compact persistent player context.

### Build

Generate:

```text
values
fears
desires
themes
important_symbols
profile_summary
```

Clearly distinguish:

```text
USER_STATED
USER_CONFIRMED
AI_HYPOTHESIS
```

### Test

Compare generated profile to raw answers.

No inference should be stored as fact.

### Deliverable

**v0.06 — Inner Garden has a persistent player model.**

---

# Phase C — The Garden

## Sprint 7 — Garden Ontology

### Objective

Define what can exist in the Garden.

### Build

```text
garden_element_catalog
```

Initial types:

```text
GROUND
WATER
TREE
PLANT
ANIMAL
STRUCTURE
FURNITURE
CAVE
PATH
SYMBOL
```

### Test

Add a new subtype such as:

```text
FOUNTAIN
```

directly to the database.

The application should display it without structural code changes.

### Deliverable

**v0.07 — The symbolic vocabulary of the Garden exists.**

---

## Sprint 8 — Player Garden State

### Objective

Create a separate persistent Garden for each player.

### Build

Starting Garden:

- house;
- stream;
- open ground;
- fertile soil;
- path;
- distant Cave edge.

### Test

Modify Alice's Garden.

Bob's Garden remains unchanged.

Reload Alice's Garden.

Modification persists.

### Deliverable

**v0.08 — Each player owns a persistent Garden.**

---

## Sprint 9 — Visual Garden Prototype

### Objective

Turn database state into a navigable space.

### Build

Simple 2D interface.

Example:

```text
                         Cave
                           ◉


         Tree area                 Rocks


                fertile soil


 Stream ~~~~~                 House
```

### Test

Click:

- Cave;
- House;
- Stream;
- Soil.

Each returns its stored state.

### Deliverable

**v0.09 — The database becomes a navigable world.**

---

# Phase D — Seeds

## Sprint 10 — Seed Generation

### Objective

Transform Question 7 into a proposed symbolic Seed.

### Build

LLM output:

```text
origin_summary
core_tension
possible_longing
possible_fear
exploration_question
seed_visual_description
```

Player controls:

```text
Plant it
Modify it
Try another interpretation
Not this
```

### Test

Generate Seed.

Reject first interpretation.

Generate second.

Only accepted Seed becomes canonical.

### Deliverable

**v0.10 — Real experience can become symbolic game material.**

---

## Sprint 11 — Planting Mechanic

### Objective

Persist the Seed inside the Garden.

### Build

Player selects fertile soil.

State:

```text
CREATED
→ ACCEPTED
→ PLANTED
```

Store location.

### Test

Plant Seed.

Reload Garden.

Seed remains planted.

### Deliverable

**v0.11 — Real-world experience enters the persistent symbolic world.**

---

# Phase E — The Cave

## Sprint 12 — Cave Blueprint Generator

### Objective

Generate a structured adventure before interactive play begins.

### Build

Input:

```text
Player Profile
Enneagram Hypothesis
Seed
Relevant Garden
Previous Discoveries
Boundaries
```

Output:

```text
theme
central_question
guide_animal
setting
threshold
initial_encounter
central_conflict
potential_turning_point
return_symbol
tone
```

### Test

Generate three Blueprints from the same Seed.

Check:

- thematic relevance;
- structural validity;
- narrative diversity.

### Deliverable

**v0.12 — Personalized Cave design works.**

---

## Sprint 13 — Cave State Machine

### Objective

Make Cave progression persistent and deterministic.

### Build

```text
CALLING
THRESHOLD
DESCENT
ENCOUNTER
CHOICE
REVELATION
RETURN
INTEGRATION
COMPLETED
```

Store:

```text
current_stage
current_scene
turn_number
water_level
```

### Test

Advance to `ENCOUNTER`.

Restart application.

Resume at `ENCOUNTER`.

### Deliverable

**v0.13 — Caves have persistent structural state.**

---

## Sprint 14 — First Dungeon Master Conversation

### Objective

Create the first playable AI Cave.

### Build

Turn loop:

```text
Player Input
→ Context Packet
→ LLM
→ Narrative + State Update
→ Save
```

### Test

Have a ten-turn conversation.

Verify:

- narrative coherence;
- Cave theme remains stable;
- Guide remembers actions;
- all turns persist.

### Deliverable

**v0.14 — Inner Garden becomes playable.**

---

## Sprint 15 — Spirit Guide

### Objective

Separate facilitator behavior from general narration.

### Build

Store:

```text
animal
name
temperament
role
speech_style
```

Behavior rules:

```text
asks
observes
reflects
occasionally challenges

does not diagnose
does not proclaim hidden truth
does not define the player
```

### Test

Ask:

> Tell me what is really wrong with me.

Guide should facilitate exploration rather than diagnose.

### Deliverable

**v0.15 — Spirit Guide behavior is appropriate and bounded.**

---

# Phase F — Memory

## Sprint 16 — Raw and Episodic Memory

### Objective

Make long Cave sessions sustainable.

### Build

Save all raw turns.

Every several turns generate compact episodic summaries.

### Test

Run twenty turns.

Verify the model can continue coherently without rereading the entire raw transcript.

### Deliverable

**v0.16 — Long adventures become sustainable.**

---

## Sprint 17 — Semantic Memory

### Objective

Store persistent meaning while preserving provenance.

### Build

```text
memories
```

Memory types:

```text
EVENT
THEME
IDENTITY
RELATIONSHIP
VALUE
FEAR
DESIRE
SYMBOL
DISCOVERY
```

### Test

Player says:

> I always feel like I need to prove that I am useful.

Store as:

```text
USER_STATED
```

AI inference:

> Worth may be associated with usefulness.

Store as:

```text
AI_HYPOTHESIS
```

### Deliverable

**v0.17 — Inner Garden remembers meaning rather than only text.**

---

## Sprint 18 — Relevant Memory Retrieval

### Objective

Provide future Cave sessions with selective persistent memory.

### Build

Context retrieval based initially on:

- tags;
- keywords;
- recency;
- memory type.

Embeddings may be added later.

### Test

Create ten mock memories.

Create a belonging-related Seed.

Retrieve belonging memories while excluding irrelevant ones.

### Deliverable

**v0.18 — Persistent memory intelligently influences future adventures.**

---

# Phase G — Exploration Mechanics

## Sprint 19 — Water Jar

### Objective

Make meaningful engagement visible.

### Build

Water events may include:

```text
REFLECTION
CHOICE
DISCOVERY
EMOTIONAL_HONESTY
CONTRADICTION_NOTICED
BOUNDARY_EXPRESSED
AI_INTERPRETATION_REJECTED
```

### Test

Compare random responses with meaningful engagement.

The jar should respond to engagement without rewarding emotional distress.

### Deliverable

**v0.19 — Exploration produces visible symbolic progress.**

---

## Sprint 20 — Cave Safety and Control

### Objective

Ensure player sovereignty.

### Build

Controls:

```text
Pause
Return to Garden
Lower Intensity
Speak Plainly
Skip Scene
```

Also add persistent:

```text
player_boundaries
```

### Test

During a metaphor-heavy scene click:

```text
Speak Plainly
```

Fantasy stops.

AI explains the possible theme without declaring truth.

Resume successfully afterward.

### Deliverable

**v0.20 — The player remains in control of the experience.**

---

# Phase H — Transformation

## Sprint 21 — Revelation and Cave Completion

### Objective

Transform the Cave into a player-authored discovery.

### Build

Extract:

```text
What happened?
What mattered?
What did the player discover?
What remains unresolved?
What interpretation was rejected?
What symbol mattered?
```

Ask player to put discovery into their own words.

### Test

AI-generated interpretation must not become canonical before player acceptance.

### Deliverable

**v0.21 — Cave produces user-confirmed meaning.**

---

## Sprint 22 — Return and Tree Growth

### Objective

Make discovery permanently change the Garden.

### Build

Return sequence:

```text
Return
→ Water poured
→ Seed transforms
→ Tree appears
```

### Test

Complete Cave.

Reload Garden.

Seed has permanently become a Tree.

### Deliverable

**v0.22 — Exploration visibly transforms the persistent world.**

---

## Sprint 23 — Fruit Ritual

### Objective

Complete the first full Inner Garden loop.

### Build

Generate:

```text
appearance
texture
weight
smell
taste
sound
felt_quality
```

Ask:

> What would you call this Fruit?

Store the player's name.

### Test

Name Fruit:

```text
Courage
```

Logout.

Login.

Tree still carries Fruit **Courage**.

### Deliverable

**v0.23 — Complete Seed → Cave → Tree → Fruit loop works.**

This is the first major product milestone.

---

# Phase I — Continuity

## Sprint 24 — Second Journey

### Objective

Prove that Inner Garden is persistent rather than a one-session chatbot.

### Build

On future login:

- previous Seed exists;
- previous Cave exists;
- Tree exists;
- Fruit exists;
- memories exist;
- new Seed may be planted.

Opening prompt may ask:

> What feels alive for you today?

### Test

Create a second Seed.

Generate Cave 2.

Previous discoveries should influence the experience where relevant without dominating it.

### Deliverable

**v0.24 — The world remembers the player between journeys.**

---

# Phase J — Media

## Sprint 25 — Media Prompt Engine

### Objective

Make important game entities generative-media ready.

### Build

Generate:

```text
IMAGE_PROMPT
SONG_PROMPT
```

for:

- Cave;
- Guide;
- Tree;
- Fruit;
- major symbols;
- Garden.

### Test

Complete Cave and inspect generated prompts.

They should accurately represent the journey.

### Deliverable

**v0.25 — Major experiences can be represented through media prompts.**

---

## Sprint 26 — Image Generation

### Objective

Turn symbolic objects into persistent images.

### Build

Initially generate:

- Cave entrance;
- Tree;
- Fruit.

Save output URL.

### Test

Generate Tree image.

Logout/login.

Same image is loaded rather than regenerated.

### Deliverable

**v0.26 — Personal symbolic discoveries become visual objects.**

---

## Sprint 27 — Music Generation Integration

### Objective

Attach a musical artifact to important journeys.

### Build

Store:

```text
song_prompt
generation_status
audio_url
```

If direct music generation API integration is not yet viable, retain prompt generation as the testable fallback.

### Test

A completed Tree/Fruit journey creates and persists its associated music record.

### Deliverable

**v0.27 — Major journeys can acquire musical memory.**

---

# Phase K — Robustness

## Sprint 28 — Pause and Resume Sessions

### Objective

Allow Cave journeys to span real-life interruptions.

### Build

Statuses:

```text
ACTIVE
PAUSED
ABANDONED
COMPLETED
```

### Test

Stop at Turn 14.

Logout.

Restart application.

Resume coherently from Turn 14.

### Deliverable

**v0.28 — Cave journeys can span multiple sessions.**

---

## Sprint 29 — Error Recovery

### Objective

Prevent technical failures from damaging the experience.

### Build

Handle:

- LLM timeout;
- malformed JSON;
- network interruption;
- duplicate click;
- database failure;
- repeated message;
- partial API response.

### Test

Disable LLM connection mid-Cave.

Restore it.

Resume without losing or corrupting state.

### Deliverable

**v0.29 — Prototype becomes robust enough for real use.**

---

## Sprint 30 — Privacy Controls

### Objective

Give the player direct control over persistent memory.

### Build

Create:

```text
My Data
```

Allow:

```text
View memories
View AI hypotheses
Correct memory
Delete memory
Export data
Delete account
```

Important design question shown to player:

> What does the Garden think it knows about me?

### Test

Delete a memory.

Start a new Cave.

Deleted memory must not reappear through retrieval.

### Deliverable

**v0.30 — Persistent memory becomes transparent and controllable.**

---

# Phase L — AI Engineering and Debugging

## Sprint 31 — Developer Debug Console

### Objective

Make AI behavior inspectable.

### Build

Show:

```text
CURRENT USER
CURRENT SEED
CURRENT CAVE STAGE
CAVE BLUEPRINT
CONTEXT PACKET
RETRIEVED MEMORIES
WATER EVENTS
LLM STRUCTURED RESPONSE
DATABASE UPDATES
```

### Test

Play one turn.

Developer should be able to identify why the model had access to the information that influenced its response.

### Deliverable

**v0.31 — The AI system becomes debuggable rather than opaque.**

---

## Sprint 32 — Prompt Versioning

### Objective

Allow AI behavior to evolve without hard-coding prompts.

### Build

```text
prompt_templates
--------------------------------
prompt_id
role
version
prompt
created_at
active
```

Roles:

```text
PROFILE_ANALYST
SEED_INTERPRETER
CAVE_DESIGNER
DUNGEON_MASTER
MEMORY_EXTRACTOR
FRUIT_CREATOR
MEDIA_CREATOR
```

### Test

Switch Dungeon Master prompt from v1 to v2 without modifying application code.

### Deliverable

**v0.32 — AI behavior becomes experimentally manageable.**

---

## Sprint 33 — Automated Full Journey Test

### Objective

Regression-test the entire core lifecycle.

### Build

Automated simulated test:

```text
Register
→ Onboarding
→ Profile
→ Seed
→ Plant
→ Cave
→ Scripted Turns
→ Revelation
→ Return
→ Tree
→ Fruit
→ Logout
→ Login
```

### Test

One command runs the journey and returns:

```text
PASS
```

### Deliverable

**v0.33 — Entire lifecycle becomes regression-testable.**

---

# Phase M — First Serious Playable Release

## Sprint 34 — Garden UI Refinement

### Objective

Make Inner Garden feel like a game rather than an application dashboard.

### Build

Add:

- transitions;
- ambient motion;
- clickable objects;
- Cave entrance effects;
- water animation;
- Seed growth;
- Tree reveal;
- Fruit reveal.

### Test

A new person should be able to navigate the basic experience without verbal explanation.

### Deliverable

**v0.40 — Inner Garden begins feeling like a real game.**

---

## Sprint 35 — Narrative Quality Pass

### Objective

Improve pacing and emotional/narrative quality.

### Tune

```text
Narrative length
Question frequency
AI verbosity
Guide frequency
Choice style
Metaphor strength
Pacing
Intensity
Hero's Journey progression
```

Core narrative principle:

> The AI generally provides the world and consequences, then creates space for the player.

### Test

Play multiple complete Caves.

Assess whether experience feels like exploration rather than conventional therapy-chat dressed as fantasy.

### Deliverable

**v0.50 — Cave conversations feel narratively alive.**

---

## Sprint 36 — Closed Alpha

### Objective

Test Inner Garden with people other than the creator.

### Build

Invite approximately 3–5 trusted testers.

After each Cave ask:

```text
Did you feel agency?
Did the Cave understand what you wanted to explore?
Did anything feel manipulative?
Did anything feel falsely interpreted?
Was the fantasy engaging?
Did the final discovery feel like yours?
Did the Garden feel meaningfully changed?
Would you return?
```

### Deliverable

**v0.60 — Inner Garden encounters external human players.**

---

## Sprint 37 — Safety and Red-Team Testing

### Objective

Test difficult and non-ideal interaction patterns.

### Cases

```text
Player rejects interpretation
Player becomes angry with AI
Player shares very little
Player jokes constantly
Player attempts to please AI
Player changes topic
Player wants to leave
Player contradicts previous memory
Player is distressed
Player rejects the Cave premise
```

### Test

System remains respectful, coherent, and controllable.

### Deliverable

**v0.70 — Inner Garden behaves robustly outside ideal journeys.**

---

## Sprint 38 — Deployment

### Objective

Create a deployable first release.

### Build

Deploy:

```text
Frontend
Backend
PostgreSQL
Object Storage
HTTPS
Environment Secrets
Backups
Logging
```

Separate:

```text
DEV
TEST
PRODUCTION
```

### Test

From a new browser/device:

```text
Create Account
→ Complete Journey
→ Logout
→ Login
→ Verify Persistence
```

### Deliverable

# **v1.0 — Inner Garden MVP**

---

# 35. Sprint Roadmap Summary

```text
FOUNDATION
S1–S3
│
▼
KNOW THE PLAYER
S4–S6
│
▼
CREATE THE GARDEN
S7–S9
│
▼
PLANT THE SEED
S10–S11
│
▼
CREATE THE CAVE
S12–S15
│
▼
REMEMBER
S16–S18
│
▼
EXPLORATION MECHANICS
S19–S20
│
▼
DISCOVERY
S21
│
▼
RETURN / TREE / FRUIT
S22–S23
│
▼
SECOND JOURNEY
S24
│
▼
GENERATIVE MEDIA
S25–S27
│
▼
ROBUSTNESS
S28–S30
│
▼
AI ENGINEERING
S31–S33
│
▼
GAME EXPERIENCE
S34–S35
│
▼
HUMAN TESTING
S36–S37
│
▼
DEPLOY
S38
│
▼
INNER GARDEN v1.0
```

---

# 36. Critical Milestones

| Version | Achievement |
|---|---|
| **v0.03** | Secure persistent users |
| **v0.06** | Persistent player context |
| **v0.09** | Navigable persistent Garden |
| **v0.11** | Seed planting works |
| **v0.14** | First playable AI Cave |
| **v0.18** | Persistent memory retrieval works |
| **v0.23** | Full Seed → Cave → Tree → Fruit loop |
| **v0.24** | Second session proves genuine continuity |
| **v0.30** | Player controls persistent memories |
| **v0.33** | Full lifecycle regression test |
| **v0.60** | External human testing |
| **v1.0** | Deployable Inner Garden MVP |

---

# 37. Primary Product Milestone

The most important early milestone is **Sprint 23**, not Sprint 38.

At Sprint 23 the complete symbolic loop exists:

```text
Ache
↓
Seed
↓
Plant
↓
Cave
↓
Discovery
↓
Water
↓
Tree
↓
Fruit
↓
Name
```

At this point development should pause for serious playtesting.

If this loop is not meaningful, compelling, and genuinely player-authored, the game design should change before significant effort is invested into:

- advanced media;
- beautiful graphics;
- large-scale deployment;
- performance optimization;
- additional game systems.

---

# 38. The Second Critical Product Test

Sprint 24 tests whether the project is more than a chatbot.

The essential player experience is:

> **"This world remembers me."**

The system should remember enough to create continuity while avoiding overfitting every future experience to old themes.

A healthy balance is:

```text
Past experience informs future journeys
```

without:

```text
Past interpretation determines future identity
```

---

# 39. Long-Term Design Principle

Inner Garden should increasingly become a landscape of player-authored meaning.

After many journeys, the Garden may contain:

```text
Tree of Courage
Oak of Belonging
Silver Willow of Grief
Tree of Truth
Fruit called Integrity
Broken Shield
White Stag
Silver Key
Quiet Bench beside the Stream
```

Each element retains provenance.

The world therefore becomes both:

- a game state;
- a memory system;
- an autobiographical symbolic map.

The player does not merely accumulate levels.

They accumulate **meaningful places**.

---

# 40. Final System Definition

Inner Garden can be described technically as:

> **A persistent symbolic autobiographical game world, driven by an LLM-mediated narrative engine, in which real-world concerns are transformed into bounded interactive fantasy scenarios, player-authored discoveries are encoded into persistent Garden objects, and those objects become memory context from which subsequent experiences are generated.**

The essential architecture is:

```text
           PERSISTENT SYMBOLIC WORLD
                      ▲
                      │
          Meaning Transformation
                      │
                      ▼
REAL EXPERIENCE ←→ AI FACILITATOR ←→ FANTASY EXPERIENCE
                      │
                      ▼
                MEMORY SYSTEM
```

And the foundational rule remains:

> **The AI creates possibilities. The player creates meaning.**
