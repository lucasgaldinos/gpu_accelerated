#!/bin/bash

# JIRA Project Configuration Script for PT Project
# This script helps configure your JIRA project with the academic framework

set -e

JIRA_BASE_URL="https://this-shall-not-be-taken.atlassian.net"
PROJECT_KEY="PT"
BOARD_ID="67"

echo "🎯 Configuring JIRA Project: $PROJECT_KEY"
echo "📍 Instance: $JIRA_BASE_URL"
echo "📋 Board: $BOARD_ID"
echo ""

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "❌ jq is required but not installed. Please install it first:"
    echo "   sudo apt-get install jq"
    exit 1
fi

# Load configuration
CONFIG_FILE="$(dirname "$0")/pt_project_setup.json"
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ Configuration file not found: $CONFIG_FILE"
    exit 1
fi

echo "📖 Loading configuration from $CONFIG_FILE"

# Extract configuration sections
PROJECT_CONFIG=$(jq '.project' "$CONFIG_FILE")
CUSTOM_FIELDS=$(jq '.customFields' "$CONFIG_FILE")
ISSUE_TYPES=$(jq '.issueTypes' "$CONFIG_FILE")
WORKFLOWS=$(jq '.workflows' "$CONFIG_FILE")

echo ""
echo "🔧 Configuration Summary:"
echo "   Project: $(echo "$PROJECT_CONFIG" | jq -r '.name')"
echo "   Custom Fields: $(echo "$CUSTOM_FIELDS" | jq 'keys | length')"
echo "   Issue Types: $(echo "$ISSUE_TYPES" | jq 'keys | length')"
echo "   Workflows: $(echo "$WORKFLOWS" | jq 'keys | length')"

echo ""
echo "📋 Next Steps for JIRA Configuration:"
echo ""

echo "1. 🔑 Set up Authentication:"
echo "   - Go to: $JIRA_BASE_URL/secure/ViewProfile.jspa"
echo "   - Create an API token under 'Security' tab"
echo "   - Export credentials:"
echo "     export JIRA_USER='your-email@example.com'"
echo "     export JIRA_TOKEN='your-api-token'"
echo ""

echo "2. 📊 Configure Custom Fields:"
echo "   Navigate to: $JIRA_BASE_URL/secure/admin/ViewCustomFields.jspa"
echo ""
echo "$CUSTOM_FIELDS" | jq -r 'to_entries[] | "   - \(.key): \(.value.name) (\(.value.type))"'
echo ""

echo "3. 🎯 Set up Issue Types:"
echo "   Navigate to: $JIRA_BASE_URL/secure/admin/ViewIssueTypes.jspa"
echo ""
echo "$ISSUE_TYPES" | jq -r 'to_entries[] | "   - \(.value.name): \(.value.description)"'
echo ""

echo "4. 🔄 Configure Workflows:"
echo "   Navigate to: $JIRA_BASE_URL/secure/admin/workflows/ListWorkflows.jspa"
echo ""
echo "$WORKFLOWS" | jq -r '.academic_development.statuses[] | "   - \(.name): \(.description)"'
echo ""

echo "5. 📝 Create Issue Templates:"
echo "   Use the templates in: $(dirname "$0")/issue_templates.md"
echo "   Copy and paste into JIRA issue creation forms"
echo ""

echo "6. 🎨 Board Configuration:"
echo "   Navigate to: $JIRA_BASE_URL/jira/software/projects/$PROJECT_KEY/boards/$BOARD_ID"
echo "   Configure columns to match academic workflow statuses"
echo ""

echo "7. 🔍 Set up JQL Queries:"
echo "   Save the queries from issue_templates.md as filters"
echo "   Create dashboards for academic progress tracking"
echo ""

# Generate sample curl commands for API usage
if [[ -n "${JIRA_USER:-}" && -n "${JIRA_TOKEN:-}" ]]; then
    echo "8. 🚀 API Testing Commands:"
    echo ""
    echo "   # Test authentication:"
    echo "   curl -u '$JIRA_USER:$JIRA_TOKEN' \\"
    echo "        '$JIRA_BASE_URL/rest/api/2/myself'"
    echo ""
    echo "   # Get project info:"
    echo "   curl -u '$JIRA_USER:$JIRA_TOKEN' \\"
    echo "        '$JIRA_BASE_URL/rest/api/2/project/$PROJECT_KEY'"
    echo ""
    echo "   # Create sample issue:"
    echo "   curl -u '$JIRA_USER:$JIRA_TOKEN' \\"
    echo "        -X POST \\"
    echo "        -H 'Content-Type: application/json' \\"
    echo "        -d @sample_issue.json \\"
    echo "        '$JIRA_BASE_URL/rest/api/2/issue/'"
else
    echo "8. 🔐 Set JIRA_USER and JIRA_TOKEN environment variables to see API commands"
fi

echo ""
echo "✅ Configuration script completed!"
echo "📚 Refer to the academic task breakdown framework for implementation guidance"
echo "🎯 Start by creating Theme issues for major research areas"