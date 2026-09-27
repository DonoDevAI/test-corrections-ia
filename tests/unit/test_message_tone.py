import pytest
from doberman.config import validate_message_tone

def test_message_tone_error_message_format():
    """Test that error message lists tones without tuple formatting"""
    with pytest.raises(ValueError) as exc_info:
        validate_message_tone('bogus')
    
    error_message = str(exc_info.value)
    
    # Verify error message contains both tones
    assert 'human' in error_message
    assert 'technical' in error_message
    
    # Verify no tuple formatting (no parentheses or quotes around tones)
    assert "('human'" not in error_message
    assert "('technical'" not in error_message
    assert '"human"' not in error_message
    assert '"technical"' not in error_message
    
    # Verify the expected format
    assert 'choose one of:' in error_message
    assert 'human, technical' in error_message