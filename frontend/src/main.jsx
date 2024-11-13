import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { ChakraProvider } from '@chakra-ui/react'
import { configureStore } from '@reduxjs/toolkit'
import Layout from './Layout.jsx'
import universalReducer from './slices/UniversalState.js'
import authReducer from './slices/AuthState.js'
import { Provider } from 'react-redux'
import MainTheme from './themes/MainTheme.js'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Version from './pages/Version.jsx'
import Home from './pages/Home.jsx'

const store = configureStore({
    reducer: {
        universal: universalReducer,
        auth: authReducer
    }
})

createRoot(document.getElementById('root')).render(
    <Provider store={store}>
        <ChakraProvider theme={MainTheme} toastOptions={{ defaultOptions: { position: 'bottom-right' } }}>
            <BrowserRouter>
                <Routes>
                    <Route path='/' element={<Layout />}>
                        <Route index element={<Home />} />
                    </Route>
                </Routes>
            </BrowserRouter>
        </ChakraProvider>
    </Provider>
)
