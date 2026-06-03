import { ref } from 'vue'
import { leadsApi } from '@/services/leads.api'
import { useToast } from '@/composables/useToast'
import { mapApiError } from '@/utils/apiErrors'

export function useLeads() {
    const toast = useToast()

    const isLoading = ref(false)
    const leads = ref([])

    async function fetchLeads(limit, offset, setTotal) {
        isLoading.value = true
        try {
            const res = await leadsApi.getLeads(limit, offset)
            if (res.status === 'ok') {
                leads.value = res.data
                if (setTotal) setTotal(res.total)
            }
        } catch (err) {
            toast.error(mapApiError(err))
        } finally {
            isLoading.value = false
        }
    }

    async function changeStatus(lead, newStatus, currentAdminUsername) {
        const oldStatus = lead.status
        const oldProcessedBy = lead.processed_by

        lead.status = newStatus
        lead.processed_by = newStatus === 'IN_PROGRESS' ? currentAdminUsername : oldProcessedBy

        try {
            await leadsApi.updateStatus(lead.id, newStatus)
            toast.success('Статус заявки изменен')
        } catch (err) {
            lead.status = oldStatus
            lead.processed_by = oldProcessedBy
            toast.error(mapApiError(err))
        }
    }

    async function removeLead(leadId) {
        if (!confirm('Вы действительно хотите безвозвратно удалить эту заявку?')) return
        try {
            await leadsApi.deleteLead(leadId)
            leads.value = leads.value.filter((l) => l.id !== leadId)
            toast.success('Заявка удалена')
        } catch (err) {
            toast.error(mapApiError(err))
        }
    }

    return { leads, isLoading, fetchLeads, changeStatus, removeLead }
}