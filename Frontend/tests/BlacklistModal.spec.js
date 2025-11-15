import { shallowMount } from '@vue/test-utils';
import BlacklistModal from '@/components/modals/BlacklistModal.vue';

// Mock bootstrap modal
window.bootstrap = {
  Modal: jest.fn().mockImplementation(() => ({
    show: jest.fn(),
    hide: jest.fn()
  }))
};

describe('BlacklistModal.vue', () => {
  const entity = { id: 42, name: 'John Doe' };

  beforeEach(() => {
    global.fetch = jest.fn();
    jest.clearAllMocks();
  });

  it('renders with correct entity name', () => {
    const wrapper = shallowMount(BlacklistModal, { propsData: { entity, role: 'doctor' } });
    expect(wrapper.text()).toContain('blacklisting');
    expect(wrapper.text()).toContain(entity.name);
  });

  it('updates reason when textarea changes', async () => {
    const wrapper = shallowMount(BlacklistModal, { propsData: { entity, role: 'doctor' } });
    const ta = wrapper.find('textarea');
    await ta.setValue('Violation of terms');
    expect(wrapper.vm.reason).toBe('Violation of terms');
  });

  it('sends POST request when confirming blacklist and emits event on success', async () => {
    // create a controllable promise so we can assert loading state
    let resolveFetch;
    global.fetch.mockImplementation(() => new Promise((res) => { resolveFetch = res; }));

    const wrapper = shallowMount(BlacklistModal, { propsData: { entity, role: 'patient' } });
    wrapper.vm.reason = 'Serious misconduct';

    const promise = wrapper.vm.submitBlacklist();

    // loading should be true immediately after calling
    expect(wrapper.vm.loading).toBe(true);

    // resolve the fetch with success
    resolveFetch({ ok: true, status: 200, text: async () => '' });
    await promise;

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(
      `/api/admin/blacklist-patient/${entity.id}`,
      expect.objectContaining({ method: 'POST', body: expect.any(String) })
    );

    expect(wrapper.emitted().blacklisted).toBeTruthy();
    expect(wrapper.vm.loading).toBe(false);
  });

  it('shows loading spinner during request', async () => {
    let resolveFetch;
    global.fetch.mockImplementation(() => new Promise((res) => { resolveFetch = res; }));

    const wrapper = shallowMount(BlacklistModal, { propsData: { entity, role: 'doctor' } });
    wrapper.vm.reason = 'Reason';

    const p = wrapper.vm.submitBlacklist();
    expect(wrapper.vm.loading).toBe(true);

    resolveFetch({ ok: true, status: 200, text: async () => '' });
    await p;

    expect(wrapper.vm.loading).toBe(false);
  });

  it('displays error message on API failure', async () => {
    global.fetch.mockResolvedValueOnce({ ok: false, status: 500, text: async () => 'Server error' });

    const wrapper = shallowMount(BlacklistModal, { propsData: { entity, role: 'doctor' } });
    wrapper.vm.reason = 'Some reason';

    await wrapper.vm.submitBlacklist();

    expect(wrapper.vm.error).toBeTruthy();
    expect(wrapper.vm.loading).toBe(false);
  });

  it('validates reason is required', async () => {
    const wrapper = shallowMount(BlacklistModal, { propsData: { entity, role: 'doctor' } });
    wrapper.vm.reason = '';
    await wrapper.vm.submitBlacklist();
    expect(wrapper.vm.error).toBe('Reason is required');
  });
});
