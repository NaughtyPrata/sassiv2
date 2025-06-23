# 🔥 Anger Meter System

## Overview

The Anger Meter is a **game-like escalation system** that tracks cumulative anger points throughout a conversation. Unlike the previous single-message sentiment analysis, the anger meter builds up over time and slowly de-escalates when anger isn't reinforced.

## How It Works

### 🎮 Game Mechanics
- **Points Accumulate**: Each angry message adds points based on intensity
- **Levels Unlock**: Cross thresholds to trigger different anger agents
- **Slow Decay**: Points naturally decrease when anger isn't reinforced
- **Bonuses**: Extra points for consecutive anger, vulgar language, etc.
- **Penalties**: Points reduced for apologies, calm language, positive emotions

### 📊 Anger Levels
- **Normal** (0-19 points): Standard responses
- **Irritated** (20-49 points): Mildly annoyed responses  
- **Agitated** (50-79 points): Clearly frustrated responses
- **Enraged** (80+ points): Full rage mode with vulgar language

## Configuration

All behavior is controlled by `anger_config.yaml` - **edit this file to fine-tune the system without touching code**.

### Key Settings

```yaml
# Base multiplier (0.7 intensity = 7 points with 10.0 multiplier)
anger_multiplier: 10.0

# When agents switch
thresholds:
  irritated: 20
  agitated: 50  
  enraged: 80

# How anger fades
decay:
  idle_rate: 2  # Points lost per non-angry message

# Extra points for specific behaviors
bonuses:
  consecutive_anger: 3     # Back-to-back angry messages
  vulgar_language: 5       # Swearing/offensive language
  
# Point reductions
penalties:
  apology_reduction: -15   # "Sorry" messages
  calm_language: -5        # "Please", "thank you", etc.
  positive_emotion: -10    # Happy/joyful messages
```

## Testing

### Command Line Test
```bash
python test_anger_meter.py
```
This runs through escalation scenarios and shows point calculations.

### Web Interface Test
```bash
python test_anger_meter_web.py
```
Starts the server with test instructions. Open `index.html` to see the anger meter in action.

### Manual Testing Messages
1. **"Hello, how are you?"** → Should show decay
2. **"This is annoying"** → Start building points  
3. **"I'm getting frustrated!"** → More points
4. **"This is fucking stupid!"** → Vulgar language bonus
5. **"I'M SO DAMN ANGRY!!!"** → All caps + consecutive anger
6. **"Sorry, I didn't mean that"** → Apology penalty (reduces points)
7. **"Thank you for patience"** → Calm language penalty

## Fine-Tuning Guide

### Making Anger Build Faster
- Increase `anger_multiplier` (10.0 → 15.0)
- Lower `thresholds` (irritated: 20 → 15)
- Increase `bonuses` values

### Making Anger Fade Slower  
- Decrease `idle_rate` (2 → 1)
- Reduce `penalties` values
- Disable `time_decay_enabled`

### Making Levels Harder to Reach
- Increase `thresholds` (enraged: 80 → 100)
- Add `escalation_cooldown` delay
- Decrease `anger_multiplier`

## Web Interface Features

The anger meter appears in the web UI showing:
- **Current Level**: Normal/Irritated/Agitated/Enraged
- **Points Bar**: Visual representation of anger level
- **Point Changes**: ⬆️+5 or ⬇️-3 with reasons
- **Real-time Updates**: Watch anger build and fade

## Technical Details

### Architecture
- **`utils/anger_meter.py`**: Core anger tracking logic
- **`anger_config.yaml`**: All tunable parameters
- **Orchestrator Integration**: Automatic routing for anger emotions
- **Web UI Integration**: Visual anger meter display

### Emotion Detection
The system triggers on these emotions:
- `anger`, `frustration`, `irritation`, `rage`, `annoyance`

### Language Pattern Detection
- **Vulgar Language**: Profanity, all caps, multiple exclamation marks
- **Apologies**: "sorry", "apologize", "my bad", "forgive me"  
- **Calm Language**: "please", "thank you", "understand", "respect"

## Integration with Other Emotions

Currently, the anger meter **only handles anger-related emotions**. Other emotions (happiness, sadness) still use the original orchestrator logic. This allows for:

1. **Anger Escalation**: Cumulative anger tracking
2. **Other Emotions**: Immediate sentiment-based routing
3. **Mixed Conversations**: Anger can decay while other emotions are processed

## Future Enhancements

If this experiment works well, similar meter systems could be added for:
- **Sadness Meter**: Depression levels that build over time
- **Happiness Meter**: Sustained joy that affects personality
- **Fear Meter**: Anxiety that accumulates and affects responses

---

**🔧 Remember**: All tuning happens in `anger_config.yaml` - no code changes needed! 