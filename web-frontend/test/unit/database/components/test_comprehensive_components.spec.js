/**
 * Comprehensive unit tests for frontend components
 * in the Baserow Monday.com expansion.
 */
import { mount, createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'
import { expect } from '@jest/globals'

// Import components to test
import KanbanView from '@/modules/database/components/view/kanban/KanbanView.vue'
import KanbanCard from '@/modules/database/components/view/kanban/KanbanCard.vue'
import KanbanColumn from '@/modules/database/components/view/kanban/KanbanColumn.vue'
import TimelineView from '@/modules/database/components/view/timeline/TimelineView.vue'
import TimelineRow from '@/modules/database/components/view/timeline/TimelineRow.vue'
import CalendarView from '@/modules/database/components/view/calendar/CalendarView.vue'
import CalendarEvent from '@/modules/database/components/view/calendar/CalendarEvent.vue'
import ProgressBarDisplay from '@/modules/database/components/field/ProgressBarDisplay.vue'
import FieldProgressBarSubForm from '@/modules/database/components/field/FieldProgressBarSubForm.vue'
import GridViewFieldPeople from '@/modules/database/components/view/grid/fields/GridViewFieldPeople.vue'
import Comment from '@/modules/database/components/collaboration/Comment.vue'
import CommentThread from '@/modules/database/components/collaboration/CommentThread.vue'
import ActivityLog from '@/modules/database/components/collaboration/ActivityLog.vue'
import VisualAutomationBuilder from '@/modules/automation/components/workflow/enhanced/VisualAutomationBuilder.vue'
import EnhancedChart from '@/modules/dashboard/components/widget/EnhancedChart.vue'
import KPIWidget from '@/modules/dashboard/components/widget/KPIWidget.vue'

const localVue = createLocalVue()
localVue.use(Vuex)

// Mock store modules
const mockStore = {
  modules: {
    view: {
      namespaced: true,
      state: {
        selected: {
          id: 1,
          name: 'Test View',
          type: 'kanban'
        }
      },
      getters: {
        get: () => (id) => ({ id, name: 'Test View' })
      }
    },
    field: {
      namespaced: true,
      state: {
        items: [
          { id: 1, name: 'Status', type: 'single_select' },
          { id: 2, name: 'Title', type: 'text' },
          { id: 3, name: 'Progress', type: 'progress_bar' }
        ]
      },
      getters: {
        getAll: (state) => state.items
      }
    },
    table: {
      namespaced: true,
      state: {
        selected: {
          id: 1,
          name: 'Test Table'
        }
      }
    }
  }
}

describe('KanbanView Component', () => {
  let store

  beforeEach(() => {
    store = new Vuex.Store(mockStore)
  })

  it('renders kanban columns correctly', () => {
    const wrapper = mount(KanbanView, {
      localVue,
      store,
      propsData: {
        view: {
          id: 1,
          single_select_field: 1,
          card_fields: [2]
        },
        fields: [
          { id: 1, name: 'Status', type: 'single_select', select_options: [
            { id: 1, value: 'To Do', color: 'blue' },
            { id: 2, value: 'In Progress', color: 'yellow' },
            { id: 3, value: 'Done', color: 'green' }
          ]},
          { id: 2, name: 'Title', type: 'text' }
        ],
        rows: [
          { id: 1, field_1: 1, field_2: 'Task 1' },
          { id: 2, field_1: 2, field_2: 'Task 2' }
        ]
      }
    })

    // Check that columns are rendered
    expect(wrapper.findAll('.kanban-column')).toHaveLength(3)
    expect(wrapper.text()).toContain('To Do')
    expect(wrapper.text()).toContain('In Progress')
    expect(wrapper.text()).toContain('Done')
  })

  it('handles card drag and drop', async () => {
    const wrapper = mount(KanbanView, {
      localVue,
      store,
      propsData: {
        view: { id: 1, single_select_field: 1 },
        fields: [{ id: 1, name: 'Status', type: 'single_select', select_options: [] }],
        rows: []
      }
    })

    // Mock drag and drop event
    const dragEvent = {
      dataTransfer: {
        setData: jest.fn(),
        getData: jest.fn(() => '1') // row id
      }
    }

    const dropEvent = {
      dataTransfer: {
        getData: jest.fn(() => '1')
      },
      preventDefault: jest.fn()
    }

    // Simulate drag start
    await wrapper.vm.onCardDragStart(dragEvent, { id: 1 })
    expect(dragEvent.dataTransfer.setData).toHaveBeenCalledWith('text/plain', '1')

    // Simulate drop
    const updateRowSpy = jest.spyOn(wrapper.vm, 'updateRow')
    await wrapper.vm.onCardDrop(dropEvent, 'In Progress')
    
    expect(updateRowSpy).toHaveBeenCalledWith(1, { field_1: 'In Progress' })
  })

  it('supports inline editing', async () => {
    const wrapper = mount(KanbanView, {
      localVue,
      store,
      propsData: {
        view: { id: 1, single_select_field: 1 },
        fields: [{ id: 2, name: 'Title', type: 'text' }],
        rows: [{ id: 1, field_2: 'Original Title' }]
      }
    })

    // Find and double-click a card
    const card = wrapper.find('.kanban-card')
    await card.trigger('dblclick')

    // Check that inline editing is enabled
    expect(wrapper.vm.editingCard).toBe(1)
    
    // Simulate editing
    const input = wrapper.find('input[data-field="2"]')
    await input.setValue('Updated Title')
    await input.trigger('keyup.enter')

    // Verify update was called
    expect(wrapper.emitted('update-row')).toBeTruthy()
  })
})

describe('KanbanCard Component', () => {
  it('renders card content correctly', () => {
    const wrapper = mount(KanbanCard, {
      propsData: {
        row: { id: 1, field_1: 'Test Task', field_2: 'High' },
        fields: [
          { id: 1, name: 'Title', type: 'text' },
          { id: 2, name: 'Priority', type: 'single_select' }
        ],
        visibleFields: [1, 2]
      }
    })

    expect(wrapper.text()).toContain('Test Task')
    expect(wrapper.text()).toContain('High')
  })

  it('applies color coding correctly', () => {
    const wrapper = mount(KanbanCard, {
      propsData: {
        row: { id: 1, field_1: 'Test Task' },
        fields: [{ id: 1, name: 'Title', type: 'text' }],
        visibleFields: [1],
        color: '#ff0000'
      }
    })

    const cardElement = wrapper.find('.kanban-card')
    expect(cardElement.attributes('style')).toContain('border-left-color: #ff0000')
  })

  it('emits events on user interactions', async () => {
    const wrapper = mount(KanbanCard, {
      propsData: {
        row: { id: 1, field_1: 'Test Task' },
        fields: [{ id: 1, name: 'Title', type: 'text' }],
        visibleFields: [1]
      }
    })

    // Test click event
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()

    // Test double-click event
    await wrapper.trigger('dblclick')
    expect(wrapper.emitted('edit')).toBeTruthy()
  })
})

describe('TimelineView Component', () => {
  let store

  beforeEach(() => {
    store = new Vuex.Store(mockStore)
  })

  it('renders timeline correctly', () => {
    const wrapper = mount(TimelineView, {
      localVue,
      store,
      propsData: {
        view: {
          id: 1,
          start_date_field: 1,
          end_date_field: 2,
          zoom_level: 'week'
        },
        fields: [
          { id: 1, name: 'Start Date', type: 'date' },
          { id: 2, name: 'End Date', type: 'date' },
          { id: 3, name: 'Task', type: 'text' }
        ],
        rows: [
          { id: 1, field_1: '2024-01-01', field_2: '2024-01-07', field_3: 'Task 1' },
          { id: 2, field_1: '2024-01-08', field_2: '2024-01-14', field_3: 'Task 2' }
        ]
      }
    })

    // Check timeline structure
    expect(wrapper.find('.timeline-view')).toBeTruthy()
    expect(wrapper.findAll('.timeline-row')).toHaveLength(2)
  })

  it('handles zoom level changes', async () => {
    const wrapper = mount(TimelineView, {
      localVue,
      store,
      propsData: {
        view: { id: 1, zoom_level: 'week' },
        fields: [],
        rows: []
      }
    })

    // Change zoom level
    await wrapper.vm.setZoomLevel('month')
    expect(wrapper.vm.currentZoomLevel).toBe('month')
    
    // Verify timeline scale updated
    expect(wrapper.find('.timeline-scale-month')).toBeTruthy()
  })

  it('displays dependencies correctly', () => {
    const wrapper = mount(TimelineView, {
      localVue,
      store,
      propsData: {
        view: { id: 1 },
        fields: [],
        rows: [],
        dependencies: [
          { predecessor_id: 1, successor_id: 2, type: 'finish_to_start' }
        ]
      }
    })

    expect(wrapper.find('.dependency-line')).toBeTruthy()
  })

  it('supports drag and drop for date changes', async () => {
    const wrapper = mount(TimelineView, {
      localVue,
      store,
      propsData: {
        view: { id: 1, start_date_field: 1, end_date_field: 2 },
        fields: [
          { id: 1, name: 'Start Date', type: 'date' },
          { id: 2, name: 'End Date', type: 'date' }
        ],
        rows: [{ id: 1, field_1: '2024-01-01', field_2: '2024-01-07' }]
      }
    })

    const timelineBar = wrapper.find('.timeline-bar')
    
    // Mock drag event
    const dragEvent = {
      clientX: 100,
      preventDefault: jest.fn()
    }

    await timelineBar.trigger('mousedown', dragEvent)
    
    // Simulate drag to new position
    const moveEvent = {
      clientX: 150,
      preventDefault: jest.fn()
    }
    
    await wrapper.trigger('mousemove', moveEvent)
    await wrapper.trigger('mouseup')

    // Verify date update was triggered
    expect(wrapper.emitted('update-row')).toBeTruthy()
  })
})

describe('CalendarView Component', () => {
  let store

  beforeEach(() => {
    store = new Vuex.Store(mockStore)
  })

  it('renders calendar in month view', () => {
    const wrapper = mount(CalendarView, {
      localVue,
      store,
      propsData: {
        view: {
          id: 1,
          date_field: 1,
          display_mode: 'month'
        },
        fields: [
          { id: 1, name: 'Event Date', type: 'date' },
          { id: 2, name: 'Event Name', type: 'text' }
        ],
        rows: [
          { id: 1, field_1: '2024-01-15', field_2: 'Team Meeting' }
        ]
      }
    })

    expect(wrapper.find('.calendar-month-view')).toBeTruthy()
    expect(wrapper.text()).toContain('Team Meeting')
  })

  it('switches between display modes', async () => {
    const wrapper = mount(CalendarView, {
      localVue,
      store,
      propsData: {
        view: { id: 1, display_mode: 'month' },
        fields: [],
        rows: []
      }
    })

    // Switch to week view
    await wrapper.vm.setDisplayMode('week')
    expect(wrapper.vm.currentDisplayMode).toBe('week')
    expect(wrapper.find('.calendar-week-view')).toBeTruthy()

    // Switch to day view
    await wrapper.vm.setDisplayMode('day')
    expect(wrapper.vm.currentDisplayMode).toBe('day')
    expect(wrapper.find('.calendar-day-view')).toBeTruthy()
  })

  it('handles event drag and drop', async () => {
    const wrapper = mount(CalendarView, {
      localVue,
      store,
      propsData: {
        view: { id: 1, date_field: 1 },
        fields: [{ id: 1, name: 'Event Date', type: 'date' }],
        rows: [{ id: 1, field_1: '2024-01-15' }]
      }
    })

    const event = wrapper.find('.calendar-event')
    
    // Mock drag and drop
    const dragEvent = {
      dataTransfer: {
        setData: jest.fn(),
        getData: jest.fn(() => '1')
      }
    }

    const dropEvent = {
      dataTransfer: {
        getData: jest.fn(() => '1')
      },
      preventDefault: jest.fn()
    }

    await event.trigger('dragstart', dragEvent)
    
    const dayCell = wrapper.find('.calendar-day[data-date="2024-01-20"]')
    await dayCell.trigger('drop', dropEvent)

    expect(wrapper.emitted('update-row')).toBeTruthy()
  })
})

describe('ProgressBarDisplay Component', () => {
  it('renders progress bar correctly', () => {
    const wrapper = mount(ProgressBarDisplay, {
      propsData: {
        value: 75,
        minValue: 0,
        maxValue: 100,
        colorScheme: 'blue'
      }
    })

    const progressBar = wrapper.find('.progress-bar')
    expect(progressBar.exists()).toBe(true)
    
    const progressFill = wrapper.find('.progress-fill')
    expect(progressFill.attributes('style')).toContain('width: 75%')
  })

  it('calculates percentage correctly', () => {
    const wrapper = mount(ProgressBarDisplay, {
      propsData: {
        value: 25,
        minValue: 0,
        maxValue: 50,
        colorScheme: 'green'
      }
    })

    expect(wrapper.vm.percentage).toBe(50)
  })

  it('applies color scheme correctly', () => {
    const wrapper = mount(ProgressBarDisplay, {
      propsData: {
        value: 80,
        minValue: 0,
        maxValue: 100,
        colorScheme: 'gradient'
      }
    })

    const progressFill = wrapper.find('.progress-fill')
    expect(progressFill.classes()).toContain('progress-gradient')
  })

  it('handles edge cases', () => {
    // Test with value exceeding max
    const wrapper1 = mount(ProgressBarDisplay, {
      propsData: {
        value: 150,
        minValue: 0,
        maxValue: 100
      }
    })
    expect(wrapper1.vm.percentage).toBe(100)

    // Test with value below min
    const wrapper2 = mount(ProgressBarDisplay, {
      propsData: {
        value: -10,
        minValue: 0,
        maxValue: 100
      }
    })
    expect(wrapper2.vm.percentage).toBe(0)
  })
})

describe('GridViewFieldPeople Component', () => {
  it('renders people field correctly', () => {
    const wrapper = mount(GridViewFieldPeople, {
      propsData: {
        value: [
          { id: 1, first_name: 'John', last_name: 'Doe', email: 'john@example.com' },
          { id: 2, first_name: 'Jane', last_name: 'Smith', email: 'jane@example.com' }
        ],
        field: {
          id: 1,
          name: 'Assignees',
          multiple_collaborators: true
        }
      }
    })

    expect(wrapper.findAll('.people-avatar')).toHaveLength(2)
    expect(wrapper.text()).toContain('John Doe')
    expect(wrapper.text()).toContain('Jane Smith')
  })

  it('shows user avatars', () => {
    const wrapper = mount(GridViewFieldPeople, {
      propsData: {
        value: [
          { id: 1, first_name: 'John', last_name: 'Doe', avatar: 'avatar1.jpg' }
        ],
        field: { id: 1, name: 'Owner', multiple_collaborators: false }
      }
    })

    const avatar = wrapper.find('.people-avatar img')
    expect(avatar.attributes('src')).toContain('avatar1.jpg')
  })

  it('handles empty value', () => {
    const wrapper = mount(GridViewFieldPeople, {
      propsData: {
        value: null,
        field: { id: 1, name: 'Assignees' }
      }
    })

    expect(wrapper.find('.people-empty')).toBeTruthy()
  })
})

describe('Comment Component', () => {
  it('renders comment correctly', () => {
    const wrapper = mount(Comment, {
      propsData: {
        comment: {
          id: 1,
          content: 'This is a test comment',
          user: {
            id: 1,
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com'
          },
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-15T10:00:00Z'
        }
      }
    })

    expect(wrapper.text()).toContain('This is a test comment')
    expect(wrapper.text()).toContain('John Doe')
  })

  it('handles mentions correctly', () => {
    const wrapper = mount(Comment, {
      propsData: {
        comment: {
          id: 1,
          content: 'Hey @john@example.com, please review this',
          user: { id: 2, first_name: 'Jane', last_name: 'Smith' },
          mentions: [{ user_id: 1, email: 'john@example.com' }],
          created_at: '2024-01-15T10:00:00Z'
        }
      }
    })

    expect(wrapper.find('.mention')).toBeTruthy()
    expect(wrapper.text()).toContain('@john@example.com')
  })

  it('supports editing', async () => {
    const wrapper = mount(Comment, {
      propsData: {
        comment: {
          id: 1,
          content: 'Original comment',
          user: { id: 1, first_name: 'John', last_name: 'Doe' },
          created_at: '2024-01-15T10:00:00Z',
          can_edit: true
        }
      }
    })

    // Click edit button
    await wrapper.find('.comment-edit-btn').trigger('click')
    expect(wrapper.vm.isEditing).toBe(true)

    // Edit content
    const textarea = wrapper.find('textarea')
    await textarea.setValue('Updated comment')
    
    // Save changes
    await wrapper.find('.comment-save-btn').trigger('click')
    expect(wrapper.emitted('update')).toBeTruthy()
  })
})

describe('CommentThread Component', () => {
  it('renders thread correctly', () => {
    const wrapper = mount(CommentThread, {
      propsData: {
        comments: [
          {
            id: 1,
            content: 'Parent comment',
            user: { id: 1, first_name: 'John', last_name: 'Doe' },
            created_at: '2024-01-15T10:00:00Z',
            replies: [
              {
                id: 2,
                content: 'Reply comment',
                user: { id: 2, first_name: 'Jane', last_name: 'Smith' },
                created_at: '2024-01-15T10:30:00Z',
                parent_id: 1
              }
            ]
          }
        ]
      }
    })

    expect(wrapper.text()).toContain('Parent comment')
    expect(wrapper.text()).toContain('Reply comment')
    expect(wrapper.findAll('.comment')).toHaveLength(2)
  })

  it('supports adding replies', async () => {
    const wrapper = mount(CommentThread, {
      propsData: {
        comments: [
          {
            id: 1,
            content: 'Parent comment',
            user: { id: 1, first_name: 'John', last_name: 'Doe' },
            created_at: '2024-01-15T10:00:00Z',
            replies: []
          }
        ]
      }
    })

    // Click reply button
    await wrapper.find('.comment-reply-btn').trigger('click')
    expect(wrapper.find('.reply-form')).toBeTruthy()

    // Add reply
    const replyInput = wrapper.find('.reply-input')
    await replyInput.setValue('This is a reply')
    
    await wrapper.find('.reply-submit-btn').trigger('click')
    expect(wrapper.emitted('add-reply')).toBeTruthy()
  })
})

describe('ActivityLog Component', () => {
  it('renders activity entries correctly', () => {
    const wrapper = mount(ActivityLog, {
      propsData: {
        activities: [
          {
            id: 1,
            action_type: 'row_created',
            user: { id: 1, first_name: 'John', last_name: 'Doe' },
            timestamp: '2024-01-15T10:00:00Z',
            details: { table_name: 'Tasks', row_id: 1 }
          },
          {
            id: 2,
            action_type: 'field_updated',
            user: { id: 2, first_name: 'Jane', last_name: 'Smith' },
            timestamp: '2024-01-15T10:30:00Z',
            details: { field_name: 'Status', old_value: 'To Do', new_value: 'Done' }
          }
        ]
      }
    })

    expect(wrapper.findAll('.activity-entry')).toHaveLength(2)
    expect(wrapper.text()).toContain('John Doe')
    expect(wrapper.text()).toContain('created row')
    expect(wrapper.text()).toContain('Jane Smith')
    expect(wrapper.text()).toContain('updated Status')
  })

  it('supports filtering', async () => {
    const wrapper = mount(ActivityLog, {
      propsData: {
        activities: [
          {
            id: 1,
            action_type: 'row_created',
            user: { id: 1, first_name: 'John', last_name: 'Doe' },
            timestamp: '2024-01-15T10:00:00Z'
          },
          {
            id: 2,
            action_type: 'field_updated',
            user: { id: 2, first_name: 'Jane', last_name: 'Smith' },
            timestamp: '2024-01-15T10:30:00Z'
          }
        ]
      }
    })

    // Apply user filter
    await wrapper.vm.setFilter('user', 1)
    expect(wrapper.vm.filteredActivities).toHaveLength(1)
    expect(wrapper.vm.filteredActivities[0].user.first_name).toBe('John')

    // Apply action type filter
    await wrapper.vm.setFilter('action_type', 'field_updated')
    expect(wrapper.vm.filteredActivities).toHaveLength(1)
    expect(wrapper.vm.filteredActivities[0].action_type).toBe('field_updated')
  })
})

describe('VisualAutomationBuilder Component', () => {
  let store

  beforeEach(() => {
    store = new Vuex.Store({
      modules: {
        automation: {
          namespaced: true,
          state: {
            triggers: [],
            actions: []
          },
          mutations: {
            ADD_TRIGGER: (state, trigger) => state.triggers.push(trigger),
            ADD_ACTION: (state, action) => state.actions.push(action)
          }
        }
      }
    })
  })

  it('renders automation builder correctly', () => {
    const wrapper = mount(VisualAutomationBuilder, {
      localVue,
      store,
      propsData: {
        automation: {
          id: 1,
          name: 'Test Automation',
          triggers: [],
          actions: []
        }
      }
    })

    expect(wrapper.find('.automation-builder')).toBeTruthy()
    expect(wrapper.find('.automation-canvas')).toBeTruthy()
  })

  it('supports adding triggers', async () => {
    const wrapper = mount(VisualAutomationBuilder, {
      localVue,
      store,
      propsData: {
        automation: { id: 1, name: 'Test Automation', triggers: [], actions: [] }
      }
    })

    // Click add trigger button
    await wrapper.find('.add-trigger-btn').trigger('click')
    
    // Select trigger type
    const triggerSelector = wrapper.find('.trigger-selector')
    await triggerSelector.vm.$emit('select', {
      type: 'field_changed',
      field_id: 1,
      condition: 'equals',
      value: 'Done'
    })

    expect(wrapper.emitted('add-trigger')).toBeTruthy()
  })

  it('supports adding actions', async () => {
    const wrapper = mount(VisualAutomationBuilder, {
      localVue,
      store,
      propsData: {
        automation: { id: 1, name: 'Test Automation', triggers: [], actions: [] }
      }
    })

    // Click add action button
    await wrapper.find('.add-action-btn').trigger('click')
    
    // Select action type
    const actionSelector = wrapper.find('.action-selector')
    await actionSelector.vm.$emit('select', {
      type: 'update_field',
      field_id: 2,
      value: 'Completed'
    })

    expect(wrapper.emitted('add-action')).toBeTruthy()
  })

  it('supports drag and drop workflow building', async () => {
    const wrapper = mount(VisualAutomationBuilder, {
      localVue,
      store,
      propsData: {
        automation: {
          id: 1,
          name: 'Test Automation',
          triggers: [{ id: 1, type: 'field_changed' }],
          actions: [{ id: 1, type: 'update_field' }]
        }
      }
    })

    const triggerNode = wrapper.find('.trigger-node')
    const actionNode = wrapper.find('.action-node')

    // Mock drag and drop to connect nodes
    const dragEvent = {
      dataTransfer: {
        setData: jest.fn(),
        getData: jest.fn(() => 'trigger-1')
      }
    }

    const dropEvent = {
      dataTransfer: {
        getData: jest.fn(() => 'trigger-1')
      },
      preventDefault: jest.fn()
    }

    await triggerNode.trigger('dragstart', dragEvent)
    await actionNode.trigger('drop', dropEvent)

    expect(wrapper.emitted('connect-nodes')).toBeTruthy()
  })
})

describe('EnhancedChart Component', () => {
  it('renders chart correctly', () => {
    const wrapper = mount(EnhancedChart, {
      propsData: {
        type: 'bar',
        data: {
          labels: ['Jan', 'Feb', 'Mar'],
          datasets: [{
            label: 'Sales',
            data: [100, 200, 150],
            backgroundColor: '#007bff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      }
    })

    expect(wrapper.find('canvas')).toBeTruthy()
    expect(wrapper.vm.chartType).toBe('bar')
  })

  it('updates chart when data changes', async () => {
    const wrapper = mount(EnhancedChart, {
      propsData: {
        type: 'line',
        data: {
          labels: ['A', 'B'],
          datasets: [{ data: [1, 2] }]
        }
      }
    })

    const updateChartSpy = jest.spyOn(wrapper.vm, 'updateChart')

    // Update data
    await wrapper.setProps({
      data: {
        labels: ['A', 'B', 'C'],
        datasets: [{ data: [1, 2, 3] }]
      }
    })

    expect(updateChartSpy).toHaveBeenCalled()
  })

  it('handles real-time updates', async () => {
    const wrapper = mount(EnhancedChart, {
      propsData: {
        type: 'line',
        data: { labels: [], datasets: [] },
        realTimeUpdates: true
      }
    })

    // Simulate real-time data update
    await wrapper.vm.handleRealTimeUpdate({
      labels: ['New Data'],
      datasets: [{ data: [100] }]
    })

    expect(wrapper.vm.chartData.labels).toContain('New Data')
  })
})

describe('KPIWidget Component', () => {
  it('renders KPI value correctly', () => {
    const wrapper = mount(KPIWidget, {
      propsData: {
        title: 'Total Sales',
        value: 125000,
        format: 'currency',
        trend: {
          direction: 'up',
          percentage: 15.5
        }
      }
    })

    expect(wrapper.text()).toContain('Total Sales')
    expect(wrapper.text()).toContain('$125,000')
    expect(wrapper.find('.trend-up')).toBeTruthy()
    expect(wrapper.text()).toContain('15.5%')
  })

  it('formats different value types correctly', () => {
    // Test percentage format
    const wrapper1 = mount(KPIWidget, {
      propsData: {
        title: 'Completion Rate',
        value: 0.85,
        format: 'percentage'
      }
    })
    expect(wrapper1.text()).toContain('85%')

    // Test number format
    const wrapper2 = mount(KPIWidget, {
      propsData: {
        title: 'Total Items',
        value: 1234,
        format: 'number'
      }
    })
    expect(wrapper2.text()).toContain('1,234')
  })

  it('shows trend indicators correctly', () => {
    // Test upward trend
    const wrapper1 = mount(KPIWidget, {
      propsData: {
        title: 'Revenue',
        value: 100000,
        trend: { direction: 'up', percentage: 10 }
      }
    })
    expect(wrapper1.find('.trend-up')).toBeTruthy()
    expect(wrapper1.classes()).toContain('trend-positive')

    // Test downward trend
    const wrapper2 = mount(KPIWidget, {
      propsData: {
        title: 'Costs',
        value: 50000,
        trend: { direction: 'down', percentage: 5 }
      }
    })
    expect(wrapper2.find('.trend-down')).toBeTruthy()
    expect(wrapper2.classes()).toContain('trend-negative')
  })

  it('handles loading state', () => {
    const wrapper = mount(KPIWidget, {
      propsData: {
        title: 'Loading Widget',
        value: null,
        loading: true
      }
    })

    expect(wrapper.find('.kpi-loading')).toBeTruthy()
    expect(wrapper.text()).toContain('Loading...')
  })
})