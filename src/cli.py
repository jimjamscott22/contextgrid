"""
Command-line interface for ContextGrid.
Handles user commands and presents formatted output.
"""

import argparse
import sys
from typing import Optional
import models


def cmd_add(args) -> int:
    """Handle 'add' command - create a new project."""
    name = args.name
    
    print(f"\nCreating project: {name}")
    print("=" * 50)
    
    # Prompt for optional fields
    description = input("Description (optional): ").strip() or None
    
    print("\nStatus options: idea, active, paused, archived")
    status = input("Status [idea]: ").strip() or "idea"
    
    print("\nType options: web, cli, library, homelab, research")
    project_type = input("Type (optional): ").strip() or None
    
    primary_language = input("Primary language (optional): ").strip() or None
    stack = input("Stack/tech (optional): ").strip() or None
    repo_url = input("Repository URL (optional): ").strip() or None
    local_path = input("Local path (optional): ").strip() or None
    
    print("\nScope options: tiny, medium, long-haul")
    scope_size = input("Scope (optional): ").strip() or None
    
    learning_goal = input("Learning goal (optional): ").strip() or None
    
    # Create the project
    try:
        project_id = models.create_project(
            name=name,
            description=description,
            status=status,
            project_type=project_type,
            primary_language=primary_language,
            stack=stack,
            repo_url=repo_url,
            local_path=local_path,
            scope_size=scope_size,
            learning_goal=learning_goal,
        )
        
        print(f"\n[OK] Project created with ID: {project_id}")
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Error creating project: {e}", file=sys.stderr)
        return 1


def cmd_list(args) -> int:
    """Handle 'list' command - show all projects."""
    status = args.status
    
    try:
        projects = models.list_projects(status=status)
        
        if not projects:
            if status:
                print(f"No projects with status: {status}")
            else:
                print("No projects found. Create one with: add <name>")
            return 0
        
        # Display header
        if status:
            print(f"\nProjects (status={status}):")
        else:
            print("\nAll Projects:")
        print("=" * 80)
        
        # Display each project
        for proj in projects:
            print(f"\n[{proj['id']}] {proj['name']}")
            print(f"    Status: {proj['status']}", end="")
            
            if proj['project_type']:
                print(f" | Type: {proj['project_type']}", end="")
            
            if proj['primary_language']:
                print(f" | Language: {proj['primary_language']}", end="")
            
            print()  # newline
            
            if proj['description']:
                print(f"    {proj['description']}")
            
            if proj['last_worked_at']:
                print(f"    Last worked: {proj['last_worked_at']}")
            else:
                print(f"    Created: {proj['created_at']}")
        
        print()
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error listing projects: {e}", file=sys.stderr)
        return 1


def cmd_show(args) -> int:
    """Handle 'show' command - display full project details."""
    project_id = args.id
    
    try:
        project = models.get_project(project_id)
        
        if not project:
            print(f"[ERROR] Project {project_id} not found", file=sys.stderr)
            return 1
        
        # Display full project details
        print(f"\nProject: {project['name']}")
        print("=" * 80)
        print(f"ID: {project['id']}")
        print(f"Status: {project['status']}")
        
        if project['description']:
            print(f"\nDescription:\n  {project['description']}")
        
        print("\nMetadata:")
        if project['project_type']:
            print(f"  Type: {project['project_type']}")
        if project['primary_language']:
            print(f"  Language: {project['primary_language']}")
        if project['stack']:
            print(f"  Stack: {project['stack']}")
        if project['scope_size']:
            print(f"  Scope: {project['scope_size']}")
        if project['learning_goal']:
            print(f"  Learning Goal: {project['learning_goal']}")
        
        print("\nLocation:")
        if project['repo_url']:
            print(f"  Repository: {project['repo_url']}")
        if project['local_path']:
            print(f"  Local: {project['local_path']}")
        
        print("\nTimestamps:")
        print(f"  Created: {project['created_at']}")
        if project['last_worked_at']:
            print(f"  Last Worked: {project['last_worked_at']}")
        
        print()
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error showing project: {e}", file=sys.stderr)
        return 1


