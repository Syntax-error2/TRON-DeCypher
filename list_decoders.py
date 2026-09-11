from app.decoders.core.registry import decoder_registry
for d in decoder_registry.list_all():
    print(f"- {d.name} ({d.category})")
