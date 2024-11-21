import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { ChakraProvider, ColorModeScript } from '@chakra-ui/react'
import { configureStore } from '@reduxjs/toolkit'
import Layout from './Layout.jsx'
import AuthLayout from './AuthLayout.jsx'
import universalReducer from './slices/UniversalState.js'
import authReducer from './slices/AuthState.js'
import { Provider } from 'react-redux'
import MainTheme from './themes/MainTheme.js'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Version from './pages/Version.jsx'
import Home from './pages/Home.jsx'
import SignUp from './pages/SignUp.jsx'
import Login from './pages/Login.jsx'
import Directory from './pages/portal/Directory.jsx'
import VerifyEmail from './pages/VerifyEmail.jsx'
import MyAccount from './pages/portal/MyAccount.jsx'
import NavLayout from './NavLayout.jsx'
import ForgotPassword from './pages/ForgotPassword.jsx'

const store = configureStore({
    reducer: {
        universal: universalReducer,
        auth: authReducer
    }
})

createRoot(document.getElementById('root')).render(
    <Provider store={store}>
        <ChakraProvider theme={MainTheme} toastOptions={{ defaultOptions: { position: 'bottom-right' } }}>
            <ColorModeScript initialColorMode={MainTheme.config.initialColorMode} />
            <BrowserRouter>
                <Routes>
                    <Route path='/' element={<Layout />}>
                        <Route index element={<Home />} />
                        <Route path='signup' element={<SignUp />} />
                        <Route path='login' element={<Login />} />
                        <Route path='verifyEmail' element={<VerifyEmail />} />
                        <Route path='forgotPassword' element={<ForgotPassword />} />
                        <Route path='portal' element={<AuthLayout />}>
                            <Route element={<NavLayout />}>
                                <Route path='files' element={<Directory />} />
                                <Route path='account' element={<MyAccount />} />
                            </Route>
                        </Route>
                    </Route>
                </Routes>
            </BrowserRouter>
        </ChakraProvider>
    </Provider>
)
