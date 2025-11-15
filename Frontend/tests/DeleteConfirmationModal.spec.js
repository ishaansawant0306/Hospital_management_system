import { shallowMount } from '@vue/test-utils';
import DeleteConfirmationModal from '@/components/modals/DeleteConfirmationModal.vue';

// Mock bootstrap modal to avoid DOM dependency
window.bootstrap = {
  Modal: jest.fn().mockImplementation(() => ({
    show: jest.fn(),
    hide: jest.fn()
  })),
};

describe('DeleteConfirmationModal.vue', () => {
  const entity = { id: 123, name: 'Dr. Who' };

  beforeEach(() => {
    // Provide a simple global fetch mock compatible with environments
    global.fetch = jest.fn();
    jest.clearAllMocks();
  });

  it('renders with correct entity name', () => {
    const wrapper = shallowMount(DeleteConfirmationModal, {
      propsData: { entity, role: 'doctor' }
    });

    expect(wrapper.text()).toContain('Are you sure you want to delete');
    expect(wrapper.text()).toContain(entity.name);
  });

  it('calls DELETE API when confirming delete', async () => {
    global.fetch.mockResolvedValueOnce({ ok: true, status: 200, text: async () => '' });

    const wrapper = shallowMount(DeleteConfirmationModal, {
      propsData: { entity, role: 'doctor' }
    });

    await wrapper.vm.confirmDelete();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(`/api/admin/delete-doctor/${entity.id}`, expect.objectContaining({ method: 'DELETE' }));
  });

  it('emits deleted on success', async () => {
    global.fetch.mockResolvedValueOnce({ ok: true, status: 200, text: async () => '' });

    const wrapper = shallowMount(DeleteConfirmationModal, {
      propsData: { entity, role: 'doctor' }
    });

    await wrapper.vm.confirmDelete();

    expect(wrapper.emitted().deleted).toBeTruthy();
  });

  it('sets error message on failure', async () => {
    global.fetch.mockResolvedValueOnce({ ok: false, status: 500, text: async () => 'Server error' });

    const wrapper = shallowMount(DeleteConfirmationModal, {
      propsData: { entity, role: 'doctor' }
    });

    await wrapper.vm.confirmDelete();

    expect(wrapper.vm.error).toBeTruthy();
  });
});
