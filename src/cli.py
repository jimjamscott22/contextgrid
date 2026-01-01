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
    
    print("\nScope options: quick, medium, long-haul")
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
    tag = args.tag if hasattr(args, 'tag') else None
    
    try:
        # Fetch projects based on filters
        if tag:
            projects = models.list_projects_by_tag(tag, status=status)
        else:
            projects = models.list_projects(status=status)
        
        if not projects:
            if tag and status:
                print(f"No projects with status '{status}' and tag '{tag}'")
            elif tag:
                print(f"No projects with tag: {tag}")
            elif status:
                print(f"No projects with status: {status}")
            else:
                print("No projects found. Create one with: add <name>")
            return 0
        
        # Display header
        header_parts = []
        if status:
            header_parts.append(f"status={status}")
        if tag:
            header_parts.append(f"tag={tag}")
        
        if header_parts:
            print(f"\nProjects ({', '.join(header_parts)}):")
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
            
            # Show tags if any
            project_tags = models.list_project_tags(proj['id'])
            if project_tags:
                print(f"    Tags: {', '.join(project_tags)}")
            
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
        
        # Display tags
        project_tags = models.list_project_tags(project_id)
        if project_tags:
            print(f"  Tags: {', '.join(project_tags)}")
        
        print("\nLocation:")
        if project['repo_url']:
            print(f"  Repository: {project['repo_url']}")
        if project['local_path']:
            print(f"  Local: {project['local_path']}")
        
        print("\nTimestamps:")
        print(f"  Created: {project['created_at']}")
        if project['last_worked_at']:
            print(f"  Last Worked: {project['last_worked_at']}")
        
        # Display recent notes
        recent_notes = models.get_recent_notes(project_id, limit=5)
        if recent_notes:
            print("\nRecent Notes:")
            print("  " + "=" * 76)
            
            # Emoji mapping
            emoji_map = {
                "log": "📋",
                "idea": "💡",
                "blocker": "🚧",
                "reflection": "🤔"
            }
            
            for note in recent_notes:
                emoji = emoji_map.get(note['note_type'], "📝")
                timestamp = note['created_at'][:19]  # Remove microseconds
                
                # Content preview
                content = note['content']
                if len(content) > 60:
                    preview = content[:57] + "..."
                else:
                    preview = content
                
                # Replace newlines with spaces
                preview = preview.replace("\n", " ")
                
                print(f"  [{note['id']}] {emoji} {note['note_type']} - {timestamp}")
                print(f"      {preview}")
            
            print(f"\n  Run 'note list {project_id}' to see all notes")
        
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


def cmd_note_add(args) -> int:
    """Handle 'note add' command - add a note to a project."""
    project_id = args.project_id
    
    try:
        # Verify project exists
        project = models.get_project(project_id)
        if not project:
            print(f"[ERROR] Project {project_id} not found", file=sys.stderr)
            return 1
        
        print(f"\nAdding note to project: {project['name']}")
        print("=" * 50)
        
        # Prompt for note type
        print("\nNote type options: log, idea, blocker, reflection")
        note_type = input("Type [log]: ").strip() or "log"
        
        # Validate note type
        if note_type not in ["log", "idea", "blocker", "reflection"]:
            print(f"[ERROR] Invalid note type: {note_type}", file=sys.stderr)
            return 1
        
        # Prompt for content (multi-line)
        print("\nEnter your note (press Enter twice to finish):")
        lines = []
        empty_count = 0
        while empty_count < 2:
            line = input()
            if line:
                lines.append(line)
                empty_count = 0
            else:
                empty_count += 1
        
        # Remove the last empty line that triggered the exit
        content = "\n".join(lines).strip()
        
        if not content:
            print("[ERROR] Note content cannot be empty", file=sys.stderr)
            return 1
        
        # Create the note
        note_id = models.create_note(project_id, content, note_type)
        
        print(f"\n[OK] Note created with ID: {note_id}")
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error creating note: {e}", file=sys.stderr)
        return 1


