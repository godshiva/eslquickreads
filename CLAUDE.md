# ESL QuickReads Development Guide

## Build & Run Commands
- Run server: `python main.py` (runs on port 1500)
- Development mode: Server runs with debug=True by default
- Initialize DB (first time only): Uncomment `db.create_all()` in `__init__.py` and run once

## Code Style Guidelines
- **Imports**: Group in order: standard lib, third-party, local packages
- **Naming**: snake_case for variables/functions, CamelCase for classes
- **Structure**: Follow Flask Blueprint pattern (route/lesson/developer/errors)
- **Templates**: Use Jinja2 templating with `templates/layout.html` as base
- **Forms**: Use WTForms for form validation in respective form/ directories
- **Models**: Define SQLAlchemy models in models/ directories
- **Error Handling**: Use appropriate HTTP status codes, custom error templates

## Database
- Uses SQLAlchemy ORM with MySQL
- Configure database in `configdata/debug.json` (development) or `configdata/prod.json` (production)

## Environment Detection
- Production environment detected by checking for `/home/algorithmguy` in path
- Different config files used based on environment