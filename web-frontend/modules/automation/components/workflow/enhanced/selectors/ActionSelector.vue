<template>
  <div class="action-selector">
    <div class="selector-header">
      <input
        v-model="searchQuery"
        type="text"
        :placeholder="$t('visualBuilder.searchActions')"
        class="search-input"
      />
      <div class="category-filters">
        <button
          v-for="category in categories"
          :key="category.key"
          :class="['category-btn', { active: selectedCategory === category.key }]"
          @click="selectedCategory = category.key"
        >
          <i :class="category.icon"></i>
          {{ category.label }}
        </button>
      </div>
    </div>
    
    <div class="actions-grid">
      <div
        v-for="action in filteredActions"
        :key="action.type"
        class="action-card"
        @click="selectAction(action)"
      >
        <div class="action-icon">
          <i :class="action.iconClass"></i>
        </div>
        <div class="action-content">
          <h4>{{ action.name }}</h4>
          <p>{{ action.description }}</p>
          <div class="action-meta">
            <span class="category-tag">{{ getCategoryLabel(action.category) }}</span>
            <span v-if="action.isPopular" class="popular-tag">
              <i class="iconoir-star"></i>
              {{ $t('visualBuilder.popular') }}
            </span>
            <span v-if="action.isNew" class="new-tag">
              {{ $t('visualBuilder.new') }}
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="filteredActions.length === 0" class="no-results">
      <i class="iconoir-search"></i>
      <h4>{{ $t('visualBuilder.noActionsFound') }}</h4>
      <p>{{ $t('visualBuilder.tryDifferentSearch') }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ActionSelector',
  data() {
    return {
      searchQuery: '',
      selectedCategory: 'all',
    }
  },
  computed: {
    categories() {
      return [
        {
          key: 'all',
          label: this.$t('visualBuilder.allActions'),
          icon: 'iconoir-list',
        },
        {
          key: 'database',
          label: this.$t('visualBuilder.database'),
          icon: 'iconoir-db',
        },
        {
          key: 'notification',
          label: this.$t('visualBuilder.notifications'),
          icon: 'iconoir-bell',
        },
        {
          key: 'integration',
          label: this.$t('visualBuilder.integrations'),
          icon: 'iconoir-globe',
        },
        {
          key: 'logic',
          label: this.$t('visualBuilder.logic'),
          icon: 'iconoir-git-fork',
        },
        {
          key: 'utility',
          label: this.$t('visualBuilder.utilities'),
          icon: 'iconoir-tools',
        },
      ]
    },
    
    availableActions() {
      const actionTypes = this.$registry.getOrderedList('node').filter(type => type.isWorkflowAction)
      
      return [
        // Enhanced actions
        {
          type: 'notification_action',
          name: this.$t('visualBuilder.sendNotification'),
          description: this.$t('visualBuilder.sendNotificationDesc'),
          iconClass: 'iconoir-bell',
          category: 'notification',
          isPopular: true,
          isNew: true,
          requiresConfig: true,
        },
        {
          type: 'webhook_action',
          name: this.$t('visualBuilder.sendWebhook'),
          description: this.$t('visualBuilder.sendWebhookDesc'),
          iconClass: 'iconoir-globe',
          category: 'integration',
          isPopular: true,
          isNew: true,
          requiresConfig: true,
        },
        {
          type: 'status_change_action',
          name: this.$t('visualBuilder.changeStatus'),
          description: this.$t('visualBuilder.changeStatusDesc'),
          iconClass: 'iconoir-edit',
          category: 'database',
          isPopular: true,
          isNew: true,
          requiresConfig: true,
        },
        {
          type: 'conditional_branch',
          name: this.$t('visualBuilder.conditionalBranch'),
          description: this.$t('visualBuilder.conditionalBranchDesc'),
          iconClass: 'iconoir-git-fork',
          category: 'logic',
          isNew: true,
          requiresConfig: true,
        },
        {
          type: 'delay',
          name: this.$t('visualBuilder.delay'),
          description: this.$t('visualBuilder.delayDesc'),
          iconClass: 'iconoir-timer',
          category: 'utility',
          isNew: true,
          requiresConfig: true,
        },
        // Standard actions from registry
        ...actionTypes.map(actionType => ({
          type: actionType.getType(),
          name: actionType.name,
          description: actionType.description,
          iconClass: actionType.iconClass || 'iconoir-play',
          category: this.categorizeAction(actionType.getType()),
          isPopular: ['create_row', 'update_row', 'http_request'].includes(actionType.getType()),
          requiresConfig: true,
        })),
      ]
    },
    
    filteredActions() {
      let actions = this.availableActions
      
      // Filter by category
      if (this.selectedCategory !== 'all') {
        actions = actions.filter(action => action.category === this.selectedCategory)
      }
      
      // Filter by search query
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        actions = actions.filter(action =>
          action.name.toLowerCase().includes(query) ||
          action.description.toLowerCase().includes(query)
        )
      }
      
      // Sort by popularity and name
      return actions.sort((a, b) => {
        if (a.isPopular && !b.isPopular) return -1
        if (!a.isPopular && b.isPopular) return 1
        return a.name.localeCompare(b.name)
      })
    },
  },
  methods: {
    selectAction(action) {
      this.$emit('select', action)
    },
    
    categorizeAction(actionType) {
      const categoryMap = {
        'create_row': 'database',
        'update_row': 'database',
        'delete_row': 'database',
        'get_row': 'database',
        'list_rows': 'database',
        'aggregate_rows': 'database',
        'http_request': 'integration',
        'smtp_email': 'notification',
        'notification_action': 'notification',
        'webhook_action': 'integration',
        'status_change_action': 'database',
        'conditional_branch': 'logic',
        'delay': 'utility',
      }
      
      return categoryMap[actionType] || 'utility'
    },
    
    getCategoryLabel(categoryKey) {
      const category = this.categories.find(c => c.key === categoryKey)
      return category ? category.label : categoryKey
    },
  },
}
</script>

<style lang="scss" scoped>
.action-selector {
  max-width: 800px;
  max-height: 600px;
  display: flex;
  flex-direction: column;
}

.selector-header {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  margin-bottom: 1rem;
  
  &:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  }
}

.category-filters {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.category-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 20px;
  color: #6c757d;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: #e9ecef;
    border-color: #007bff;
    color: #007bff;
  }
  
  &.active {
    background: #007bff;
    border-color: #007bff;
    color: white;
  }
  
  i {
    font-size: 1rem;
  }
}

.actions-grid {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.action-card {
  display: flex;
  padding: 1.5rem;
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #007bff;
    box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);
    transform: translateY(-2px);
  }
}

.action-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  flex-shrink: 0;
  
  i {
    font-size: 1.5rem;
    color: white;
  }
}

.action-content {
  flex: 1;
  
  h4 {
    margin: 0 0 0.5rem 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: #333;
  }
  
  p {
    margin: 0 0 1rem 0;
    font-size: 0.9rem;
    color: #666;
    line-height: 1.4;
  }
}

.action-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.category-tag,
.popular-tag,
.new-tag {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.category-tag {
  background: #e9ecef;
  color: #6c757d;
}

.popular-tag {
  background: #fff3cd;
  color: #856404;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  
  i {
    font-size: 0.8rem;
  }
}

.new-tag {
  background: #d1ecf1;
  color: #0c5460;
}

.no-results {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  color: #6c757d;
  
  i {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
  }
  
  h4 {
    margin: 0 0 0.5rem 0;
    font-size: 1.2rem;
    font-weight: 600;
  }
  
  p {
    margin: 0;
    font-size: 1rem;
  }
}
</style>