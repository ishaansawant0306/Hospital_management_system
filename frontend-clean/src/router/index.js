import { createRouter, createWebHistory } from 'vue-router';
import { getUserRole, getToken } from '../utils/tokenManager';



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
    path: '/register',
    name: 'Register',
    component: () => import('../components/Register.vue'),
    meta: {
      title: 'Hospital Management - Register',
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
  const token = getToken();
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
    // Allow access to login/register even if authenticated
    // This fixes the issue where users couldn't access login page to switch accounts
    next();
  }
});

router.afterEach((to, from) => {
  console.log(`Navigated from ${from.path} to ${to.path}`);
});

export default router;
