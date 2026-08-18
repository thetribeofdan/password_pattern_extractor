{
  "type": "object",
  "required": [
    "password",
    <!-- "normalized", -->
    "tokens",
    <!-- "normalized_tokens", -->
    "numbers",
    "symbols",
    "pattern",
    "capitalization",
    "length",
    "token_positions"
  ],
  "properties": {
    "password": {
      "type": "string"
    },
    <!-- "normalized": {
      "type": "string"
    }, -->
    "tokens": {
      "type": "array",
      "items": { "type": "string" }
    },
    <!-- "normalized_tokens": {
      "type": "array",
      "items": { "type": "string" }
    }, -->
    "numbers": {
      "type": "array",
      "items": { "type": "string" }
    },
    "symbols": {
      "type": "array",
      "items": { "type": "string" }
    },
    "pattern": {
      "type": "string"
    },
    "length": {
      "type": "integer"
    },
    "token_positions": {
      "type": "array",
      "items": { "type": "integer" }
    }
  }
}