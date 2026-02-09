# Contributing to MACP-Powered AI Research Assistant

Thank you for your interest in contributing to MACP-Powered AI Research Assistant! This project is part of the YSenseAI™ ecosystem and follows our ethical AI principles.

---

## Ways to Contribute

### 1. **Improve Documentation**

- Fix typos or unclear explanations
- Add examples or use cases
- Translate documentation to other languages
- Create video tutorials

### 2. **Report Bugs**

- Use GitHub Issues to report bugs
- Include steps to reproduce
- Provide example MACP files if relevant

### 3. **Suggest Features**

- Use GitHub Issues for feature requests
- Explain the use case
- Describe expected behavior

### 4. **Build Tools (Phase 2)**

- Paper metadata fetcher
- Learning log CLI
- Citation tracker
- Knowledge graph generator

### 5. **Create Examples**

- Real-world research workflows
- Domain-specific examples
- Integration guides

---

## Contribution Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Follow ethical AI principles

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Test your changes
5. Commit with descriptive messages
6. Push to your fork
7. Open a Pull Request

### Commit Message Format

```
type: brief description

Detailed explanation (if needed)

Closes #issue-number
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

**Example:**
```
feat: add paper metadata fetcher for Hugging Face API

Implements automatic metadata fetching from Hugging Face Papers API
to populate research_papers.json template.

Closes #12
```

---

## Development Setup

### Prerequisites

- Git
- Python 3.8+ (for Phase 2 tools)
- GitHub account

### Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/macp-research-assistant.git
cd macp-research-assistant

# Add upstream remote
git remote add upstream https://github.com/creator35lwb-web/macp-research-assistant.git

# Install development dependencies (Phase 2)
pip install -r requirements-dev.txt
```

---

## Testing

### Manual Testing

1. Create test project
2. Copy `.macp/` templates
3. Follow workflow in README
4. Verify all steps work

### Automated Testing (Phase 2)

```bash
pytest tests/
```

---

## Documentation Standards

- Use clear, concise language
- Include examples
- Follow Markdown best practices
- Keep README up-to-date

---

## Questions?

- Open a GitHub Issue
- Email: creator35lwb@gmail.com
- X (Twitter): @creator35lwb

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to MACP-Powered AI Research Assistant!**
