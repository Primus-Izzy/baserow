<template>
  <div class="trigger-selector">
    <div class="selector-header">
      <input
        v-model="searchQuery"
        type="text"
        :placeholder="$t('visualBuilder.searchTriggers')"
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
    
    <div class="triggers-grid">
      <div
        v-for="trigger in filteredTriggers"
        :key="trigger.type"
        class="trigger-card"
        @click="selectTrigger(trigger)"
      >
        <div class="trigger-icon">
          <i :class="trigger.iconClass"></i>
        </div>
        <div class="trigger-content">
          <h4>{{ trigger.name }}</h4>
          <p>{{ trigger.description }}</p>
          <div class="trigger-meta">
            <span class="category-tag">{{ getCategoryLabel(trigger.category) }}</span>
            <span v-if="trigger.isPopular" class="popular-tag">
              <i class="iconoir-star"></i>
              {{ $t('visualBuilder.popular') }}
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="filteredTriggers.length === 0" class="no-results">
      <i class="iconoir-search"></i>
      <h4>{{ $t('visualBuilder.noTriggersFound') }}</h4>
      <p>{{ $t('visualBuilder.tryDifferentSearch') }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TriggerSelector',
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
          label: this.$t('visualBuilder.allTriggers'),
          icon: 'iconoir-list',
        },
        {
          key: 'database',
          label: this.$t('visualBuilder.database'),
          icon: 'iconoir-db',
        },
        {
          key: 'time',
          label: this.$t('visualBuilder.time'),
          icon: 'iconoir-clock'),
        },
        {
          key: 'external',
          label: this.$t('visualBuilder.external'),
          icon: 'iconoir-globe',
        },
        {
          key: 'user',
          label: this.$t('visualBuilder.user'),
          icon: 'iconoir-user',
        },
      ]
    },
    
    availableTriggers() {
      const triggerTypes = this.$registry.getOrderedList('node').filter(type => type.isTrigger)
      
      return [
        // Enhanced triggers
        {
          type: 'date_based_trigger',
          name: this.$t('visualBuilder.dateBasedTrigger'),
          description: this.$t('visualBuilder.dateBasedTriggerDesc'),
          iconClass: 'iconoir-calendar',
          category: 'time',
          isPopular: true,
          requiresConfig: true,
        },
        {
          type: 'webhook_trigger',
          name: this.$t('visualBuilder.webhookTrigger'),
          description: this.$t('visualBuilder.webhookTriggerDesc'),
          iconClass: 'iconoir-globe',
          category: 'external',
          isPopular: true,
          requiresConfig: true,
        },
        {
          type: 'linked_record_change_trigger',
          name: this.$t('visualBuilder.linkedRecordChangeTrigger'),
          description: this.$t('visualBuilder.linkedRecordChangeTriggerDesc'),
          iconClass: 'iconoir-link',
          category: 'database',
          requiresConfig: true,
        },
        {
          type: 'conditional_trigger',
          name: this.$t('visualBuilder.conditionalTrigger'),
          description: this.$t('visualBuilder.conditionalTriggerDesc'),
          iconClass: 'iconoir-git-fork',
          category: 'database',
          requiresConfig: true,
        },
        // Standard triggers from registry
        ...triggerTypes.map(triggerType => ({
          type: triggerType.getType(),
          name: triggerType.name,
          description: triggerType.description,
          iconClass: triggerType.iconClass || 'iconoir-flash',
          category: this.categorizeTrigger(triggerType.getType()),
          isPopular: ['rows_created', 'rows_updated'].includes(triggerType.getType()),
          requiresConfig: true,
        })),
      ]
    },
    
    filteredTriggers() {
      let triggers = this.availableTriggers
      
      // Filter by category
      if (this.selectedCategory !== 'all') {
        triggers = triggers.filter(trigger => trigger.category === this.selectedCategory)
      }
      
      // Filter by search query
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        triggers = triggers.filter(trigger =>
          trigger.name.toLowerCase().includes(query) ||
          trigger.description.toLowerCase().includes(query)
        )
      }
      
      // Sort by popularity and name
      return triggers.sort((a, b) => {
        if (a.isPopular && !b.isPopular) return -1
        if (!a.isPopular && b.isPopular) return 1
        return a.name.localeCompare(b.name)
      })
    },
  },
  methods: {
    selectTrigger(trigger) {
      this.$emit('select', trigger)
    },
    
    categorizeTrigger(triggerType) {
      const categoryMap = {
        'rows_created': 'database',
        'rows_updated': 'database',
        'rows_deleted': 'database',
        'date_based_trigger': 'time',
        'webhook_trigger': 'external',
        'linked_record_change_trigger': 'database',
        'conditional_trigger': 'database',
      }
      
      return categoryMap[triggerType] || 'database'
    },
    
    getCategoryLabel(categoryKey) {
      const category = this.categories.find(c => c.key === categoryKey)
      return category ? category.label : categoryKey
    },
  },
}
</script>

<style lang="scss" scoped>
.trigger-selector {
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

.triggers-grid {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.trigger-card {
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

.trigger-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

.trigger-content {
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

.trigger-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.category-tag,
.popular-tag {
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