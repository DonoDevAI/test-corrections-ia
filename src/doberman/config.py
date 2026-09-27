# src/doberman/config.py (around line 429)
# Fix: Join MESSAGE_TONES tuple elements with comma instead of displaying raw tuple

def validate_message_tone(tone):
    """Validate that a message tone is one of the allowed values."""
    from doberman.config import MESSAGE_TONES
    
    if tone not in MESSAGE_TONES:
        # FIXED: Use ', '.join() to display 'human, technical' instead of ('human', 'technical')
        raise ValueError(f"unknown message tone '{tone}'; choose one of: {', '.join(MESSAGE_TONES)}")
    
    return tone

# MESSAGE_TONES definition (tuple of valid tones)
MESSAGE_TONES = ('human', 'technical')