def cmd_update(args) -> int:
    """Handle 'update' command - modify project fields."""
    project_id = args.id
    
    try:
        # Check if project exists
        project = models.get_project(project_id)
        if not project:
            print(f"[ERROR] Project {project_id} not found", file=sys.stderr)
            return 1
        
        print(f"\nUpdating project: {project['name']}")
        print("=" * 50)
        print("(Press Enter to keep current value)\n")
        
        # Build update dictionary
        updates = {}
        
        # Prompt for each field
        new_name = input(f"Name [{project['name']}]: ").strip()
        if new_name:
            updates['name'] = new_name
        
        new_desc = input(f"Description [{project['description'] or ''}]: ").strip()
        if new_desc:
            updates['description'] = new_desc
        
        print("\nStatus options: idea, active, paused, archived")
        new_status = input(f"Status [{project['status']}]: ").strip()
        if new_status:
            updates['status'] = new_status
        
        print("\nType options: web, cli, library, homelab, research")
        new_type = input(f"Type [{project['project_type'] or ''}]: ").strip()
        if new_type:
            updates['project_type'] = new_type
        
        new_lang = input(f"Language [{project['primary_language'] or ''}]: ").strip()
        if new_lang:
            updates['primary_language'] = new_lang
        
        new_stack = input(f"Stack [{project['stack'] or ''}]: ").strip()
        if new_stack:
            updates['stack'] = new_stack
        
        new_repo = input(f"Repository [{project['repo_url'] or ''}]: ").strip()
        if new_repo:
            updates['repo_url'] = new_repo
        
        new_path = input(f"Local path [{project['local_path'] or ''}]: ").strip()
        if new_path:
            updates['local_path'] = new_path
        
        print("\nScope options: tiny, medium, long-haul")
        new_scope = input(f"Scope [{project['scope_size'] or ''}]: ").strip()
        if new_scope:
            updates['scope_size'] = new_scope
        
        new_goal = input(f"Learning goal [{project['learning_goal'] or ''}]: ").strip()
        if new_goal:
            updates['learning_goal'] = new_goal
        
        # Apply updates
        if updates:
            success = models.update_project(project_id, **updates)
            if success:
                print(f"\n[OK] Project {project_id} updated")
                return 0
            else:
                print(f"\n[ERROR] Failed to update project {project_id}", file=sys.stderr)
                return 1
        else:
            print("\nNo changes made")
            return 0
        
    except Exception as e:
        print(f"[ERROR] Error updating project: {e}", file=sys.stderr)
        return 1


def cmd_touch(args) -> int:
    """Handle 'touch' command - update last_worked_at timestamp."""
    project_id = args.id
    
    try:
        success = models.update_last_worked(project_id)
        
        if success:
            print(f"[OK] Updated last_worked_at for project {project_id}")
            return 0
        else:
            print(f"[ERROR] Project {project_id} not found", file=sys.stderr)
            return 1
        
    except Exception as e:
        print(f"[ERROR] Error touching project: {e}", file=sys.stderr)
        return 1


