# Enhanced JoyCaption Features

## New Features Added

### 1. Avatar Names
Instead of generic terms like "a woman" or "the person", you can specify a custom name that will be used throughout the caption.

### 2. Attractiveness Rating
The model analyzes the person's physical attractiveness and provides a rating from 1-10.

## Usage Examples

### Basic Usage with Avatar Name
```bash
# Interactive prompt for avatar name
python batch_caption_enhanced.py /path/to/images/

# Specify avatar name via command line
python batch_caption_enhanced.py /path/to/images/ --avatar-name "Sarah"
```

### With Attractiveness Rating
```bash
# Include attractiveness rating
python batch_caption_enhanced.py /path/to/images/ --rate-attractiveness

# Combined: avatar name + attractiveness rating
python batch_caption_enhanced.py /path/to/images/ --avatar-name "Emma" --rate-attractiveness
```

## Example Output

### Before (Generic):
```json
{
  "caption": "This is a close-up photograph of a young woman with fair skin...",
  "model": "fancyfeast/llama-joycaption-beta-one-hf-llava"
}
```

### After (Enhanced):
```json
{
  "caption": "This is a close-up photograph of Emma's face, capturing her from the shoulders up. Emma has fair skin with a few freckles...",
  "model": "fancyfeast/llama-joycaption-beta-one-hf-llava",
  "mode": "detailed_uncensored",
  "avatar_name": "Emma",
  "attractiveness_rating": 8
}
```

## Attractiveness Rating Scale

- **1-2**: Very unattractive
- **3-4**: Below average
- **5-6**: Average
- **7-8**: Above average/attractive
- **9-10**: Extremely attractive/model-like

## Advanced Usage

### Batch Processing with Different Names
```bash
# Process different directories with different avatar names
python batch_caption_enhanced.py dataset/emma/ --avatar-name "Emma" --rate-attractiveness
python batch_caption_enhanced.py dataset/sarah/ --avatar-name "Sarah" --rate-attractiveness
python batch_caption_enhanced.py dataset/misc/ --rate-attractiveness  # No specific name
```

### Integration with Training Scripts
```python
import json

def load_enhanced_caption(image_path):
    json_path = image_path.with_suffix('.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    return {
        'caption': data['caption'],
        'avatar_name': data.get('avatar_name'),
        'attractiveness': data.get('attractiveness_rating')
    }

# Example usage in training
caption_data = load_enhanced_caption("emma_001.png")
print(f"Caption: {caption_data['caption']}")
print(f"Avatar: {caption_data['avatar_name']}")
print(f"Rating: {caption_data['attractiveness']}/10")
```

## Benefits for Fine-tuning

### 1. Consistent Character Names
- Better for character-specific model training
- Helps model learn to associate specific names with visual features
- Useful for creating character-consistent datasets

### 2. Attractiveness Metadata
- Filter datasets by attractiveness ratings
- Train models with attractiveness conditioning
- Quality control for model training data
- Useful for beauty/fashion applications

## Command Line Reference

```bash
python batch_caption_enhanced.py <directory> [options]

Options:
  --avatar-name NAME           Use specific name instead of generic terms
  --rate-attractiveness        Include 1-10 attractiveness rating
  --mode MODE                  Caption mode (training, detailed_uncensored, etc.)
  --recursive                  Process subdirectories
  --dry-run                    Preview what would be processed
  --skip-existing             Skip images that already have JSON files (default)
```

## Notes

- Avatar names work best with single-person images
- Attractiveness rating is subjective and based on conventional beauty standards
- The model uses objective criteria for rating (facial symmetry, features, etc.)
- Both features are optional and can be used independently