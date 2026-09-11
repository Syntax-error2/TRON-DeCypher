import logging

from app.decoders.core.models import (
    DecoderInput,
    DecoderResult,
    TransformationPipeline,
    TransformationStep,
)
from app.decoders.core.registry import DecoderRegistry, decoder_registry

logger = logging.getLogger(__name__)

class PipelineRunner:
    def __init__(self, registry: DecoderRegistry = decoder_registry) -> None:
        self.registry = registry
        
    def run_step(self, step: TransformationStep, input_data: DecoderInput) -> DecoderResult:
        decoder = self.registry.get(step.decoder_name)
        if not decoder:
            return DecoderResult(
                success=False,
                decoder=step.decoder_name,
                errors=[f"Decoder '{step.decoder_name}' not found."]
            )
            
        try:
            result = decoder.decode(input_data, step.parameters)
            step.result = result
            return result
        except Exception as e:
            logger.error(f"Error running decoder {step.decoder_name}: {e}")
            return DecoderResult(
                success=False,
                decoder=step.decoder_name,
                errors=[str(e)]
            )
            
    def run_pipeline(self, pipeline: TransformationPipeline, initial_input: DecoderInput) -> list[DecoderResult]:
        results: list[DecoderResult] = []
        current_input = initial_input
        
        for step in pipeline.steps:
            result = self.run_step(step, current_input)
            results.append(result)
            
            if not result.success:
                logger.warning(f"Pipeline stopped at step {step.id} due to failure.")
                break
                
            # Prepare next input
            if result.output_data is not None:
                current_input = DecoderInput(data=result.output_data, source_type="bytes")
            elif result.output_text is not None:
                current_input = DecoderInput(text=result.output_text, source_type="text")
            else:
                logger.warning(f"Pipeline stopped: no output from step {step.id}")
                break
                
        return results
