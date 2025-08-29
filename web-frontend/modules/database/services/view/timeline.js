import { ViewService } from '@baserow/modules/database/services/view'

export class TimelineService extends ViewService {
  static getType() {
    return 'timeline'
  }

  /**
   * Fetches the dependencies for a timeline view.
   */
  async getDependencies(viewId) {
    const { data } = await this.client.get(`/database/views/timeline/${viewId}/dependencies/`)
    return data
  }

  /**
   * Creates a new dependency between two tasks.
   */
  async createDependency(viewId, values) {
    const { data } = await this.client.post(`/database/views/timeline/${viewId}/dependencies/`, values)
    return data
  }

  /**
   * Deletes a dependency.
   */
  async deleteDependency(viewId, dependencyId) {
    await this.client.delete(`/database/views/timeline/${viewId}/dependencies/${dependencyId}/`)
  }

  /**
   * Fetches the milestones for a timeline view.
   */
  async getMilestones(viewId) {
    const { data } = await this.client.get(`/database/views/timeline/${viewId}/milestones/`)
    return data
  }

  /**
   * Creates a new milestone.
   */
  async createMilestone(viewId, values) {
    const { data } = await this.client.post(`/database/views/timeline/${viewId}/milestones/`, values)
    return data
  }

  /**
   * Updates a milestone.
   */
  async updateMilestone(viewId, milestoneId, values) {
    const { data } = await this.client.patch(`/database/views/timeline/${viewId}/milestones/${milestoneId}/`, values)
    return data
  }

  /**
   * Deletes a milestone.
   */
  async deleteMilestone(viewId, milestoneId) {
    await this.client.delete(`/database/views/timeline/${viewId}/milestones/${milestoneId}/`)
  }

  /**
   * Triggers schedule recalculation for dependent tasks.
   */
  async recalculateSchedule(viewId, values) {
    const { data } = await this.client.post(`/database/views/timeline/${viewId}/recalculate-schedule/`, values)
    return data
  }

  /**
   * Fetches the critical path for the timeline view.
   */
  async getCriticalPath(viewId) {
    const { data } = await this.client.get(`/database/views/timeline/${viewId}/critical-path/`)
    return data
  }
}

export default new TimelineService()