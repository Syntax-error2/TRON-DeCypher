import logging

from app.decoders.core.detector import DecoderDetectionService
from app.decoders.core.models import (
    DecoderInput,
    TransformationPipeline,
    TransformationStep,
)
from app.decoders.core.pipeline import PipelineRunner

logger = logging.getLogger(__name__)

class AutoDecodeService:
    def __init__(self, runner: PipelineRunner, detector: DecoderDetectionService) -> None:
        self.runner = runner
        self.detector = detector
        
    def auto_decode(self, initial_input: DecoderInput, max_depth: int = 5, min_confidence: float = 0.6) -> TransformationPipeline:
        """
        Attempts to automatically decode data by iteratively applying the highest confidence decoder.
        Stops when depth is reached or confidence falls below threshold.
        """
        pipeline = TransformationPipeline(id="auto_pipeline", name="Auto-Decode Pipeline")
        current_input = initial_input
        seen_hashes = set()
        
        for depth in range(max_depth):
            # 1. Check for loops
            data_hash = hash(current_input.text if current_input.text is not None else current_input.data)
            if data_hash in seen_hashes:
                logger.info(f"Auto-decode loop detected at depth {depth}. Stopping.")
                break
            seen_hashes.add(data_hash)
            
            # 2. Detect next
            detections = self.detector.detect(current_input, min_confidence=min_confidence)
            if not detections:
                logger.info(f"No decoders found with confidence >= {min_confidence}. Stopping.")
                break
                
            best_match = detections[0]
            logger.info(f"Auto-decode step {depth+1}: chose {best_match.decoder_name} ({best_match.confidence})")
            
            # 3. Create step and run
            import uuid
            step = TransformationStep(
                id=uuid.uuid4().hex[:8],
                decoder_name=best_match.decoder_name,
                parameters={}
            )
            
            result = self.runner.run_step(step, current_input)
            if not result.success:
                logger.warning(f"Auto-decode failed on {best_match.decoder_name}. Stopping.")
                break
                
            pipeline.steps.append(step)
            
            # 4. Prepare next input
            if result.output_data is not None:
                current_input = DecoderInput(data=result.output_data, source_type="bytes")
            elif result.output_text is not None:
                current_input = DecoderInput(text=result.output_text, source_type="text")
            else:
                break
                
        return pipeline
