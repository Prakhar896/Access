import React from 'react'
import withAuth from '../../components/hoc/withAuth'
import { Box, Heading, Text } from '@chakra-ui/react';
import { useSelector } from 'react-redux';
import withNavbar from '../../components/hoc/withNavbar';

function Directory() {
    const { username } = useSelector(state => state.auth);

    return (
        <Box display={'flex'} flexDir={'column'} justifyContent={'left'} m={'1rem'} p={'10px'}>
            <Heading as={'h1'} fontSize={'3xl'} fontFamily={'Ubuntu'}>My Files</Heading>
        </Box>
    )
}

export default withAuth(withNavbar(Directory));