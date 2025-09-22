#!/usr/bin/env python3
"""
JIRA Project Setup Script for GPU TSP Project

This script creates a complete JIRA project with:
- Custom fields for academic workflow
- Issue types for Epic/Story/Task hierarchy  
- Workflows for academic phases
- Sample issues from templates

Usage:
    python setup_jira_project.py --url https://yoursite.atlassian.net --token YOUR_TOKEN
"""
import json
import sys
import argparse
from typing import Dict, List, Any
import requests
from requests.auth import HTTPBasicAuth


class JiraProjectSetup:
    """Setup GPU TSP JIRA project with academic workflow."""
    
    def __init__(self, jira_url: str, email: str, token: str):
        self.jira_url = jira_url.rstrip('/')
        self.auth = HTTPBasicAuth(email, token)
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.project_key = 'TSPU'
        self.project_name = 'GPU TSP Optimization'
    
    def create_project(self) -> Dict[str, Any]:
        """Create the main JIRA project."""
        url = f"{self.jira_url}/rest/api/3/project"
        
        payload = {
            "key": self.project_key,
            "name": self.project_name,
            "description": "GPU-Accelerated TSP/VRP Optimization with Academic Research Integration",
            "leadAccountId": None,  # Will be set to current user
            "projectTypeKey": "software",
            "projectTemplateKey": "com.pyxis.greenhopper.jira:gh-simplified-agility-kanban"
        }
        
        response = requests.post(url, json=payload, headers=self.headers, auth=self.auth)
        return response.json() if response.status_code == 201 else None
    
    def create_custom_fields(self) -> List[Dict[str, Any]]:
        """Create custom fields for academic workflow."""
        fields = [
            {
                "name": "Academic Phase",
                "description": "Current phase of academic research (TCC)",
                "type": "com.atlassian.jira.plugin.system.customfieldtypes:select",
                "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:selectsearcher",
                "options": [
                    "Phase 1 - Foundation and Environment",
                    "Phase 2 - Core Architecture", 
                    "Phase 3 - Algorithm Implementation",
                    "Phase 4 - Database Integration",
                    "Phase 5 - Performance Analysis"
                ]
            },
            {
                "name": "Learning Objectives",
                "description": "Educational objectives for this work item",
                "type": "com.atlassian.jira.plugin.system.customfieldtypes:textarea",
                "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher"
            },
            {
                "name": "Research Context",
                "description": "Academic research context and literature references",
                "type": "com.atlassian.jira.plugin.system.customfieldtypes:textarea",
                "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher"
            },
            {
                "name": "TCC Milestone",
                "description": "Brazilian TCC thesis milestone alignment",
                "type": "com.atlassian.jira.plugin.system.customfieldtypes:select",
                "options": [
                    "Project Definition",
                    "Literature Review", 
                    "Methodology Design",
                    "Implementation Phase",
                    "Results Analysis",
                    "Documentation",
                    "Defense Preparation"
                ]
            },
            {
                "name": "RACI Assignment",
                "description": "RACI matrix assignment for academic team structure",
                "type": "com.atlassian.jira.plugin.system.customfieldtypes:textarea",
                "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher"
            },
            {
                "name": "Validation Criteria",
                "description": "Academic validation and acceptance criteria",
                "type": "com.atlassian.jira.plugin.system.customfieldtypes:textarea",
                "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher"
            },
            {
                "name": "Technical Complexity",
                "description": "Technical complexity assessment",
                "type": "com.atlassian.jira.plugin.system.customfieldtypes:select",
                "options": ["Low", "Medium", "High", "Critical"]
            },
            {
                "name": "Backend Requirements",
                "description": "Required computational backends",
                "type": "com.atlassian.jira.plugin.system.customfieldtypes:multiselect",
                "options": ["NumPy", "Numba", "CuPy", "JAX", "PyTorch"]
            },
            {
                "name": "Performance Target",
                "description": "Specific performance targets and metrics",
                "type": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
                "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher"
            },
            {
                "name": "Test Coverage Target",
                "description": "Target test coverage percentage",
                "type": "com.atlassian.jira.plugin.system.customfieldtypes:float",
                "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:numbersearcher"
            }
        ]
        
        created_fields = []
        for field in fields:
            url = f"{self.jira_url}/rest/api/3/field"
            response = requests.post(url, json=field, headers=self.headers, auth=self.auth)
            if response.status_code == 201:
                created_fields.append(response.json())
            else:
                print(f"Failed to create field {field['name']}: {response.text}")
        
        return created_fields
    
    def create_sample_epic(self) -> Dict[str, Any]:
        """Create sample epic from template."""
        url = f"{self.jira_url}/rest/api/3/issue"
        
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": "GPU-Accelerated TSP Algorithm Implementation",
                "description": """
## Epic Summary
Implement and validate a complete GPU-accelerated algorithm for the Traveling Salesman Problem using CUDA/CuPy with academic research validation.

## Background
The Traveling Salesman Problem (TSP) is a classic NP-hard optimization problem with significant real-world applications. This epic implements a GPU-accelerated solution as part of a Brazilian TCC (thesis) project.

## Objectives
- Implement multiple TSP algorithms (Nearest Neighbor, 2-opt, Genetic Algorithm)
- Provide CPU and GPU backend support (NumPy, Numba, CuPy)
- Achieve hexagonal architecture with clean interfaces
- Validate performance against academic benchmarks
- Generate reproducible research results

## Acceptance Criteria
- All algorithms implemented with Protocol-based interfaces
- Performance benchmarks show GPU speedup > 5x for problems with n > 1000
- Code coverage > 90% for all implementations
- Academic paper draft completed with statistical validation
- Documentation meets TCC standards
                """,
                "issuetype": {"name": "Epic"},
                "customfield_10001": "Phase 3 - Algorithm Implementation",  # Academic Phase
                "customfield_10002": """
- Understand GPU memory management and coalescing
- Master parallel algorithm design patterns  
- Learn performance optimization techniques
- Practice academic research methodology
                """,  # Learning Objectives
                "customfield_10003": "Literature review completed. Building on work by Applegate et al. (2006) and recent GPU optimization research by Zhang et al. (2023).",  # Research Context
                "customfield_10004": "Implementation Phase",  # TCC Milestone
                "customfield_10005": """
Responsible: Development Team
Accountable: Project Lead
Consulted: Academic Advisor
Informed: Thesis Committee
                """,  # RACI Assignment
                "customfield_10006": "Statistical significance testing using TSPLIB instances. Performance comparison with Concorde solver baseline."  # Validation Criteria
            }
        }
        
        response = requests.post(url, json=payload, headers=self.headers, auth=self.auth)
        return response.json() if response.status_code == 201 else None
    
    def create_sample_story(self, epic_key: str) -> Dict[str, Any]:
        """Create sample story linked to epic."""
        url = f"{self.jira_url}/rest/api/3/issue"
        
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": "TSP-GPU-002 - Nearest Neighbor Algorithm Implementation",
                "description": """
## User Story
As a performance researcher
I want a Nearest Neighbor TSP implementation with CPU and GPU backends
So that I can compare algorithm performance and validate the architecture design

## Technical Requirements
- Implement Protocol-based NearestNeighborSolver interface
- Support multiple computational backends (NumPy, Numba, CuPy)
- Handle distance matrix input up to 10,000 cities
- Return valid TSP tour with total distance calculation
- Provide deterministic results for reproducible research

## Acceptance Criteria
- NearestNeighborSolver Protocol interface defined
- NumPy backend implementation completed
- CuPy backend implementation completed
- Numba JIT backend implementation completed
- Performance benchmarking suite implemented
- Unit tests achieve >95% coverage
                """,
                "issuetype": {"name": "Story"},
                "parent": {"key": epic_key},
                "customfield_10001": "Phase 3 - Algorithm Implementation",  # Academic Phase
                "customfield_10007": "Medium",  # Technical Complexity
                "customfield_10008": ["NumPy", "Numba", "CuPy"],  # Backend Requirements
                "customfield_10009": "5x GPU speedup for n > 1000 cities",  # Performance Target
                "customfield_10010": 95.0  # Test Coverage Target
            }
        }
        
        response = requests.post(url, json=payload, headers=self.headers, auth=self.auth)
        return response.json() if response.status_code == 201 else None
    
    def create_sample_task(self, story_key: str) -> Dict[str, Any]:
        """Create sample task linked to story."""
        url = f"{self.jira_url}/rest/api/3/issue"
        
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": "TSP-GPU-002-04 - Implement CuPy GPU Backend",
                "description": """
## Task Summary
Implement the CuPy backend for the Nearest Neighbor TSP solver to enable GPU acceleration with proper memory management and performance optimization.

## Implementation Requirements
- Implement NearestNeighborCuPyBackend class
- Handle GPU memory transfers efficiently
- Optimize for memory coalescing patterns
- Implement error handling for GPU memory limitations
- Support distance matrices up to GPU memory limits

## Acceptance Criteria
- CuPy backend implements NearestNeighborSolver Protocol
- Handles distance matrices up to 10,000 cities (memory permitting)
- Produces identical results to NumPy baseline
- Achieves >5x speedup vs NumPy for n >= 1000
- Type hints on all methods and >95% test coverage
                """,
                "issuetype": {"name": "Task"},
                "parent": {"key": story_key},
                "customfield_10007": "High",  # Technical Complexity
                "customfield_10011": "CuPy/CUDA",  # Implementation Backend
                "customfield_10012": ">5x speedup vs NumPy baseline",  # Performance Requirement
                "customfield_10013": "Support up to GPU memory limits (~8GB typical)"  # Memory Requirement
            }
        }
        
        response = requests.post(url, json=payload, headers=self.headers, auth=self.auth)
        return response.json() if response.status_code == 201 else None
    
    def setup_project(self) -> Dict[str, Any]:
        """Complete project setup workflow."""
        results = {
            'project': None,
            'custom_fields': [],
            'sample_issues': []
        }
        
        print("🚀 Setting up GPU TSP JIRA project...")
        
        # Create project
        print("📁 Creating project...")
        project = self.create_project()
        if project:
            results['project'] = project
            print(f"✅ Project created: {project.get('key', 'Unknown')}")
        else:
            print("❌ Failed to create project")
            return results
        
        # Create custom fields
        print("🔧 Creating custom fields...")
        custom_fields = self.create_custom_fields()
        results['custom_fields'] = custom_fields
        print(f"✅ Created {len(custom_fields)} custom fields")
        
        # Create sample issues
        print("📝 Creating sample issues...")
        epic = self.create_sample_epic()
        if epic:
            results['sample_issues'].append(epic)
            epic_key = epic.get('key')
            print(f"✅ Created epic: {epic_key}")
            
            story = self.create_sample_story(epic_key)
            if story:
                results['sample_issues'].append(story)
                story_key = story.get('key')
                print(f"✅ Created story: {story_key}")
                
                task = self.create_sample_task(story_key)
                if task:
                    results['sample_issues'].append(task)
                    task_key = task.get('key')
                    print(f"✅ Created task: {task_key}")
        
        print("🎉 Project setup complete!")
        return results


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description='Setup GPU TSP JIRA project')
    parser.add_argument('--url', required=True, help='JIRA instance URL')
    parser.add_argument('--email', required=True, help='JIRA user email')
    parser.add_argument('--token', required=True, help='JIRA API token')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be created')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - Showing what would be created:")
        print()
        print("📁 Project: GPU TSP Optimization (TSPU)")
        print("🔧 Custom Fields: 10 academic workflow fields")
        print("📝 Sample Issues: 1 Epic, 1 Story, 1 Task")
        print()
        print("To actually create the project, run without --dry-run")
        return
    
    # Setup project
    setup = JiraProjectSetup(args.url, args.email, args.token)
    results = setup.setup_project()
    
    # Print summary
    print("\n📊 Setup Summary:")
    print(f"   Project: {'✅' if results['project'] else '❌'}")
    print(f"   Custom Fields: {len(results['custom_fields'])} created")
    print(f"   Sample Issues: {len(results['sample_issues'])} created")
    
    if results['project']:
        project_url = f"{args.url}/projects/{results['project']['key']}"
        print(f"\n🌐 Project URL: {project_url}")


if __name__ == '__main__':
    main()