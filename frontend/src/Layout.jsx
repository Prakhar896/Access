import { Box, Button, Heading, Spinner, Text, useToast } from '@chakra-ui/react'
import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Outlet, useNavigate } from 'react-router-dom'
import configureShowToast from './components/showToast'
import { fetchSession, setDisableSessionCheck } from './slices/AuthState'

function Layout() {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const toast = useToast();
    const showToast = configureShowToast(toast);
    const { disableSessionCheck } = useSelector(state => state.auth);

    useEffect(() => {
        dispatch(fetchSession());
    }, [])

    useEffect(() => {
        if (disableSessionCheck == true) {
            dispatch(setDisableSessionCheck(false));
        }
    }, [disableSessionCheck])

    return (
        <div className='defaultLayout'>
            <Outlet />
        </div>
    )
}

export default Layout