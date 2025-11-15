import { createRouter, createWebHistory } from 'vue-router';
import { getUserRole } from '../utils/tokenManager';



const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../components/Login.vue'),
    meta: {
      title: 'Hospital Management - Login',
      requiresAuth: false
    }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('../components/AdminDashboard.vue'),
    meta: {
      title: 'Hospital Management - Admin Dashboard',
      requiresAuth: true,
      requiredRole: 'Admin'
    }
  },
  {
    path: '/doctor',
    name: 'DoctorDashboard',
    component: () => import('../components/DoctorDashboard.vue'),
    meta: {
      title: 'Hospital Management - Doctor Dashboard',
      requiresAuth: true,
      requiredRole: 'Doctor'
    }
  },
  {
    path: '/patient',
    name: 'PatientDashboard',
    component: () => import('../components/PatientDashboard.vue'),
    meta: {
      title: 'Hospital Management - Patient Dashboard',
      requiresAuth: true,
      requiredRole: 'Patient'
    }
  },

  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const requiresAuth = to.meta.requiresAuth;
  const requiredRole = to.meta.requiredRole;
  const token = localStorage.getItem('access_token');
  const userRole = getUserRole();

  if (to.meta.title) {
    document.title = to.meta.title;
  }

  if (requiresAuth) {
    if (!token) {
      next('/login');
    } else if (requiredRole && userRole !== requiredRole) {
      next('/login');
    } else {
      next();
    }
  } else {
    if (token && to.path === '/login') {
      const role = getUserRole();
      if (role === 'Admin') {
        next('/admin');
      } else if (role === 'Doctor') {
        next('/doctor');
      } else if (role === 'Patient') {
        next('/patient');
      } else {
        next('/login');
    }
    } else {
      next();
    }
  }
});

router.afterEach((to, from) => {
  console.log(`Navigated from ${from.path} to ${to.path}`);
});

export default router;
