# Developer Documentation

This section provides comprehensive documentation for developers who want to extend, customize, or integrate with the expanded Baserow platform.

## Overview

The Baserow Monday.com expansion maintains the existing plugin architecture while adding new extension points for views, fields, automations, and integrations. All new features follow the same patterns and conventions as the core Baserow system.

## Architecture Overview

### Backend Architecture (Django)
- **Field Types**: Extensible field system with new advanced types
- **View Types**: Pluggable view system supporting custom visualizations  
- **Automation Engine**: Event-driven automation with custom triggers and actions
- **Collaboration System**: Real-time features using Django Channels
- **Permission System**: Hierarchical permissions with row-level security
- **Integration Framework**: OAuth 2.0 and webhook-based external integrations

### Frontend Architecture (Nuxt.js/Vue.js)
- **Component System**: Reusable Vue components following design system
- **State Management**: Vuex stores with real-time synchronization
- **View Components**: Pluggable view types with shared base functionality
- **Mobile Optimization**: Responsive design with touch interactions
- **Real-time Updates**: WebSocket integration for live collaboration

## Getting Started

### Development Environment Setup

1. **Clone the Repository**
```bash
git clone https://github.com/baserow/baserow.git
cd baserow
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py runserver
```

3. **Frontend Setup**
```bash
cd web-frontend
npm install
npm run dev
```

4. **Enable Expansion Features**
```bash
# Add to backend settings
INSTALLED_APPS += [
    'baserow.contrib.database.views.kanban',
    'baserow.contrib.database.views.timeline', 
    'baserow.contrib.database.views.calendar',
    'baserow.contrib.database.fields.progress_bar',
    'baserow.contrib.database.fields.people',
    'baserow.contrib.automation.enhanced',
    'baserow.contrib.dashboard.enhanced',
    'baserow.contrib.collaboration',
    'baserow.contrib.integrations',
]
```

### Project Structure

```
baserow/
├── backend/
│   ├── src/baserow/contrib/
│   │   ├── database/
│   │   │   ├── fields/          # Field type implementations
│   │   │   ├── views/           # View type implementations
│   │   │   ├── collaboration/   # Real-time collaboration
│   │   │   └── permissions/     # Granular permissions
│   │   ├── automation/          # Automation engine
│   │   ├── dashboard/           # Dashboard and reporting
│   │   ├── integrations/        # External integrations
│   │   └── mobile/              # Mobile optimizations
│   └── tests/                   # Test suites
├── web-frontend/
│   ├── modules/
│   │   ├── database/            # Database-related components
│   │   ├── automation/          # Automation UI components
│   │   ├── dashboard/           # Dashboard components
│   │   └── integrations/        # Integration components
│   └── test/                    # Frontend tests
└── docs/                        # Documentation
```

## Extension Points

### Creating Custom Field Types
- [Field Type Development Guide](./field-types.md)
- Base classes and interfaces
- Serialization and validation
- Frontend components
- Database migrations

### Creating Custom View Types  
- [View Type Development Guide](./view-types.md)
- View model implementation
- API endpoints and serializers
- Frontend view components
- Configuration interfaces

### Automation Extensions
- [Automation Development Guide](./automation.md)
- Custom trigger types
- Custom action types
- Workflow templates
- Error handling

### Integration Development
- [Integration Development Guide](./integrations.md)
- OAuth 2.0 providers
- Webhook handlers
- Data synchronization
- Rate limiting

## API Development

### RESTful API Guidelines
- Follow existing Baserow API patterns
- Use Django REST Framework serializers
- Implement proper pagination
- Include comprehensive error handling
- Add API documentation

### WebSocket API
- Real-time collaboration features
- Room-based message routing
- Authentication and authorization
- Message serialization
- Connection management

### Batch Operations
- Efficient bulk data operations
- Transaction management
- Progress tracking
- Error handling and rollback

## Testing Guidelines

### Backend Testing
```python
# Example field type test
class TestProgressBarField(APITestCase):
    def test_create_progress_bar_field(self):
        field = self.create_progress_bar_field(
            table=self.table,
            source_type='numeric_field',
            source_field=self.numeric_field
        )
        self.assertEqual(field.progress_bar_source_type, 'numeric_field')
```

