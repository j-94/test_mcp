# Contributing to Self-Improving Website Cloner

Thank you for considering contributing to the Self-Improving Website Cloner project! This document outlines the process for contributing to this project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How Can I Contribute?

### Reporting Bugs

- Use the GitHub issue tracker to report bugs
- Describe the bug in detail, including steps to reproduce
- Include browser/OS/environment information
- Attach screenshots if applicable

### Suggesting Features

- Use the GitHub issue tracker for feature suggestions
- Clearly describe the feature and its use case
- Explain how it enhances the project

### Code Contributions

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Implement your changes
4. Add tests for your changes if applicable
5. Ensure all tests pass
6. Update documentation to reflect your changes
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Development Guidelines

### Code Style

- Use consistent indentation (2 spaces)
- Follow modern JavaScript/ES6+ conventions
- Add meaningful comments for complex logic
- Use descriptive variable and function names

### Testing

- Write tests for new features
- Ensure existing tests pass
- Prioritize test coverage for critical functionality

### Documentation

- Update README.md for user-facing changes
- Update CLAUDE.md for developer-facing changes
- Add comments for complex functions
- Document API endpoints and parameters

## Extending the System

### Adding New Domains

To adapt the system for a new domain:

1. Create a new domain-specific extraction module
2. Customize the feedback templates for domain-specific features
3. Update the implementation templates with domain patterns
4. Document the new domain integration

### Enhancing the VLM Analysis

To improve the visual comparison abilities:

1. Update the prompt templates in `VLM-Powered Image Comparison` section
2. Extend the structured feedback schema for new analysis types
3. Add specific implementation patterns for new feedback types

## Getting Help

If you need help with your contribution:

- Open a discussion in GitHub Discussions
- Reach out to maintainers
- Check existing documentation in the repository

Thank you for your contributions!