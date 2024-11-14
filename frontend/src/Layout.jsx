import { Box, Button, Heading, Spinner, Text, useToast } from '@chakra-ui/react'
import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Outlet, useNavigate } from 'react-router-dom'
import configureShowToast from './components/showToast'
import { fetchSession } from './slices/AuthState'

function Layout() {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const toast = useToast();
    const showToast = configureShowToast(toast);

    useEffect(() => {
        dispatch(fetchSession());
    }, [])

    return (
        <div className='defaultLayout'>
            <Outlet />
        </div>
    )
}

export default Layout