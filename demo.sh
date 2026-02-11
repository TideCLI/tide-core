#!/bin/bash
# Tide OS - Demo Script
# Run this to demonstrate all features for final year project

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║           Tide OS - Final Year Project Demo               ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

cd /home/snoozescript/tide-os/tide-py

echo "═══════════════════════════════════════════════════════════"
echo "Demo 1: System Health Check (tide-doctor)"
echo "═══════════════════════════════════════════════════════════"
python3 tide.py --doctor
echo ""
read -p "Press Enter to continue..."

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Demo 2: List Available Models (tide --models)"
echo "═══════════════════════════════════════════════════════════"
python3 tide.py --models
echo ""
read -p "Press Enter to continue..."

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Demo 3: Single Prompt Mode"
echo "Query: 'What is Tide OS?'"
echo "═══════════════════════════════════════════════════════════"
python3 tide.py "What is Tide OS and how does it work?"
echo ""
read -p "Press Enter to continue..."

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Demo 4: Shell Command Generation (tide --shell)"
echo "Query: 'find all Python files modified today'"
echo "═══════════════════════════════════════════════════════════"
python3 tide.py --shell "find all Python files modified today"
echo ""
read -p "Press Enter to continue..."

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Demo 5: Code Explanation (tide --explain)"
echo "Code: 'ps aux | grep python'"
echo "═══════════════════════════════════════════════════════════"
python3 tide.py --explain "ps aux | grep python"
echo ""
read -p "Press Enter to continue..."

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Demo 6: Code Generation (tide --write)"
echo "Query: 'function to reverse a string in Python'"
echo "═══════════════════════════════════════════════════════════"
python3 tide.py --write "function to reverse a string" --language python
echo ""
read -p "Press Enter to continue..."

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Demo 7: Interactive Mode (brief)"
echo "Type 'exit' to continue with the demo"
echo "═══════════════════════════════════════════════════════════"
echo "Starting interactive mode..."
echo "Try asking: 'Explain how Linux works'"
echo ""
python3 tide.py
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "                    Demo Complete!                          "
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Summary of demonstrated features:"
echo "  ✓ System health diagnostics"
echo "  ✓ Local model management"
echo "  ✓ AI-powered Q&A"
echo "  ✓ Shell command generation"
echo "  ✓ Code explanation"
echo "  ✓ Code generation"
echo "  ✓ Interactive chat mode"
echo ""
echo "All features work OFFLINE - no internet required!"
echo ""
