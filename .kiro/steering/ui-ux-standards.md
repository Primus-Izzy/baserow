# UI/UX Standards for Baserow Expansion

## Design System
- Maintain consistency with existing Baserow design language
- Use the established color palette and typography
- Follow Material Design principles where applicable
- Ensure accessibility compliance (WCAG 2.1 AA)

## View System Architecture
All views should follow a consistent pattern:
- **View Controller**: Manages data fetching and state
- **View Component**: Renders the specific view type
- **View Settings**: Configurable options panel
- **View Toolbar**: Actions and filters specific to the view

## Interaction Patterns
- **Drag & Drop**: Use consistent visual feedback across all views
- **Inline Editing**: Double-click to edit, Enter to save, Escape to cancel
- **Context Menus**: Right-click for contextual actions
- **Keyboard Shortcuts**: Implement consistent shortcuts across views
- **Loading States**: Show skeleton loaders for better perceived performance

## Mobile Considerations
- Touch-friendly targets (minimum 44px)
- Swipe gestures for mobile-specific actions
- Collapsible sidebars and toolbars
- Optimized layouts for portrait and landscape modes

## Performance Guidelines
- Virtualize large lists and tables
- Lazy load images and heavy components
- Implement efficient caching strategies
- Use debounced search and filtering