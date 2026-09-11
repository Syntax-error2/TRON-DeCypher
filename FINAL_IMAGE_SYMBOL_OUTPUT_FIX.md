# Final Image Symbol Output Fix

## Root Cause
The root cause of the bug was a UI state overlap. The application originally mapped `Page 2: Image Mode` directly to `output_stack.setCurrentIndex(1)` (which contained `lbl_img_preview`). When an image was uploaded, `load_image` populated the output panel's preview label with the original image rather than restricting the image strictly to the left-side `input_stack`. Consequently, any textual image analyses (metadata, symbol mappings, candidate cracking) rendered behind the scenes, but the UI forced the visible result pane back to displaying the original image pixels rather than the recovered plain text.

## Files Changed
- `app/ui/views/decoder_view.py`:
  - Patched `load_image(path)`: Re-assigned `QPixmap` rendering to `self.lbl_image_drop` within the input stack so the original image remains persistently visible purely as evidence.
  - Set `load_image` to force `self.output_stack.setCurrentIndex(0)` and clear `self.txt_output` so the output canvas remains clean for text extraction.
  - Patched `switch_mode(index)`: Mode 1 (Image Input) no longer auto-triggers the output view to swap to the image renderer. The right-hand panel strictly stays in text mode unless a transformative operation (e.g., bitplane extraction) overrides it.
- `tests/unit/test_symbol_decoder.py`:
  - Appended `test_output_type_safety()` to definitively enforce `isinstance(result.decoded_text, str)` and assert `result.decoded_text != image_path`.

## Separation of Concerns (Input vs. Result)
- **Input Area**: Houses `lbl_image_drop` which now serves double-duty as a persistent `QPixmap` preview container. The source evidence never leaves the left pane.
- **Output Area**: `txt_output` receives all plain-text extractions (OCR, QR, metadata, Symbol candidates). The `lbl_img_preview` in the right pane is now strictly reserved for generated artifacts (like a forensic Stego filter).

## Symbol Detection & Mapping
- Symbol `recognizer.py` and `segmenter.py` correctly identify sequences (e.g. tracking repetitive runes or glyphs).
- The Mapping table inside the image toolkit populates these. User translations override the profile.
- `Auto Solve` generates English-scored mapping combinations across 4 reading directions.

## Output Handling (OCR / QR / Stego / Metadata)
All image-based text extractions correctly utilize `self.txt_output` and force `output_stack.setCurrentIndex(0)`.
`run_img_meta`, `run_img_ocr`, and `run_img_qr` correctly cast to structured strings instead of raw file paths.

## Decoder Handoff & Flag Detection
- `[Send to Decoder]` hooks the top candidate string from `last_sym_result` and injects it into `self.txt_input`, switching back to Text Mode. It cleanly ignores the image path.
- The Symbol solver inherently scores `CTF{...}` strings dynamically, adding a `[FLAG CANDIDATE]` visual label before placing it in `txt_output`.

## Testing & Validation
All Pytest fixtures (including the synthetic polygon mocking) passed successfully. Static typing via `mypy` is structurally sound regarding the `SymbolDecodeResult`. The application separates evidence context from artifact context.