### Frontend Testing
```javascript
// Example component test
import { mount } from '@vue/test-utils'
import KanbanView from '@/components/view/kanban/KanbanView.vue'

describe('KanbanView', () => {
  test('renders kanban columns correctly', () => {
    const wrapper = mount(KanbanView, {
      propsData: { view: mockKanbanView }
    })
    expect(wrapper.find('.kanban-column')).toBeTruthy()
  })
})
```

### E2E Testing
```javascript
// Example E2E test
test('kanban drag and drop functionality', async ({ page }) => {
  await page.goto('/database/1/table/1/kanban/1')
  await page.dragAndDrop('.kanban-card[data-id="1"]', '.kanban-column[data-status="in-progress"]')
  await expect(page.locator('.kanban-card[data-id="1"]')).toBeInViewport()
})
```

## Performance Considerations

### Database Optimization
- Efficient queries for large datasets
- Proper indexing strategies
- Query optimization for views
- Caching strategies

### Frontend Performance
- Component lazy loading
- Virtual scrolling for large lists
- Optimistic updates
- Bundle size optimization

### Real-time Performance
- WebSocket connection pooling
- Message batching and throttling
- Room-based updates
- Connection recovery

## Security Guidelines

### Authentication and Authorization
- JWT token validation
- API key management
- Permission checking
- Rate limiting

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection

### Privacy Compliance
- GDPR compliance features
- Data anonymization
- Audit logging
- Consent management

## Deployment Considerations

### Docker Configuration
```dockerfile
# Example Dockerfile additions
FROM baserow/baserow:latest
COPY --from=builder /app/backend/src/baserow/contrib/ /baserow/backend/src/baserow/contrib/
RUN pip install -r requirements/expansion.txt
```

### Environment Variables
```bash
# Expansion-specific settings
BASEROW_ENABLE_KANBAN_VIEW=true
BASEROW_ENABLE_TIMELINE_VIEW=true
BASEROW_ENABLE_CALENDAR_VIEW=true
BASEROW_ENABLE_AUTOMATION=true
BASEROW_WEBSOCKET_URL=ws://localhost:8000/ws/
```

### Database Migrations
```python
# Example migration
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('database', '0195_previous_migration'),
    ]
    
    operations = [
        migrations.CreateModel(
            name='KanbanView',
            fields=[
                ('view_ptr', models.OneToOneField(
                    auto_created=True,
                    on_delete=models.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to='database.View'
                )),
                ('single_select_field', models.ForeignKey(
                    on_delete=models.CASCADE,
                    to='database.Field'
                )),
            ],
            bases=('database.view',),
        ),
    ]
```

## Contributing Guidelines

### Code Style
- Follow existing Baserow coding standards
- Use Black for Python code formatting
- Use ESLint/Prettier for JavaScript formatting
- Write comprehensive docstrings and comments

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Update documentation
6. Submit pull request with detailed description

### Documentation Requirements
- API documentation for new endpoints
- User guides for new features
- Developer documentation for extensions
- Migration guides for breaking changes

## Resources and References

### Core Baserow Documentation
- [Baserow API Documentation](https://baserow.io/docs/apis/rest-api)
- [Plugin Development Guide](https://baserow.io/docs/plugins/introduction)
- [Field Type Development](https://baserow.io/docs/plugins/field-type)
- [View Type Development](https://baserow.io/docs/plugins/view-type)

### External Libraries and Tools
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Channels](https://channels.readthedocs.io/)
- [Vue.js](https://vuejs.org/)
- [Nuxt.js](https://nuxtjs.org/)
- [Chart.js](https://www.chartjs.org/)

### Community Resources
- [GitHub Repository](https://github.com/baserow/baserow)
- [Community Forum](https://community.baserow.io/)
- [Discord Server](https://discord.gg/baserow)
- [Developer Blog](https://baserow.io/blog)

This developer documentation provides the foundation for extending and customizing the expanded Baserow platform. For specific implementation details, refer to the individual guides for each component type.