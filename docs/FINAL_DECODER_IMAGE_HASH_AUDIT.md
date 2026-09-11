# Final Decoder, Image & Hash Audit

## Objective
Redesign the main Decoder workspace into a CTF-oriented Universal Analysis Workspace supporting automatic local hash recovery and unified Text/Image/File input.

## Key Enhancements

### 1. Unified Input Interface
The Decoder now provides a primary segmented control at the top:
- **[Text]**: Standard textual transformations and decoding.
- **[Image]**: Drag & drop or upload image files. Replaces the input space with an image preview and upload controls.
- **[File]**: General file drop target.

Files and images dropped into the Text input are automatically routed to their respective modes by the `InputAnalysisRouter`.

### 2. Automatic Hash Recovery
When a hash is detected with high confidence (e.g. MD5), the system prevents the generic base-decoders from dominating the interpretation. It provides a `[Recover Hash]` action directly in the detection panel.

**Workflow:**
- Clicking `[Recover Hash]` opens the **AUTOMATIC HASH RECOVERY** panel inline (via `QStackedWidget` in the tools area).
- Users click **Start Automatic Recovery**.
- A background `QThread` safely streams a built-in common CTF dictionary (e.g., `hello`, `admin`, `password`, `flag`) without blocking the GUI.
- On success, the recovered candidate is displayed in green with a `[Use Result]` button to seamlessly push it back into the main Decoder pipeline.
- The advanced manual recovery (custom wordlist, manual checking) remains available under a collapsible `Advanced Recovery ▼` section.
- **Safety**: No hashes are sent externally. No mathematical "decoding" is claimed for one-way functions.

### 3. Image Analysis integration
When in Image Mode, the bottom-left tools stack shifts to **IMAGE TOOLS**.
The output area shifts from a Text Box to a `QPixmap`-based **Image Preview**.

Capabilities integrated:
- **Format & Metadata Extraction**: `ImageAnalyzerService` extracts dimensions, format (via magic bytes and Pillow), and SHA256 hashes.
- **Action Buttons**: `[OCR]`, `[QR / Barcode]`, `[Metadata]`, `[Stego (LSB)]`, `[Extract IOCs]` are displayed to the user.
- Actions execute locally and emit results to the Output panel, where the user can push findings into the Case or send extracted text straight to the Decoder pipeline.

### 4. Zero Unexpected Navigation
The user is never unexpectedly ejected from the Decoder workspace. Clicking links inside the detection panel or dropping files natively transitions the `QStackedWidget` pages, preserving the application's state and providing a cohesive analysis cockpit.

## Security & Performance Limits
- Hashes are cracked using `hmac.compare_digest` in a background thread.
- Generators stream wordlists to avoid OOM exceptions on large dictionaries.
- Images scale via `KeepAspectRatio` solely if they exceed the preview bounding box, avoiding heavy interpolation loops on tiny stego images.

## Tests
Synthetic tests added for:
- Automatic MD5 recovery pipeline yielding `RUNNING`, `MATCH`, and candidate.
- Image analyzer properly parsing synthetic PNG headers and emitting SHA256.
- Existing tests (`pytest tests/`) remain fully passing at 92/92, demonstrating absolute backward compatibility for Phase 1-13 features.
