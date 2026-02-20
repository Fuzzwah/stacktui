# Configuration — Delta Spec

## MODIFIED Requirements

### Requirement: TOML Configuration Loading

The system MUST load configuration from a `dashboard.toml` file using Python's stdlib `tomllib`.

#### Scenario: Config file search order

- GIVEN no `--config` flag is provided
- WHEN the application starts
- THEN it searches for `dashboard.toml` in the current working directory first
- AND falls back to the package's parent directory (i.e., the repository root when installed in development mode)
- AND exits with an error if no config file is found
