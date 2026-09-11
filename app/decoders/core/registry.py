import logging

from app.decoders.core.base import DecoderBase

logger = logging.getLogger(__name__)

class DecoderRegistry:
    def __init__(self) -> None:
        self._decoders: dict[str, DecoderBase] = {}
        
    def register(self, decoder: DecoderBase) -> None:
        if decoder.name in self._decoders:
            logger.warning(f"Decoder {decoder.name} already registered. Overwriting.")
        self._decoders[decoder.name] = decoder
        logger.debug(f"Registered decoder: {decoder.name}")
        
    def get(self, name: str) -> DecoderBase | None:
        return self._decoders.get(name)
        
    def list_all(self) -> list[DecoderBase]:
        return list(self._decoders.values())

decoder_registry = DecoderRegistry()
