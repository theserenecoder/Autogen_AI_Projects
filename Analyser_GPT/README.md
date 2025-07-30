# Analyser GPT - Automated Data Analysis System

## Overview
Analyser GPT is an intelligent multi-agent system built on Autogen 0.6 framework that automates data analysis and visualization tasks. Using a team of specialized agents working in coordination through RoundRobinGroupChat, it provides seamless analysis of data files with automated code generation and execution.

## Key Features
- Automated code generation for data analysis and visualization
- Secure execution in isolated Docker container
- Intelligent dependency management
- Multi-agent architecture for specialized tasks

## System Architecture
The system comprises two main agents:

1. **Data Analyser Agent**
    - Generates analysis and visualization code
    - Determines required dependencies
    - Provides installation instructions
    - Defines analysis logic

2. **Code Executor Agent**
    - Runs code in Docker container
    - Manages dependency installation
    - Executes analysis safely
    - Returns visualization results

## Security Features
- Isolated execution environment using Docker
- Protected local file system
- Contained dependency installation

## Dependencies
- Autogen 0.6 framework
- Docker
- Python environment
- Required data analysis libraries (installed automatically)

## Usage
The system accepts data files and analysis queries, then:
1. Generates appropriate analysis code
2. Sets up required environment
3. Executes analysis securely
4. Returns visualizations and insights

## Note
All operations are performed in a containerized environment to ensure system safety and stability.