def cmd_note_list(args) -> int:
    """Handle 'note list' command - list notes for a project."""
    project_id = args.project_id
    note_type = args.type if hasattr(args, 'type') else None
    
    try:
        # Verify project exists
        project = models.get_project(project_id)
        if not project:
            print(f"[ERROR] Project {project_id} not found", file=sys.stderr)
            return 1
        
        # Fetch notes
        notes = models.list_notes(project_id, note_type)
        
        if not notes:
            if note_type:
                print(f"\nNo {note_type} notes found for project: {project['name']}")
            else:
                print(f"\nNo notes found for project: {project['name']}")
            print(f"Add one with: note add {project_id}")
            return 0
        
        # Display header
        print(f"\nNotes for project: {project['name']}")
        if note_type:
            print(f"(filtered by type: {note_type})")
        print("=" * 80)
        
        # Emoji mapping
        emoji_map = {
            "log": "📋",
            "idea": "💡",
            "blocker": "🚧",
            "reflection": "🤔"
        }
        
        # Display each note
        for note in notes:
            emoji = emoji_map.get(note['note_type'], "📝")
            note_type_display = note['note_type']
            timestamp = note['created_at'][:19]  # Remove microseconds
            
            # Content preview (first 80 chars)
            content = note['content']
            if len(content) > 80:
                preview = content[:77] + "..."
            else:
                preview = content
            
            # Replace newlines with spaces in preview
            preview = preview.replace("\n", " ")
            
            print(f"\n[{note['id']}] {emoji} {note_type_display}")
            print(f"    {timestamp}")
            print(f"    {preview}")
        
        print()
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error listing notes: {e}", file=sys.stderr)
        return 1


def cmd_note_show(args) -> int:
    """Handle 'note show' command - show full note details."""
    note_id = args.note_id
    
    try:
        note = models.get_note(note_id)
        
        if not note:
            print(f"[ERROR] Note {note_id} not found", file=sys.stderr)
            return 1
        
        # Get project info
        project = models.get_project(note['project_id'])
        project_name = project['name'] if project else f"Project {note['project_id']}"
        
        # Emoji mapping
        emoji_map = {
            "log": "📋",
            "idea": "💡",
            "blocker": "🚧",
            "reflection": "🤔"
        }
        emoji = emoji_map.get(note['note_type'], "📝")
        
        # Display note
        print(f"\nNote #{note['id']} {emoji}")
        print("=" * 80)
        print(f"Project: {project_name}")
        print(f"Type: {note['note_type']}")
        print(f"Created: {note['created_at']}")
        print("\nContent:")
        print(note['content'])
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error showing note: {e}", file=sys.stderr)
        return 1


def cmd_note_delete(args) -> int:
    """Handle 'note delete' command - delete a note."""
    note_id = args.note_id
    
    try:
        # Fetch the note first
        note = models.get_note(note_id)
        
        if not note:
            print(f"[ERROR] Note {note_id} not found", file=sys.stderr)
            return 1
        
        # Show the note
        print(f"\nNote #{note['id']} - {note['note_type']}")
        print(f"Created: {note['created_at']}")
        print(f"Content: {note['content'][:100]}{'...' if len(note['content']) > 100 else ''}")
        
        # Ask for confirmation
        confirm = input("\nDelete this note? (y/N): ").strip().lower()
        
        if confirm != 'y':
            print("Cancelled")
            return 0
        
        # Delete the note
        success = models.delete_note(note_id)
        
        if success:
            print(f"[OK] Note {note_id} deleted")
            return 0
        else:
            print(f"[ERROR] Failed to delete note {note_id}", file=sys.stderr)
            return 1
        
    except Exception as e:
        print(f"[ERROR] Error deleting note: {e}", file=sys.stderr)
        return 1


def cmd_tag_add(args) -> int:
    """Handle 'tag add' command - add a tag to a project."""
    project_id = args.project_id
    tag_name = args.tag_name.strip().lower()
    
    try:
        # Verify project exists
        project = models.get_project(project_id)
        if not project:
            print(f"[ERROR] Project {project_id} not found", file=sys.stderr)
            return 1
        
        # Add the tag
        added = models.add_tag_to_project(project_id, tag_name)
        
        if added:
            print(f"[OK] Tag '{tag_name}' added to project: {project['name']}")
            return 0
        else:
            print(f"[INFO] Tag '{tag_name}' already exists on project: {project['name']}")
            return 0
        
    except Exception as e:
        print(f"[ERROR] Error adding tag: {e}", file=sys.stderr)
        return 1


