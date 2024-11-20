import React from 'react'
import { Box, Heading, useMediaQuery, useToast } from '@chakra-ui/react';
import configureShowToast from '../../components/showToast';
import { useSelector } from 'react-redux';

function MyAccount() {
    const { username, loaded } = useSelector(state => state.auth);
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");

    const toast = useToast();
    const showToast = configureShowToast(toast);

    return (
        <Box display={'flex'} flexDir={'column'} justifyContent={'left'} m={!limitedScreen ? '1rem' : '10px'} p={'10px'}>
            <Box display={'flex'} justifyContent={'left'} flexDirection={'row'} alignItems={'center'}>
                <Heading as={'h1'} fontSize={'3xl'} fontFamily={'Ubuntu'}>My Account</Heading>
            </Box>
        </Box>
    )
}

export default MyAccount;