import { shallowMount, createLocalVue } from '@vue/test-utils';
import CreateDoctorModal from '@/components/modals/CreateDoctorModal.vue';
import * as tokenManager from '@/utils/tokenManager';

// Mock the tokenManager
jest.mock('@/utils/tokenManager', () => ({
  getAuthHeaders: jest.fn(() => ({
    Authorization: 'Bearer test-token'
  }))
}));

// Mock fetch
global.fetch = jest.fn();

// Mock bootstrap Modal
window.bootstrap = {
  Modal: class {
    constructor(element) {
      this.element = element;
    }
    hide() {}
    show() {}
    static getInstance(element) {
      return new window.bootstrap.Modal(element);
    }
  }
};

describe('CreateDoctorModal.vue', () => {
  let wrapper;
  const localVue = createLocalVue();

  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch.mockClear();

    // Create a mock DOM element for the modal
    document.body.innerHTML = '<div id="createDoctorModal"></div>';

    wrapper = shallowMount(CreateDoctorModal, {
      localVue,
      mocks: {
        $emit: jest.fn()
      }
    });
  });

  afterEach(() => {
    wrapper.destroy();
  });

  describe('Component Rendering', () => {
    it('renders the modal correctly', () => {
      expect(wrapper.find('.modal').exists()).toBe(true);
      expect(wrapper.find('.modal-title').text()).toContain('Create New Doctor');
    });

    it('renders all form inputs', () => {
      const inputs = wrapper.findAll('input');
      expect(inputs.length).toBe(3);
    });

    it('renders form labels', () => {
      const labels = wrapper.findAll('label');
      expect(labels.length).toBeGreaterThanOrEqual(3);
      expect(labels.at(0).text()).toContain('Name');
      expect(labels.at(1).text()).toContain('Specialization');
      expect(labels.at(2).text()).toContain('Availability');
    });

    it('renders submit button', () => {
      const submitButton = wrapper.findAll('button').filter(btn => btn.text().includes('Create Doctor'));
      expect(submitButton.length).toBeGreaterThan(0);
    });

    it('renders cancel button', () => {
      const cancelButton = wrapper.findAll('button').filter(btn => btn.text().includes('Cancel'));
      expect(cancelButton.length).toBeGreaterThan(0);
    });
  });

  describe('Form Input Binding', () => {
    it('binds name input correctly', async () => {
      const nameInput = wrapper.findAll('input').at(0);
      await nameInput.setValue('Dr. John Doe');
      expect(wrapper.vm.formData.name).toBe('Dr. John Doe');
    });

    it('binds specialization input correctly', async () => {
      const specializationInput = wrapper.findAll('input').at(1);
      await specializationInput.setValue('Cardiology');
      expect(wrapper.vm.formData.specialization).toBe('Cardiology');
    });

    it('binds availability input correctly', async () => {
      const availabilityInput = wrapper.findAll('input').at(2);
      await availabilityInput.setValue('Mon-Fri 9AM-5PM');
      expect(wrapper.vm.formData.availability).toBe('Mon-Fri 9AM-5PM');
    });
  });

  describe('Form Validation', () => {
    it('shows error when name is empty', async () => {
      wrapper.vm.formData.name = '';
      wrapper.vm.formData.specialization = 'Cardiology';
      wrapper.vm.formData.availability = 'Mon-Fri';

      await wrapper.vm.submitCreate();

      expect(wrapper.vm.error).toBe('Doctor name is required');
      expect(wrapper.vm.isLoading).toBe(false);
    });

    it('shows error when specialization is empty', async () => {
      wrapper.vm.formData.name = 'Dr. John';
      wrapper.vm.formData.specialization = '';
      wrapper.vm.formData.availability = 'Mon-Fri';

      await wrapper.vm.submitCreate();

      expect(wrapper.vm.error).toBe('Specialization is required');
      expect(wrapper.vm.isLoading).toBe(false);
    });

    it('shows error when availability is empty', async () => {
      wrapper.vm.formData.name = 'Dr. John';
      wrapper.vm.formData.specialization = 'Cardiology';
      wrapper.vm.formData.availability = '';

      await wrapper.vm.submitCreate();

      expect(wrapper.vm.error).toBe('Availability is required');
      expect(wrapper.vm.isLoading).toBe(false);
    });

    it('clears error when user starts typing', async () => {
      wrapper.vm.error = 'Some error';
      wrapper.vm.formData.name = 'Dr. ';
      await wrapper.vm.$nextTick();
      expect(wrapper.vm.error).toBeNull();
    });
  });

  describe('API Integration', () => {
    it('makes POST request to correct endpoint', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, name: 'Dr. John' })
      });

      wrapper.vm.formData = {
        name: 'Dr. John Doe',
        specialization: 'Cardiology',
        availability: 'Mon-Fri 9AM-5PM'
      };

      await wrapper.vm.submitCreate();

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:5000/api/admin/create-doctor',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token'
          }),
          body: JSON.stringify({
            name: 'Dr. John Doe',
            specialization: 'Cardiology',
            availability: 'Mon-Fri 9AM-5PM'
          })
        })
      );
    });

    it('uses getAuthHeaders for authorization', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, name: 'Dr. John' })
      });

      wrapper.vm.formData = {
        name: 'Dr. John Doe',
        specialization: 'Cardiology',
        availability: 'Mon-Fri 9AM-5PM'
      };

      await wrapper.vm.submitCreate();

      expect(tokenManager.getAuthHeaders).toHaveBeenCalled();
    });
  });

  describe('Success Event Emission', () => {
    it('emits created event on successful submission', async () => {
      const mockResponse = { id: 1, name: 'Dr. John Doe' };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      wrapper.vm.formData = {
        name: 'Dr. John Doe',
        specialization: 'Cardiology',
        availability: 'Mon-Fri 9AM-5PM'
      };

      await wrapper.vm.submitCreate();
      await wrapper.vm.$nextTick();

      expect(wrapper.emitted('created')).toBeTruthy();
      expect(wrapper.emitted('created')[0][0]).toEqual(mockResponse);
    });

    it('resets form after successful submission', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, name: 'Dr. John' })
      });

      wrapper.vm.formData = {
        name: 'Dr. John Doe',
        specialization: 'Cardiology',
        availability: 'Mon-Fri 9AM-5PM'
      };

      await wrapper.vm.submitCreate();
      await wrapper.vm.$nextTick();

      expect(wrapper.vm.formData.name).toBe('');
      expect(wrapper.vm.formData.specialization).toBe('');
      expect(wrapper.vm.formData.availability).toBe('');
    });

    it('shows success message on successful submission', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, name: 'Dr. John' })
      });

      wrapper.vm.formData = {
        name: 'Dr. John Doe',
        specialization: 'Cardiology',
        availability: 'Mon-Fri 9AM-5PM'
      };

      await wrapper.vm.submitCreate();
      await wrapper.vm.$nextTick();

      expect(wrapper.vm.success).toBe('Doctor created successfully!');
    });
  });

  describe('Error Handling', () => {
    it('handles API error response', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ message: 'Doctor already exists' })
      });

      wrapper.vm.formData = {
        name: 'Dr. John Doe',
        specialization: 'Cardiology',
        availability: 'Mon-Fri 9AM-5PM'
      };

      await wrapper.vm.submitCreate();
      await wrapper.vm.$nextTick();

      expect(wrapper.vm.error).toBe('Doctor already exists');
    });

    it('handles network errors', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      wrapper.vm.formData = {
        name: 'Dr. John Doe',
        specialization: 'Cardiology',
        availability: 'Mon-Fri 9AM-5PM'
      };

      await wrapper.vm.submitCreate();
      await wrapper.vm.$nextTick();

      expect(wrapper.vm.error).toContain('Network error');
    });

    it('displays error message in UI', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ message: 'Validation failed' })
      });

      wrapper.vm.formData = {
        name: 'Dr. John Doe',
        specialization: 'Cardiology',
        availability: 'Mon-Fri 9AM-5PM'
      };

      await wrapper.vm.submitCreate();
      await wrapper.vm.$nextTick();

      const errorAlert = wrapper.find('.alert-danger');
      expect(errorAlert.exists()).toBe(true);
      expect(errorAlert.text()).toContain('Validation failed');
    });
  });

  describe('Loading State', () => {
    it('sets isLoading to true during submission', async () => {
      global.fetch.mockImplementationOnce(
        () => new Promise(resolve => setTimeout(() => resolve({ ok: true, json: async () => ({}) }), 100))
      );

      wrapper.vm.formData = {
        name: 'Dr. John Doe',
        specialization: 'Cardiology',
        availability: 'Mon-Fri 9AM-5PM'
      };

      const submitPromise = wrapper.vm.submitCreate();
      await wrapper.vm.$nextTick();

      expect(wrapper.vm.isLoading).toBe(true);

      await submitPromise;
      await wrapper.vm.$nextTick();

      expect(wrapper.vm.isLoading).toBe(false);
    });

    it('disables submit button during loading', async () => {
      wrapper.vm.isLoading = true;
      await wrapper.vm.$nextTick();

      const submitButton = wrapper.findAll('button').filter(btn => btn.text().includes('Create Doctor'));
      expect(submitButton.at(0).attributes('disabled')).toBeDefined();
    });
  });

  describe('Form Reset', () => {
    it('clears all form data', () => {
      wrapper.vm.formData = {
        name: 'Dr. John Doe',
        specialization: 'Cardiology',
        availability: 'Mon-Fri 9AM-5PM'
      };
      wrapper.vm.error = 'Some error';
      wrapper.vm.success = 'Some success';

      wrapper.vm.resetForm();

      expect(wrapper.vm.formData.name).toBe('');
      expect(wrapper.vm.formData.specialization).toBe('');
      expect(wrapper.vm.formData.availability).toBe('');
      expect(wrapper.vm.error).toBeNull();
      expect(wrapper.vm.success).toBeNull();
    });
  });

  describe('Modal Interaction', () => {
    it('closes modal on successful submission', async () => {
      jest.useFakeTimers();

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, name: 'Dr. John' })
      });

      wrapper.vm.formData = {
        name: 'Dr. John Doe',
        specialization: 'Cardiology',
        availability: 'Mon-Fri 9AM-5PM'
      };

      await wrapper.vm.submitCreate();
      jest.advanceTimersByTime(1500);

      jest.useRealTimers();
    });
  });

  describe('Data Initial State', () => {
    it('initializes with empty form data', () => {
      expect(wrapper.vm.formData.name).toBe('');
      expect(wrapper.vm.formData.specialization).toBe('');
      expect(wrapper.vm.formData.availability).toBe('');
    });

    it('initializes with no errors or success messages', () => {
      expect(wrapper.vm.error).toBeNull();
      expect(wrapper.vm.success).toBeNull();
    });

    it('initializes with isLoading as false', () => {
      expect(wrapper.vm.isLoading).toBe(false);
    });
  });
});
