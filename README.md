# Crouton Kit

A collection of powerful Claude Code plugins designed to enhance your development workflow with AI-powered tools for coding, learning, debugging, and more.

## Overview

Crouton Kit is a comprehensive suite of Claude Code plugins that provide specialized agents, commands, hooks, and rules to streamline your development process. Whether you're learning new code, debugging issues, managing git workflows, or building features, these plugins offer intelligent assistance at every step.

## Available Plugins

### 🔧 devcore
**Core development agents and code quality hooks**
- Custom agents for code review and quality assurance
- Automated code quality checks
- Senior advisor and programmer agents
- Commands: `code-review`, `delegate-fixes`

### 📚 learn
**Interactive learning commands to help you understand code deeply**
- Guided learning sessions with progress tracking
- Multiple learning methods: Quiz, Explain, Predict, Trace, Debug
- Deep understanding verification before moving on
- Commands: `understand`

### 🌿 git-workflow
**Git automation with logical commit creation**
- Automated git workflow management
- Intelligent commit creation
- Commands: `git`

### 💡 knowledge-capture
**Requirements gathering, interviews, and learning commands**
- Interactive interview mode for requirements gathering
- Collaborative brainstorming tools
- Knowledge documentation
- Commands: `interview`, `collaborate`, `learn`

### 🛠️ dev-utilities
**Developer utilities (notifications, command creation)**
- Notification system for development events
- Custom command creation tools
- Developer productivity enhancements

### 🐛 debugging
**Systematic debugging and bug investigation workflows**
- Structured debugging approach
- Bug investigation workflows
- Commands: `debug`, `investigate-fix`

### 🚀 rpi
**Feature development workflow: arch → plan → implement → review → fix**
- Complete feature development lifecycle
- Architecture planning
- Implementation guidance
- Review and fix workflows
- Commands: `arch`, `plan`, `implement`, `review`, `fix`

### 🌐 web
**Web development tools including frontend design workflows**
- Frontend design workflows
- Web development utilities
- Commands: `design` (frontend)

## Prerequisites

Before installing Crouton Kit plugins, ensure you have:

1. **Claude Code** - You need to have Claude Code (Claude.ai with Code capabilities) or Claude Desktop with MCP enabled
2. **Git** - Version control system for cloning the repository
3. **A code editor or IDE** - Such as VS Code, Cursor, or other editors that support Claude Code plugins

## Installation

### Step 1: Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/CaptainCrouton89/crouton-kit.git
cd crouton-kit
```

### Step 2: Locate Your Claude Code Plugin Directory

The location of your Claude Code plugin directory depends on your operating system:

- **macOS**: `~/Library/Application Support/Claude/plugins/`
- **Linux**: `~/.config/Claude/plugins/`
- **Windows**: `%APPDATA%\Claude\plugins\`

If the `plugins` directory doesn't exist, create it:

```bash
# macOS
mkdir -p ~/Library/Application\ Support/Claude/plugins/

# Linux
mkdir -p ~/.config/Claude/plugins/

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path "$env:APPDATA\Claude\plugins"
```

### Step 3: Install Plugins

You have two options for installing the plugins:

#### Option A: Symlink Method (Recommended)

This method allows you to easily update plugins by pulling from git:

```bash
# Navigate to Claude's plugin directory
# macOS
cd ~/Library/Application\ Support/Claude/plugins/

# Linux
cd ~/.config/Claude/plugins/

# Windows
cd %APPDATA%\Claude\plugins\

