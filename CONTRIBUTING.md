# Contributing to Midea Smart Home

Thank you for considering contributing to our project! We appreciate your efforts to make this project better.

Before you start contributing, please take a moment to review the following guidelines.

## How Can I Contribute?

### Reporting Bugs

If you encounter a bug in the project, please [open an issue](https://github.com/Cyborg2017/midea_smart_home/issues/new/) on GitHub and provide the detailed information about the bug, including the steps to reproduce the bug, the logs of debug level and the time when it occurs.

The [method](https://www.home-assistant.io/integrations/logger/#log-filters) to set the integration's log level:

```yaml
# Set the log level in configuration.yaml

logger:
  default: critical
  logs:
    custom_components.midea_smart_home: debug
```

### Requesting New Device Support

If you want to request support for a new Midea device type, please [open an issue](https://github.com/Cyborg2017/midea_smart_home/issues/new/) with the device information, including device model, device code, and discovery logs.

### Suggesting Enhancements

If you have ideas for enhancements or new features, you are welcome to [open an issue](https://github.com/Cyborg2017/midea_smart_home/issues/new/) on GitHub to discuss your ideas.

### Contributing Code

1. Fork the repository and create your branch from `staging`.
2. Ensure that your code adheres to the project coding standard.
3. Make sure that your commit messages are descriptive and meaningful.
4. Pull requests should be accompanied by a clear description of the problem and the solution.
5. Update the documents if necessary.
6. Run tests if they are available and ensure they pass.

## Pull Request Guidelines

Before submitting a pull request, please make sure that the following requirements are met:

- Your pull request addresses a single issue or feature.
- You have tested your changes locally.
- Your code follows the project's [code style](#code-style).
- All existing tests pass, and you have added new tests if applicable.
- Any dependent changes are documented.

## Code Style

We follow [Google Style](https://google.github.io/styleguide/pyguide.html) for code style and formatting. Please make sure to adhere to this guideline in your contributions.

## Commit Message Format

```
<type>: <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

type: commit type is one of the following

- feat: A new feature.
- fix: A bug fix.
- docs: Documentation only changes.
- style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc.).
- refactor: A code change that neither fixes a bug nor adds a feature.
- perf: A code change that improves performance.
- test: Adding missing tests or correcting existing tests.
- chore: Changes to the build process or auxiliary tools and libraries.
- revert: Reverting a previous commit.

subject: A short summary in imperative, present tense. Not capitalized. No period at the end.

body: A detailed description of the commit and the motivation for the change. The body is mandatory for all commits except for those of type "docs".

footer: Optional. The footer is the place to reference GitHub issues and PRs that this commit closes or is related to.

## Naming Conventions

### Home Assistant Naming

When describing Home Assistant, always use "Home Assistant". Variables can use `hass` or `hass_xxx`.

### Device Naming

When referring to device types, use clear and descriptive names:
- Air Conditioner (0xAC)
- Drying Rack (0x17)
- Washing Machine (0xD9/0xDA/0xDB)
- Water Heater (0xE2)
- Bath Heater (0x26)
- Range Hood (0xB6)
- Robot Vacuum (0xB8)
- Clothes Dryer (0xDC)
- Electric Fan (0xFA)
- Heater (0xFB)
- Air Purifier (0xFC)
- Humidifier (0xFD)

### Other Naming Conventions

- When using mixed Chinese and English sentences in the document, there must be a space between Chinese and English or the English words must be quoted by Chinese quotation marks. (It is best to write code comments this way too.)

## Supported Devices

| Code | Device Type |
|------|-------------|
| 0xAC | Air Conditioner |
| 0x17 | Drying Rack |
| 0xD9 | Twin Tub Washer |
| 0xDA | Top Load Washer |
| 0xDB | Front Load Washer |
| 0xE2 | Water Heater |
| 0x26 | Bath Heater |
| 0xB6 | Range Hood |
| 0xB8 | Robot Vacuum |
| 0xDC | Clothes Dryer |
| 0xFA | Electric Fan |
| 0xFB | Heater |
| 0xFC | Air Purifier |
| 0xFD | Humidifier |

## Licensing

When contributing to this project, you agree that your contributions will be licensed under the project's [Apache License 2.0](LICENSE).

## How to Get Help

If you need help or have questions, feel free to [open an issue](https://github.com/Cyborg2017/midea_smart_home/issues/new/) on GitHub.
