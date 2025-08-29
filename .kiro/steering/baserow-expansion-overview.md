# Baserow Expansion to Monday.com-Like Platform

## Project Vision
Transform Baserow into a comprehensive project management and collaboration platform that rivals Monday.com while maintaining its open-source nature and database-first approach.

## Core Principles
- **Database-First**: Every feature should leverage Baserow's strong database foundation
- **User Experience**: Prioritize intuitive, modern UI/UX that matches or exceeds Monday.com
- **Flexibility**: Maintain Baserow's customization strengths while adding structured workflows
- **Performance**: Ensure all new features scale well with large datasets
- **Open Source**: Keep the platform accessible and extensible

## Architecture Guidelines
- Follow existing Baserow patterns for backend (Django) and frontend (Nuxt.js)
- Maintain API-first approach for all new features
- Ensure real-time capabilities using WebSockets where appropriate
- Design for mobile-first responsive layouts
- Implement progressive enhancement for complex features

## Development Standards
- All new features must include comprehensive tests
- Follow existing code style and linting rules
- Document API changes thoroughly
- Consider backward compatibility for existing installations
- Implement feature flags for gradual rollouts