# Create symlink to the crouton-kit repository
ln -s /path/to/crouton-kit/plugins/* .
```

Replace `/path/to/crouton-kit` with the actual path where you cloned the repository.

#### Option B: Copy Method

Copy the plugins directly to your Claude plugin directory:

```bash
# macOS
cp -r /path/to/crouton-kit/plugins/* ~/Library/Application\ Support/Claude/plugins/

# Linux
cp -r /path/to/crouton-kit/plugins/* ~/.config/Claude/plugins/

# Windows (PowerShell)
Copy-Item -Path "C:\path\to\crouton-kit\plugins\*" -Destination "$env:APPDATA\Claude\plugins\" -Recurse
```

### Step 4: Install Specific Plugins (Optional)

If you don't want all plugins, you can install only the ones you need. For example, to install just the `learn` and `debugging` plugins:

```bash
# Using symlink (macOS/Linux)
cd ~/Library/Application\ Support/Claude/plugins/  # or ~/.config/Claude/plugins/ on Linux
ln -s /path/to/crouton-kit/plugins/learn .
ln -s /path/to/crouton-kit/plugins/debugging .

# Using copy (macOS)
cp -r /path/to/crouton-kit/plugins/learn ~/Library/Application\ Support/Claude/plugins/
cp -r /path/to/crouton-kit/plugins/debugging ~/Library/Application\ Support/Claude/plugins/
```

### Step 5: Restart Claude Code

After installing the plugins, restart Claude Code for the changes to take effect.

### Step 6: Verify Installation

To verify that the plugins are installed correctly:

1. Open Claude Code
2. Check if the new commands are available in your command palette
3. Try running a simple command like `/understand` (from the learn plugin)

## Usage

### Using Commands

Each plugin provides custom commands that you can invoke in Claude Code. Commands are typically prefixed with `/` or called directly.

**Examples:**

```
/understand          # Start an interactive learning session (learn plugin)
/code-review commit  # Review your recent code changes (devcore plugin)
/debug              # Start systematic debugging (debugging plugin)
/arch authentication # Plan a new authentication feature (rpi plugin)
```

### Using Agents

Some plugins provide custom agents that handle specific tasks. These agents can be invoked through commands or automatically triggered by hooks.

**Example agents in devcore:**
- `junior-engineer` - For straightforward coding tasks
- `programmer` - For general development work
- `senior-advisor` - For architectural guidance
- `library-docs-writer` - For documentation

### Using Hooks

Plugins may include hooks that automatically trigger on certain events:
- Pre-commit hooks for code quality checks
- Post-commit hooks for notifications
- Custom workflow triggers

## Configuration

### Marketplace Configuration

The repository includes a `.claude-plugin/marketplace.json` file that defines all available plugins. You can customize this file to:
- Enable/disable specific plugins
- Change plugin versions
- Modify plugin descriptions

### Plugin-Specific Configuration

Each plugin has its own `.claude-plugin/plugin.json` file with metadata:
- Plugin name and version
- Author information
- Description

You can customize individual plugins by modifying their respective configuration files.

## Updating Plugins

### If You Used Symlink Method

Simply pull the latest changes from the repository:

```bash
cd /path/to/crouton-kit
git pull origin main
```

The changes will automatically be reflected in Claude Code after restarting.

### If You Used Copy Method

You'll need to re-copy the updated plugins:

```bash
# Remove old plugins
rm -rf ~/Library/Application\ Support/Claude/plugins/*

# Copy updated plugins
cp -r /path/to/crouton-kit/plugins/* ~/Library/Application\ Support/Claude/plugins/
```

Then restart Claude Code.

## Troubleshooting

### Plugins Not Showing Up

1. **Check plugin directory path**: Ensure you've placed plugins in the correct location for your OS
2. **Check directory structure**: Each plugin should be in its own folder with a `.claude-plugin/plugin.json` file
3. **Restart Claude Code**: Make sure you've restarted Claude Code after installation
4. **Check permissions**: Ensure the plugin files have read permissions

### Commands Not Working

1. **Verify plugin structure**: Each plugin should have a `commands/` directory with `.md` files
2. **Check command syntax**: Some commands require arguments (e.g., `/code-review commit`)
3. **Review logs**: Check Claude Code logs for error messages

### Symlink Issues on Windows

Windows may require administrator privileges to create symlinks. Run your terminal as administrator or use the copy method instead.

### Plugin Conflicts

If you have other Claude Code plugins installed, there might be naming conflicts. Try:
1. Renaming conflicting commands
2. Disabling conflicting plugins
3. Installing only specific plugins you need

## Customization

### Creating Your Own Commands

You can add custom commands by creating `.md` files in a plugin's `commands/` directory. Follow the existing command structure:

```markdown
---
description: Your command description
argument-hint: <optional arguments>
---

# Command content and instructions
Your command implementation here...
```

### Creating Your Own Agents

Add agent definitions as `.md` files in a plugin's `agents/` directory. These agents can be invoked by commands.

### Adding Rules

Create rules in a plugin's `rules/` directory to enforce coding standards and best practices.

### Creating Hooks

Add hooks in a plugin's `hooks/` directory with a `hooks.json` configuration file to trigger automated actions.

## Plugin Structure

Each plugin follows this structure:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # Plugin metadata
├── commands/                # Command definitions (.md files)
├── agents/                  # Agent definitions (.md files)
├── rules/                   # Coding rules (.md files)
└── hooks/                   # Hook configurations
    └── hooks.json
```

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a new branch for your feature or fix
3. Make your changes following the existing plugin structure
4. Test your changes thoroughly
5. Submit a pull request with a clear description

## License

Please refer to the LICENSE file in this repository for licensing information.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub: https://github.com/CaptainCrouton89/crouton-kit/issues
- Check existing issues for solutions
- Review the plugin documentation in each plugin's directory

## Credits

Created by Silas Rhyneer

---

**Happy Coding with Crouton Kit! 🍞✨**
