# Void Loop Content Engine

The Void Loop Content Engine is a modular, Python-based framework for generating and managing structured content across multiple output formats and distribution channels. It is designed to support automated workflows, templated generation, and account-specific customization.

---

## Purpose

This project aims to automate the creation, formatting, and distribution of high-quality content using OpenAI APIs and flexible data models. Each account can define its own templates and schedule, enabling efficient management of distinct content streams.

---

## Core Concepts

- **Account**: Defines settings for a single content stream (e.g., brand, platform, audience).
- **Template**: Defines a structured format for generating content.
- **Output**: Responsible for rendering content, applying the account+template logic, and pushing to platforms (site, social, PDF, email, etc.).

---

## Folder Structure
```
VoidLoopContentEngine/
├── config/ # Static configuration files, one per account 
├── data/ # Persistent or historical content data
├── diagrams/ # System design diagrams (e.g., domain model, use cases)
├── models/ # Core data schemas and classes (Account, Template, Output)
├── services/ # Logic for generation, formatting, dispatching, etc.
├── templates/ # Content templates per account and format
├── main.py # Entry point CLI for generating or scheduling content
├── requirements.txt
```