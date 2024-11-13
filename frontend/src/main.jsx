import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { ChakraProvider } from '@chakra-ui/react'
import { configureStore } from '@reduxjs/toolkit'
import App from './App.jsx'
import universalReducer from './slices/UniversalState.js'
import { Provider } from 'react-redux'
import MainTheme from './themes/MainTheme.js'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Version from './pages/Version.jsx'

const store = configureStore({
    reducer: {
        universal: universalReducer
    }
})

createRoot(document.getElementById('root')).render(
    <Provider store={store}>
        <ChakraProvider theme={MainTheme} toastOptions={{ defaultOptions: { position: 'bottom-right' } }}>
            <BrowserRouter>
                <Routes>
                    <Route path={'/'} element={<App />} />
                    <Route path='/version' element={<Version />} />
                </Routes>
            </BrowserRouter>
        </ChakraProvider>
    </Provider>
)