def cmd_tag_remove(args) -> int:
    """Handle 'tag remove' command - remove a tag from a project."""
    project_id = args.project_id
    tag_name = args.tag_name.strip().lower()
    
    try:
        # Verify project exists
        project = models.get_project(project_id)
        if not project:
            print(f"[ERROR] Project {project_id} not found", file=sys.stderr)
            return 1
        
        # Remove the tag
        removed = models.remove_tag_from_project(project_id, tag_name)
        
        if removed:
            print(f"[OK] Tag '{tag_name}' removed from project: {project['name']}")
            return 0
        else:
            print(f"[ERROR] Tag '{tag_name}' not found on project: {project['name']}", file=sys.stderr)
            return 1
        
    except Exception as e:
        print(f"[ERROR] Error removing tag: {e}", file=sys.stderr)
        return 1


def cmd_tag_list(args) -> int:
    """Handle 'tag list' command - list all tags or tags for a project."""
    project_id = args.project_id if hasattr(args, 'project_id') and args.project_id else None
    
    try:
        if project_id:
            # List tags for a specific project
            project = models.get_project(project_id)
            if not project:
                print(f"[ERROR] Project {project_id} not found", file=sys.stderr)
                return 1
            
            tags = models.list_project_tags(project_id)
            
            if not tags:
                print(f"\nNo tags found for project: {project['name']}")
                print(f"Add one with: tag add {project_id} <tag_name>")
                return 0
            
            print(f"\nTags for project: {project['name']}")
            print("=" * 80)
            for tag in tags:
                print(f"  • {tag}")
            print()
            
        else:
            # List all tags with counts
            tags = models.list_all_tags()
            
            if not tags:
                print("\nNo tags found. Create one by adding it to a project:")
                print("  tag add <project_id> <tag_name>")
                return 0
            
            print("\nAll Tags:")
            print("=" * 80)
            for tag_info in tags:
                count = tag_info['project_count']
                plural = "project" if count == 1 else "projects"
                print(f"  • {tag_info['name']} ({count} {plural})")
            print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error listing tags: {e}", file=sys.stderr)
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
    parser_list.add_argument(
        "--tag",
        help="Filter by tag"
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
    
    # Note commands
    parser_note = subparsers.add_parser("note", help="Manage project notes")
    note_subparsers = parser_note.add_subparsers(dest="note_command", help="Note operations")
    
    # Note add command
    parser_note_add = note_subparsers.add_parser("add", help="Add a note to a project")
    parser_note_add.add_argument("project_id", type=int, help="Project ID")
    parser_note_add.set_defaults(func=cmd_note_add)
    
    # Note list command
    parser_note_list = note_subparsers.add_parser("list", help="List notes for a project")
    parser_note_list.add_argument("project_id", type=int, help="Project ID")
    parser_note_list.add_argument(
        "--type",
        choices=["log", "idea", "blocker", "reflection"],
        help="Filter by note type"
    )
    parser_note_list.set_defaults(func=cmd_note_list)
    
    # Note show command
    parser_note_show = note_subparsers.add_parser("show", help="Show full note details")
    parser_note_show.add_argument("note_id", type=int, help="Note ID")
    parser_note_show.set_defaults(func=cmd_note_show)
    
    # Note delete command
    parser_note_delete = note_subparsers.add_parser("delete", help="Delete a note")
    parser_note_delete.add_argument("note_id", type=int, help="Note ID")
    parser_note_delete.set_defaults(func=cmd_note_delete)
    
    # Tag commands
    parser_tag = subparsers.add_parser("tag", help="Manage project tags")
    tag_subparsers = parser_tag.add_subparsers(dest="tag_command", help="Tag operations")
    
    # Tag add command
    parser_tag_add = tag_subparsers.add_parser("add", help="Add a tag to a project")
    parser_tag_add.add_argument("project_id", type=int, help="Project ID")
    parser_tag_add.add_argument("tag_name", help="Tag name")
    parser_tag_add.set_defaults(func=cmd_tag_add)
    
    # Tag remove command
    parser_tag_remove = tag_subparsers.add_parser("remove", help="Remove a tag from a project")
    parser_tag_remove.add_argument("project_id", type=int, help="Project ID")
    parser_tag_remove.add_argument("tag_name", help="Tag name")
    parser_tag_remove.set_defaults(func=cmd_tag_remove)
    
    # Tag list command
    parser_tag_list = tag_subparsers.add_parser("list", help="List all tags or tags for a project")
    parser_tag_list.add_argument("project_id", type=int, nargs='?', help="Optional: Project ID to show tags for")
    parser_tag_list.set_defaults(func=cmd_tag_list)
    
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

