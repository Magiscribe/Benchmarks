import Layout from '@/components/layouts/Layout';
import Home from '@/pages';
import Dashboard from '@/pages/dashboard';
import AuthConfirm from '@/pages/auth/confirm';
import AuthRequestResetPassword from '@/pages/auth/request-reset';
import AuthResetPassword from '@/pages/auth/reset';
import AuthSettings from '@/pages/auth/settings';
import AuthSignIn from '@/pages/auth/sign-in';
import AuthSignUp from '@/pages/auth/sign-up';
import { Protected } from '@/providers/Protected';
import { Outlet, createBrowserRouter } from 'react-router-dom';

// Auth Routes
const AuthRoutes = [
  { path: 'sign-up', element: <AuthSignUp /> },
  { path: 'sign-in', element: <AuthSignIn /> },
  { path: 'confirm', element: <AuthConfirm /> },
  { path: 'request-reset', element: <AuthRequestResetPassword /> },
  { path: 'reset', element: <AuthResetPassword /> },
  { path: 'settings', element: <AuthSettings /> }
];

// Main App Routes
const ProtectedAppRoutes = [
  {
    path: '/dashboard',
    element: <Dashboard />
  }
];

// Check if authentication is disabled
const authDisabled = import.meta.env.VITE_ENABLE_COGNITO_LOGIN !== 'true' && 
                    import.meta.env.VITE_ENABLE_CUSTOM_PROVIDER !== 'true';

// Root Router Configuration
const routerConfig = [
  {
    element: <Layout />,
    children: [
      {
        path: '/',
        element: <Home />
      },
      // Conditionally wrap routes with protection based on auth config
      {
        element: authDisabled ? <Outlet /> : (
          <Protected>
            <Outlet />
          </Protected>
        ),
        children: ProtectedAppRoutes
      },
      // Only include auth routes if authentication is enabled
      ...(authDisabled ? [] : [{
        path: '/auth',
        children: AuthRoutes
      }])
    ]
  }
];

const router = createBrowserRouter(routerConfig);

export default router;
