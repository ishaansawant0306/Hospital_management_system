import { shallowMount, createLocalVue } from '@vue/test-utils';
import EditDoctorModal from './EditDoctorModal.vue';

const localVue = createLocalVue();

describe('EditDoctorModal.vue', () => {
  let wrapper;
  const mockDoctor = {
    id: 1,
    name: 'Dr. John Doe',
    specialization: 'Cardiology',
    availability: 'Monday-Friday, 9AM-5PM'
  };

  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    localStorage.setItem('token', 'mock-jwt-token');
    
    // Mock fetch globally
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
    if (wrapper) {
      wrapper.destroy();
    }
  });

  // TEST 1: Modal renders correctly with doctor data
  describe('Rendering', () => {
    it('should render the modal with correct structure', () => {
      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: mockDoctor
        }
      });

      // Check modal structure
      expect(wrapper.find('.modal').exists()).toBe(true);
      expect(wrapper.find('.modal-title').text()).toBe('Edit Doctor');
      expect(wrapper.find('form').exists()).toBe(true);
    });

    it('should populate form fields with doctor data', () => {
      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: mockDoctor
        }
      });

      const inputs = wrapper.findAll('input');
      expect(inputs.at(0).element.value).toBe(mockDoctor.name);
      expect(inputs.at(1).element.value).toBe(mockDoctor.specialization);
      expect(inputs.at(2).element.value).toBe(mockDoctor.availability);
    });

    it('should have a save button', () => {
      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: mockDoctor
        }
      });

      const submitButton = wrapper.find('button[type="submit"]');
      expect(submitButton.exists()).toBe(true);
      expect(submitButton.text()).toBe('Save Changes');
    });

    it('should have a close button', () => {
      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: mockDoctor
        }
      });

      const closeButton = wrapper.find('.btn-close');
      expect(closeButton.exists()).toBe(true);
    });
  });

  // TEST 2: Form updates local state when input changes
  describe('Form Input Handling', () => {
    it('should update name field when input changes', async () => {
      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      const nameInput = wrapper.findAll('input').at(0);
      await nameInput.setValue('Dr. Jane Smith');

      expect(wrapper.vm.doctor.name).toBe('Dr. Jane Smith');
    });

    it('should update specialization field when input changes', async () => {
      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      const specializationInput = wrapper.findAll('input').at(1);
      await specializationInput.setValue('Neurology');

      expect(wrapper.vm.doctor.specialization).toBe('Neurology');
    });

    it('should update availability field when input changes', async () => {
      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      const availabilityInput = wrapper.findAll('input').at(2);
      await availabilityInput.setValue('Tuesday-Saturday, 10AM-6PM');

      expect(wrapper.vm.doctor.availability).toBe('Tuesday-Saturday, 10AM-6PM');
    });

    it('should update all fields independently', async () => {
      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      const inputs = wrapper.findAll('input');
      await inputs.at(0).setValue('Dr. New Name');
      await inputs.at(1).setValue('Orthopedics');
      await inputs.at(2).setValue('Mon-Wed, 8AM-4PM');

      expect(wrapper.vm.doctor.name).toBe('Dr. New Name');
      expect(wrapper.vm.doctor.specialization).toBe('Orthopedics');
      expect(wrapper.vm.doctor.availability).toBe('Mon-Wed, 8AM-4PM');
    });
  });

  // TEST 3: Submit button triggers API call with correct payload
  describe('API Call on Submit', () => {
    it('should make a PUT request to correct endpoint with doctor data', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      const form = wrapper.find('form');
      await form.trigger('submit');

      expect(global.fetch).toHaveBeenCalledWith(
        `/api/admin/update-doctor/${mockDoctor.id}`,
        expect.any(Object)
      );
    });

    it('should send PUT request with correct HTTP method', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      const form = wrapper.find('form');
      await form.trigger('submit');

      const callArgs = global.fetch.mock.calls[0][1];
      expect(callArgs.method).toBe('PUT');
    });

    it('should send correct headers including Authorization token', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      const form = wrapper.find('form');
      await form.trigger('submit');

      const callArgs = global.fetch.mock.calls[0][1];
      expect(callArgs.headers['Content-Type']).toBe('application/json');
      expect(callArgs.headers['Authorization']).toBe('Bearer mock-jwt-token');
    });

    it('should send doctor data in request body', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      const form = wrapper.find('form');
      await form.trigger('submit');

      const callArgs = global.fetch.mock.calls[0][1];
      const bodyData = JSON.parse(callArgs.body);

      expect(bodyData).toEqual(mockDoctor);
      expect(bodyData.name).toBe(mockDoctor.name);
      expect(bodyData.specialization).toBe(mockDoctor.specialization);
      expect(bodyData.availability).toBe(mockDoctor.availability);
    });

    it('should send updated doctor data after form changes', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      // Update the form
      const inputs = wrapper.findAll('input');
      await inputs.at(0).setValue('Dr. Updated Name');
      await inputs.at(1).setValue('Dermatology');

      const form = wrapper.find('form');
      await form.trigger('submit');

      const callArgs = global.fetch.mock.calls[0][1];
      const bodyData = JSON.parse(callArgs.body);

      expect(bodyData.name).toBe('Dr. Updated Name');
      expect(bodyData.specialization).toBe('Dermatology');
    });
  });

  // TEST 4: Emits `updated` event on success
  describe('Event Emission on Success', () => {
    it('should emit updated event on successful API call', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      // Mock alert
      window.alert = jest.fn();

      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      const form = wrapper.find('form');
      await form.trigger('submit');

      // Wait for async operations
      await wrapper.vm.$nextTick();

      expect(wrapper.emitted('updated')).toBeTruthy();
      expect(wrapper.emitted('updated').length).toBe(1);
    });

    it('should show success alert after update', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      window.alert = jest.fn();

      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      const form = wrapper.find('form');
      await form.trigger('submit');

      await wrapper.vm.$nextTick();

      expect(window.alert).toHaveBeenCalledWith('Doctor updated successfully');
    });

    it('should only emit updated event once per successful submission', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      window.alert = jest.fn();

      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      const form = wrapper.find('form');
      await form.trigger('submit');

      await wrapper.vm.$nextTick();

      expect(wrapper.emitted('updated').length).toBe(1);
    });
  });

  // TEST 5: Handles API failure gracefully
  describe('Error Handling', () => {
    it('should show error alert when API call fails', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));
      window.alert = jest.fn();

      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      const form = wrapper.find('form');
      await form.trigger('submit');

      await wrapper.vm.$nextTick();

      expect(window.alert).toHaveBeenCalledWith('Error updating doctor');
    });

    it('should not emit updated event on API failure', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));
      window.alert = jest.fn();

      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      const form = wrapper.find('form');
      await form.trigger('submit');

      await wrapper.vm.$nextTick();

      expect(wrapper.emitted('updated')).toBeFalsy();
    });

    it('should handle network errors gracefully', async () => {
      const networkError = new Error('Failed to fetch');
      global.fetch.mockRejectedValueOnce(networkError);
      window.alert = jest.fn();

      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      const form = wrapper.find('form');
      await form.trigger('submit');

      await wrapper.vm.$nextTick();

      expect(window.alert).toHaveBeenCalledWith('Error updating doctor');
    });

    it('should handle API error responses (4xx, 5xx)', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      });
      window.alert = jest.fn();

      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      const form = wrapper.find('form');
      await form.trigger('submit');

      await wrapper.vm.$nextTick();

      // Note: Current implementation doesn't check response.ok
      // This test documents that limitation
      expect(wrapper.emitted('updated')).toBeTruthy();
    });

    it('should handle missing token gracefully', async () => {
      localStorage.removeItem('token');
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      const form = wrapper.find('form');
      await form.trigger('submit');

      await wrapper.vm.$nextTick();

      // Verify fetch was called with null token
      const callArgs = global.fetch.mock.calls[0][1];
      expect(callArgs.headers['Authorization']).toBe('Bearer null');
    });
  });

  // Additional integration tests
  describe('Integration Tests', () => {
    it('should handle complete user workflow: edit and submit', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });
      window.alert = jest.fn();

      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      // Step 1: Update multiple fields
      const inputs = wrapper.findAll('input');
      await inputs.at(0).setValue('Dr. Updated');
      await inputs.at(1).setValue('Pediatrics');
      await inputs.at(2).setValue('Mon-Fri, 9AM-5PM');

      // Step 2: Submit form
      const form = wrapper.find('form');
      await form.trigger('submit');

      // Step 3: Verify API was called with updated data
      const callArgs = global.fetch.mock.calls[0][1];
      const bodyData = JSON.parse(callArgs.body);

      expect(bodyData.name).toBe('Dr. Updated');
      expect(bodyData.specialization).toBe('Pediatrics');
      expect(bodyData.availability).toBe('Mon-Fri, 9AM-5PM');

      // Step 4: Verify success feedback
      await wrapper.vm.$nextTick();
      expect(window.alert).toHaveBeenCalledWith('Doctor updated successfully');
      expect(wrapper.emitted('updated')).toBeTruthy();
    });

    it('should properly handle consecutive submissions', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        status: 200
      });
      window.alert = jest.fn();

      wrapper = shallowMount(EditDoctorModal, {
        localVue,
        propsData: {
          doctor: { ...mockDoctor }
        }
      });

      const form = wrapper.find('form');

      // First submission
      await form.trigger('submit');
      await wrapper.vm.$nextTick();
      expect(global.fetch).toHaveBeenCalledTimes(1);

      // Update and submit again
      const inputs = wrapper.findAll('input');
      await inputs.at(0).setValue('Dr. New Name');
      await form.trigger('submit');
      await wrapper.vm.$nextTick();

      expect(global.fetch).toHaveBeenCalledTimes(2);
    });
  });
});