def cmd_roadmap(args) -> int:
    """Handle 'roadmap' command - generate ROADMAP.md visualization."""
    from pathlib import Path
    from datetime import datetime
    
    output_file = args.output if hasattr(args, 'output') and args.output else "ROADMAP.md"
    
    try:
        # Fetch all projects grouped by status
        all_projects = models.list_projects()
        
        if not all_projects:
            print("No projects found. Create some projects first!")
            return 0
        
        # Group projects by status
        status_groups = {
            "idea": [],
            "active": [],
            "paused": [],
            "archived": []
        }
        
        for project in all_projects:
            status = project.get("status", "idea")
            if status in status_groups:
                status_groups[status].append(project)
        
        # Generate Markdown content
        lines = []
        lines.append("# Project Roadmap")
        lines.append("")
        lines.append(f"*Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*")
        lines.append("")
        lines.append("A visual overview of all projects tracked in ContextGrid.")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Status legend
        lines.append("## Legend")
        lines.append("")
        lines.append("- **Idea**: Early concept, not yet started")
        lines.append("- **Active**: Currently being worked on")
        lines.append("- **Paused**: On hold, may resume later")
        lines.append("- **Archived**: Completed or abandoned")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Generate sections for each status
        status_config = {
            "active": {"emoji": "🚀", "title": "Active Projects", "desc": "Currently in development"},
            "idea": {"emoji": "💡", "title": "Ideas", "desc": "Concepts waiting to be started"},
            "paused": {"emoji": "⏸️", "title": "Paused Projects", "desc": "On hold for now"},
            "archived": {"emoji": "📦", "title": "Archived Projects", "desc": "Completed or shelved"}
        }
        
        for status in ["active", "idea", "paused", "archived"]:
            projects = status_groups[status]
            config = status_config[status]
            
            lines.append(f"## {config['emoji']} {config['title']}")
            lines.append("")
            lines.append(f"*{config['desc']}*")
            lines.append("")
            
            if not projects:
                lines.append("_No projects in this status._")
                lines.append("")
            else:
                for project in projects:
                    lines.append(f"### {project['name']}")
                    lines.append("")
                    
                    # Basic info
                    if project.get('description'):
                        lines.append(f"> {project['description']}")
                        lines.append("")
                    
                    # Metadata table
                    lines.append("| Property | Value |")
                    lines.append("|----------|-------|")
                    lines.append(f"| **ID** | `{project['id']}` |")
                    lines.append(f"| **Status** | `{project['status']}` |")
                    
                    if project.get('project_type'):
                        lines.append(f"| **Type** | {project['project_type']} |")
                    
                    if project.get('primary_language'):
                        lines.append(f"| **Language** | {project['primary_language']} |")
                    
                    if project.get('stack'):
                        lines.append(f"| **Stack** | {project['stack']} |")
                    
                    if project.get('scope_size'):
                        lines.append(f"| **Scope** | {project['scope_size']} |")
                    
                    if project.get('learning_goal'):
                        lines.append(f"| **Learning Goal** | {project['learning_goal']} |")
                    
                    # Location
                    if project.get('local_path'):
                        lines.append(f"| **Path** | `{project['local_path']}` |")
                    
                    if project.get('repo_url'):
                        lines.append(f"| **Repository** | {project['repo_url']} |")
                    
                    # Timestamps
                    lines.append(f"| **Created** | {project['created_at'][:10]} |")
                    
                    if project.get('last_worked_at'):
                        lines.append(f"| **Last Worked** | {project['last_worked_at'][:10]} |")
                    
                    lines.append("")
                    lines.append("---")
                    lines.append("")
            
            lines.append("")
        
        # Summary section
        lines.append("## 📊 Summary")
        lines.append("")
        lines.append("| Status | Count |")
        lines.append("|--------|-------|")
        for status in ["active", "idea", "paused", "archived"]:
            count = len(status_groups[status])
            lines.append(f"| {status.capitalize()} | {count} |")
        lines.append(f"| **Total** | **{len(all_projects)}** |")
        lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Generated by [ContextGrid](https://github.com/yourusername/contextgrid)*")
        lines.append("")
        
        # Write to file
        content = "\n".join(lines)
        output_path = Path(output_file)
        output_path.write_text(content, encoding="utf-8")
        
        print(f"[OK] Roadmap generated: {output_path.absolute()}")
        print(f"     Projects: {len(all_projects)}")
        print(f"     Active: {len(status_groups['active'])}, Ideas: {len(status_groups['idea'])}")
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error generating roadmap: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="contextgrid",
        description="ContextGrid - Personal project tracker",
        epilog="Track what you're building, where it lives, and what's next."
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add command
    parser_add = subparsers.add_parser("add", help="Create a new project")
    parser_add.add_argument("name", help="Project name")
    parser_add.set_defaults(func=cmd_add)
    
    # List command
    parser_list = subparsers.add_parser("list", help="List all projects")
    parser_list.add_argument(
        "--status",
        choices=["idea", "active", "paused", "archived"],
        help="Filter by status"
    )
    parser_list.set_defaults(func=cmd_list)
    
    # Show command
    parser_show = subparsers.add_parser("show", help="Show project details")
    parser_show.add_argument("id", type=int, help="Project ID")
    parser_show.set_defaults(func=cmd_show)
    
    # Update command
    parser_update = subparsers.add_parser("update", help="Update project fields")
    parser_update.add_argument("id", type=int, help="Project ID")
    parser_update.set_defaults(func=cmd_update)
    
    # Touch command
    parser_touch = subparsers.add_parser("touch", help="Update last_worked_at timestamp")
    parser_touch.add_argument("id", type=int, help="Project ID")
    parser_touch.set_defaults(func=cmd_touch)
    
    # Roadmap command
    parser_roadmap = subparsers.add_parser("roadmap", help="Generate ROADMAP.md visualization")
    parser_roadmap.add_argument(
        "--output",
        default="ROADMAP.md",
        help="Output file path (default: ROADMAP.md)"
    )
    parser_roadmap.set_defaults(func=cmd_roadmap)
    
    return parser


def main(argv: Optional[list] = None) -> int:
    """
    Main CLI entry point.
    
    Args:
        argv: Command-line arguments (defaults to sys.argv[1:])
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to command handler
    return args.func(args)

