# Universal Decoder Engine

The Universal Decoder Engine is a modular, pipeline-based system for analyzing and transforming encoded or obfuscated data in TRON-DeCypher.

## Architecture

- **DecoderInput**: A normalized input model that abstracts over raw text and bytes.
- **DecoderResult**: A normalized output model containing the transformed data, success status, warnings, errors, and any metadata output by the decoder.
- **DecoderBase**: The abstract base class that all decoders implement (extending `PluginBase`).
- **DecoderRegistry**: Dynamically registers and stores instantiated decoder plugins.
- **TransformationPipeline**: A sequence of `TransformationStep` objects representing a repeatable chain of decodings.
- **PipelineRunner**: Executes pipelines sequentially, routing output from step N into step N+1 safely.

## Detection Engine

The `DecoderDetectionService` analyzes a `DecoderInput` across all registered decoders. 
Each decoder implements a `detect` method that applies heuristics (e.g., regex matching, byte distribution, partial trial decoding) and returns a confidence score (0.0 - 1.0) and reasoning metadata.

## Auto-Decode Capabilities

The `AutoDecodeService` leverages the Detection Engine to iteratively decode obfuscated data (e.g. Hex -> Base64 -> ROT13). 
It features configurable maximum depth to prevent infinite loops and maintains a hash set of inputs at each step to prevent recursive loop traps (e.g. A -> B -> A).

## Supported Decoders

- Base64 (Standard & URL-safe)
- Base32
- Hex
- URL Encoding
- HTML Entities
- Unicode Escapes
- Binary ASCII
- ROT13 & Caesar
- Atbash
- Morse Code
- XOR (Single-byte / specific key)

## Adding a New Decoder

To add a new decoder, subclass `DecoderBase` and implement:
1. `detect(self, input_data: DecoderInput)`: Return a confidence score and metadata.
2. `decode(self, input_data: DecoderInput, context: Dict[str, Any])`: Perform the transformation and return a `DecoderResult` using `self._create_result()`.

Register your decoder in `app/decoders/__init__.py`.
