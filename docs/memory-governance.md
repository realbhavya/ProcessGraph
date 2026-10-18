# Memory Governance

Memory is never written directly into the active retrieval set. New memories begin as candidates linked to an outcome, the entity they concern, and one or more evidence entities. Type-specific confidence thresholds apply. Semantic memories require an expiry timestamp.

A named reviewer must approve or reject a candidate. Only active, unexpired, confidence-qualified memories are returned. Replacement memories must first be active; supersession creates an explicit `SUPERSEDES` edge and marks the older memory `superseded`. Every review is retained as a `MemoryReview` node.
