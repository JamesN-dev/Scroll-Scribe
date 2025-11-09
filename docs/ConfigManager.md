# ConfigManager Implementation Plan

## Overview

The ConfigManager system will provide a unified configuration experience for ScrollScribe, supporting both interactive wizard setup and direct file editing while maintaining CLI scriptability.

## Core Requirements

1. **Command-Based Configuration**
   - One `scribe_config.json` file in user's working directory
   - Separate sections for `discover` and `scrape` commands matching CLI structure
   - `process` command inherits from both sections (discovery phase + scraping phase)
   - Support CLI flag overrides for all settings

2. **Backward Compatibility**
   - Maintain existing command behavior when no config file exists
   - Preserve all current CLI flag functionality
   - Ensure scripts using current CLI flags continue working

3. **User Experience**
   - Interactive wizard for new users (`scribe config`)
   - Direct editing for power users (`scribe config --edit`)
   - Clear validation and error messages
   - Load existing values as defaults when editing

## Implementation Phases

### Phase 1: Core ConfigManager Class

1. **Base Configuration Structure**
   ```python
   class ConfigManager:
       def __init__(self):
           self.config_path = "scribe_config.json"
           self.default_config = {
               "discover": {
                   "output_file": "urls.txt",
                   "output_format": "txt",
                   "verbose": False
               },
               "scrape": {
                   "output_dir": "output/",
                   "start_at": 0,
                   "fast": False,
                   "prompt": "",
                   "model": "openrouter/mistralai/codestral-2501",
                   "api_key_env": "OPENROUTER_API_KEY",
                   "base_url": "https://openrouter.ai/api/v1",
                   "max_tokens": 8192,
                   "timeout": 25000,
                   "wait": "networkidle",
                   "session": False,
                   "session_id": None,
                   "verbose": False
               }
           }
   ```

2. **Core Methods**
   - `load_config()` - Load and validate config file
   - `save_config()` - Write config with proper formatting
   - `get_effective_config(command)` - Merge defaults, file config, and CLI overrides for specific command
   - `get_discover_config()` - Get effective config for discover command
   - `get_scrape_config()` - Get effective config for scrape command
   - `validate_config()` - Schema validation with detailed errors
   - `determine_output_format()` - Handle discover format detection logic

### Phase 2: CLI Integration

1. **Typer Command Updates**
   - Add `config` subcommand group
   - Implement `--edit` flag handler
   - Wire up config loading in all commands

2. **Override System**
   - Create override precedence: CLI flags > config file > defaults
   - Update argument parsing to handle overrides
   - Document override behavior

### Phase 3: Interactive Wizard

1. **Questionary Integration**
   - Create question flow for all settings
   - Add validation for each input
   - Support loading current values as defaults

2. **Editor Integration**
   - Implement `$EDITOR` launching
   - Add post-edit validation
   - Provide clear error messages

## Configuration Schema

```json
{
  "discover": {
    "output_file": "urls.txt",
    "output_format": "txt",
    "verbose": false
  },
  "scrape": {
    "output_dir": "output/",
    "start_at": 0,
    "fast": false,
    "prompt": "",
    "model": "openrouter/mistralai/codestral-2501",
    "api_key_env": "OPENROUTER_API_KEY",
    "base_url": "https://openrouter.ai/api/v1",
    "max_tokens": 8192,
    "timeout": 25000,
    "wait": "networkidle",
    "session": false,
    "session_id": null,
    "verbose": false
  }
}
```

### Format Detection Logic

For the `discover` command, format is determined by:
1. **File extension** (priority): `.csv`, `.json`, `.txt` in `output_file`
2. **Fallback**: `output_format` setting if no extension detected
3. **Default**: "txt" if neither is specified

Examples:
- `"output_file": "urls.csv"` → CSV format (from extension)
- `"output_file": "urls"` + `"output_format": "json"` → JSON format (from fallback)
- `"output_file": "urls"` → TXT format (default)

## Testing Strategy

1. **Unit Tests**
   - Config file loading/saving
   - Validation logic for both command sections
   - Override merging for discover and scrape commands
   - Schema verification
   - Format detection logic (extension vs fallback)

2. **Integration Tests**
   - CLI flag overrides for both discover and scrape commands
   - Process command inheriting from both sections
   - Wizard flows for both command configurations
   - Editor integration
   - Format detection edge cases
   - Error handling

3. **User Testing**
   - Test with both new and experienced users
   - Verify backward compatibility
   - Check error message clarity

## Success Criteria

1. Users can configure ScrollScribe through:
   - Interactive wizard (`scribe config`)
   - Direct file editing (`scribe config --edit`)
   - CLI flags (maintains scriptability)

2. Configuration is:
   - Validated on load/save
   - Properly merged with CLI flags
   - Documented in README

3. Error messages are:
   - Clear and actionable
   - Help users fix issues
   - Preserve work in progress

## Timeline Estimate

1. **Phase 1 (Core Class)**: 2-3 days
   - Basic implementation: 1 day
   - Testing: 1-2 days

2. **Phase 2 (CLI Integration)**: 2-3 days
   - Implementation: 1-2 days
   - Testing: 1 day

3. **Phase 3 (Wizard)**: 3-4 days
   - Implementation: 2 days
   - Testing: 1-2 days

Total: 7-10 days including testing and documentation

## Future Considerations

1. **Config Versioning**
   - Add schema version field
   - Support upgrading old configs
   - Maintain backward compatibility

2. **Advanced Features**
   - Config profiles (dev/prod)
   - Environment-specific settings
   - Project-level defaults

3. **Security**
   - Sensitive value handling
   - Config file permissions
   - API key management

## Next Steps

1. Review and approve this implementation plan
2. Create GitHub issues for each phase
3. Begin with Phase 1 core ConfigManager class
4. Regular testing throughout development