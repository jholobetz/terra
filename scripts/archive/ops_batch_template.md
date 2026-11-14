# OPS Content Generation Template (JSON Mode)

To ensure seamless integration with the `batch_ingest.py` utility, all subagent content generation must follow this strict JSON schema.

## The Prompt Pattern
"Generate Organic Platinum Standard (OPS) content for the following subtopics: [SLUG_LIST].

### CRITICAL MANDATES:
1. Lead: "In Media Res" (no "The...", no title in first 15 words).
2. Word Count: 750+ words per subtopic.
3. Format: Continuous HTML prose within the 'content' field. **MUST use `<p>` tags for all paragraphs.** Do NOT rely on newlines for separation.
4. Math: High MathJax density.
5. Hero Formula: Centered \[ ... \] with an Interpretation paragraph.
6. Technical Level: Graduate physics.
7. Outgoing Links: 5+ per subtopic.
8. Prose Structural Variety: The number of paragraphs MUST vary organically between 4 and 6 (or more) depending on the complexity of the topic. Strictly forbid standardizing on a fixed paragraph count (e.g. exactly 4 paragraphs) across multiple subtopics. The division of paragraphs must reflect the logical structure of the argument.

### OUTPUT FORMAT:
Return a SINGLE, valid JSON object. Do not include any text before or after the JSON block.

JSON Schema:
{
  "slug-name": {
    "title": "Clean Title",
    "content": "HTML Prose...",
    "standard": "platinum",
    "parents": ["parent-slug"]
  }
}
"

## Processing
The resulting output should be saved directly to `subfiles/batch_payload.json` and then ingested via:
`python3 scripts/maintenance/batch_ingest.py subfiles/batch_payload.json`
